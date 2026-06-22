"""
本地模型相关API接口
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models import User
from app.services import get_current_user
from app.services.local_model_service import local_model_service

router = APIRouter(prefix="/local-model", tags=["本地模型"])


class ChatMessage(BaseModel):
    role: str
    content: str


class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.7


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.7


@router.get("/models")
async def get_model_list(
    current_user: User = Depends(get_current_user),
):
    """获取本地模型列表"""
    models = local_model_service.get_model_list()
    return [
        {
            "id": m.id,
            "name": m.name,
            "description": m.description,
            "size_mb": m.size_mb,
            "model_type": m.model_type.value,
            "status": m.status.value,
            "quant_type": m.quant_type,
            "parameters": m.parameters,
            "context_length": m.context_length,
            "is_default": m.is_default,
        }
        for m in models
    ]


@router.get("/models/supported")
async def get_supported_models(
    current_user: User = Depends(get_current_user),
):
    """获取支持的模型列表（可下载）"""
    return local_model_service.get_supported_models()


@router.get("/models/{model_id}")
async def get_model(
    model_id: str,
    current_user: User = Depends(get_current_user),
):
    """获取指定模型信息"""
    model = local_model_service.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    return {
        "id": model.id,
        "name": model.name,
        "description": model.description,
        "size_mb": model.size_mb,
        "model_type": model.model_type.value,
        "status": model.status.value,
        "quant_type": model.quant_type,
        "parameters": model.parameters,
        "context_length": model.context_length,
        "is_default": model.is_default,
    }


@router.post("/models/{model_id}/set-default")
async def set_default_model(
    model_id: str,
    current_user: User = Depends(get_current_user),
):
    """设置默认模型"""
    success = local_model_service.set_default_model(model_id)
    if not success:
        raise HTTPException(status_code=404, detail="Model not found")

    return {"success": True, "message": "Default model updated"}


@router.get("/models/default")
async def get_default_model(
    current_user: User = Depends(get_current_user),
):
    """获取默认模型"""
    model = local_model_service.get_default_model()
    if not model:
        return None

    return {
        "id": model.id,
        "name": model.name,
        "description": model.description,
        "size_mb": model.size_mb,
        "model_type": model.model_type.value,
        "status": model.status.value,
        "quant_type": model.quant_type,
        "parameters": model.parameters,
        "context_length": model.context_length,
        "is_default": model.is_default,
    }


@router.post("/models/{model_id}/load")
async def load_model(
    model_id: str,
    current_user: User = Depends(get_current_user),
):
    """加载模型"""
    result = await local_model_service.load_model(model_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Model load failed"))

    return {"success": True, "message": result.get("message", "Model loaded")}


@router.post("/models/unload")
async def unload_model(
    current_user: User = Depends(get_current_user),
):
    """卸载当前模型"""
    await local_model_service.unload_model()
    return {"success": True, "message": "Model unloaded"}


@router.delete("/models/{model_id}")
async def delete_model(
    model_id: str,
    current_user: User = Depends(get_current_user),
):
    """删除模型"""
    success = local_model_service.delete_model(model_id)
    if not success:
        raise HTTPException(status_code=404, detail="Model not found")

    return {"success": True, "message": "Model deleted"}


@router.post("/generate")
async def generate_text(
    request: GenerateRequest,
    current_user: User = Depends(get_current_user),
):
    """生成文本"""
    try:
        result = await local_model_service.generate(
            prompt=request.prompt,
            max_tokens=request.max_tokens or 512,
            temperature=request.temperature or 0.7,
        )

        return {
            "text": result.text,
            "tokens_generated": result.tokens_generated,
            "tokens_per_second": result.tokens_per_second,
            "inference_time_ms": result.inference_time_ms,
            "prompt_tokens": result.prompt_tokens,
        }
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """对话式生成"""
    try:
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        result = await local_model_service.chat(
            messages=messages,
            max_tokens=request.max_tokens or 512,
            temperature=request.temperature or 0.7,
        )

        return {
            "text": result.text,
            "tokens_generated": result.tokens_generated,
            "tokens_per_second": result.tokens_per_second,
            "inference_time_ms": result.inference_time_ms,
            "prompt_tokens": result.prompt_tokens,
        }
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status")
async def get_model_status(
    current_user: User = Depends(get_current_user),
):
    """获取当前模型状态"""
    current = local_model_service.current_model
    if not current:
        return {
            "loaded": False,
            "model": None,
        }

    return {
        "loaded": True,
        "model": {
            "id": current.id,
            "name": current.name,
            "status": current.status.value,
        },
    }
