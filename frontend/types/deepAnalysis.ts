/**
 * TypeScript 类型定义 - 深度分析功能
 * ConveVisAna Frontend Integration
 */

// ============ 质量评估相关类型 ============

export interface MetricScore {
  score: number;
  threshold: number;
  passed: boolean;
  reason?: string;
}

export interface QualityMetrics {
  relevancy: MetricScore;
  helpfulness: MetricScore;
  coherence: MetricScore;
  toxicity: MetricScore;
  bias: MetricScore;
}

export interface QAPairDetail {
  question: string;
  answer: string;
  metrics: Partial<QualityMetrics>;
  overall_score?: number;
}

export interface QualityEvaluationResult {
  pairs_evaluated: number;
  metrics: QualityMetrics;
  details?: QAPairDetail[];
  average_score?: number;
  cached?: boolean;
}

// ============ 流程分析相关类型 ============

export interface QuestionClassification {
  primary_type: string;
  secondary_type?: string;
  confidence: number;
}

export interface TurnAnalysis {
  sentiment: 'positive' | 'neutral' | 'negative';
  complexity: 'low' | 'medium' | 'high';
  score: number;
}

export interface ConversationTurn {
  question: string;
  answer: string;
  question_type: string;
  turn_number?: number;
  role?: 'user' | 'assistant' | 'system';
  classification?: QuestionClassification;
  analysis?: TurnAnalysis;
  timestamp?: string;
}

export interface FlowSummary {
  question_type_counts: Record<string, number>;
  avg_question_length: number;
  avg_response_length: number;
  conversation_flow?: 'coherent' | 'scattered' | 'mixed';
  total_turns: number;
}

export interface FlowAnalysisResult {
  conversation_id?: string;
  total_turns: number;
  turns: ConversationTurn[];
  summary: FlowSummary;
  cached?: boolean;
}

// ============ 报告生成相关类型 ============

export interface ReportMetadata {
  user_name?: string;
  report_title?: string;
  generated_at?: string;
}

export interface ReportRequest {
  quality_metrics?: QualityEvaluationResult;
  flow_analysis?: FlowAnalysisResult;
  metadata?: ReportMetadata;
}

export interface ReportResponse {
  html?: string;
  download_url?: string;
  format?: 'html' | 'pdf';
}

// ============ 健康检查类型 ============

export interface BackendHealthResponse {
  status: 'healthy' | 'unhealthy';
  has_api_key: boolean;
  version?: string;
  timestamp?: string;
}

// ============ API 错误类型 ============

export interface APIError {
  error: string;
  detail?: string;
  code?: string;
  status?: number;
}

// ============ 分析状态类型 ============

export type AnalysisStatus = 'idle' | 'loading' | 'success' | 'error';

export interface AnalysisState {
  status: AnalysisStatus;
  error?: string;
  progress?: number;
  message?: string;
}
