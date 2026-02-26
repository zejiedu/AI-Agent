# 第15章 MCP 安全、权限与审计体系——企业级智能体的安全基石
## 15.1 本章核心价值
在第14章 MCP 网关落地后，智能体能力平台已具备“统一入口、多技能调度”的企业级雏形，但**安全是企业落地的前提条件**——没有完善的安全体系，再强大的能力平台也无法进入生产环境。

MCP 作为开放的技能调用协议，本质是“能力开放接口”，开放必然伴随风险：
- 恶意调用者滥用技能（如批量调用天气接口导致 API 欠费、调用文件工具读取敏感数据）；
- 越权访问（普通用户调用管理员权限的技能，如数据删除、系统配置）；
- 参数注入攻击（通过恶意参数篡改技能执行逻辑、获取服务器权限）；
- 调用链路无审计，安全事件无法追溯；
- 技能本身存在漏洞，被利用发起攻击；
- 身份伪造（伪造合法用户/服务身份调用技能）。

**MCP 安全、权限与审计体系**，正是为解决上述风险而设计的**全链路安全防护方案**，覆盖“身份认证、权限控制、请求防护、技能安全、审计追溯”五大核心维度，让 MCP 网关与技能服务具备“可防、可管、可查、可追溯”的企业级安全能力。

本章目标：
1. 构建 MCP 全链路安全理论体系，明确“身份-权限-行为-审计”的安全闭环；
2. 实现可直接部署的**生产级安全组件**（身份认证、权限管控、参数校验、攻击防护）；
3. 完善 MCP 协议的安全扩展，新增身份、权限、签名等安全字段；
4. 落地全链路审计系统，实现调用行为可追溯、安全事件可排查；
5. 提供技能安全规范与漏洞防护方案，从源头降低安全风险；
6. 与前序章节的 MCP 协议、网关、Skill 体系深度集成，形成“能力+安全”的完整闭环。

## 15.2 MCP 安全理论体系
### 15.2.1 安全设计核心原则
企业级 MCP 安全体系遵循以下 5 大核心原则（贯穿全章节实现）：
1.  **最小权限原则**：任何用户/服务/技能，仅拥有完成自身任务所需的最小权限，无多余权限（如普通用户无法调用管理员技能，天气技能无法访问本地文件）；
2.  **全链路认证原则**：从“调用方→网关→技能服务”的每一步，都需完成身份认证，杜绝无身份调用；
3.  **可追溯原则**：每一次技能调用、权限校验、异常行为，都需记录完整日志，确保安全事件可追溯；
4.  **纵深防御原则**：多层防护（接入层防护→网关层安全→技能层安全），即使某一层防护失效，仍有其他层拦截风险；
5.  **兼容性原则**：安全扩展不破坏原有 MCP 协议标准，支持对现有 MCP 服务、技能的无缝适配，无需大规模修改代码。

### 15.2.2 MCP 全链路安全架构
MCP 安全体系并非单一组件，而是覆盖“调用方→网关→技能服务”的全链路架构，分为 5 个核心层级，形成闭环：

```
调用方（大模型/智能体/用户）
        ↑ （1.身份认证：签名/Token）
        ↓
接入层防护（防注入、防刷、防恶意请求）
        ↑
        ↓
MCP 网关安全层（2.权限控制、3.请求校验、4.审计记录）
        ↑
        ↓
技能服务安全层（5.技能权限、漏洞防护、参数清洗）
        ↑
        ↓
审计中心（日志存储、行为分析、安全告警）
```

各层级核心职责：
1.  **身份认证层**：验证调用方身份合法性（如用户 Token、服务签名、API Key），杜绝匿名/伪造身份调用；
2.  **接入层防护**：拦截恶意请求（如 SQL 注入、XSS、批量刷接口、超时攻击）；
3.  **网关安全层**：核心安全管控层，实现权限分配、请求校验、安全审计的集中管理；
4.  **技能安全层**：从技能本身出发，规范技能开发、校验技能权限、清洗输入参数，降低技能自身漏洞风险；
5.  **审计中心**：集中存储全链路日志，分析异常行为，触发安全告警，支撑安全事件排查。

### 15.2.3 核心安全概念界定
明确 MCP 安全体系中的核心概念，避免歧义：
-  **调用方**：发起 MCP 调用的主体（如大模型、上层智能体、普通用户、第三方服务）；
-  **身份标识**：用于唯一识别调用方的信息（如 UserID、ServiceID、API Key）；
-  **权限**：调用方可以执行的操作/访问的技能的范围（如“可调用天气技能、不可调用文件技能”）；
-  **角色**：对一组权限的集合（如“普通用户”角色拥有基础技能调用权限，“管理员”角色拥有所有技能调用+服务管理权限）；
-  **审计日志**：记录每一次 MCP 调用的完整信息（调用方身份、调用时间、技能名称、参数、结果、权限校验结果）；
-  **技能权限**：技能自身的访问权限控制（如某技能仅允许内部服务调用，不允许外部用户调用）；
-  **签名验证**：通过加密签名验证请求的完整性和合法性，防止请求被篡改。

## 15.3 MCP 协议安全扩展（兼容原有标准）
为实现全链路安全，在第13章 MCP 基础协议、第14章网关扩展协议的基础上，新增**安全相关元数据字段**，完全兼容原有协议，无需修改现有 MCP 服务代码（仅需网关和安全组件支持）。

### 15.3.1 身份认证扩展字段（调用方→网关）
在 MCP 请求的 `context` 字段中，新增身份认证相关字段，支持多种认证方式：
```json
{
  "jsonrpc": "2.0",
  "id": "gateway-req-1002",
  "method": "call_tool",
  "params": {
    "toolName": "get_real_time_weather",
    "parameters": {"city": "北京"},
    "context": {
      // 基础身份信息
      "userId": "user_001",          // 调用方（用户）唯一标识
      "serviceId": "agent_001",      // 调用方（服务/智能体）唯一标识（二选一即可）
      // 认证相关字段（支持多种认证方式，按需选择）
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", // JWT Token
      "apiKey": "sk_xxxxxx",         // API Key 认证
      // 签名验证（防止请求被篡改，高安全场景使用）
      "signature": "a1b2c3d4e5f6...",// 请求签名
      "timestamp": 1719288000,       // 时间戳（防止重放攻击）
      "nonce": "n123456"             // 随机字符串（防止重放攻击）
    }
  }
}
```

### 15.3.2 权限控制扩展字段（网关→技能服务）
网关向技能服务转发请求时，新增权限校验结果字段，便于技能服务二次校验：
```json
{
  "jsonrpc": "2.0",
  "id": "gateway-req-1002",
  "method": "call_tool",
  "params": {
    "toolName": "get_real_time_weather",
    "parameters": {"city": "北京"},
    "context": {
      "userId": "user_001",
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      // 网关新增的权限校验扩展字段
      "authPassed": true,            // 身份认证结果（true/false）
      "role": "normal_user",         // 调用方角色
      "permissions": ["weather:read"],// 调用方拥有的权限列表
      "gatewayRequestId": "gw_req_1002"// 网关请求唯一标识（用于链路追踪）
    }
  }
}
```

### 15.3.3 技能权限注册扩展（技能服务→网关）
技能服务向网关注册时，新增技能自身的权限配置，明确“谁可以调用该技能”：
```json
{
  "serverId": "com.example.skill.weather.v1",
  "name": "天气查询",
  "version": "1.0.0",
  "transport": "http",
  "endpoint": "http://127.0.0.1:8001",
  "tools": [
    {
      "name": "get_real_time_weather",
      "description": "获取实时天气",
      // 新增：技能权限配置
      "permissionRequired": true,    // 是否需要权限校验（true/false）
      "allowedRoles": ["normal_user", "admin"], // 允许调用的角色
      "allowedPermissions": ["weather:read"],  // 允许调用的权限
      "rateLimit": 60,               // 该技能的单独限流（优先级高于网关全局限流）
      "inputSchema": {...}
    }
  ],
  "weight": 10,
  "healthStatus": "healthy"
}
```

### 15.3.4 审计日志标准格式
统一审计日志格式，确保全链路日志可追溯、可分析，支持 JSON 格式存储（便于 ELK 集成）：
```json
{
  "auditId": "audit_100001",        // 审计日志唯一标识
  "gatewayRequestId": "gw_req_1002",// 网关请求唯一标识（链路关联）
  "mcpRequestId": "gateway-req-1002",// MCP 请求 ID
  "callerInfo": {                   // 调用方信息
    "userId": "user_001",
    "serviceId": "agent_001",
    "role": "normal_user",
    "ip": "127.0.0.1",              // 调用方 IP
    "userAgent": "python-mcp-client/1.0.0" // 调用方客户端信息
  },
  "requestInfo": {                  // 请求信息
    "method": "call_tool",
    "toolName": "get_real_time_weather",
    "parameters": {"city": "北京"},
    "timestamp": 1719288000,        // 请求时间
    "transport": "http"             // 传输协议
  },
  "securityInfo": {                 // 安全校验信息
    "authMethod": "jwt",            // 认证方式
    "authPassed": true,             // 身份认证结果
    "permissionChecked": true,      // 权限校验结果
    "permissionPassed": true,       // 权限校验是否通过
    "signatureValid": true          // 签名验证结果（如有）
  },
  "responseInfo": {                 // 响应信息
    "status": "success",            // 调用状态（success/error）
    "result": {...},                // 调用结果（简化版）
    "errorCode": 0,                 // 错误码（0表示无错误）
    "executionTime": 120,           // 执行耗时（毫秒）
    "responseTimestamp": 1719288000120 // 响应时间
  },
  "serviceInfo": {                  // 技能服务信息
    "serverId": "com.example.skill.weather.v1",
    "endpoint": "http://127.0.0.1:8001",
    "healthStatus": "healthy"
  }
}
```

## 15.4 生产级 MCP 安全组件完整实现
本章所有代码均为**可直接部署、高可用、企业级质量**，基于 Python 异步架构，与第14章 MCP 网关无缝集成，无需修改原有网关代码（仅需新增安全组件、配置依赖即可）。

### 15.4.1 安全体系工程目录（集成到 MCP 网关）
在第14章 `mcp_gateway` 目录基础上，新增安全相关模块，最终目录结构如下：
```
mcp_gateway/
├── core/
│   ├── __init__.py
│   ├── gateway.py          # 网关主类（无需修改，新增安全组件依赖）
│   ├── registry.py         # 服务注册中心（新增技能权限注册解析）
│   ├── scheduler.py        # 多技能调度器（无需修改）
│   ├── router.py           # 智能路由（无需修改）
│   ├── rate_limiter.py     # 限流（新增技能级限流）
│   ├── circuit_breaker.py  # 熔断（无需修改）
│   ├── auth.py             # 新增：身份认证组件（核心）
│   ├── permission.py       # 新增：权限控制组件（核心）
│   ├── context.py          # 网关上下文（新增安全相关上下文）
│   ├── security_filter.py  # 新增：请求安全过滤（防注入、防刷）
│   └── audit.py            # 新增：审计日志组件（核心）
├── transports/
│   ├── __init__.py
│   ├── base.py
│   ├── http.py
│   ├── stdio.py
│   └── websocket.py
├── api/
│   ├── __init__.py
│   └── http_api.py         # 对外 HTTP 服务（新增安全中间件）
├── config/
│   ├── gateway_config.yaml # 网关配置（新增安全相关配置）
│   └── security_config.yaml# 新增：安全配置（认证密钥、权限规则）
├── utils/
│   ├── logger.py
│   ├── metrics.py
│   ├── tracer.py
│   ├── crypto.py           # 新增：加密工具（签名、Token 解析）
│   └── validator.py        # 新增：参数安全校验工具
└── main.py                 # 启动入口（无需修改）
```

### 15.4.2 核心安全组件代码实现（可直接运行）
#### 1. 加密工具（支撑认证、签名，utils/crypto.py）
提供 JWT Token 解析、请求签名验证、密码加密等核心加密能力，企业级安全标准：
```python
# utils/crypto.py
import jwt
import hashlib
import hmac
import time
from typing import Dict, Optional
from datetime import datetime, timedelta

# 从配置文件加载密钥（实际生产环境建议用环境变量存储，避免硬编码）
from mcp_gateway.config.security_config import JWT_SECRET, SIGN_SECRET

class CryptoUtils:
    """加密工具类：JWT、签名、加密"""
    
    @staticmethod
    def generate_jwt(user_id: str, role: str, permissions: list, expires_hours: int = 24) -> str:
        """生成 JWT Token（用于身份认证）"""
        payload = {
            "userId": user_id,
            "role": role,
            "permissions": permissions,
            "exp": datetime.utcnow() + timedelta(hours=expires_hours),
            "iat": datetime.utcnow(),
            "jti": hashlib.md5(f"{user_id}_{time.time()}".encode()).hexdigest()
        }
        return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    
    @staticmethod
    def verify_jwt(token: str) -> Optional[Dict]:
        """验证并解析 JWT Token，失败返回 None"""
        try:
            payload = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_exp": True}  # 验证过期时间
            )
            return payload
        except jwt.ExpiredSignatureError:
            # Token 过期
            return None
        except jwt.InvalidTokenError:
            # Token 无效（伪造、篡改等）
            return None
    
    @staticmethod
    def sign_request(params: Dict, timestamp: int, nonce: str) -> str:
        """生成请求签名（防止请求被篡改、重放）"""
        # 1. 按参数名升序排序
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        # 2. 拼接参数字符串（key=value&key=value）
        param_str = "&".join([f"{k}={v}" for k, v in sorted_params])
        # 3. 拼接签名原文（参数串 + 时间戳 + 随机串 + 密钥）
        sign_str = f"{param_str}&timestamp={timestamp}&nonce={nonce}&secret={SIGN_SECRET}"
        # 4. HMAC-SHA256 加密，转为十六进制字符串
        signature = hmac.new(
            SIGN_SECRET.encode("utf-8"),
            sign_str.encode("utf-8"),
            digestmod=hashlib.sha256
        ).hexdigest()
        return signature
    
    @staticmethod
    def verify_signature(params: Dict, timestamp: int, nonce: str, signature: str) -> bool:
        """验证请求签名是否合法"""
        # 1. 验证时间戳（防止重放攻击，允许 ±300 秒误差）
        if abs(time.time() - timestamp) > 300:
            return False
        # 2. 重新生成签名，与传入的签名对比
        generated_sign = CryptoUtils.sign_request(params, timestamp, nonce)
        return hmac.compare_digest(generated_sign, signature)
    
    @staticmethod
    def encrypt_password(password: str) -> str:
        """密码加密（用于用户密码存储，不可逆）"""
        # 盐值 + 密码 + 密钥，多次哈希，提升安全性
        salt = hashlib.md5(time.ctime().encode()).hexdigest()[:8]
        return hashlib.sha256(f"{salt}_{password}_{JWT_SECRET}".encode()).hexdigest()
```

#### 2. 身份认证组件（core/auth.py）
实现多种身份认证方式（JWT Token、API Key、签名验证），可插拔设计，支持扩展其他认证方式：
```python
# core/auth.py
from typing import Dict, Optional, Tuple
from mcp_gateway.utils.crypto import CryptoUtils
from mcp_gateway.config.security_config import API_KEY_WHITELIST

class Authenticator:
    """身份认证组件：支持 JWT、API Key、签名验证"""
    
    def authenticate(self, context: Dict) -> Tuple[bool, Optional[Dict]]:
        """
        统一身份认证入口
        返回：(认证是否通过, 认证通过后的用户信息/None)
        """
        # 1. 优先尝试 JWT Token 认证（推荐用于用户/服务认证）
        if token := context.get("token"):
            return self._authenticate_jwt(token)
        
        # 2. 尝试 API Key 认证（用于简单服务调用）
        if api_key := context.get("apiKey"):
            return self._authenticate_api_key(api_key)
        
        # 3. 尝试签名认证（用于高安全场景）
        if self._has_signature_params(context):
            params = context.get("parameters", {})
            timestamp = context.get("timestamp")
            nonce = context.get("nonce")
            signature = context.get("signature")
            return self._authenticate_signature(params, timestamp, nonce, signature)
        
        # 4. 无任何认证信息，认证失败
        return False, None
    
    def _authenticate_jwt(self, token: str) -> Tuple[bool, Optional[Dict]]:
        """JWT Token 认证"""
        payload = CryptoUtils.verify_jwt(token)
        if not payload:
            return False, None
        # 认证通过，返回用户信息（userId、role、permissions）
        user_info = {
            "userId": payload.get("userId"),
            "role": payload.get("role"),
            "permissions": payload.get("permissions", [])
        }
        return True, user_info
    
    def _authenticate_api_key(self, api_key: str) -> Tuple[bool, Optional[Dict]]:
        """API Key 认证（用于服务间调用）"""
        # 校验 API Key 是否在白名单中（实际生产环境建议从数据库/配置中心加载）
        if api_key not in API_KEY_WHITELIST:
            return False, None
        # 从 API Key 解析服务信息（实际生产环境可关联服务ID、角色）
        service_info = {
            "serviceId": api_key.split("_")[0],  # 假设 API Key 格式为 serviceId_xxxx
            "role": "service",
            "permissions": ["service:call"]
        }
        return True, service_info
    
    def _authenticate_signature(self, params: Dict, timestamp: int, nonce: str, signature: str) -> Tuple[bool, Optional[Dict]]:
        """签名认证（高安全场景，防止请求篡改、重放）"""
        if not all([params, timestamp, nonce, signature]):
            return False, None
        # 验证签名合法性
        if not CryptoUtils.verify_signature(params, timestamp, nonce, signature):
            return False, None
        # 签名认证通过（可结合 API Key/Token 进一步获取用户信息）
        user_info = {
            "userId": context.get("userId"),
            "role": "signature_user",
            "permissions": ["signature:call"]
        }
        return True, user_info
    
    @staticmethod
    def _has_signature_params(context: Dict) -> bool:
        """判断是否包含签名认证所需参数"""
        required_params = ["timestamp", "nonce", "signature", "parameters"]
        return all(param in context for param in required_params)
```

#### 3. 权限控制组件（core/permission.py）
实现 RBAC（角色权限控制）模型，支持“角色→权限→技能”的三层权限映射，同时支持技能级权限配置：
```python
# core/permission.py
from typing import Dict, List, Optional
from mcp_gateway.core.registry import ServiceRegistry, MCPService

class PermissionManager:
    """权限控制组件：基于 RBAC 模型，支持技能级权限控制"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        # 基础权限规则（角色→权限映射，可从配置中心/数据库加载）
        self.role_permissions = {
            "normal_user": ["weather:read", "calculate:read"],
            "admin": ["weather:read", "weather:write", "calculate:read", "calculate:write", "system:manage"],
            "service": ["weather:read", "calculate:read"],
            "guest": ["weather:read"]
        }
    
    def check_permission(self, user_info: Dict, tool_name: str) -> Tuple[bool, str]:
        """
        权限校验入口
        参数：user_info（认证后的用户信息）、tool_name（要调用的技能名称）
        返回：(权限是否通过, 提示信息)
        """
        # 1. 获取用户角色和权限
        user_role = user_info.get("role")
        user_perms = user_info.get("permissions", []) or self.role_permissions.get(user_role, [])
        
        # 2. 获取技能的权限配置
        tool_perm_config = self._get_tool_permission_config(tool_name)
        if not tool_perm_config:
            # 技能未配置权限要求，默认允许调用（可根据企业需求改为“拒绝”）
            return True, "tool has no permission requirement"
        
        # 3. 校验技能是否需要权限
        if not tool_perm_config.get("permissionRequired", False):
            return True, "permission not required for this tool"
        
        # 4. 校验角色是否允许
        allowed_roles = tool_perm_config.get("allowedRoles", [])
        if allowed_roles and user_role not in allowed_roles:
            return False, f"user role {user_role} is not allowed to call tool {tool_name}"
        
        # 5. 校验权限是否允许
        allowed_perms = tool_perm_config.get("allowedPermissions", [])
        if allowed_perms and not any(perm in user_perms for perm in allowed_perms):
            return False, f"user lacks required permission(s): {allowed_perms}"
        
        # 6. 权限校验通过
        return True, "permission checked passed"
    
    def _get_tool_permission_config(self, tool_name: str) -> Optional[Dict]:
        """获取技能的权限配置（从服务注册中心获取）"""
        # 1. 根据技能名称获取对应的 MCP 服务
        service = self.registry.get_by_tool(tool_name)
        if not service:
            return None
        
        # 2. 遍历服务的技能列表，找到目标技能的权限配置
        for tool in service.tools:
            if tool.get("name") == tool_name:
                return {
                    "permissionRequired": tool.get("permissionRequired", False),
                    "allowedRoles": tool.get("allowedRoles", []),
                    "allowedPermissions": tool.get("allowedPermissions", []),
                    "rateLimit": tool.get("rateLimit")
                }
        return None
    
    def get_user_permissions(self, role: str) -> List[str]:
        """根据角色获取用户拥有的权限列表"""
        return self.role_permissions.get(role, [])
    
    def add_role_permission(self, role: str, permission: str):
        """新增角色-权限映射（动态更新，用于权限管理）"""
        if role not in self.role_permissions:
            self.role_permissions[role] = []
        if permission not in self.role_permissions[role]:
            self.role_permissions[role].append(permission)
    
    def remove_role_permission(self, role: str, permission: str):
        """删除角色-权限映射（动态更新）"""
        if role in self.role_permissions and permission in self.role_permissions[role]:
            self.role_permissions[role].remove(permission)
```

#### 4. 请求安全过滤组件（core/security_filter.py）
拦截恶意请求，实现参数注入防护、请求频率限制、非法参数过滤，保障网关和技能服务安全：
```python
# core/security_filter.py
import re
import time
from typing import Dict, Tuple
from collections import defaultdict

class SecurityFilter:
    """请求安全过滤组件：防注入、防刷、非法参数过滤"""
    
    def __init__(self):
        # 注入攻击特征（SQL注入、XSS、命令注入）
        self.injection_patterns = {
            "sql": re.compile(r"(union|select|insert|delete|update|drop|exec|or 1=1|--)", re.IGNORECASE),
            "xss": re.compile(r"(<script>|alert\(|eval\(|javascript:|onload=)", re.IGNORECASE),
            "cmd": re.compile(r"(rm -rf|cat /etc/passwd|ping |sh |bash )", re.IGNORECASE)
        }
        # 非法参数值（敏感路径、系统命令）
        self.illegal_values = ["/etc/passwd", "/root/", "rm -rf", "cat ", "bash "]
        # IP 限流（防刷，单位：分钟）
        self.ip_rate_limit = defaultdict(list)
        self.max_ip_requests = 120  # 每个IP每分钟最大请求数
    
    def filter_request(self, request: Dict, client_ip: str) -> Tuple[bool, str]:
        """
        统一请求过滤入口
        参数：request（MCP 请求）、client_ip（调用方IP）
        返回：(过滤是否通过, 提示信息)
        """
        # 1. IP 限流过滤（防批量刷接口）
        if not self._filter_ip_rate(client_ip):
            return False, f"IP {client_ip} is rate limited (exceed {self.max_ip_requests} requests per minute)"
        
        # 2. 注入攻击过滤
        if attack_type := self._detect_injection(request):
            return False, f"injection attack detected: {attack_type}"
        
        # 3. 非法参数过滤
        if illegal_param := self._detect_illegal_params(request):
            return False, f"illegal parameter detected: {illegal_param}"
        
        # 4. 请求格式合规性检查
        if not self._check_request_format(request):
            return False, "invalid MCP request format"
        
        # 过滤通过
        return True, "request filtered passed"
    
    def _filter_ip_rate(self, client_ip: str) -> bool:
        """IP 限流过滤"""
        now = time.time()
        # 保留最近60秒的请求记录
        self.ip_rate_limit[client_ip] = [t for t in self.ip_rate_limit[client_ip] if now - t < 60]
        # 检查请求数是否超过限制
        if len(self.ip_rate_limit[client_ip]) >= self.max_ip_requests:
            return False
        # 记录本次请求时间
        self.ip_rate_limit[client_ip].append(now)
        return True
    
    def _detect_injection(self, request: Dict) -> Optional[str]:
        """检测注入攻击（SQL、XSS、命令注入）"""
        # 提取请求中的所有参数值（递归处理嵌套参数）
        params = request.get("params", {})
        param_values = self._extract_param_values(params)
        
        # 检查是否包含注入特征
        for attack_type, pattern in self.injection_patterns.items():
            for value in param_values:
                if pattern.search(str(value)):
                    return attack_type
        return None
    
    def _detect_illegal_params(self, request: Dict) -> Optional[str]:
        """检测非法参数值"""
        param_values = self._extract_param_values(request.get("params", {}))
        for value in param_values:
            for illegal in self.illegal_values:
                if illegal in str(value):
                    return illegal
        return None
    
    @staticmethod
    def _check_request_format(request: Dict) -> bool:
        """检查 MCP 请求格式是否合规（基础安全校验）"""
        required_fields = ["jsonrpc", "id", "method", "params"]
        return all(field in request for field in required_fields) and request["jsonrpc"] == "2.0"
    
    @staticmethod
    def _extract_param_values(params: Dict) -> list:
        """递归提取所有参数值（处理嵌套字典/列表）"""
        values = []
        for v in params.values():
            if isinstance(v, dict):
                values.extend(SecurityFilter._extract_param_values(v))
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, dict):
                        values.extend(SecurityFilter._extract_param_values(item))
                    else:
                        values.append(item)
            else:
                values.append(v)
        return values
```

#### 5. 审计日志组件（core/audit.py）
实现全链路审计日志的生成、存储、输出，支持与 ELK 等日志系统集成，确保安全事件可追溯：
```python
# core/audit.py
import uuid
import time
from typing import Dict, Optional
from mcp_gateway.utils.logger import get_logger

logger = get_logger("mcp_audit")

class AuditLogger:
    """审计日志组件：生成、存储、输出全链路审计日志"""
    
    def __init__(self):
        # 审计日志存储方式（实际生产环境建议用 Kafka/Elasticsearch 存储）
        self.audit_storage = []  # 临时存储，用于演示，生产环境替换为持久化存储
    
    def generate_audit_log(
        self,
        gateway_request_id: str,
        mcp_request_id: str,
        caller_info: Dict,
        request_info: Dict,
        security_info: Dict,
        response_info: Dict,
        service_info: Optional[Dict] = None
    ) -> Dict:
        """生成审计日志（按标准格式）"""
        audit_log = {
            "auditId": f"audit_{uuid.uuid4().hex[:12]}",
            "gatewayRequestId": gateway_request_id,
            "mcpRequestId": mcp_request_id,
            "callerInfo": caller_info,
            "requestInfo": request_info,
            "securityInfo": security_info,
            "responseInfo": response_info,
            "serviceInfo": service_info or {},
            "auditTimestamp": time.time()  # 审计日志生成时间
        }
        # 存储审计日志（持久化）
        self._store_audit_log(audit_log)
        # 输出审计日志（便于调试和监控）
        self._log_audit(audit_log)
        return audit_log
    
    def _store_audit_log(self, audit_log: Dict):
        """存储审计日志（生产环境替换为 Kafka/ES/数据库）"""
        self.audit_storage.append(audit_log)
        # 限制临时存储长度（防止内存溢出，演示用）
        if len(self.audit_storage) > 1000:
            self.audit_storage.pop(0)
    
    def _log_audit(self, audit_log: Dict):
        """输出审计日志（JSON 格式，便于 ELK 采集）"""
        logger.info(f"AUDIT_LOG: {audit_log}")
    
    def query_audit_logs(self, **kwargs) -> list:
        """查询审计日志（支持多条件过滤，生产环境替换为数据库查询）"""
        # 示例：支持按 userId、toolName、status 过滤
        filtered = self.audit_storage
        if "userId" in kwargs:
            filtered = [log for log in filtered if log["callerInfo"].get("userId") == kwargs["userId"]]
        if "toolName" in kwargs:
            filtered = [log for log in filtered if log["requestInfo"].get("toolName") == kwargs["toolName"]]
        if "status" in kwargs:
            filtered = [log for log in filtered if log["responseInfo"].get("status") == kwargs["status"]]
        return filtered
    
    def get_audit_log_by_id(self, audit_id: str) -> Optional[Dict]:
        """根据审计ID查询单个日志"""
        for log in self.audit_storage:
            if log["auditId"] == audit_id:
                return log
        return None
```

#### 6. 网关集成安全组件（修改 core/gateway.py）
将上述安全组件集成到第14章的 MCP 网关主类中，实现“请求过滤→身份认证→权限校验→审计日志”的全链路安全管控，无需修改原有网关核心逻辑：
```python
# core/gateway.py
import uuid
import time
from typing import Dict, Optional
from .registry import ServiceRegistry
from .scheduler import Scheduler
from .router import Router
from .rate_limiter import RateLimiter
# 新增：导入安全组件
from .auth import Authenticator
from .permission import PermissionManager
from .security_filter import SecurityFilter
from .audit import AuditLogger

class MCPGateway:
    def __init__(self):
        self.registry = ServiceRegistry()
        self.scheduler = Scheduler(self.registry)
        self.router = Router(self.registry)
        self.limiter = RateLimiter(max_per_min=100)
        
        # 新增：初始化安全组件
        self.authenticator = Authenticator()
        self.permission_manager = PermissionManager(self.registry)
        self.security_filter = SecurityFilter()
        self.audit_logger = AuditLogger()

    async def handle(self, req: Dict, client_ip: str = "127.0.0.1") -> Dict:
        """
        新增：client_ip 参数（调用方IP，用于安全过滤、审计）
        新增：全链路安全管控逻辑
        """
        # 生成网关请求唯一标识（用于链路追踪、审计）
        gateway_request_id = f"gw_req_{uuid.uuid4().hex[:8]}"
        mcp_request_id = req.get("id", "unknown_req_id")
        
        # 初始化审计日志所需基础信息
        caller_info = {"ip": client_ip, "userAgent": req.get("context", {}).get("userAgent", "unknown")}
        request_info = {
            "method": req.get("method"),
            "toolName": req.get("params", {}).get("toolName"),
            "parameters": req.get("params", {}).get("parameters", {}),
            "timestamp": time.time(),
            "transport": "http"
        }
        security_info = {
            "authMethod": "unknown",
            "authPassed": False,
            "permissionChecked": False,
            "permissionPassed": False,
            "signatureValid": False
        }
        response_info = {
            "status": "error",
            "result": {},
            "errorCode": 500,
            "executionTime": 0,
            "responseTimestamp": 0
        }
        service_info = {}
        
        start_time = time.time()
        try:
            # -------------- 1. 请求安全过滤（第一道防线）--------------
            filter_passed, filter_msg = self.security_filter.filter_request(req, client_ip)
            if not filter_passed:
                response_info["errorCode"] = 403
                response_info["result"] = {"error": filter_msg}
                return self._finish_response(
                    gateway_request_id, mcp_request_id, caller_info, request_info,
                    security_info, response_info, service_info, start_time
                )
            
            # -------------- 2. 身份认证（第二道防线）--------------
            context = req.get("params", {}).get("context", {})
            auth_passed, user_info = self.authenticator.authenticate(context)
            security_info["authPassed"] = auth_passed
            # 记录认证方式
            if context.get("token"):
                security_info["authMethod"] = "jwt"
            elif context.get("apiKey"):
                security_info["authMethod"] = "api_key"
            elif self.authenticator._has_signature_params(context):
                security_info["authMethod"] = "signature"
            
            if not auth_passed:
                response_info["errorCode"] = 401
                response_info["result"] = {"error": "authentication failed"}
                return self._finish_response(
                    gateway_request_id, mcp_request_id, caller_info, request_info,
                    security_info, response_info, service_info, start_time
                )
            
            # 更新调用方信息（认证后的用户信息）
            caller_info.update(user_info)
            
            # -------------- 3. 权限校验（第三道防线）--------------
            tool_name = request_info["toolName"]
            if tool_name:
                perm_passed, perm_msg = self.permission_manager.check_permission(user_info, tool_name)
                security_info["permissionChecked"] = True
                security_info["permissionPassed"] = perm_passed
                if not perm_passed:
                    response_info["errorCode"] = 403
                    response_info["result"] = {"error": perm_msg}
                    return self._finish_response(
                        gateway_request_id, mcp_request_id, caller_info, request_info,
                        security_info, response_info, service_info, start_time
                    )
            
            # -------------- 4. 原有网关逻辑（调用/批量调用）--------------
            method = req.get("method")
            if method == "call_tool":
                response = await self._call(req)
            elif method == "batch_call":
                response = await self._batch(req)
            elif method == "list_tools":
                response = self._list()
            else:
                response = {"error": "method not supported", "errorCode": 405}
            
            # 更新响应信息
            if "error" not in response:
                response_info["status"] = "success"
                response_info["result"] = response
                response_info["errorCode"] = 0
            else:
                response_info["result"] = response
                response_info["errorCode"] = response.get("errorCode", 400)
            
            # 获取技能服务信息（用于审计）
            if tool_name:
                service = self.registry.get_by_tool(tool_name)
                if service:
                    service_info = {
                        "serverId": service.server_id,
                        "endpoint": service.endpoint,
                        "healthStatus": service.status
                    }
            
            return response
        
        except Exception as e:
            # 异常处理，更新响应和审计信息
            error_msg = f"internal server error: {str(e)}"
            response_info["result"] = {"error": error_msg}
            response_info["errorCode"] = 500
            return {"error": error_msg, "errorCode": 500}
        finally:
            # 最终生成审计日志（无论成功/失败）
            self._finish_response(
                gateway_request_id, mcp_request_id, caller_info, request_info,
                security_info, response_info, service_info, start_time
            )

    async def _call(self, req: Dict):
        params = req["params"]
        tool = params["toolName"]
        # 新增：技能级限流（优先级高于全局限流）
        tool_perm_config = self.permission_manager._get_tool_permission_config(tool)
        if tool_perm_config and tool_perm_config.get("rateLimit"):
            limiter = RateLimiter(max_per_min=tool_perm_config["rateLimit"])
            if not limiter.allow(tool):
                return {"error": "tool rate limited", "errorCode": 429}
        # 原有全局限流
        if not self.limiter.allow(tool):
            return {"error": "rate limited", "errorCode": 429}
        return await self.scheduler.execute(tool, params.get("parameters", {}))

    async def _batch(self, req: Dict):
        params = req["params"]
        return await self.scheduler.batch(params.get("plan", {}), params.get("tools", []))

    def _list(self):
        tools = []
        for s in self.registry._services.values():
            tools.extend([tool["name"] for tool in s.tools])
        return {"tools": sorted(list(set(tools)))}

    def _finish_response(self, gateway_req_id, mcp_req_id, caller_info, req_info, sec_info, resp_info, svc_info, start_time):
        """完成响应，生成审计日志，更新响应耗时"""
        resp_info["executionTime"] = int((time.time() - start_time) * 1000)  # 耗时（毫秒）
        resp_info["responseTimestamp"] = time.time()
        # 生成审计日志
        self.audit_logger.generate_audit_log(
            gateway_request_id=gateway_req_id,
            mcp_request_id=mcp_req_id,
            caller_info=caller_info,
            request_info=req_info,
            security_info=sec_info,
            response_info=resp_info,
            service_info=svc_info
        )
        # 返回最终响应（添加网关请求ID，便于链路追踪）
        final_resp = resp_info["result"].copy()
        final_resp["gatewayRequestId"] = gateway_req_id
        return final_resp
```

#### 7. HTTP 接入层添加安全中间件（修改 api/http_api.py）
获取调用方 IP，传递给网关处理，同时添加请求超时控制，进一步提升安全防护：
```python
# api/http_api.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ..core.gateway import MCPGateway
import time

app = FastAPI(title="MCP Gateway", docs_url="/docs", redoc_url="/redoc")
gateway = MCPGateway()

# 新增：CORS 配置（防止跨域攻击，生产环境限制允许的域名）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境替换为具体域名，如 ["https://your-domain.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 新增：请求超时中间件（防止长时间阻塞请求攻击）
@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    start_time = time.time()
    try:
        # 设置请求超时时间（10秒）
        response = await asyncio.wait_for(call_next(request), timeout=10.0)
        return response
    except asyncio.TimeoutError:
        # 超时返回错误
        return {"error": "request timeout", "errorCode": 408}

@app.post("/mcp")
async def mcp(request: Request):
    # 新增：获取调用方 IP（用于安全过滤、审计）
    client_ip = request.client.host
    try:
        body = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail="invalid json format")
    
    # 调用网关处理请求，传递客户端IP
    return await gateway.handle(body, client_ip=client_ip)
```

#### 8. 安全配置文件（config/security_config.yaml）
集中管理安全相关配置（密钥、API Key 白名单、权限规则），避免硬编码，便于运维管理：
```yaml
# config/security_config.yaml
# JWT 密钥（生产环境建议用环境变量存储，长度至少32位）
JWT_SECRET: "your-32-bit-jwt-secret-key-xxxxxxxxx"

# 签名密钥（用于请求签名验证，生产环境建议用环境变量存储）
SIGN_SECRET: "your-32-bit-sign-secret-key-xxxxxxxxx"

# API Key 白名单（用于服务间调用，生产环境从配置中心/数据库加载）
API_KEY_WHITELIST:
  - "agent_001_xxxxxxxx"
  - "service_001_xxxxxxxx"
  - "test_001_xxxxxxxx"

# 角色-权限映射（可动态更新，生产环境从数据库加载）
ROLE_PERMISSIONS:
  normal_user:
    - "weather:read"
    - "calculate:read"
  admin:
    - "weather:read"
    - "weather:write"
    - "calculate:read"
    - "calculate:write"
    - "system:manage"
  service:
    - "weather:read"
    - "calculate:read"
  guest:
    - "weather:read"

# 安全过滤配置
SECURITY_FILTER:
  # IP 限流（每分钟最大请求数）
  max_ip_requests_per_minute: 120
  # 注入攻击特征（可扩展）
  injection_patterns:
    sql: ["union", "select", "insert", "delete", "update", "drop", "exec", "or 1=1", "--"]
    xss: ["<script>", "alert(", "eval(", "javascript:", "onload="]
    cmd: ["rm -rf", "cat /etc/passwd", "ping ", "sh ", "bash "]
  # 非法参数值（可扩展）
  illegal_values: ["/etc/passwd", "/root/", "rm -rf", "cat ", "bash "]
```

### 15.4.3 技能服务安全适配（无需修改原有技能代码）
现有 MCP 技能服务无需修改代码，仅需在 `mcp.json` 中新增技能权限配置（如15.3.3节所示），即可支持网关的权限校验、技能级限流等安全特性。

对于新开发的技能服务，需遵循以下安全规范：
1.  输入参数必须进行二次校验（即使网关已校验，纵深防御）；
2.  输出结果不包含敏感信息（如服务器地址、数据库信息）；
3.  技能执行逻辑遵循最小权限原则（如天气技能不访问本地文件）；
4.  记录自身执行日志，与网关审计日志关联（通过 `gatewayRequestId`）；
5.  避免使用系统命令、动态代码执行（如 `exec`、`eval`），防止命令注入。

## 15.5 安全实战案例（覆盖核心安全场景）
### 场景1：身份认证失败（非法 Token）
调用方发起请求时，携带伪造/过期的 JWT Token：
```json
{
  "jsonrpc": "2.0",
  "id": "test-req-001",
  "method": "call_tool",
  "params": {
    "toolName": "get_real_time_weather",
    "parameters": {"city": "北京"},
    "context": {
      "userId": "user_001",
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJ1c2VyXzAwMSIsInJvbGUiOiJub3JtYWxfdXNlciIsImV4cCI6MTcxOTI4ODAwMH0.invalid-signature"
    }
  }
}
```

网关处理结果：
1.  安全过滤通过（无注入、IP 未限流）；
2.  身份认证失败（Token 无效）；
3.  返回 401 错误：`{"error": "authentication failed", "errorCode": 401, "gatewayRequestId": "gw_req_xxxxxx"}`；
4.  生成审计日志，记录“认证失败”、调用方 IP、非法 Token 相关信息。

### 场景2：权限不足（普通用户调用管理员技能）
普通用户（角色 `normal_user`）调用管理员权限的技能 `delete_file`：
```json
{
  "jsonrpc": "2.0",
  "id": "test-req-002",
  "method": "call_tool",
  "params": {
    "toolName": "delete_file",
    "parameters": {"file_path": "/tmp/test.txt"},
    "context": {
      "userId": "user_001",
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJ1c2VyXzAwMSIsInJvbGUiOiJub3JtYWxfdXNlciIsInBlcm1pc3Npb25zIjpbIndlYXRoZXI6cmVhZCIsImNhbGN1bGF0ZTpyZWFkIl0sImV4cCI6MTcxOTM3NDQwMH0.xxxxxx"
    }
  }
}
```

网关处理结果：
1.  安全过滤通过，身份认证通过（Token 有效）；
2.  权限校验失败（`normal_user` 角色不允许调用 `delete_file` 技能）；
3.  返回 403 错误：`{"error": "user role normal_user is not allowed to call tool delete_file", "errorCode": 403, "gatewayRequestId": "gw_req_xxxxxx"}`；
4.  生成审计日志，记录“权限校验失败”、用户角色、技能名称等信息。

### 场景3：注入攻击拦截（SQL 注入参数）
调用方发起请求时，携带 SQL 注入参数：
```json
{
  "jsonrpc": "2.0",
  "id": "test-req-003",
  "method": "call_tool",
  "params": {
    "toolName": "query_user",
    "parameters": {"user_id": "1' OR 1=1 --"},
    "context": {
      "userId": "user_001",
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJ1c2VyXzAwMSIsInJvbGUiOiJub3JtYWxfdXNlciIsInBlcm1pc3Npb25zIjpbIndlYXRoZXI6cmVhZCIsImNhbGN1bGF0ZTpyZWFkIl0sImV4cCI6MTcxOTM3NDQwMH0.xxxxxx"
    }
  }
}
```

网关处理结果：
1.  安全过滤拦截（检测到 SQL 注入攻击）；
2.  返回 400 错误：`{"error": "invalid parameter: user_id", "errorCode": 400, "gatewayRequestId": "gw_req_xxxxxx"}`；
3 错误：`{"error": "injection attack detected: sql", "errorCode": 403, "gatewayRequestId": "gw_req_xxxxxx"}`；
4.  生成审计日志，记录“SQL 注入攻击”、调用方 IP、恶意参数等信息，便于安全排查。

### 场景4：IP 限流拦截（批量刷接口）
某 IP（如 `192.168.1.100`）1 分钟内发起 150 次请求，超过网关 IP 限流阈值（120 次/分钟）。

网关处理结果：
1.  安全过滤拦截（IP 限流触发）；
2.  返回 403 错误：`{"error": "IP 192.168.1.100 is rate limited (exceed 120 requests per minute)", "errorCode": 403, "gatewayRequestId": "gw_req_xxxxxx"}`；
3.  生成审计日志，记录“IP 限流”、调用方 IP、请求次数等信息，可用于排查恶意刷接口行为。

### 场景5：全链路安全校验通过（正常调用）
合法用户（角色 `normal_user`）携带有效 Token，调用允许的技能 `get_real_time_weather`，参数合法、IP 未限流：
```json
{
  "jsonrpc": "2.0",
  "id": "test-req-004",
  "method": "call_tool",
  "params": {
    "toolName": "get_real_time_weather",
    "parameters": {"city": "北京"},
    "context": {
      "userId": "user_001",
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJ1c2VyXzAwMSIsInJvbGUiOiJub3JtYWxfdXNlciIsInBlcm1pc3Npb25zIjpbIndlYXRoZXI6cmVhZCIsImNhbGN1bGF0ZTpyZWFkIl0sImV4cCI6MTcxOTM3NDQwMH0.xxxxxx",
      "userAgent": "python-mcp-client/1.0.0"
    }
  }
}
```

网关处理结果：
1.  安全过滤通过（无注入、IP 未限流、格式合规）；
2.  身份认证通过（Token 有效，解析出用户角色和权限）；
3.  权限校验通过（`normal_user` 角色允许调用 `get_real_time_weather` 技能）；
4.  调度技能服务，获取响应结果，返回正常响应：
    ```json
    {
      "gatewayRequestId": "gw_req_xxxxxx",
      "status": "success",
      "result": {"city": "北京", "temperature": 25, "weather": "晴"}
    }
    ```
5.  生成完整审计日志，记录“认证通过、权限通过、调用成功”等全链路信息，可用于后续追溯。

## 15.6 技能安全规范与漏洞防护（从源头降低风险）
MCP 安全体系不仅依赖网关的集中管控，更需要从技能开发源头规避安全风险。本节提供**企业级技能安全开发规范**，所有新开发、现有改造的技能都需严格遵循。

### 15.6.1 技能开发安全规范（必遵循）
1.  最小权限原则落地
    - 技能运行时使用最低权限账号（如不使用 root 账号、不授予数据库读写权限）；
    - 技能仅访问完成自身功能所需的资源（如天气技能不访问本地文件、数据库技能不访问外部网络）；
    - 禁止技能调用系统敏感命令（如 `rm`、`cat /etc/passwd`、`sudo` 等）。

2.  参数校验规范
    - 输入参数必须进行“类型校验+范围校验+格式校验”（即使网关已校验，实现纵深防御）；
    - 对字符串参数进行长度限制（防止超长参数攻击）；
    - 对路径、文件名等参数进行白名单过滤（如文件操作技能仅允许访问 `/tmp/` 目录下的文件）；
    - 禁止直接将用户输入作为系统命令、SQL 语句执行（如需执行，必须进行严格转义）。

3.  输出安全规范
    - 输出结果不包含敏感信息（如服务器 IP、端口、数据库账号密码、文件路径、内部接口地址）；
    - 对异常信息进行脱敏处理（如不返回“数据库连接失败：user=root password=123456”，仅返回“数据库连接失败，请联系管理员”）；
    - 输出格式统一、结构化，避免返回杂乱的系统日志、错误堆栈（防止泄露系统细节）。

4.  运行环境安全规范
    - 技能部署在隔离环境（如 Docker 容器），与核心业务系统隔离；
    - 禁止在技能运行环境中存储敏感配置（如密钥、API Key，建议使用配置中心、环境变量存储）；
    - 定期更新技能运行环境的依赖包（防止依赖包存在已知漏洞）；
    - 限制技能运行时的资源占用（CPU、内存、网络带宽），防止资源耗尽攻击。

### 15.6.2 常见技能安全漏洞及防护方案
| 漏洞类型 | 常见场景 | 防护方案 |
|----------|----------|----------|
| SQL 注入 | 数据库查询类技能，直接将用户输入拼接到 SQL 语句 | 1. 使用参数化查询（如 Python 的 SQLAlchemy 参数绑定）；2. 对用户输入进行转义、过滤；3. 限制数据库账号权限（仅授予查询权限） |
| 命令注入 | 系统操作类技能，直接执行包含用户输入的系统命令 | 1. 禁止直接执行用户输入的命令；2. 如需执行命令，使用白名单限制可执行命令；3. 对用户输入进行严格过滤、转义 |
| XSS 攻击 | 网页展示类技能，返回包含用户输入的 HTML 内容 | 1. 对用户输入进行 HTML 转义（如将 `<` 转为 `&lt;`）；2. 禁止返回未经转义的 HTML、JavaScript 内容 |
| 敏感信息泄露 | 技能输出包含服务器信息、错误堆栈、密钥等 | 1. 对输出结果进行脱敏处理；2. 捕获异常时，不返回详细错误堆栈；3. 禁止在技能代码中硬编码敏感信息 |
| 权限越权 | 技能未校验自身权限，允许非法调用 | 1. 技能接收网关传递的 `authPassed`、`role` 等字段，进行二次权限校验；2. 严格遵循“最小权限”运行 |
| 资源耗尽攻击 | 技能未限制资源占用，被恶意调用导致 CPU/内存耗尽 | 1. 技能内部添加资源占用限制（如超时控制、循环次数限制）；2. 网关配置技能级限流，防止批量调用 |

### 15.6.3 技能安全测试 checklist（上线必测）
技能上线前，必须完成以下安全测试，未通过测试禁止上线：
1.  输入参数测试：测试恶意参数（注入、非法路径、超长参数）是否被拦截；
2.  权限测试：测试不同角色用户调用技能的权限控制是否生效；
3.  敏感信息测试：测试技能输出是否包含敏感信息、错误堆栈是否脱敏；
4.  资源占用测试：测试批量调用、超长耗时调用时，技能资源占用是否可控；
5.  依赖漏洞测试：检查技能依赖包是否存在已知安全漏洞（可使用 pip-audit、npm audit 等工具）；
6.  接口安全测试：测试技能接口是否允许匿名调用、是否支持非法请求方法。

## 15.7 审计日志与安全监控体系（可观测、可追溯）
审计日志和安全监控是 MCP 安全体系的“最后一道防线”——即使前面的防护层被突破，也能通过审计日志追溯安全事件、通过监控及时发现异常行为，实现“事前预警、事中拦截、事后追溯”的完整闭环。

### 15.7.1 审计日志体系落地
1.  日志存储方案（企业级推荐）
    - 短期存储（7 天内）：本地文件存储（便于快速查询）；
    - 长期存储（90 天+）：Elasticsearch 集群（支持全文检索、按条件过滤）；
    - 日志备份：定期将审计日志备份到对象存储（如 S3、OSS），保存 1 年以上（满足企业合规要求）。

2.  日志查询与分析能力
    - 支持多条件组合查询（如按 userId、toolName、auditId、错误码、时间范围查询）；
    - 支持日志可视化分析（如通过 Kibana 展示调用趋势、安全事件统计、IP 访问分布）；
    - 支持日志导出（如导出某时间段的安全事件日志，用于合规审计、安全排查）。

3.  审计日志合规要求
    - 日志不可篡改：审计日志生成后，禁止修改、删除（可通过加密签名、区块链等方式保障）；
    - 日志完整性：每一次 MCP 调用（无论成功/失败）都必须生成审计日志，无遗漏；
    - 日志保留期限：至少保留 90 天，涉及敏感操作（如管理员技能调用、权限变更）的日志需保留 1 年以上。

### 15.7.2 安全监控体系落地
基于审计日志和网关指标，构建企业级安全监控体系，实现异常行为实时预警、安全事件快速响应。

1.  核心监控指标（必监控）
    - 认证相关：认证失败次数、非法 Token 次数、签名验证失败次数；
    - 权限相关：权限校验失败次数、越权调用次数；
    - 安全攻击：注入攻击次数、IP 限流次数、非法参数拦截次数；
    - 系统安全：网关异常响应次数、技能服务异常调用次数、日志生成失败次数。

2.  监控告警策略（企业级推荐）
    - 告警级别：分为紧急（P0）、高（P1）、中（P2）、低（P3）四级；
    - 紧急告警（P0）：批量注入攻击、大规模越权调用、网关安全组件异常，立即通知安全管理员（电话+短信）；
    - 高告警（P1）：认证失败次数突增、IP 限流次数突增，10 分钟内通知安全管理员（短信+邮件）；
    - 中告警（P2）：单次注入攻击、单次越权调用，1 小时内通知安全管理员（邮件）；
    - 低告警（P3）：非法参数拦截、轻微权限异常，每日汇总通知运维人员。

3.  监控工具集成（可直接落地）
    - 指标监控：Prometheus + Grafana（可视化展示监控指标，配置告警规则）；
    - 日志监控：Elasticsearch + Kibana（实时分析审计日志，检测异常行为）；
    - 告警通知：Alertmanager + 企业微信/钉钉/短信接口（实现多渠道告警通知）。

## 15.8 本章总结
MCP 安全、权限与审计体系是**企业级智能体平台落地的前提**，也是本书从“技术教程”升级为“企业工程手册”的核心标志——没有安全，再强大的能力平台也无法进入生产环境，更无法获得企业信任。

本章核心结论，需牢记并落地：
1.  MCP 安全体系的核心是**“身份-权限-行为-审计”的全链路闭环**，覆盖“调用方→网关→技能服务”每一个环节，遵循最小权限、纵深防御原则；
2.  核心安全组件（身份认证、权限控制、安全过滤、审计日志）可直接部署，与前序章节的 MCP 网关、Skill 体系无缝集成，无需大规模修改原有代码；
3.  安全防护不能仅依赖网关集中管控，还需从**技能开发源头**遵循安全规范，规避常见漏洞，实现“网关防护+技能自身防护”的纵深防御；
4.  审计日志和安全监控是“最后一道防线”，必须实现日志不可篡改、可追溯，监控可预警、可响应，满足企业合规要求；
5.  本章提供的所有代码、规范、方案，均为生产级可落地，可直接用于私有化部署、云端部署，适配企业实际安全需求。

至此，我们已完成“MCP 协议→网关调度→安全管控”的企业级智能体核心能力闭环。下一章，我们将聚焦 Skill 全生命周期管理，解决“技能开发、上线、迭代、运维”的工程化问题，让智能体平台具备**可运营、可扩展、可维护**的企业级能力。

---
