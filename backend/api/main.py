"""
ConveVisAna FastAPI Backend
提供 RESTful API 接口供前端调用
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# 导入核心模块
import sys
sys.path.append(str(Path(__file__).parent.parent))
from core.data_loader import ChatDataLoader
from core.custom_llm import ChatAIAPIModel, create_default_model
from core.evaluate_chats import ChatQualityEvaluator
from core.conversation_flow_analyzer import ConversationFlowAnalyzer

# 导入配置中心
from config.llm_config import LLMConfig, get_api_key, get_model_for_task

# 加载环境变量（强制使用 .env 覆盖进程环境，避免旧值残留）
load_dotenv(override=True)

app = FastAPI(
    title="ConveVisAna API",
    description="ChatGPT 对话分析 API - 提供 AI 驱动的质量评估和流程分析",
    version="1.0.0"
)

# 配置 CORS - 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js 开发环境
        "http://localhost:3001",  # Next.js 开发环境 (备用端口)
        "http://localhost:5173",  # Vite 开发环境
        "https://*.vercel.app",   # Vercel 部署
        "https://*.netlify.app",  # Netlify 部署
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 数据模型 ============

class EvaluationRequest(BaseModel):
    """质量评估请求"""
    conversation_id: Optional[str] = None
    max_qa_pairs: int = 3
    selected_metrics: Optional[List[str]] = None
    model: str = "claude-3-5-sonnet-20240620"


class FlowAnalysisRequest(BaseModel):
    """流程分析请求"""
    conversation_id: Optional[str] = None


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str
    api_available: bool
    has_api_key: bool  # 前端期望的字段


# ============ 辅助函数 ============

def save_temp_file(content: bytes, filename: str) -> Path:
    """保存临时文件"""
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    temp_file = temp_dir / filename
    temp_file.write_bytes(content)
    return temp_file


def parse_conversations_data(file_path: Path) -> List[Dict]:
    """解析对话数据文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


# ============ API 端点 ============

@app.get("/", response_model=HealthResponse)
async def root():
    """根路径 - API 信息"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "api_available": True
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "api_available": LLMConfig.is_api_available(),
        "has_api_key": LLMConfig.is_api_available()
    }


@app.post("/api/evaluate-quality")
async def evaluate_quality(
    file: UploadFile = File(...),
    max_qa_pairs: int = 3,
    model: str = None  # 默认使用配置中心的评估模型
):
    """
    评估对话质量
    
    使用 deepeval 和 LLM 对对话进行多维度质量评估
    
    参数:
    - file: conversations.json 文件
    - max_qa_pairs: 评估的问答对数量（默认3，防止成本过高）
    - model: 使用的 LLM 模型（默认使用硅基流动免费模型）
    
    返回:
    - 评估结果包括相关性、有用性、连贯性、同理心、毒性、偏见等指标
    """
    try:
        # 使用配置中心检查 API Key
        api_key = get_api_key()
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="未配置 API Key。请在 .env 文件中设置 CHATAIAPI_KEY 或 CHATAI_API_KEY"
            )
        
        # 保存上传的文件（固定文件名为 conversations.json）
        content = await file.read()
        temp_file = save_temp_file(content, "conversations.json")
        
        # 获取文件所在目录
        data_folder = temp_file.parent
        
        # 使用配置的默认模型（如果未指定）
        model = model or get_model_for_task("evaluation")
        
        # 创建评估器
        evaluator = ChatQualityEvaluator(
            str(data_folder),
            model=model,
            use_custom_api=True
        )
        
        # 执行评估
        results = evaluator.evaluate_conversation(
            max_qa_pairs=max_qa_pairs
        )

        # === 适配前端预期的数据结构 (QualityEvaluationResult) ===
        summary_metrics = results.get('summary', {}).get('metrics', {})

        def metric_entry(name: str):
            m = summary_metrics.get(name)
            if not m:
                return None
            score = m.get('average_score', 0)
            threshold = getattr(evaluator.metrics.get(name), 'threshold', 0)
            # 对毒性/偏见类指标采用“越低越好”的通过逻辑
            if name in ['toxicity', 'bias']:
                passed = score <= threshold if threshold else True
            else:
                passed = score >= threshold if threshold else True
            return {
                'score': score,
                'threshold': threshold,
                'passed': passed,
            }

        metrics_payload = {
            'relevancy': metric_entry('relevancy'),
            'helpfulness': metric_entry('helpfulness'),
            'coherence': metric_entry('coherence'),
            'toxicity': metric_entry('toxicity'),
            'bias': metric_entry('bias'),
        }

        # 前端用于可视化的整体得分（保持与前端计算方式一致）
        def safe_score(entry, inverse=False):
            if not entry or entry.get('score') is None:
                return 0
            return (1 - entry['score']) if inverse else entry['score']

        average_score = (
            safe_score(metrics_payload['relevancy']) +
            safe_score(metrics_payload['helpfulness']) +
            safe_score(metrics_payload['coherence']) +
            safe_score(metrics_payload['toxicity'], inverse=True) +
            safe_score(metrics_payload['bias'], inverse=True)
        ) / 5

        response_payload = {
            'pairs_evaluated': results.get('total_qa_pairs', 0),
            'metrics': metrics_payload,
            'average_score': average_score,
            # 兼容字段：保留原始结果以便调试或下载
            'raw': results,
        }

        # 清理临时文件
        temp_file.unlink()

        return JSONResponse(content={
            "success": True,
            "data": response_payload,
            "message": f"成功评估 {max_qa_pairs} 个问答对"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"评估失败: {str(e)}")


@app.post("/api/analyze-flow")
async def analyze_flow(
    file: UploadFile = File(...),
    model: str = None  # 支持指定模型，默认使用配置中心的流程分析模型
):
    """
    分析对话流程
    
    识别对话模式、问题类型分布、对话长度趋势等
    
    参数:
    - file: conversations.json 文件
    - model: 使用的 LLM 模型（默认使用硅基流动免费模型）
    
    返回:
    - 流程分析结果包括问题类型分布、对话长度统计等
    """
    try:
        # 使用配置中心检查 API Key
        api_key = get_api_key()
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="未配置 API Key。请在 .env 文件中设置 CHATAIAPI_KEY 或 CHATAI_API_KEY"
            )
        
        # 保存上传的文件（固定文件名为 conversations.json）
        content = await file.read()
        temp_file = save_temp_file(content, "conversations.json")
        
        # 解析数据
        conversations_data = parse_conversations_data(temp_file)
        
        # 找到最长的对话
        longest_conv = max(
            conversations_data,
            key=lambda c: len([n for n in c.get('mapping', {}).values() 
                              if n.get('message')])
        )
        
        # 使用配置的默认模型（如果未指定）
        model_name = model or get_model_for_task("flow_analysis")
        
        # 创建 LLM 模型
        llm_model = ChatAIAPIModel(api_key=api_key, model=model_name)
        
        # 创建分析器
        analyzer = ConversationFlowAnalyzer(llm_model)
        
        # 提取对话回合
        # 这里需要实现提取逻辑，简化版：
        from core.data_loader import ChatDataLoader
        
        loader = ChatDataLoader(str(temp_file.parent))
        conversations = loader.load_conversations()
        
        if not conversations:
            raise HTTPException(status_code=400, detail="未找到有效对话")
        
        # 选择最长的对话
        conv = max(conversations, key=lambda c: len(c.messages))
        
        # 转换为分析格式
        turns = []
        for i in range(0, len(conv.messages) - 1, 2):
            if i + 1 < len(conv.messages):
                user_msg = conv.messages[i]
                assistant_msg = conv.messages[i + 1]
                
                if user_msg.role == 'user' and assistant_msg.role == 'assistant':
                    turns.append({
                        "question": user_msg.content,
                        "answer": assistant_msg.content
                    })
        
        # 执行分析（原始结果）
        result = analyzer.analyze_conversation_flow(
            turns,
            conversation_title=conv.title
        )

        # ========== 适配前端所需结构 ==========
        # 构造带 question_type 的前端 turns
        turn_analysis = result.get('turn_analysis', [])
        frontend_turns = []
        for i, t in enumerate(turns):
            qtype = 'other'
            if i < len(turn_analysis):
                qtype = turn_analysis[i].get('question_type', 'other') or 'other'
            frontend_turns.append({
                "question": t.get('question', ''),
                "answer": t.get('answer', ''),
                "question_type": qtype,
                "turn_number": i + 1
            })

        # 统计与均值
        total_turns = len(frontend_turns)
        avg_question_length = (
            sum(len(t.get('question', '') or '') for t in frontend_turns) / total_turns
            if total_turns > 0 else 0
        )
        avg_response_length = (
            sum(len(t.get('answer', '') or '') for t in frontend_turns) / total_turns
            if total_turns > 0 else 0
        )
        question_type_counts: Dict[str, int] = {}
        for t in frontend_turns:
            qt = t.get('question_type') or 'other'
            question_type_counts[qt] = question_type_counts.get(qt, 0) + 1

        frontend_data = {
            "conversation_id": None,
            "total_turns": total_turns,
            "turns": frontend_turns,
            "summary": {
                "question_type_counts": question_type_counts,
                "avg_question_length": avg_question_length,
                "avg_response_length": avg_response_length,
                "total_turns": total_turns,
            },
            "cached": False,
            # 附带原始结果，便于调试（前端无需依赖）
            "_raw": {
                "flow_summary": result.get('flow_summary', {}),
                "turn_analysis": turn_analysis,
            }
        }
        
        # 清理临时文件
        temp_file.unlink()
        
        return JSONResponse(content={
            "success": True,
            "data": frontend_data,
            "message": f"成功分析对话流程，包含 {len(turns)} 个回合"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"流程分析失败: {str(e)}")


@app.post("/api/generate-report")
async def generate_report(
    analysis_data: Dict = Body(...),
    report_type: str = "html"
):
    """
    生成分析报告
    
    根据分析数据生成可视化报告
    
    参数:
    - analysis_data: 分析数据（来自 analyze-flow 的结果）
    - report_type: 报告类型（html/json）
    
    返回:
    - 生成的报告内容
    """
    try:
        if report_type == "html":
            from utils.generate_flow_report import generate_html_report
            
            # 保存临时分析数据
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)
            
            temp_json = temp_dir / "analysis.json"
            with open(temp_json, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2)
            
            # 生成 HTML 报告
            output_file = temp_dir / "report.html"
            generate_html_report(str(temp_json), str(output_file))
            
            # 读取报告内容
            with open(output_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # 清理临时文件
            temp_json.unlink()
            output_file.unlink()
            
            return JSONResponse(content={
                "success": True,
                "data": {
                    "html": html_content
                },
                "message": "报告生成成功"
            })
        else:
            return JSONResponse(content={
                "success": True,
                "data": analysis_data,
                "message": "JSON 格式报告"
            })
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
