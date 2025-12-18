/**
 * 深度分析状态管理 Hook
 * @module hooks/useDeepAnalysis
 */

import { useState, useCallback } from 'react';
import {
  QualityEvaluationResult,
  FlowAnalysisResult,
  AnalysisStatus,
} from '@/types/deepAnalysis';
import { apiClient } from '@/utils/apiClient';

interface UseDeepAnalysisReturn {
  // 状态
  qualityStatus: AnalysisStatus;
  flowStatus: AnalysisStatus;
  qualityError: string | null;
  flowError: string | null;
  qualityResult: QualityEvaluationResult | null;
  flowResult: FlowAnalysisResult | null;
  
  // 操作
  runQualityEvaluation: (file: File, maxPairs?: number) => Promise<QualityEvaluationResult>;
  runFlowAnalysis: (file: File) => Promise<FlowAnalysisResult>;
  reset: () => void;
  
  // 派生状态
  isAnyLoading: boolean;
  hasAnyError: boolean;
  hasAnyResult: boolean;
}

/**
 * 深度分析状态管理 Hook
 */
export function useDeepAnalysis(): UseDeepAnalysisReturn {
  // 质量评估状态
  const [qualityStatus, setQualityStatus] = useState<AnalysisStatus>('idle');
  const [qualityError, setQualityError] = useState<string | null>(null);
  const [qualityResult, setQualityResult] = useState<QualityEvaluationResult | null>(null);

  // 流程分析状态
  const [flowStatus, setFlowStatus] = useState<AnalysisStatus>('idle');
  const [flowError, setFlowError] = useState<string | null>(null);
  const [flowResult, setFlowResult] = useState<FlowAnalysisResult | null>(null);

  /**
   * 运行质量评估
   */
  const runQualityEvaluation = useCallback(
    async (file: File, maxPairs?: number): Promise<QualityEvaluationResult> => {
      setQualityStatus('loading');
      setQualityError(null);

      try {
        const result = await apiClient.evaluateQuality(file, maxPairs);
        setQualityResult(result);
        setQualityStatus('success');
        return result;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : '质量评估失败';
        setQualityError(errorMessage);
        setQualityStatus('error');
        throw err;
      }
    },
    []
  );

  /**
   * 运行流程分析
   */
  const runFlowAnalysis = useCallback(
    async (file: File): Promise<FlowAnalysisResult> => {
      setFlowStatus('loading');
      setFlowError(null);

      try {
        const result = await apiClient.analyzeFlow(file);
        setFlowResult(result);
        setFlowStatus('success');
        return result;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : '流程分析失败';
        setFlowError(errorMessage);
        setFlowStatus('error');
        throw err;
      }
    },
    []
  );

  /**
   * 重置所有状态
   */
  const reset = useCallback(() => {
    setQualityStatus('idle');
    setQualityError(null);
    setQualityResult(null);
    setFlowStatus('idle');
    setFlowError(null);
    setFlowResult(null);
  }, []);

  // 派生状态
  const isAnyLoading = qualityStatus === 'loading' || flowStatus === 'loading';
  const hasAnyError = Boolean(qualityError || flowError);
  const hasAnyResult = Boolean(qualityResult || flowResult);

  return {
    // 状态
    qualityStatus,
    flowStatus,
    qualityError,
    flowError,
    qualityResult,
    flowResult,
    
    // 操作
    runQualityEvaluation,
    runFlowAnalysis,
    reset,
    
    // 派生状态
    isAnyLoading,
    hasAnyError,
    hasAnyResult,
  };
}
