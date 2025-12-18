/**
 * API 客户端 - 与 ConveVisAna 后端通信
 * @module utils/apiClient
 */

import {
  QualityEvaluationResult,
  FlowAnalysisResult,
  ReportResponse,
  ReportRequest,
  BackendHealthResponse,
  APIError,
} from '@/types/deepAnalysis';

/**
 * ConveVisAna API 客户端类
 */
export class ConveVisAnaClient {
  private baseURL: string;

  constructor(baseURL?: string) {
    // 优先使用传入的 URL，否则使用环境变量，最后回退到空字符串
    this.baseURL = 
      baseURL || 
      process.env.NEXT_PUBLIC_BACKEND_BASE_URL || 
      (typeof window !== 'undefined' && (window as any).__BACKEND_URL__) ||
      '';
  }

  /**
   * 设置基础 URL（用于动态配置）
   */
  setBaseURL(url: string) {
    this.baseURL = url;
  }

  /**
   * 获取当前基础 URL
   */
  getBaseURL(): string {
    return this.baseURL;
  }

  /**
   * 通用 fetch 包装器，处理错误和响应
   */
  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...options?.headers,
        },
      });

      // 处理非 2xx 响应
      if (!response.ok) {
        let errorDetail: APIError;
        try {
          errorDetail = await response.json();
        } catch {
          errorDetail = {
            error: response.statusText,
            detail: `HTTP ${response.status}`,
            status: response.status,
          };
        }
        throw new Error(errorDetail.detail || errorDetail.error || '请求失败');
      }

      return response.json();
    } catch (error) {
      // 网络错误或其他异常
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('未知错误');
    }
  }

  /**
   * 健康检查 - 验证后端是否可用
   * @returns 后端健康状态
   */
  async checkHealth(): Promise<BackendHealthResponse> {
    return this.request<BackendHealthResponse>('/api/health');
  }

  /**
   * 质量评估 - 使用 DeepEval 评估对话质量
   * @param file conversations.json 文件
   * @param maxPairs 最大评估对数（可选）
   * @returns 质量评估结果
   */
  async evaluateQuality(
    file: File,
    maxPairs?: number
  ): Promise<QualityEvaluationResult> {
    const formData = new FormData();
    formData.append('file', file);
    if (maxPairs) {
      formData.append('max_pairs', maxPairs.toString());
    }

    return this.request<QualityEvaluationResult>('/api/evaluate-quality', {
      method: 'POST',
      body: formData,
    });
  }

  /**
   * 流程分析 - 使用 LLM 分析对话流程
   * @param file conversations.json 文件
   * @returns 流程分析结果
   */
  async analyzeFlow(file: File): Promise<FlowAnalysisResult> {
    const formData = new FormData();
    formData.append('file', file);

    return this.request<FlowAnalysisResult>('/api/analyze-flow', {
      method: 'POST',
      body: formData,
    });
  }

  /**
   * 生成报告 - 根据分析结果生成 HTML 报告
   * @param data 分析数据
   * @returns 报告响应（HTML 或下载链接）
   */
  async generateReport(data: ReportRequest): Promise<ReportResponse> {
    return this.request<ReportResponse>('/api/generate-report', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
  }

  /**
   * 检查后端是否已配置
   */
  isConfigured(): boolean {
    return Boolean(this.baseURL);
  }
}

// 导出单例实例
export const apiClient = new ConveVisAnaClient();

// 导出便捷函数
export const checkBackendHealth = () => apiClient.checkHealth();
export const evaluateQuality = (file: File, maxPairs?: number) =>
  apiClient.evaluateQuality(file, maxPairs);
export const analyzeFlow = (file: File) => apiClient.analyzeFlow(file);
export const generateReport = (data: ReportRequest) =>
  apiClient.generateReport(data);
