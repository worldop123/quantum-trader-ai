from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import asyncio

from app.config import settings
from app.database import engine, Base, get_db
from app.models import User
from app.api import api_router
from app.websocket import manager
from app.services import get_password_hash, market_data_service

# 创建数据库表
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    # 启动时初始化默认用户
    db = next(get_db())
    try:
        # 创建普通测试用户
        test_user = db.query(User).filter(User.email == "test@quantumtrader.ai").first()
        if not test_user:
            test_user = User(
                email="test@quantumtrader.ai",
                username="testuser",
                hashed_password=get_password_hash("Test123456"),
                is_active=True,
                is_admin=False,
            )
            db.add(test_user)

        # 创建管理员用户
        admin_user = db.query(User).filter(User.email == "admin@quantumtrader.ai").first()
        if not admin_user:
            admin_user = User(
                email="admin@quantumtrader.ai",
                username="admin",
                hashed_password=get_password_hash("Admin123456"),
                is_active=True,
                is_admin=True,
            )
            db.add(admin_user)

        db.commit()
        print("✅ 默认用户初始化完成")
        print(f"   普通用户: test@quantumtrader.ai / Test123456")
        print(f"   管理员: admin@quantumtrader.ai / Admin123456")
    except Exception as e:
        print(f"⚠️  初始化用户时出错: {e}")
        db.rollback()
    finally:
        db.close()

    # 启动行情数据推送服务
    await market_data_service.start()

    yield
    # 关闭时的清理工作
    await market_data_service.stop()
    print("👋 应用关闭中...")


app = FastAPI(
    title="QuantumTrader AI量化交易系统",
    description="专业的AI量化交易平台后端API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router)


# WebSocket端点
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    """WebSocket连接端点

    连接时需要在query参数中传递token进行认证
    支持的消息类型：
    - ping: 心跳
    - subscribe: 订阅频道 {type: "subscribe", channel: "ticker:BTC-USDT"}
    - unsubscribe: 取消订阅 {type: "unsubscribe", channel: "ticker:BTC-USDT"}
    - unsubscribe_all: 取消所有订阅
    """
    from jose import JWTError, jwt
    import json

    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket, user_id)

    try:
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data) if isinstance(data, str) else data
                msg_type = message.get("type")

                if msg_type == "ping":
                    # 心跳响应
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": int(asyncio.get_event_loop().time() * 1000)
                    })

                elif msg_type == "subscribe":
                    # 订阅频道
                    channel = message.get("channel")
                    if channel:
                        manager.subscribe(channel, user_id, websocket)
                        await websocket.send_json({
                            "type": "subscribed",
                            "channel": channel,
                            "success": True
                        })

                elif msg_type == "unsubscribe":
                    # 取消订阅
                    channel = message.get("channel")
                    if channel:
                        manager.unsubscribe(channel, user_id, websocket)
                        await websocket.send_json({
                            "type": "unsubscribed",
                            "channel": channel,
                            "success": True
                        })

                elif msg_type == "unsubscribe_all":
                    # 取消所有订阅
                    manager.unsubscribe_all(user_id, websocket)
                    await websocket.send_json({
                        "type": "unsubscribed_all",
                        "success": True
                    })

                elif msg_type == "get_status":
                    # 获取连接状态
                    await websocket.send_json({
                        "type": "status",
                        "data": {
                            "user_id": user_id,
                            "connections": manager.get_connection_count(),
                            "users": manager.get_user_count(),
                            "subscriptions": manager.get_subscription_count()
                        }
                    })

            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "QuantumTrader Backend"
    }


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "QuantumTrader AI量化交易系统",
        "version": "1.0.0",
        "docs": "/docs",
        "api_prefix": "/api",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
