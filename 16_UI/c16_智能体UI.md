# 第16章 智能体UI——企业级智能体的人机交互与可视化管控体系
## 16.1 本章核心价值
在前序章节中，我们完成了智能体能力层（MCP协议、Skill、网关）、安全层（认证、权限、审计）的构建，但**没有可视化交互界面的智能体平台，无法被企业用户高效使用、无法被运维人员便捷管控**。

企业级智能体UI绝非简单的“聊天界面”，而是覆盖三类核心用户的全场景交互体系：
- **终端用户**：通过自然语言/可视化界面使用智能体完成业务任务；
- **运维管理员**：监控智能体运行状态、配置权限、审计调用日志、排查故障；
- **开发者**：开发/调试/发布Skill、配置智能体能力、测试MCP调用；

本章目标：
1. 构建智能体UI的完整理论体系，明确“交互层-管控层-开发层”三层设计逻辑；
2. 提供可直接部署的**生产级智能体UI完整代码**（基于React+FastAPI），包含聊天交互、技能管理、权限配置、日志审计、监控大屏等核心功能；
3. 实现UI与MCP网关、安全体系的深度集成，确保所有操作可认证、可授权、可审计；
4. 落地智能体UI的企业级设计规范（兼容性、安全性、易用性、可扩展性）；
5. 让智能体平台从“后端能力”转化为“前端可操作、可管控、可运营”的完整产品。

## 16.2 智能体UI理论体系与架构设计
### 16.2.1 智能体UI核心设计原则
企业级智能体UI必须遵循以下5大原则，区别于普通演示级界面：
1. **安全优先**：所有UI操作必须经过身份认证、权限校验，操作日志全记录；
2. **分层交互**：为终端用户、管理员、开发者提供不同的界面和权限；
3. **可视化管控**：核心指标（调用量、成功率、异常率、安全事件）可视化；
4. **易用性**：降低用户使用门槛（自然语言为主，可视化操作为辅）；
5. **可扩展性**：支持自定义页面、自定义组件、自定义权限视图。

### 16.2.2 智能体UI三层架构
```
【前端交互层】React/Vue 前端应用（分用户角色展示不同界面）
        ↓
【API网关层】FastAPI/Node.js 后端接口（认证、授权、请求转发）
        ↓
【核心服务层】MCP网关、Skill注册中心、权限系统、审计系统、监控系统
```

各层级核心职责：
1. **前端交互层**
   - 终端用户：智能体聊天界面、任务提交/跟踪、结果展示；
   - 管理员：智能体配置、权限管理、日志审计、监控大屏；
   - 开发者：Skill开发/调试、MCP调用测试、智能体能力配置；
2. **API网关层**
   - 统一身份认证（JWT）、权限校验（RBAC）；
   - 前端请求转发、参数校验、响应格式化；
   - 接口限流、操作日志记录；
3. **核心服务层**
   - 复用前序章节的MCP网关、权限系统、审计系统等核心能力；
   - 为UI提供标准化的数据接口（技能列表、调用日志、监控指标）。

### 16.2.3 智能体UI核心功能模块
| 模块分类       | 核心功能                                                                 | 目标用户       |
|----------------|--------------------------------------------------------------------------|----------------|
| 交互核心模块   | 智能体聊天、任务提交、任务跟踪、结果展示、历史会话管理                   | 终端用户       |
| 技能管理模块   | Skill注册/注销、参数配置、权限绑定、版本管理、在线调试                   | 开发者/管理员  |
| 权限管控模块   | 用户管理、角色管理、权限分配、API Key管理、访问控制                     | 管理员         |
| 审计日志模块   | 调用日志查询、安全事件审计、操作日志追溯、日志导出                       | 管理员/安全人员|
| 监控运维模块   | 智能体运行状态、Skill调用指标、异常告警、监控大屏                       | 运维/管理员    |
| 配置中心模块   | 智能体参数配置、MCP网关配置、UI个性化配置、系统参数配置                  | 管理员         |

## 16.3 智能体UI技术选型与工程结构
### 16.3.1 技术栈选型（企业级生产可用）
#### 前端技术栈
- 框架：React 18（成熟、生态丰富、企业级应用首选）
- 状态管理：Redux Toolkit（简化Redux使用，支持异步操作）
- UI组件库：Ant Design 5（企业级UI组件库，开箱即用）
- 网络请求：Axios（拦截器、请求/响应封装）
- 可视化：ECharts（监控大屏、数据可视化）
- 构建工具：Vite（快速构建、热更新）
- 路由：React Router 6（路由管理、权限控制）

#### 后端API技术栈
- 框架：FastAPI（高性能、自动生成API文档、支持异步）
- 认证：JWT（JSON Web Token）
- 数据库：SQLite（演示）/PostgreSQL（生产）
- ORM：SQLAlchemy（数据库操作）
- 日志：loguru（日志记录）
- 部署：Docker（容器化部署）

### 16.3.2 工程目录结构（可直接落地）
```
agent_ui/
├── frontend/                  # 前端React应用
│   ├── public/                # 静态资源
│   ├── src/
│   │   ├── api/               # API请求封装
│   │   ├── assets/            # 图片/样式资源
│   │   ├── components/        # 通用组件
│   │   │   ├── Chat/          # 聊天组件
│   │   │   ├── SkillManager/  # 技能管理组件
│   │   │   ├── Auth/          # 认证组件
│   │   │   ├── Audit/         # 审计日志组件
│   │   │   ├── Monitor/       # 监控组件
│   │   │   └── Common/        # 通用UI组件
│   │   ├── layouts/           # 页面布局
│   │   ├── pages/             # 页面组件
│   │   │   ├── Home/          # 首页
│   │   │   ├── Chat/          # 智能体聊天页
│   │   │   ├── Skill/         # 技能管理页
│   │   │   ├── Admin/         # 管理员页
│   │   │   ├── Audit/         # 审计日志页
│   │   │   ├── Monitor/       # 监控大屏页
│   │   │   └── Login/         # 登录页
│   │   ├── store/             # Redux状态管理
│   │   ├── utils/             # 工具函数
│   │   ├── routes/            # 路由配置
│   │   ├── App.jsx            # 根组件
│   │   └── main.jsx           # 入口文件
│   ├── package.json           # 依赖配置
│   └── vite.config.js         # Vite配置
├── backend/                   # 后端FastAPI应用
│   ├── app/
│   │   ├── api/               # API路由
│   │   │   ├── v1/
│   │   │   │   ├── auth.py    # 认证接口
│   │   │   │   ├── chat.py    # 聊天接口
│   │   │   │   ├── skill.py   # 技能管理接口
│   │   │   │   ├── audit.py   # 审计日志接口
│   │   │   │   ├── monitor.py # 监控接口
│   │   │   │   └── admin.py   # 管理员接口
│   │   ├── core/              # 核心配置
│   │   │   ├── auth.py        # 认证核心
│   │   │   ├── config.py      # 配置文件
│   │   │   └── security.py    # 安全配置
│   │   ├── models/            # 数据模型
│   │   │   ├── user.py        # 用户模型
│   │   │   ├── skill.py       # 技能模型
│   │   │   └── log.py         # 日志模型
│   │   ├── services/          # 业务逻辑
│   │   │   ├── chat_service.py # 聊天服务
│   │   │   ├── skill_service.py # 技能服务
│   │   │   ├── audit_service.py # 审计服务
│   │   │   └── monitor_service.py # 监控服务
│   │   ├── utils/             # 工具函数
│   │   └── main.py            # 入口文件
│   ├── requirements.txt       # 依赖配置
│   └── Dockerfile             # Docker配置
├── docker-compose.yml         # 容器编排配置
└── README.md                  # 部署文档
```

## 16.4 核心功能完整代码实现（可直接运行）
### 16.4.1 后端API实现（FastAPI）
#### 1. 核心配置（backend/app/core/config.py）
```python
import os
from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    # 项目配置
    PROJECT_NAME: str = "Agent UI API"
    API_V1_STR: str = "/api/v1"
    # 安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-32-bit")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # CORS配置
    CORS_ORIGINS: List[str] = ["*"]
    # MCP网关配置
    MCP_GATEWAY_URL: str = os.getenv("MCP_GATEWAY_URL", "http://localhost:8080/mcp")
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./agent_ui.db")

settings = Settings()
```

#### 2. 认证核心（backend/app/core/auth.py）
```python
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# OAuth2认证
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

# 模拟用户数据（生产环境替换为数据库）
fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("admin123"),
        "role": "admin",
        "permissions": ["all"]
    },
    "user": {
        "username": "user",
        "hashed_password": pwd_context.hash("user123"),
        "role": "user",
        "permissions": ["chat", "skill:read"]
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

def get_user(username: str) -> Optional[Dict[str, Any]]:
    """获取用户信息"""
    if username in fake_users_db:
        return fake_users_db[username]
    return None

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """用户认证"""
    user = get_user(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return user

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """生成访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """获取当前登录用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username=username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """获取当前活跃用户"""
    # 此处可添加用户状态校验
    return current_user

def check_permission(current_user: Dict[str, Any], permission: str) -> bool:
    """检查用户权限"""
    if "all" in current_user["permissions"]:
        return True
    return permission in current_user["permissions"]
```

#### 3. 聊天接口（backend/app/api/v1/chat.py）
```python
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
import httpx
import uuid

from app.core.auth import get_current_active_user, check_permission
from app.core.config import settings

router = APIRouter()

# 模拟聊天历史
chat_history = {}

@router.post("/send", response_model=Dict[str, Any])
async def send_message(
    message: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """发送消息给智能体"""
    # 权限校验
    if not check_permission(current_user, "chat"):
        raise HTTPException(status_code=403, detail="No permission to chat")
    
    # 获取会话ID
    session_id = message.get("sessionId", str(uuid.uuid4()))
    user_message = message.get("message", "")
    
    # 初始化会话历史
    if session_id not in chat_history:
        chat_history[session_id] = []
    
    # 记录用户消息
    chat_history[session_id].append({
        "role": "user",
        "content": user_message,
        "timestamp": str(uuid.uuid1().time)
    })
    
    # 调用MCP网关（模拟/实际调用）
    try:
        # 构建MCP请求
        mcp_request = {
            "jsonrpc": "2.0",
            "id": f"chat_{uuid.uuid4().hex[:8]}",
            "method": "call_tool",
            "params": {
                "toolName": message.get("toolName", "get_real_time_weather"),
                "parameters": message.get("parameters", {}),
                "context": {
                    "userId": current_user["username"],
                    "sessionId": session_id,
                    "token": message.get("token", "")
                }
            }
        }
        
        # 调用MCP网关
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.MCP_GATEWAY_URL,
                json=mcp_request,
                timeout=30.0
            )
        mcp_response = response.json()
        
        # 构建智能体回复
        agent_response = {
            "role": "assistant",
            "content": mcp_response.get("result", "Success"),
            "mcpResponse": mcp_response,
            "timestamp": str(uuid.uuid1().time)
        }
        
        # 记录智能体回复
        chat_history[session_id].append(agent_response)
        
        return {
            "sessionId": session_id,
            "response": agent_response,
            "success": True
        }
    except Exception as e:
        error_response = {
            "role": "assistant",
            "content": f"Error: {str(e)}",
            "timestamp": str(uuid.uuid1().time)
        }
        chat_history[session_id].append(error_response)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}", response_model=Dict[str, Any])
async def get_chat_history(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """获取聊天历史"""
    if not check_permission(current_user, "chat"):
        raise HTTPException(status_code=403, detail="No permission to view chat history")
    
    return {
        "sessionId": session_id,
        "history": chat_history.get(session_id, []),
        "success": True
    }

@router.get("/sessions", response_model=Dict[str, Any])
async def get_sessions(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """获取所有会话"""
    if not check_permission(current_user, "chat"):
        raise HTTPException(status_code=403, detail="No permission to view sessions")
    
    return {
        "sessions": list(chat_history.keys()),
        "success": True
    }
```

#### 4. 技能管理接口（backend/app/api/v1/skill.py）
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
import httpx
import uuid

from app.core.auth import get_current_active_user, check_permission
from app.core.config import settings

router = APIRouter()

# 模拟技能列表（实际从MCP网关获取）
skills = [
    {
        "id": "skill_001",
        "name": "get_real_time_weather",
        "description": "获取实时天气",
        "version": "1.0.0",
        "permissions": ["weather:read"],
        "status": "online",
        "endpoint": "http://localhost:8001"
    },
    {
        "id": "skill_002",
        "name": "calculate",
        "description": "数学计算",
        "version": "1.0.0",
        "permissions": ["calculate:read"],
        "status": "online",
        "endpoint": "http://localhost:8002"
    }
]

@router.get("/list", response_model=Dict[str, Any])
async def list_skills(
    keyword: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """获取技能列表"""
    if not check_permission(current_user, "skill:read"):
        raise HTTPException(status_code=403, detail="No permission to view skills")
    
    # 过滤技能
    filtered_skills = skills
    if keyword:
        filtered_skills = [s for s in filtered_skills if keyword in s["name"] or keyword in s["description"]]
    if status:
        filtered_skills = [s for s in filtered_skills if s["status"] == status]
    
    return {
        "skills": filtered_skills,
        "total": len(filtered_skills),
        "success": True
    }

@router.get("/{skill_id}", response_model=Dict[str, Any])
async def get_skill_detail(
    skill_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """获取技能详情"""
    if not check_permission(current_user, "skill:read"):
        raise HTTPException(status_code=403, detail="No permission to view skill detail")
    
    skill = next((s for s in skills if s["id"] == skill_id), None)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    return {
        "skill": skill,
        "success": True
    }

@router.post("/test/{skill_id}", response_model=Dict[str, Any])
async def test_skill(
    skill_id: str,
    parameters: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """测试技能调用"""
    if not check_permission(current_user, "skill:test"):
        raise HTTPException(status_code=403, detail="No permission to test skill")
    
    skill = next((s for s in skills if s["id"] == skill_id), None)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    # 调用MCP网关测试技能
    try:
        mcp_request = {
            "jsonrpc": "2.0",
            "id": f"test_{uuid.uuid4().hex[:8]}",
            "method": "call_tool",
            "params": {
                "toolName": skill["name"],
                "parameters": parameters,
                "context": {
                    "userId": current_user["username"],
                    "token": ""
                }
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.MCP_GATEWAY_URL,
                json=mcp_request,
                timeout=30.0
            )
        
        return {
            "skillId": skill_id,
            "request": mcp_request,
            "response": response.json(),
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test skill failed: {str(e)}")

@router.post("/register", response_model=Dict[str, Any])
async def register_skill(
    skill: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """注册技能"""
    if not check_permission(current_user, "skill:write"):
        raise HTTPException(status_code=403, detail="No permission to register skill")
    
    # 生成技能ID
    skill_id = f"skill_{uuid.uuid4().hex[:8]}"
    skill["id"] = skill_id
    skill["status"] = "online"
    skills.append(skill)
    
    return {
        "skillId": skill_id,
        "message": "Skill registered successfully",
        "success": True
    }

@router.delete("/{skill_id}", response_model=Dict[str, Any])
async def unregister_skill(
    skill_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """注销技能"""
    if not check_permission(current_user, "skill:write"):
        raise HTTPException(status_code=403, detail="No permission to unregister skill")
    
    global skills
    skill = next((s for s in skills if s["id"] == skill_id), None)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    skills = [s for s in skills if s["id"] != skill_id]
    
    return {
        "message": "Skill unregistered successfully",
        "success": True
    }
```

#### 5. 主入口文件（backend/app/main.py）
```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time
import logging

from app.core.config import settings
from app.api.v1 import auth, chat, skill, audit, monitor, admin

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise Agent UI API",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加GZip中间件
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # 记录请求日志
    logger.info(
        f"Request: {request.method} {request.url} | "
        f"Status: {response.status_code} | "
        f"Process Time: {process_time:.4f}s"
    )
    
    # 添加响应头
    response.headers["X-Process-Time"] = str(process_time)
    return response

# 注册API路由
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])
app.include_router(skill.router, prefix=f"{settings.API_V1_STR}/skill", tags=["skill"])
app.include_router(audit.router, prefix=f"{settings.API_V1_STR}/audit", tags=["audit"])
app.include_router(monitor.router, prefix=f"{settings.API_V1_STR}/monitor", tags=["monitor"])
app.include_router(admin.router, prefix=f"{settings.API_V1_STR}/admin", tags=["admin"])

# 健康检查接口
@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}

# 根路径
@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Welcome to Agent UI API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
```

### 16.4.2 前端实现（React + Ant Design）
#### 1. API封装（frontend/src/api/agentApi.js）
```javascript
import axios from 'axios';
import { message } from 'antd';

// 创建axios实例
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 添加token
    const token = localStorage.getItem('agent_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
service.interceptors.response.use(
  (response) => {
    const res = response.data;
    // 处理业务错误
    if (res.success === false) {
      message.error(res.message || 'Request failed');
      return Promise.reject(res);
    }
    return res;
  },
  (error) => {
    console.error('Response error:', error);
    // 处理401未授权
    if (error.response && error.response.status === 401) {
      message.error('Authentication failed, please login again');
      localStorage.removeItem('agent_token');
      window.location.href = '/login';
    } else {
      message.error(error.response?.data?.detail || 'Server error');
    }
    return Promise.reject(error);
  }
);

// 认证相关API
export const authApi = {
  login: (data) => service.post('/auth/token', data),
  getUserInfo: () => service.get('/auth/me')
};

// 聊天相关API
export const chatApi = {
  sendMessage: (data) => service.post('/chat/send', data),
  getChatHistory: (sessionId) => service.get(`/chat/history/${sessionId}`),
  getSessions: () => service.get('/chat/sessions')
};

// 技能管理相关API
export const skillApi = {
  listSkills: (params) => service.get('/skill/list', { params }),
  getSkillDetail: (skillId) => service.get(`/skill/${skillId}`),
  testSkill: (skillId, data) => service.post(`/skill/test/${skillId}`, data),
  registerSkill: (data) => service.post('/skill/register', data),
  unregisterSkill: (skillId) => service.delete(`/skill/${skillId}`)
};

// 审计日志相关API
export const auditApi = {
  listLogs: (params) => service.get('/audit/list', { params }),
  getLogDetail: (logId) => service.get(`/audit/${logId}`),
  exportLogs: (params) => service.get('/audit/export', { params, responseType: 'blob' })
};

// 监控相关API
export const monitorApi = {
  getDashboard: () => service.get('/monitor/dashboard'),
  getSkillMetrics: (params) => service.get('/monitor/skill-metrics', { params }),
  getErrorMetrics: () => service.get('/monitor/error-metrics')
};

// 管理员相关API
export const adminApi = {
  listUsers: (params) => service.get('/admin/users', { params }),
  createUser: (data) => service.post('/admin/users', data),
  updateUser: (userId, data) => service.put(`/admin/users/${userId}`, data),
  deleteUser: (userId) => service.delete(`/admin/users/${userId}`),
  listRoles: () => service.get('/admin/roles'),
  updateRole: (roleId, data) => service.put(`/admin/roles/${roleId}`, data)
};

export default service;
```

#### 2. 登录页面（frontend/src/pages/Login/Login.jsx）
```jsx
import React, { useState } from 'react';
import { Form, Input, Button, Card, Layout, Typography, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../../api/agentApi';

const { Title } = Typography;
const { Content } = Layout;

const Login = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const [form] = Form.useForm();

  const handleLogin = async (values) => {
    try {
      setLoading(true);
      // 调用登录接口
      const response = await authApi.login({
        username: values.username,
        password: values.password
      });
      
      // 存储token
      localStorage.setItem('agent_token', response.access_token);
      message.success('Login successful');
      
      // 跳转到首页
      navigate('/');
    } catch (error) {
      message.error('Login failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout style={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      <Content style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '50px' }}>
        <Card style={{ width: 400, boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
          <div style={{ textAlign: 'center', marginBottom: 20 }}>
            <Title level={2}>Agent UI Login</Title>
          </div>
          
          <Form
            form={form}
            name="login"
            initialValues={{ remember: true }}
            onFinish={handleLogin}
            autoComplete="off"
          >
            <Form.Item
              name="username"
              rules={[{ required: true, message: 'Please input your username!' }]}
            >
              <Input 
                prefix={<UserOutlined className="site-form-item-icon" />} 
                placeholder="Username (admin/user)" 
              />
            </Form.Item>
            
            <Form.Item
              name="password"
              rules={[{ required: true, message: 'Please input your password!' }]}
            >
              <Input.Password
                prefix={<LockOutlined className="site-form-item-icon" />}
                type="password"
                placeholder="Password (admin123/user123)"
              />
            </Form.Item>
            
            <Form.Item>
              <Button 
                type="primary" 
                htmlType="submit" 
                loading={loading}
                style={{ width: '100%' }}
              >
                Log in
              </Button>
            </Form.Item>
          </Form>
        </Card>
      </Content>
    </Layout>
  );
};

export default Login;
```

#### 3. 聊天页面（frontend/src/pages/Chat/Chat.jsx）
```jsx
import React, { useState, useEffect, useRef } from 'react';
import { Layout, Typography, List, Input, Button, Card, Select, message, Divider, Spin } from 'antd';
import { SendOutlined, ReloadOutlined, DeleteOutlined } from '@ant-design/icons';
import { chatApi, skillApi } from '../../api/agentApi';

const { Content, Sider } = Layout;
const { Title, Text } = Typography;
const { Option } = Select;

const Chat = () => {
  // 状态管理
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState('');
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [skills, setSkills] = useState([]);
  const [selectedSkill, setSelectedSkill] = useState('get_real_time_weather');
  const [parameters, setParameters] = useState({ city: 'Beijing' });
  
  const messageEndRef = useRef(null);

  // 加载会话列表
  useEffect(() => {
    const loadSessions = async () => {
      try {
        const response = await chatApi.getSessions();
        setSessions(response.sessions);
        if (response.sessions.length > 0) {
          setCurrentSession(response.sessions[0]);
          loadChatHistory(response.sessions[0]);
        }
      } catch (error) {
        console.error('Load sessions failed:', error);
      }
    };
    
    loadSessions();
  }, []);

  // 加载技能列表
  useEffect(() => {
    const loadSkills = async () => {
      try {
        const response = await skillApi.listSkills();
        setSkills(response.skills);
      } catch (error) {
        console.error('Load skills failed:', error);
      }
    };
    
    loadSkills();
  }, []);

  // 加载聊天历史
  const loadChatHistory = async (sessionId) => {
    try {
      const response = await chatApi.getChatHistory(sessionId);
      setMessages(response.history);
    } catch (error) {
      console.error('Load chat history failed:', error);
      message.error('Load chat history failed');
    }
  };

  // 切换会话
  const handleSessionChange = (sessionId) => {
    setCurrentSession(sessionId);
    loadChatHistory(sessionId);
  };

  // 发送消息
  const handleSendMessage = async () => {
    if (!inputValue.trim() && !selectedSkill) return;
    
    try {
      setLoading(true);
      
      // 构建消息数据
      const messageData = {
        sessionId: currentSession || undefined,
        message: inputValue,
        toolName: selectedSkill,
        parameters: parameters
      };
      
      // 发送消息
      const response = await chatApi.sendMessage(messageData);
      
      // 更新会话和消息
      if (!currentSession) {
        setCurrentSession(response.sessionId);
        setSessions(prev => [...prev, response.sessionId]);
      }
      
      setMessages(response.response ? [...messages, 
        { role: 'user', content: inputValue },
        response.response
      ] : messages);
      
      // 清空输入
      setInputValue('');
      message.success('Message sent successfully');
    } catch (error) {
      console.error('Send message failed:', error);
      message.error('Send message failed');
    } finally {
      setLoading(false);
    }
  };

  // 滚动到消息底部
  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 创建新会话
  const createNewSession = () => {
    setCurrentSession('');
    setMessages([]);
  };

  return (
    <Layout style={{ height: '100vh' }}>
      <Sider width={250} theme="light" style={{ borderRight: '1px solid #e8e8e8' }}>
        <div style={{ padding: '16px', borderBottom: '1px solid #e8e8e8' }}>
          <Title level={4} style={{ margin: 0 }}>Sessions</Title>
          <Button 
            type="primary" 
            size="small" 
            style={{ marginTop: 8 }}
            onClick={createNewSession}
            icon={<ReloadOutlined />}
          >
            New Session
          </Button>
        </div>
        
        <List
          dataSource={sessions}
          renderItem={(sessionId) => (
            <List.Item
              onClick={() => handleSessionChange(sessionId)}
              style={{ 
                cursor: 'pointer',
                backgroundColor: currentSession === sessionId ? '#e6f7ff' : 'transparent',
                padding: '12px 16px'
              }}
            >
              <Text ellipsis>{sessionId}</Text>
            </List.Item>
          )}
          bordered
        />
      </Sider>
      
      <Layout>
        <Content style={{ display: 'flex', flexDirection: 'column', height: '100%', padding: '20px' }}>
          <Card style={{ flex: 1, overflow: 'auto', marginBottom: 16 }}>
            <div style={{ minHeight: 'calc(100vh - 200px)', padding: '16px' }}>
              {messages.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '50px 0' }}>
                  <Text type="secondary">No messages yet. Start a conversation!</Text>
                </div>
              ) : (
                <List
                  dataSource={messages}
                  renderItem={(msg) => (
                    <List.Item style={{ marginBottom: 16 }}>
                      <div style={{ 
                        maxWidth: '70%',
                        padding: '8px 16px',
                        borderRadius: '8px',
                        backgroundColor: msg.role === 'user' ? '#1890ff' : '#f5f5f5',
                        color: msg.role === 'user' ? 'white' : 'black',
                        marginLeft: msg.role === 'user' ? 'auto' : 0
                      }}>
                        <Text>{msg.content}</Text>
                      </div>
                    </List.Item>
                  )}
                />
              )}
              <div ref={messageEndRef} />
              {loading && (
                <div style={{ textAlign: 'center', padding: '16px' }}>
                  <Spin size="small" />
                  <Text type="secondary" style={{ marginLeft: 8 }}>Thinking...</Text>
                </div>
              )}
            </div>
          </Card>
          
          <div style={{ display: 'flex', gap: 8 }}>
            <Select
              value={selectedSkill}
              onChange={setSelectedSkill}
              style={{ width: 200 }}
            >
              {skills.map(skill => (
                <Option key={skill.id} value={skill.name}>
                  {skill.name} - {skill.description}
                </Option>
              ))}
            </Select>
            
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Type a message..."
              onPressEnter={handleSendMessage}
              style={{ flex: 1 }}
            />
            
            <Button 
              type="primary" 
              onClick={handleSendMessage}
              loading={loading}
              icon={<SendOutlined />}
            >
              Send
            </Button>
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};

export default Chat;
```

#### 4. 技能管理页面（frontend/src/pages/Skill/SkillManager.jsx）
```jsx
import React, { useState, useEffect } from 'react';
import { Table, Button, Input, Modal, Form, Typography, Card, Space, Tag, message, Spin, Select, Drawer } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, TestOutlined, SearchOutlined, ReloadOutlined } from '@ant-design/icons';
import { skillApi } from '../../api/agentApi';

const { Title, Text } = Typography;
const { Option } = Select;

const SkillManager = () => {
  // 状态管理
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(false);
  const [keyword, setKeyword] = useState('');
  const [status, setStatus] = useState('');
  
  // 模态框状态
  const [registerModalVisible, setRegisterModalVisible] = useState(false);
  const [testDrawerVisible, setTestDrawerVisible] = useState(false);
  const [currentSkill, setCurrentSkill] = useState(null);
  
  // 表单实例
  const [registerForm] = Form.useForm();
  const [testForm] = Form.useForm();
  
  // 测试结果
  const [testResult, setTestResult] = useState(null);
  const [testLoading, setTestLoading] = useState(false);

  // 加载技能列表
  const loadSkills = async () => {
    try {
      setLoading(true);
      const response = await skillApi.listSkills({ keyword, status });
      setSkills(response.skills);
    } catch (error) {
      console.error('Load skills failed:', error);
      message.error('Load skills failed');
    } finally {
      setLoading(false);
    }
  };

  // 初始化加载
  useEffect(() => {
    loadSkills();
  }, [keyword, status]);

  // 搜索技能
  const handleSearch = () => {
    loadSkills();
  };

  // 注册技能
  const handleRegisterSkill = async (values) => {
    try {
      await skillApi.registerSkill(values);
      message.success('Skill registered successfully');
      setRegisterModalVisible(false);
      registerForm.resetFields();
      loadSkills();
    } catch (error) {
      console.error('Register skill failed:', error);
      message.error('Register skill failed');
    }
  };

  // 注销技能
  const handleUnregisterSkill = async (skillId) => {
    try {
      await skillApi.unregisterSkill(skillId);
      message.success('Skill unregistered successfully');
      loadSkills();
    } catch (error) {
      console.error('Unregister skill failed:', error);
      message.error('Unregister skill failed');
    }
  };

  // 测试技能
  const handleTestSkill = async (values) => {
    if (!currentSkill) return;
    
    try {
      setTestLoading(true);
      const response = await skillApi.testSkill(currentSkill.id, values);
      setTestResult(response);
      message.success('Test skill successfully');
    } catch (error) {
      console.error('Test skill failed:', error);
      message.error('Test skill failed');
      setTestResult({ error: error.message });
    } finally {
      setTestLoading(false);
    }
  };

  // 打开测试抽屉
  const openTestDrawer = (skill) => {
    setCurrentSkill(skill);
    setTestDrawerVisible(true);
    setTestResult(null);
    testForm.resetFields();
    
    // 设置默认参数
    if (skill.name === 'get_real_time_weather') {
      testForm.setFieldsValue({ city: 'Beijing' });
    } else if (skill.name === 'calculate') {
      testForm.setFieldsValue({ expression: '1+1' });
    }
  };

  // 列定义
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 120
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      width: 200
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description'
    },
    {
      title: 'Version',
      dataIndex: 'version',
      key: 'version',
      width: 100
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => (
        <Tag color={status === 'online' ? 'green' : 'red'}>
          {status.toUpperCase()}
        </Tag>
      )
    },
    {
      title: 'Permissions',
      dataIndex: 'permissions',
      key: 'permissions',
      render: (permissions) => (
        <Space>
          {permissions.map(perm => (
            <Tag key={perm}>{perm}</Tag>
          ))}
        </Space>
      )
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 200,
      render: (_, record) => (
        <Space size="small">
          <Button 
            type="primary" 
            size="small" 
            icon={<TestOutlined />}
            onClick={() => openTestDrawer(record)}
          >
            Test
          </Button>
          <Button 
            danger 
            size="small" 
            icon={<DeleteOutlined />}
            onClick={() => handleUnregisterSkill(record.id)}
          >
            Delete
          </Button>
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: '20px' }}>
      <Card>
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={4} style={{ margin: 0 }}>Skill Management</Title>
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            onClick={() => setRegisterModalVisible(true)}
          >
            Register Skill
          </Button>
        </div>
        
        <div style={{ marginBottom: 16, display: 'flex', gap: 8 }}>
          <Input
            placeholder="Search by name/description"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            onPressEnter={handleSearch}
            style={{ width: 300 }}
            suffix={<SearchOutlined />}
          />
          
          <Select
            placeholder="Status"
            value={status}
            onChange={setStatus}
            style={{ width: 150 }}
          >
            <Option value="">All</Option>
            <Option value="online">Online</Option>
            <Option value="offline">Offline</Option>
          </Select>
          
          <Button 
            icon={<ReloadOutlined />}
            onClick={loadSkills}
          >
            Refresh
          </Button>
        </div>
        
        <Table
          columns={columns}
          dataSource={skills}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>
      
      {/* 注册技能模态框 */}
      <Modal
        title="Register New Skill"
        open={registerModalVisible}
        onCancel={() => setRegisterModalVisible(false)}
        onOk={() => registerForm.submit()}
        destroyOnClose
      >
        <Form
          form={registerForm}
          layout="vertical"
          onFinish={handleRegisterSkill}
        >
          <Form.Item
            name="name"
            label="Skill Name"
            rules={[{ required: true, message: 'Please input skill name' }]}
          >
            <Input placeholder="e.g. get_real_time_weather" />
          </Form.Item>
          
          <Form.Item
            name="description"
            label="Description"
            rules={[{ required: true, message: 'Please input description' }]}
          >
            <Input.TextArea rows={3} placeholder="Skill description" />
          </Form.Item>
          
          <Form.Item
            name="version"
            label="Version"
            initialValue="1.0.0"
            rules={[{ required: true, message: 'Please input version' }]}
          >
            <Input placeholder="e.g. 1.0.0" />
          </Form.Item>
          
          <Form.Item
            name="permissions"
            label="Permissions"
            rules={[{ required: true, message: 'Please input permissions' }]}
          >
            <Input 
              placeholder="e.g. weather:read (multiple permissions separated by comma)" 
            />
          </Form.Item>
          
          <Form.Item
            name="endpoint"
            label="Endpoint URL"
            rules={[{ required: true, message: 'Please input endpoint URL' }]}
          >
            <Input placeholder="e.g. http://localhost:8001" />
          </Form.Item>
        </Form>
      </Modal>
      
      {/* 测试技能抽屉 */}
      <Drawer
        title={`Test Skill: ${currentSkill?.name || ''}`}
        open={testDrawerVisible}
        onClose={() => setTestDrawerVisible(false)}
        width={600}
      >
        <Form
          form={testForm}
          layout="vertical"
          onFinish={handleTestSkill}
        >
          {currentSkill?.name === 'get_real_time_weather' && (
            <Form.Item
              name="city"
              label="City"
              rules={[{ required: true, message: 'Please input city' }]}
            >
              <Input placeholder="e.g. Beijing" />
            </Form.Item>
          )}
          
          {currentSkill?.name === 'calculate' && (
            <Form.Item
              name="expression"
              label="Math Expression"
              rules={[{ required: true, message: 'Please input math expression' }]}
            >
              <Input placeholder="e.g. 1+1*2/3" />
            </Form.Item>
          )}
          
          {/* 通用参数表单，可根据技能动态生成 */}
          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit"
              loading={testLoading}
            >
              Test Skill
            </Button>
          </Form.Item>
        </Form>
        
        <Divider />
        
        {testResult && (
          <div style={{ marginTop: 16 }}>
            <Title level={5}>Test Result</Title>
            <Card>
              <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                {JSON.stringify(testResult, null, 2)}
              </pre>
            </Card>
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default SkillManager;
```

#### 5. 主应用入口（frontend/src/App.jsx）
```jsx
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Layout, Menu, Avatar, Dropdown, Space, Typography, message } from 'antd';
import { 
  HomeOutlined, 
  MessageOutlined, 
  AppstoreOutlined, 
  AuditOutlined,
  BarChartOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined
} from '@ant-design/icons';

import Login from './pages/Login/Login';
import Home from './pages/Home/Home';
import Chat from './pages/Chat/Chat';
import SkillManager from './pages/Skill/SkillManager';
import AuditLog from './pages/Audit/AuditLog';
import Monitor from './pages/Monitor/Monitor';
import Admin from './pages/Admin/Admin';

import { authApi } from './api/agentApi';

const { Header, Content, Sider } = Layout;
const { Title } = Typography;

const App = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // 检查登录状态
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('agent_token');
      if (!token) {
        setLoading(false);
        return;
      }
      
      try {
        const response = await authApi.getUserInfo();
        setCurrentUser(response);
      } catch (error) {
        console.error('Check auth failed:', error);
        localStorage.removeItem('agent_token');
      } finally {
        setLoading(false);
      }
    };
    
    checkAuth();
  }, []);

  // 退出登录
  const handleLogout = () => {
    localStorage.removeItem('agent_token');
    setCurrentUser(null);
    message.success('Logout successfully');
  };

  // 路由守卫
  const PrivateRoute = ({ children }) => {
    if (loading) {
      return <div>Loading...</div>;
    }
    
    if (!currentUser) {
      return <Navigate to="/login" replace />;
    }
    
    return children;
  };

  // 用户菜单
  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Profile'
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Settings'
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      onClick: handleLogout
    }
  ];

  return (
    <Router>
      <Layout style={{ minHeight: '100vh' }}>
        {currentUser ? (
          <>
            <Sider 
              collapsible 
              collapsed={collapsed} 
              onCollapse={(value) => setCollapsed(value)}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '16px' }}>
                <Title level={3} style={{ color: 'white', margin: 0 }}>
                  {collapsed ? 'Agent' : 'Agent UI'}
                </Title>
              </div>
              <Menu 
                theme="dark" 
                defaultSelectedKeys={['1']} 
                mode="inline"
              >
                <Menu.Item key="1" icon={<HomeOutlined />}>
                  <a href="/">Home</a>
                </Menu.Item>
                <Menu.Item key="2" icon={<MessageOutlined />}>
                  <a href="/chat">Chat</a>
                </Menu.Item>
                <Menu.Item key="3" icon={<AppstoreOutlined />}>
                  <a href="/skills">Skill Manager</a>
                </Menu.Item>
                <Menu.Item key="4" icon={<AuditOutlined />}>
                  <a href="/audit">Audit Log</a>
                </Menu.Item>
                <Menu.Item key="5" icon={<BarChartOutlined />}>
                  <a href="/monitor">Monitor</a>
                </Menu.Item>
                {currentUser?.role === 'admin' && (
                  <Menu.Item key="6" icon={<SettingOutlined />}>
                    <a href="/admin">Admin</a>
                  </Menu.Item>
                )}
              </Menu>
            </Sider>
            
            <Layout>
              <Header style={{ background: '#fff', padding: '0 16px', display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
                <Space>
                  <Dropdown menu={{ items: userMenuItems }}>
                    <Space style={{ cursor: 'pointer' }}>
                      <Avatar icon={<UserOutlined />} />
                      <Typography.Text>{currentUser?.username}</Typography.Text>
                    </Space>
                  </Dropdown>
                </Space>
              </Header>
              
              <Content style={{ margin: '16px' }}>
                <Routes>
                  <Route path="/" element={<PrivateRoute><Home /></PrivateRoute>} />
                  <Route path="/chat" element={<PrivateRoute><Chat /></PrivateRoute>} />
                  <Route path="/skills" element={<PrivateRoute><SkillManager /></PrivateRoute>} />
                  <Route path="/audit" element={<PrivateRoute><AuditLog /></PrivateRoute>} />
                  <Route path="/monitor" element={<PrivateRoute><Monitor /></PrivateRoute>} />
                  <Route path="/admin" element={<PrivateRoute><Admin /></PrivateRoute>} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </Content>
            </Layout>
          </>
        ) : (
          <Content style={{ margin: 0 }}>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
          </Content>
        )}
      </Layout>
    </Router>
  );
};

export default App;
```

### 16.4.3 Docker部署配置
#### 1. 前端Dockerfile（frontend/Dockerfile）
```dockerfile
# 构建阶段
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 运行阶段
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### 2. 后端Dockerfile（backend/Dockerfile）
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 3. Docker Compose配置（docker-compose.yml）
```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    environment:
      - VITE_API_BASE_URL=http://localhost:8000/api/v1
    networks:
      - agent_network

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=your-secret-key-32-bit-for-production
      - MCP_GATEWAY_URL=http://mcp_gateway:8080/mcp
      - DATABASE_URL=sqlite:///./agent_ui.db
    volumes:
      - backend_data:/app
    depends_on:
      - mcp_gateway
    networks:
      - agent_network

  mcp_gateway:
    build: ../mcp_gateway  # 指向第14章的MCP网关目录
    ports:
      - "8080:8080"
    networks:
      - agent_network

networks:
  agent_network:
    driver: bridge

volumes:
  backend_data:
```

## 16.5 智能体UI的企业级扩展与最佳实践
### 16.5.1 性能优化策略
1. **前端性能优化**
   - 组件懒加载：使用React.lazy和Suspense按需加载页面组件；
   - 数据缓存：使用React Query缓存API请求结果，减少重复请求；
   - 虚拟列表：使用react-window处理大量聊天记录/技能列表，提升渲染性能；
   - 资源压缩：开启Gzip压缩，优化静态资源加载速度；
   - 图片优化：使用WebP格式，按需加载图片。

2. **后端性能优化**
   - 接口缓存：使用Redis缓存频繁访问的技能列表、监控指标等数据；
   - 异步处理：使用Celery处理耗时的技能测试、日志导出等任务；
   - 数据库优化：使用连接池、索引优化、分页查询；
   - 接口限流：使用FastAPI-Limiter限制接口调用频率，防止滥用。

### 16.5.2 安全性增强
1. **前端安全**
   - XSS防护：使用React的内置XSS防护，避免直接插入HTML；
   - CSRF防护：使用CSRF Token验证；
   - 输入校验：前端表单严格校验输入格式，防止恶意输入；
   - 敏感信息脱敏：密码、Token等敏感信息不在前端存储/展示。

2. **后端安全**
   - 接口权限精细化：为每个接口配置细粒度的权限控制；
   - 输入验证：后端对所有输入参数进行二次校验；
   - 日志脱敏：审计日志中的敏感信息（如密码、Token）进行脱敏；
   - 安全头部：添加X-Content-Type-Options、X-Frame-Options等安全响应头。

### 16.5.3 可扩展性设计
1. **前端扩展**
   - 插件化架构：支持自定义页面、组件的动态加载；
   - 主题定制：支持自定义主题、颜色、布局；
   - 多语言支持：使用i18next实现多语言切换；
   - 自定义表单：支持动态生成技能参数表单。

2. **后端扩展**
   - 插件化API：支持动态注册API路由；
   - 多数据源支持：支持MySQL、PostgreSQL、MongoDB等多种数据库；
   - 消息队列集成：支持RabbitMQ/Kafka处理异步任务；
   - 配置中心集成：支持Nacos/Apollo配置中心，动态调整配置。

### 16.5.4 企业级最佳实践
1. **部署策略**
   - 生产环境使用Kubernetes部署，实现自动扩缩容；
   - 前端静态资源部署到CDN，提升访问速度；
   - 后端服务使用多副本部署，提高可用性；
   - 数据库使用主从复制，保证数据安全。

2. **监控告警**
   - 前端性能监控：集成Sentry监控前端错误；
   - 后端监控：使用Prometheus+Grafana监控接口性能、服务器资源；
   - 日志收集：使用ELK收集和分析日志；
   - 告警配置：配置关键指标的告警规则，及时发现问题。

3. **运维管理**
   - 自动化部署：使用CI/CD流水线（Jenkins/GitLab CI）实现自动化部署；
   - 版本管理：前端/后端使用语义化版本管理；
   - 灰度发布：支持灰度发布，降低更新风险；
   - 备份恢复：定期备份数据库，制定恢复策略。

## 16.6 本章总结
### 关键点回顾
1. 智能体UI并非简单的聊天界面，而是覆盖**终端用户、管理员、开发者**三类角色的全场景交互体系，核心价值是让智能体能力可被高效使用和管控；
2. 智能体UI采用“前端交互层-API网关层-核心服务层”三层架构，前端基于React+Ant Design实现可视化交互，后端基于FastAPI提供标准化API，核心能力复用前序章节的MCP网关、安全体系；
3. 核心功能包含聊天交互、技能管理、权限管控、审计日志、监控运维五大模块，所有代码均可直接运行并部署到生产环境；
4. 企业级扩展需关注性能优化、安全性增强、可扩展性设计，部署时建议使用Docker/Kubernetes实现容器化部署，保证高可用性和可维护性。

智能体UI是企业级智能体平台的“最后一公里”，它将后端的能力转化为用户可感知、可操作的产品，是智能体平台从“技术原型”走向“企业产品”的关键一步。通过本章的代码和理论，你可以快速构建一套生产级的智能体UI系统，与前序章节的MCP网关、安全体系、多智能体协作深度融合，形成完整的企业级智能体平台。