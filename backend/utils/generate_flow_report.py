"""
对话流程可视化工具 - 生成对话分析的可视化报告
"""
import json
from pathlib import Path
from typing import Dict, Any


def generate_html_report(analysis_file: str, output_file: str = 'evaluation_results/flow_report.html'):
    """
    生成对话流程分析的 HTML 可视化报告
    
    Args:
        analysis_file: 分析结果 JSON 文件路径
        output_file: 输出的 HTML 文件路径
    """
    with open(analysis_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    summary = data['flow_summary']
    turns = data['turn_analysis']
    high_value = data['high_value_turns']
    low_value = data['low_value_turns']
    topic_shifts = data['topic_shifts']
    
    # 生成 HTML
    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>对话流程分析报告 - {data['conversation_title']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.15);
        }}
        
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        
        .section {{
            padding: 40px;
        }}
        
        .section-title {{
            font-size: 1.8em;
            color: #333;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
        }}
        
        .timeline {{
            position: relative;
            padding-left: 30px;
        }}
        
        .timeline::before {{
            content: '';
            position: absolute;
            left: 10px;
            top: 0;
            bottom: 0;
            width: 3px;
            background: linear-gradient(to bottom, #667eea, #764ba2);
        }}
        
        .turn-card {{
            position: relative;
            margin-bottom: 25px;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        
        .turn-card:hover {{
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .turn-card::before {{
            content: attr(data-turn);
            position: absolute;
            left: -28px;
            top: 20px;
            width: 20px;
            height: 20px;
            background: #667eea;
            border-radius: 50%;
            border: 3px solid white;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
        }}
        
        .turn-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .turn-index {{
            font-weight: bold;
            color: #667eea;
            font-size: 1.1em;
        }}
        
        .badges {{
            display: flex;
            gap: 8px;
        }}
        
        .badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        
        .badge-high {{
            background: #d4edda;
            color: #155724;
        }}
        
        .badge-medium {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .badge-low {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .badge-technical {{
            background: #cce5ff;
            color: #004085;
        }}
        
        .badge-deepening {{
            background: #d1ecf1;
            color: #0c5460;
        }}
        
        .badge-clarifying {{
            background: #e7e7ff;
            color: #383874;
        }}
        
        .badge-emotional {{
            background: #ffe6f0;
            color: #6b0030;
        }}
        
        .badge-off-topic {{
            background: #e0e0e0;
            color: #666;
        }}
        
        .turn-question {{
            color: #333;
            margin: 10px 0;
            padding: 15px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 5px;
        }}
        
        .turn-reason {{
            color: #666;
            font-size: 0.95em;
            font-style: italic;
            margin-top: 10px;
        }}
        
        .chart-container {{
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        
        .bar-chart {{
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}
        
        .bar-item {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .bar-label {{
            min-width: 120px;
            font-weight: 500;
            color: #333;
        }}
        
        .bar {{
            flex: 1;
            height: 30px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 5px;
            position: relative;
            transition: width 0.5s;
        }}
        
        .bar-value {{
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            color: white;
            font-weight: bold;
        }}
        
        .highlight-section {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }}
        
        .highlight-card {{
            background: white;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 10px;
            border-left: 5px solid #28a745;
        }}
        
        .highlight-card.low {{
            border-left-color: #dc3545;
        }}
        
        footer {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{data['conversation_title']}</h1>
            <p class="subtitle">对话流程分析报告</p>
        </header>
        
        <div class="summary">
            <div class="stat-card">
                <div class="stat-label">总回合数</div>
                <div class="stat-value">{summary['total_turns']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">高价值问题</div>
                <div class="stat-value">{summary['high_value_ratio']:.0%}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">低价值问题</div>
                <div class="stat-value">{summary['low_value_ratio']:.0%}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">话题转移</div>
                <div class="stat-value">{summary['topic_shifts_count']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">效率分数</div>
                <div class="stat-value">{summary['efficiency_score']:.2f}</div>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">📊 问题类型分布</h2>
            <div class="chart-container">
                <div class="bar-chart">
"""
    
    # 添加问题类型分布条形图
    max_count = max(summary['question_type_distribution'].values())
    type_names = {
        'technical': '技术性问题',
        'deepening': '深入性问题',
        'clarifying': '澄清性问题',
        'emotional': '情感性问题',
        'off-topic': '偏题/闲聊'
    }
    
    for qtype, count in summary['question_type_distribution'].items():
        width_percent = (count / max_count * 100) if max_count > 0 else 0
        html += f"""
                    <div class="bar-item">
                        <div class="bar-label">{type_names.get(qtype, qtype)}</div>
                        <div class="bar" style="width: {width_percent}%">
                            <span class="bar-value">{count}次</span>
                        </div>
                    </div>
"""
    
    html += """
                </div>
            </div>
        </div>
        
"""
    
    # 高价值问题
    if high_value:
        html += """
        <div class="section highlight-section">
            <h2 class="section-title">⭐ 高价值问题</h2>
"""
        for item in high_value[:10]:
            html += f"""
            <div class="highlight-card">
                <div class="turn-header">
                    <span class="turn-index">第 {item['turn_index']} 轮</span>
                    <span class="badge badge-{item['type']}">{type_names.get(item['type'], item['type'])}</span>
                </div>
                <div class="turn-question">{item['question'][:200]}...</div>
                <div class="turn-reason">💡 {item['reason']}</div>
            </div>
"""
        html += """
        </div>
"""
    
    # 低价值问题
    if low_value:
        html += """
        <div class="section">
            <h2 class="section-title">⚠️ 低价值问题</h2>
"""
        for item in low_value[:10]:
            html += f"""
            <div class="highlight-card low">
                <div class="turn-header">
                    <span class="turn-index">第 {item['turn_index']} 轮</span>
                    <span class="badge badge-{item['type']}">{type_names.get(item['type'], item['type'])}</span>
                </div>
                <div class="turn-question">{item['question'][:200]}...</div>
                <div class="turn-reason">⚠️ {item['reason']}</div>
            </div>
"""
        html += """
        </div>
"""
    
    # 完整时间线
    html += """
        <div class="section">
            <h2 class="section-title">📈 对话流程时间线</h2>
            <div class="timeline">
"""
    
    for turn in turns:
        value_class = turn['value_level']
        type_class = turn['question_type']
        
        html += f"""
                <div class="turn-card" data-turn="{turn['turn_index']}">
                    <div class="turn-header">
                        <span class="turn-index">第 {turn['turn_index']} 轮</span>
                        <div class="badges">
                            <span class="badge badge-{value_class}">{value_class.upper()}</span>
                            <span class="badge badge-{type_class}">{type_names.get(type_class, type_class)}</span>
"""
        
        if turn.get('topic_shift'):
            html += """
                            <span class="badge" style="background: #ffc107; color: #000;">话题转移</span>
"""
        
        html += f"""
                        </div>
                    </div>
                    <div class="turn-question">{turn['question']}</div>
                    <div class="turn-reason">{turn['reason']}</div>
                </div>
"""
    
    html += """
            </div>
        </div>
        
        <footer>
            <p>Generated by ConveVisAna - Conversation Flow Analyzer</p>
        </footer>
    </div>
</body>
</html>
"""
    
    # 保存 HTML
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ HTML 报告已生成: {output_file}")


if __name__ == '__main__':
    generate_html_report('evaluation_results/conversation_flow_analysis.json')
