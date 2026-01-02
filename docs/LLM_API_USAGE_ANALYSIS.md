# ConveVisAna 后端 LLM API 使用情况分析

> 📅 生成日期: 2026年1月2日  
> 🎯 目的: 全面梳理项目中 LLM API 的使用情况，提出统一管理方案

---

## 📋 目录

- [当前使用概况](#当前使用概况)
- [API Key 配置分析](#api-key-配置分析)
- [模型使用位置](#模型使用位置)
- [存在的问题](#存在的问题)
- [改进方案](#改进方案)
- [实施建议](#实施建议)

---

## 🔍 当前使用概况

### 支持的 API 服务

项目当前支持以下 LLM API 服务：

| 服务类型 | 优先级 | 配置方式 | 状态 |
|---------|--------|---------|------|
| **ChatAIAPI** (转发服务) | 🥇 首选 | `CHATAIAPI_KEY` / `CHATAI_API_KEY` | ✅ 正常使用 |
| **OpenAI API** (原生) | 🥈 备选 | `OPENAI_API_KEY` | ⚠️ 可选配置 |
| **API_KEY_OVERRIDE** | 🚀 临时 | PowerShell 环境变量注入 | ✅ 支持运行时覆盖 |

### 当前使用的模型

| 模型名称 | 用途 | 位置 | 默认值 |
|---------|------|------|--------|
| `claude-3-5-sonnet-20240620` | 质量评估 | `evaluate_chats.py` | ✅ 是 |
| `claude-3-5-sonnet-20240620` | API 端点默认 | `main.py` | ✅ 是 |
| `deepseek-chat` | 流程分析 | `conversation_flow_analyzer.py` | ⚠️ 硬编码调用 |
| 用户可选 | API 请求参数 | 前端传递 | ⭐ 支持动态切换 |

### 关键统计数据

- **API Key 读取位置**: 5 处
- **模型配置位置**: 4 处
- **硬编码默认模型**: 3 处
- **环境变量数量**: 7 个

---

## 🔑 API Key 配置分析

### 环境变量层级

项目使用**多层级回退机制**读取 API Key：

```python
# 优先级从高到低
api_key = (
    os.getenv("API_KEY_OVERRIDE")     # 1. 运行时注入（最高优先级）
    or os.getenv("OPENAI_API_KEY")    # 2. OpenAI 原生 API
    or os.getenv("CHATAIAPI_KEY")     # 3. ChatAI API（首选）
    or os.getenv("CHATAI_API_KEY")    # 4. ChatAI API（别名）
)
```

### 配置文件位置

#### 1. backend/.env （主配置文件）

```env
# ChatAIAPI Key - 转发服务（推荐）
CHATAIAPI_KEY=sk-yEI0NzjjM24Ec0RUpMyrQQGYN6cvGx27F6XCNYEIxyaigQJP
CHATAI_API_KEY=sk-yEI0NzjjM24Ec0RUpMyrQQGYN6cvGx27F6XCNYEIxyaigQJP

# API 基础 URL
CHATAI_BASE_URL=https://api.chataiapi.com/v1

# 可选：OpenAI 原生 API
# OPENAI_API_KEY=your_openai_api_key_here
```

#### 2. backend/.env.example （配置模板）

提供了完整的配置说明和示例值。

### API Key 读取位置汇总

| 文件路径 | 读取方式 | 用途 |
|---------|---------|------|
| `api/main.py` (L106-110) | 多层级回退 | `/api/health` 健康检查 |
| `api/main.py` (L141-145) | 多层级回退 | `/api/evaluate-quality` 评估端点 |
| `api/main.py` (L251-255) | 多层级回退 | `/api/analyze-flow` 流程分析 |
| `core/evaluate_chats.py` (L64-67) | 三层回退 | 评估器初始化 |
| `core/custom_llm.py` | 参数传递 | LLM 模型初始化 |

### ⚠️ 发现的问题

1. **代码重复**: API Key 读取逻辑在 3 个不同文件中重复出现
2. **不一致性**: 某些地方缺少 `API_KEY_OVERRIDE` 支持
3. **维护困难**: 修改读取逻辑需要同步多处代码

---

## 📍 模型使用位置

### 1. backend/core/custom_llm.py

**核心 LLM 适配器** - 所有模型调用的基础类

```python
class ChatAIAPIModel(DeepEvalBaseLLM):
    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20240620",  # ⚠️ 硬编码默认值
        base_url: str = "https://api.chataiapi.com/v1"
    ):
        # ... 模型初始化逻辑
```

**便捷函数**:
```python
def create_claude_sonnet(api_key: str) -> ChatAIAPIModel:
    return ChatAIAPIModel(api_key=api_key, model="claude-3-5-sonnet-20240620")

def create_deepseek_chat(api_key: str) -> ChatAIAPIModel:
    return ChatAIAPIModel(api_key=api_key, model="deepseek-chat")
```

**配置项**:
- ✅ `CHATAI_BASE_URL` - API 基础地址
- ✅ `CHATAI_TIMEOUT` - 请求超时 (格式: "连接,读取" 或单值)
- ✅ `CHATAI_RETRY_TOTAL` - 重试次数 (默认 3)
- ✅ `CHATAI_RETRY_BACKOFF` - 重试退避因子 (默认 1.5)

---

### 2. backend/core/evaluate_chats.py

**质量评估器** - 负责对话质量评估

```python
class ChatQualityEvaluator:
    def __init__(
        self,
        data_folder: str,
        model: str = "claude-3-5-sonnet-20240620",  # ⚠️ 硬编码默认值
        use_custom_api: bool = True
    ):
        # ... 初始化评估指标
```

**使用的评估指标**:
- `relevancy` - 答案相关性
- `helpfulness` - 有用性 (GEval)
- `coherence` - 连贯性 (GEval)
- `empathy` - 共情能力 (GEval)
- `toxicity` - 毒性检测
- `bias` - 偏见检测

**特点**:
- 所有指标都使用同一个 LLM 模型
- 支持自定义模型和原生 OpenAI API

---

### 3. backend/core/conversation_flow_analyzer.py

**流程分析器** - 分析对话发展过程

```python
class ConversationFlowAnalyzer:
    def __init__(self, model):
        self.model = model  # 接收外部传入的模型实例
```

**调用位置** (`api/main.py` L279):
```python
# 创建 LLM 模型
model = create_deepseek_chat(api_key)  # ⚠️ 硬编码使用 DeepSeek

# 创建分析器
analyzer = ConversationFlowAnalyzer(model)
```

**分析功能**:
- 问题分类 (clarifying, deepening, emotional, technical, off-topic)
- 价值等级评估 (high, medium, low)
- 话题转移检测
- 流程摘要生成

---

### 4. backend/api/main.py

**FastAPI 端点** - 接收前端请求

#### 端点 1: `/api/evaluate-quality` (L123)

```python
async def evaluate_quality(
    file: UploadFile = File(...),
    max_qa_pairs: int = 3,
    model: str = "claude-3-5-sonnet-20240620"  # ⚠️ 硬编码默认值
):
    # 创建评估器
    evaluator = ChatQualityEvaluator(
        str(data_folder),
        model=model,  # ✅ 支持动态传入
        use_custom_api=True
    )
```

#### 端点 2: `/api/analyze-flow` (L237)

```python
async def analyze_flow(file: UploadFile = File(...)):
    # 创建 LLM 模型
    model = create_deepseek_chat(api_key)  # ⚠️ 固定使用 DeepSeek
    
    # 创建分析器
    analyzer = ConversationFlowAnalyzer(model)
```

### 模型使用矩阵

| 功能模块 | 默认模型 | 是否可配置 | 配置方式 |
|---------|---------|-----------|---------|
| 质量评估 API | Claude Sonnet 3.5 | ✅ 是 | API 请求参数 `model` |
| 流程分析 API | DeepSeek Chat | ❌ 否 | 硬编码 |
| 评估器类 | Claude Sonnet 3.5 | ✅ 是 | 构造函数参数 |
| LLM 适配器 | Claude Sonnet 3.5 | ✅ 是 | 构造函数参数 |

---

## ⚠️ 存在的问题

### 问题 1: 配置分散 🔴 严重

**现象**: 模型名称硬编码在多个文件中

```python
# custom_llm.py
model: str = "claude-3-5-sonnet-20240620"

# evaluate_chats.py
model: str = "claude-3-5-sonnet-20240620"

# main.py
model: str = "claude-3-5-sonnet-20240620"
```

**影响**:
- 更换默认模型需要修改 3+ 处代码
- 容易遗漏某个位置导致不一致
- 无法全局快速切换模型

---

### 问题 2: API Key 读取逻辑重复 🟡 中等

**现象**: 同样的代码出现在多个文件

```python
# api/main.py - 出现 3 次
api_key = (
    os.getenv("API_KEY_OVERRIDE")
    or os.getenv("OPENAI_API_KEY")
    or os.getenv("CHATAIAPI_KEY")
    or os.getenv("CHATAI_API_KEY")
)

# core/evaluate_chats.py - 略有差异
api_key = (
    os.getenv('API_KEY_OVERRIDE')
    or os.getenv('CHATAIAPI_KEY')
    or os.getenv('CHATAI_API_KEY')
)
```

**影响**:
- DRY 原则违背
- 修改优先级需要同步多处
- 某些地方不支持 `OPENAI_API_KEY`

---

### 问题 3: 流程分析模型固定 🟡 中等

**现象**: `analyze_flow` 端点硬编码使用 DeepSeek

```python
# api/main.py L279
model = create_deepseek_chat(api_key)  # 无法修改
```

**影响**:
- 用户无法为流程分析选择其他模型
- 与质量评估 API 的灵活性不一致
- 如果 DeepSeek 不可用会导致功能失效

---

### 问题 4: 缺少集中配置文件 🟢 轻微

**现象**: 没有单一的配置管理模块

**影响**:
- 新增模型支持需要修改多处
- 配置项文档分散
- 难以实现配置热重载

---

### 问题 5: 环境变量命名不统一 🟢 轻微

**现象**: 同一配置有多个别名

```env
CHATAIAPI_KEY=xxx
CHATAI_API_KEY=xxx
OPENAI_API_KEY=xxx
API_KEY_OVERRIDE=xxx
```

**影响**:
- 用户容易混淆使用哪个变量名
- 文档需要解释多个名称
- 增加理解成本

---

## 💡 改进方案

### 方案概述

创建**统一配置管理中心**，集中管理所有 LLM 相关配置。

### 架构设计

```
backend/
├── config/
│   ├── __init__.py
│   ├── llm_config.py      # 🆕 LLM 配置管理中心
│   └── models.py          # 🆕 模型预设配置
├── core/
│   ├── custom_llm.py      # ✏️ 简化，使用配置
│   ├── evaluate_chats.py  # ✏️ 使用配置
│   └── conversation_flow_analyzer.py
└── api/
    └── main.py            # ✏️ 使用配置
```

---

### 方案 1: 创建配置管理模块 ⭐ 推荐

#### 文件: `backend/config/llm_config.py`

```python
"""
LLM 配置管理中心
统一管理所有 LLM API 相关配置
"""
import os
from typing import Optional, Dict
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(override=True)


class LLMConfig:
    """LLM 配置管理类"""
    
    # ============ API Key 配置 ============
    
    @staticmethod
    def get_api_key() -> Optional[str]:
        """
        获取 API Key（按优先级）
        
        优先级:
        1. API_KEY_OVERRIDE (运行时注入)
        2. CHATAIAPI_KEY (ChatAI 主键)
        3. CHATAI_API_KEY (ChatAI 别名)
        4. OPENAI_API_KEY (OpenAI 原生)
        """
        return (
            os.getenv("API_KEY_OVERRIDE")
            or os.getenv("CHATAIAPI_KEY")
            or os.getenv("CHATAI_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )
    
    @staticmethod
    def get_base_url() -> str:
        """获取 API 基础 URL"""
        return os.getenv(
            "CHATAI_BASE_URL", 
            "https://api.chataiapi.com/v1"
        )
    
    # ============ 模型配置 ============
    
    # 默认模型配置
    DEFAULT_MODELS = {
        "evaluation": "claude-3-5-sonnet-20240620",  # 质量评估默认
        "flow_analysis": "deepseek-chat",            # 流程分析默认
        "general": "claude-3-5-sonnet-20240620"      # 通用默认
    }
    
    @classmethod
    def get_default_model(cls, task: str = "general") -> str:
        """
        获取指定任务的默认模型
        
        Args:
            task: 任务类型 (evaluation, flow_analysis, general)
        """
        # 支持环境变量覆盖
        env_key = f"DEFAULT_MODEL_{task.upper()}"
        return os.getenv(env_key, cls.DEFAULT_MODELS.get(task, cls.DEFAULT_MODELS["general"]))
    
    # ============ 超时和重试配置 ============
    
    @staticmethod
    def get_timeout() -> tuple:
        """获取超时配置 (连接超时, 读取超时)"""
        env_timeout = os.getenv("CHATAI_TIMEOUT")
        if env_timeout:
            try:
                parts = [p.strip() for p in env_timeout.split(',')]
                if len(parts) == 2:
                    return (float(parts[0]), float(parts[1]))
                else:
                    t = float(parts[0])
                    return (t, t)
            except:
                pass
        return (15, 60)  # 默认值
    
    @staticmethod
    def get_retry_config() -> Dict[str, int]:
        """获取重试配置"""
        return {
            "total": int(os.getenv("CHATAI_RETRY_TOTAL", "3")),
            "backoff": float(os.getenv("CHATAI_RETRY_BACKOFF", "1.5"))
        }
    
    # ============ 模型预设 ============
    
    SUPPORTED_MODELS = {
        # Claude 系列
        "claude-3-5-sonnet-20240620": {
            "name": "Claude 3.5 Sonnet",
            "provider": "Anthropic",
            "cost": "medium",
            "speed": "fast",
            "quality": "excellent",
            "recommended_for": ["evaluation", "complex_reasoning"]
        },
        
        # DeepSeek 系列
        "deepseek-chat": {
            "name": "DeepSeek Chat",
            "provider": "DeepSeek",
            "cost": "low",
            "speed": "very_fast",
            "quality": "good",
            "recommended_for": ["flow_analysis", "batch_processing"]
        },
        "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B": {
            "name": "DeepSeek R1 Distill",
            "provider": "DeepSeek",
            "cost": "very_low",
            "speed": "very_fast",
            "quality": "good",
            "recommended_for": ["reasoning", "fast_response"]
        },
        "deepseek-ai/DeepSeek-V3.2": {
            "name": "DeepSeek V3.2",
            "provider": "DeepSeek",
            "cost": "low",
            "speed": "fast",
            "quality": "excellent",
            "recommended_for": ["comprehensive_analysis"]
        },
        
        # OpenAI 系列 (如果使用)
        "gpt-4o-mini": {
            "name": "GPT-4o Mini",
            "provider": "OpenAI",
            "cost": "medium",
            "speed": "fast",
            "quality": "excellent",
            "recommended_for": ["general"]
        }
    }
    
    @classmethod
    def get_model_info(cls, model_name: str) -> Optional[Dict]:
        """获取模型详细信息"""
        return cls.SUPPORTED_MODELS.get(model_name)
    
    @classmethod
    def list_models(cls) -> list:
        """列出所有支持的模型"""
        return list(cls.SUPPORTED_MODELS.keys())


# ============ 便捷函数 ============

def get_api_key() -> Optional[str]:
    """快捷获取 API Key"""
    return LLMConfig.get_api_key()


def get_model_for_task(task: str) -> str:
    """快捷获取任务默认模型"""
    return LLMConfig.get_default_model(task)
```

**优点**:
- ✅ 单一数据源 (Single Source of Truth)
- ✅ 易于维护和扩展
- ✅ 支持环境变量覆盖
- ✅ 包含模型元数据便于选择

---

### 方案 2: 修改现有代码使用配置

#### 修改 `custom_llm.py`

```python
from config.llm_config import LLMConfig

class ChatAIAPIModel(DeepEvalBaseLLM):
    def __init__(
        self,
        api_key: str = None,
        model: str = None,  # 改为可选
        base_url: str = None
    ):
        # 使用配置中心的默认值
        self.api_key = api_key or LLMConfig.get_api_key()
        self._requested_model = model or LLMConfig.get_default_model("general")
        self.base_url = (base_url or LLMConfig.get_base_url()).rstrip('/')
        
        # 使用配置的超时和重试
        self._timeout = LLMConfig.get_timeout()
        retry_config = LLMConfig.get_retry_config()
        # ... 其余代码
```

#### 修改 `evaluate_chats.py`

```python
from config.llm_config import get_api_key, get_model_for_task

class ChatQualityEvaluator:
    def __init__(
        self,
        data_folder: str,
        model: str = None,  # 改为可选
        use_custom_api: bool = True
    ):
        self.data_folder = data_folder
        # 使用配置的默认模型
        self.model_name = model or get_model_for_task("evaluation")
        self.use_custom_api = use_custom_api
        
        if use_custom_api:
            api_key = get_api_key()  # 使用统一函数
            if not api_key:
                raise ValueError("未配置 API Key")
            self.custom_llm = ChatAIAPIModel(api_key=api_key, model=self.model_name)
```

#### 修改 `main.py`

```python
from config.llm_config import get_api_key, get_model_for_task

@app.post("/api/evaluate-quality")
async def evaluate_quality(
    file: UploadFile = File(...),
    max_qa_pairs: int = 3,
    model: str = None  # 改为可选，使用 None 作为默认值
):
    try:
        api_key = get_api_key()  # 使用统一函数
        if not api_key:
            raise HTTPException(status_code=500, detail="未配置 API Key")
        
        # 使用配置的默认模型
        model = model or get_model_for_task("evaluation")
        
        evaluator = ChatQualityEvaluator(
            str(data_folder),
            model=model,
            use_custom_api=True
        )
        # ...

@app.post("/api/analyze-flow")
async def analyze_flow(
    file: UploadFile = File(...),
    model: str = None  # 🆕 新增模型参数
):
    try:
        api_key = get_api_key()
        if not api_key:
            raise HTTPException(status_code=500, detail="未配置 API Key")
        
        # 支持动态选择模型
        model_name = model or get_model_for_task("flow_analysis")
        llm_model = ChatAIAPIModel(api_key=api_key, model=model_name)
        
        analyzer = ConversationFlowAnalyzer(llm_model)
        # ...
```

---

### 方案 3: 新增环境变量配置

在 `.env` 中新增：

```env
# ============ 模型默认配置 ============
# 可以通过环境变量覆盖代码中的默认值

# 质量评估默认模型
DEFAULT_MODEL_EVALUATION=claude-3-5-sonnet-20240620

# 流程分析默认模型
DEFAULT_MODEL_FLOW_ANALYSIS=deepseek-chat

# 通用默认模型
DEFAULT_MODEL_GENERAL=claude-3-5-sonnet-20240620
```

**使用场景**:
```bash
# 快速切换评估模型为 DeepSeek V3.2
DEFAULT_MODEL_EVALUATION=deepseek-ai/DeepSeek-V3.2 python start_server.py

# 或在 PowerShell 中
$env:DEFAULT_MODEL_EVALUATION="deepseek-ai/DeepSeek-V3.2"
python start_server.py
```

---

## 🚀 实施建议

### 阶段 1: 创建配置模块 (1-2小时)

**步骤**:
1. 创建 `backend/config/` 目录
2. 创建 `llm_config.py` 文件
3. 实现 `LLMConfig` 类
4. 添加单元测试

**验证**:
```python
# 测试配置读取
from config.llm_config import LLMConfig

print("API Key:", LLMConfig.get_api_key()[:20] + "...")
print("评估模型:", LLMConfig.get_default_model("evaluation"))
print("流程模型:", LLMConfig.get_default_model("flow_analysis"))
print("支持的模型:", LLMConfig.list_models())
```

---

### 阶段 2: 重构现有代码 (2-3小时)

**优先级**:
1. ✅ 修改 `custom_llm.py` - 使用配置获取默认值
2. ✅ 修改 `evaluate_chats.py` - 使用统一 API Key 函数
3. ✅ 修改 `main.py` - 支持流程分析模型选择
4. ✅ 更新 `.env.example` - 添加新配置项

**注意事项**:
- 保持向后兼容，默认参数使用 `None`
- 添加充分的注释说明
- 确保所有测试通过

---

### 阶段 3: 测试和文档 (1小时)

**测试清单**:
- [ ] API Key 读取正确
- [ ] 默认模型配置生效
- [ ] 环境变量覆盖工作
- [ ] 质量评估 API 正常
- [ ] 流程分析 API 正常
- [ ] 模型切换功能正常

**文档更新**:
- [ ] 更新 `README.md` - 新增配置说明
- [ ] 更新 `API_MODEL_GUIDE.md` - 简化模型切换指南
- [ ] 创建 `CONFIG_GUIDE.md` - 详细配置说明

---

### 阶段 4: 增强功能 (可选)

#### 功能 1: 模型性能监控

```python
class LLMConfig:
    @staticmethod
    def log_model_usage(model: str, task: str, tokens: int, duration: float):
        """记录模型使用情况"""
        # 可以记录到日志或数据库
        pass
```

#### 功能 2: 成本估算

```python
class LLMConfig:
    PRICING = {
        "claude-3-5-sonnet-20240620": {"input": 0.003, "output": 0.015},
        "deepseek-chat": {"input": 0.0001, "output": 0.0002},
        # ...
    }
    
    @classmethod
    def estimate_cost(cls, model: str, input_tokens: int, output_tokens: int) -> float:
        """估算成本 (USD)"""
        pricing = cls.PRICING.get(model)
        if not pricing:
            return 0.0
        return (input_tokens * pricing["input"] / 1000 + 
                output_tokens * pricing["output"] / 1000)
```

#### 功能 3: 模型健康检查

```python
from config.llm_config import LLMConfig

async def check_model_availability(model: str) -> bool:
    """检查模型是否可用"""
    try:
        api_key = LLMConfig.get_api_key()
        test_model = ChatAIAPIModel(api_key=api_key, model=model)
        test_model.generate("test")
        return True
    except:
        return False

# 在启动时检查
@app.on_event("startup")
async def startup_check():
    default_model = LLMConfig.get_default_model("evaluation")
    is_available = await check_model_availability(default_model)
    if not is_available:
        logger.warning(f"默认模型 {default_model} 不可用")
```

---

## 📊 对比：改进前后

### 切换模型对比

#### 改进前 ❌

要将所有模型从 Claude 切换到 DeepSeek V3.2：

```bash
# 需要修改 3 个文件的代码
1. vim backend/core/custom_llm.py      # 修改默认值
2. vim backend/core/evaluate_chats.py  # 修改默认值
3. vim backend/api/main.py             # 修改默认值
4. 重启服务
```

#### 改进后 ✅

方法 1 - 修改配置文件：
```bash
# 修改 .env
DEFAULT_MODEL_EVALUATION=deepseek-ai/DeepSeek-V3.2
DEFAULT_MODEL_FLOW_ANALYSIS=deepseek-ai/DeepSeek-V3.2
DEFAULT_MODEL_GENERAL=deepseek-ai/DeepSeek-V3.2
```

方法 2 - 运行时覆盖：
```powershell
$env:DEFAULT_MODEL_EVALUATION="deepseek-ai/DeepSeek-V3.2"
python start_server.py
```

方法 3 - API 请求时指定：
```javascript
// 前端代码
await fetch('/api/evaluate-quality', {
  method: 'POST',
  body: formData,
  headers: {
    'X-Model': 'deepseek-ai/DeepSeek-V3.2'
  }
})
```

---

### 代码维护对比

| 方面 | 改进前 | 改进后 |
|------|--------|--------|
| **API Key 读取** | 3+ 处重复代码 | 1 个统一函数 |
| **默认模型配置** | 3 处硬编码 | 1 个配置文件 |
| **添加新模型** | 需要文档说明 | 自动包含元数据 |
| **切换模型** | 修改代码 | 修改配置 |
| **测试难度** | 需要 mock 环境变量 | 直接注入配置 |

---

## 🎯 快速开始：使用新配置系统

### 示例 1: 快速切换到 SiliconFlow 的 DeepSeek 模型

```bash
# 1. 修改 .env
CHATAIAPI_KEY=sk-pgorpekchnscrzsupkywglclsxxouuhzjtiierkcxaoxxxqu
CHATAI_BASE_URL=https://api.siliconflow.cn/v1

# 2. 配置默认模型
DEFAULT_MODEL_EVALUATION=deepseek-ai/DeepSeek-V3.2
DEFAULT_MODEL_FLOW_ANALYSIS=deepseek-ai/DeepSeek-R1-Distill-Qwen-7B

# 3. 启动服务
python backend/start_server.py
```

### 示例 2: 混合使用不同模型

```python
# 质量评估用高质量模型
evaluator = ChatQualityEvaluator(
    data_folder,
    model="claude-3-5-sonnet-20240620"  # 高质量
)

# 流程分析用快速模型
analyzer = ConversationFlowAnalyzer(
    ChatAIAPIModel(model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B")  # 快速
)
```

### 示例 3: 成本优化配置

```env
# 使用最经济的模型组合
DEFAULT_MODEL_EVALUATION=deepseek-chat          # 成本低
DEFAULT_MODEL_FLOW_ANALYSIS=deepseek-ai/DeepSeek-R1-Distill-Qwen-7B  # 最便宜

# 批量处理时的超时配置
CHATAI_TIMEOUT=20,120  # 连接20s, 读取120s
CHATAI_RETRY_TOTAL=5   # 增加重试次数
```

---

## 📝 总结

### 当前状况

- ❌ 配置分散在多个文件
- ❌ API Key 读取逻辑重复
- ❌ 模型硬编码，难以切换
- ❌ 缺少统一管理机制

### 改进目标

- ✅ 创建统一配置中心
- ✅ 消除重复代码
- ✅ 支持灵活模型切换
- ✅ 提供模型元数据管理

### 预期收益

1. **开发效率**: 修改配置从 "3个文件" → "1个文件"
2. **可维护性**: 统一数据源，减少 70% 重复代码
3. **灵活性**: 支持运行时、环境变量、API 参数三种配置方式
4. **可扩展性**: 新增模型只需更新配置文件

### 建议优先级

1. 🔴 **高优先级**: 创建配置模块 (立即实施)
2. 🟡 **中优先级**: 重构现有代码 (本周完成)
3. 🟢 **低优先级**: 增强功能 (后续迭代)

---

## 🔗 相关文档

- [API_MODEL_GUIDE.md](API_MODEL_GUIDE.md) - 模型配置指南
- [README.md](../README.md) - 项目主文档
- [backend/.env.example](../backend/.env.example) - 配置模板

---

**文档生成时间**: 2026年1月2日  
**作者**: GitHub Copilot  
**版本**: v1.0

