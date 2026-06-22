"""
本地模型服务
基于llama.cpp的本地大模型推理服务

依赖：llama-cpp-python (pip install llama-cpp-python)
若未安装该依赖，服务会自动降级为不可用状态，并返回友好的提示信息。
"""
import os
import time
import glob
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

# 尝试导入 llama_cpp，如果不可用则标记为不可用
try:
    from llama_cpp import Llama
    _LLAMA_AVAILABLE = True
    _LLAMA_IMPORT_ERROR = None
except ImportError as _e:
    Llama = None  # type: ignore
    _LLAMA_AVAILABLE = False
    _LLAMA_IMPORT_ERROR = str(_e)


class ModelStatus(Enum):
    """模型状态"""
    NOT_DOWNLOADED = "not_downloaded"
    DOWNLOADING = "downloading"
    READY = "ready"
    LOADING = "loading"
    RUNNING = "running"
    ERROR = "error"


class ModelType(Enum):
    """模型类型"""
    TEXT_GENERATION = "text_generation"
    EMBEDDING = "embedding"
    MULTIMODAL = "multimodal"


@dataclass
class LocalModel:
    """本地模型信息"""
    id: str
    name: str
    description: str
    path: str
    size_mb: int
    model_type: ModelType
    status: ModelStatus
    quant_type: str  # 量化类型：q4_0, q4_1, q5_0, q5_1, q8_0, f16
    parameters: str  # 参数规模：7B, 13B, 34B等
    context_length: int  # 上下文长度
    is_default: bool = False


@dataclass
class InferenceResult:
    """推理结果"""
    text: str
    tokens_generated: int
    tokens_per_second: float
    inference_time_ms: float
    prompt_tokens: int


# 推荐模型列表（含HuggingFace下载URL）
SUPPORTED_MODELS: List[Dict[str, Any]] = [
    {
        "id": "deepseek-coder-6.7b-instruct-q4_k_m",
        "name": "DeepSeek Coder 6.7B Instruct",
        "description": "DeepSeek代码大模型，适合代码生成和分析，量化版本可在消费级显卡上运行",
        "size_mb": 4060,
        "quant_type": "q4_k_m",
        "parameters": "6.7B",
        "context_length": 16384,
        "download_url": "https://huggingface.co/TheBloke/deepseek-coder-6.7B-instruct-GGUF/resolve/main/deepseek-coder-6.7b-instruct.Q4_K_M.gguf",
    },
    {
        "id": "llama-3-8b-instruct-q4_k_m",
        "name": "Llama 3 8B Instruct",
        "description": "Meta Llama 3指令微调模型，通用对话能力强，推荐作为默认模型",
        "size_mb": 4920,
        "quant_type": "q4_k_m",
        "parameters": "8B",
        "context_length": 8192,
        "download_url": "https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf",
    },
    {
        "id": "qwen2-7b-instruct-q4_k_m",
        "name": "Qwen2 7B Instruct",
        "description": "阿里通义千问2代指令模型，中文表现优秀，适合量化策略分析",
        "size_mb": 4420,
        "quant_type": "q4_k_m",
        "parameters": "7B",
        "context_length": 32768,
        "download_url": "https://huggingface.co/Qwen/Qwen2-7B-Instruct-GGUF/resolve/main/qwen2-7b-instruct-q4_k_m.gguf",
    },
    {
        "id": "phi-3-mini-4k-instruct-q4_k_m",
        "name": "Phi-3 Mini 4K Instruct",
        "description": "微软Phi-3轻量模型，仅需2GB内存，适合资源受限环境",
        "size_mb": 2190,
        "quant_type": "q4_k_m",
        "parameters": "3.8B",
        "context_length": 4096,
        "download_url": "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4_k_m.gguf",
    },
    {
        "id": "mistral-7b-instruct-v0.2-q4_k_m",
        "name": "Mistral 7B Instruct v0.2",
        "description": "Mistral 7B指令模型，推理速度快，通用能力强",
        "size_mb": 4370,
        "quant_type": "q4_k_m",
        "parameters": "7B",
        "context_length": 32768,
        "download_url": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
    },
]


class LocalModelService:
    """本地模型服务"""

    def __init__(self, models_dir: str = "./models"):
        self.models_dir = models_dir
        self.models: Dict[str, LocalModel] = {}
        self.current_model: Optional[LocalModel] = None
        self._llama = None  # llama.cpp实例
        self._llama_available = _LLAMA_AVAILABLE
        self._llama_import_error = _LLAMA_IMPORT_ERROR

        # 确保模型目录存在
        os.makedirs(models_dir, exist_ok=True)

        # 初始化时扫描一次模型
        self.scan_models()

    def scan_models(self) -> List[LocalModel]:
        """扫描本地模型目录下的 .gguf 文件"""
        self.models = {}
        found_models: List[LocalModel] = []

        # 扫描 models_dir 下的所有 .gguf 文件
        if os.path.exists(self.models_dir):
            gguf_files = glob.glob(os.path.join(self.models_dir, "**", "*.gguf"), recursive=True)
            for filepath in gguf_files:
                try:
                    model = self._parse_gguf_file(filepath)
                    if model:
                        self.models[model.id] = model
                        found_models.append(model)
                except Exception as e:
                    print(f"⚠️  解析模型文件失败 {filepath}: {e}")

        # 补充推荐模型列表中尚未下载的模型
        for supported in SUPPORTED_MODELS:
            if supported["id"] not in self.models:
                model = LocalModel(
                    id=supported["id"],
                    name=supported["name"],
                    description=supported["description"],
                    path=os.path.join(self.models_dir, f"{supported['id']}.gguf"),
                    size_mb=supported["size_mb"],
                    model_type=ModelType.TEXT_GENERATION,
                    status=ModelStatus.NOT_DOWNLOADED,
                    quant_type=supported["quant_type"],
                    parameters=supported["parameters"],
                    context_length=supported["context_length"],
                    is_default=(supported["id"] == "llama-3-8b-instruct-q4_k_m"),
                )
                self.models[model.id] = model
                found_models.append(model)

        return found_models

    def _parse_gguf_file(self, filepath: str) -> Optional[LocalModel]:
        """从 .gguf 文件路径解析模型信息"""
        filename = os.path.basename(filepath)
        name_without_ext = os.path.splitext(filename)[0]

        # 获取文件大小（MB）
        try:
            size_bytes = os.path.getsize(filepath)
            size_mb = int(size_bytes / (1024 * 1024))
        except OSError:
            size_mb = 0

        # 尝试从文件名推断量化类型和参数规模
        quant_type = "unknown"
        for qt in ["q4_0", "q4_1", "q5_0", "q5_1", "q8_0", "f16", "q4_k_m", "q5_k_m", "q6_k"]:
            if qt in name_without_ext.lower():
                quant_type = qt
                break

        parameters = "unknown"
        for p in ["70b", "34b", "13b", "8b", "7b", "6.7b", "3.8b", "3b", "1.5b", "1b"]:
            if p in name_without_ext.lower():
                parameters = p.upper()
                break

        # 生成友好的显示名称
        display_name = name_without_ext.replace("-", " ").replace("_", " ").title()

        return LocalModel(
            id=name_without_ext,
            name=display_name,
            description=f"本地模型文件: {filename}",
            path=filepath,
            size_mb=size_mb,
            model_type=ModelType.TEXT_GENERATION,
            status=ModelStatus.READY,
            quant_type=quant_type,
            parameters=parameters,
            context_length=8192,
            is_default=False,
        )

    def get_model_list(self) -> List[LocalModel]:
        """获取模型列表"""
        if not self.models:
            self.scan_models()
        return list(self.models.values())

    def get_model(self, model_id: str) -> Optional[LocalModel]:
        """获取指定模型"""
        return self.models.get(model_id)

    def set_default_model(self, model_id: str) -> bool:
        """设置默认模型"""
        if model_id not in self.models:
            return False

        for model in self.models.values():
            model.is_default = False

        self.models[model_id].is_default = True
        return True

    def get_default_model(self) -> Optional[LocalModel]:
        """获取默认模型"""
        for model in self.models.values():
            if model.is_default:
                return model
        return None

    async def load_model(self, model_id: str) -> Dict[str, Any]:
        """加载模型

        Returns:
            Dict包含 success (bool) 和 message (str)
        """
        model = self.models.get(model_id)
        if not model:
            return {"success": False, "message": f"模型不存在: {model_id}"}

        # 检查 llama_cpp 是否可用
        if not self._llama_available:
            model.status = ModelStatus.ERROR
            return {
                "success": False,
                "message": "本地模型未安装，请安装 llama-cpp-python (pip install llama-cpp-python) 后重试",
            }

        # 检查模型文件是否存在
        if not os.path.exists(model.path):
            model.status = ModelStatus.NOT_DOWNLOADED
            return {
                "success": False,
                "message": f"模型文件不存在: {model.path}，请先下载模型",
            }

        model.status = ModelStatus.LOADING

        try:
            # 真实加载模型
            self._llama = Llama(
                model_path=model.path,
                n_ctx=model.context_length,
                n_gpu_layers=0,  # 默认使用CPU，可根据环境调整
                verbose=False,
            )
            model.status = ModelStatus.READY
            self.current_model = model
            return {"success": True, "message": f"模型 {model.name} 加载成功"}
        except Exception as e:
            model.status = ModelStatus.ERROR
            self._llama = None
            return {"success": False, "message": f"模型加载失败: {str(e)}"}

    async def unload_model(self) -> bool:
        """卸载当前模型"""
        if self.current_model:
            self.current_model.status = ModelStatus.READY
            self.current_model = None
            self._llama = None
        return True

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        stop: Optional[List[str]] = None,
    ) -> InferenceResult:
        """生成文本

        如果 llama_cpp 可用则进行真实推理；
        如果不可用则返回说明性文本（非"开发中"）。
        """
        start_time = time.time()

        # 检查 llama_cpp 是否可用
        if not self._llama_available:
            text = (
                "本地模型未安装，请安装 llama-cpp-python（pip install llama-cpp-python）后重试。"
                "安装完成后，下载 .gguf 模型文件到 ./models/ 目录即可使用本地推理。"
            )
            inference_time = time.time() - start_time
            return InferenceResult(
                text=text,
                tokens_generated=len(text),
                tokens_per_second=len(text) / inference_time if inference_time > 0 else 0,
                inference_time_ms=inference_time * 1000,
                prompt_tokens=len(prompt),
            )

        # 检查是否有已加载的模型
        if not self.current_model or self.current_model.status != ModelStatus.READY or self._llama is None:
            raise RuntimeError("No model loaded")

        # 真实推理
        try:
            output = self._llama(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop or [],
                echo=False,
            )

            generated_text = output.get("choices", [{}])[0].get("text", "")
            usage = output.get("usage", {})
            tokens_generated = usage.get("completion_tokens", len(generated_text))
            prompt_tokens = usage.get("prompt_tokens", len(prompt))

            inference_time = time.time() - start_time

            return InferenceResult(
                text=generated_text,
                tokens_generated=tokens_generated,
                tokens_per_second=tokens_generated / inference_time if inference_time > 0 else 0,
                inference_time_ms=inference_time * 1000,
                prompt_tokens=prompt_tokens,
            )
        except Exception as e:
            raise RuntimeError(f"推理失败: {str(e)}")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> InferenceResult:
        """对话式生成"""
        # 将消息格式化为prompt
        prompt = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt += f"System: {content}\n"
            elif role == "user":
                prompt += f"User: {content}\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n"

        prompt += "Assistant: "

        return await self.generate(prompt, max_tokens, temperature)

    def delete_model(self, model_id: str) -> bool:
        """删除模型文件"""
        model = self.models.get(model_id)
        if not model:
            return False

        # 删除实际的模型文件
        if os.path.exists(model.path):
            try:
                os.remove(model.path)
            except OSError as e:
                print(f"⚠️  删除模型文件失败: {e}")
                return False

        model.status = ModelStatus.NOT_DOWNLOADED
        # 重新扫描以更新列表
        self.scan_models()
        return True

    def get_supported_models(self) -> List[Dict[str, Any]]:
        """获取支持的模型列表（可下载，含HuggingFace下载URL）"""
        return list(SUPPORTED_MODELS)

    def is_llama_available(self) -> bool:
        """检查 llama_cpp 是否可用"""
        return self._llama_available


# 创建全局实例
local_model_service = LocalModelService()
