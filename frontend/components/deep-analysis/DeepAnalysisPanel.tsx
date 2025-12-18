/**
 * 深度分析主面板组件
 * @module components/deep-analysis/DeepAnalysisPanel
 */

'use client'

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Loader, AlertCircle, CheckCircle, XCircle } from 'lucide-react';
import { useDeepAnalysis } from '@/hooks/useDeepAnalysis';
import { useBackendStatus } from '@/hooks/useBackendStatus';
import QualityMetricsCard from './QualityMetricsCard';
import FlowAnalysisSection from './FlowAnalysisSection';

interface DeepAnalysisPanelProps {
  conversationFile: File | null;
  conversationData?: any;
}

export default function DeepAnalysisPanel({ 
  conversationFile,
  conversationData 
}: DeepAnalysisPanelProps) {
  const [analysisType, setAnalysisType] = useState<'none' | 'quality' | 'flow'>('none');
  
  const { 
    qualityStatus,
    flowStatus,
    qualityError, 
    flowError, 
    qualityResult, 
    flowResult,
    runQualityEvaluation,
    runFlowAnalysis 
  } = useDeepAnalysis();

  const { isHealthy, isChecking, error: backendError } = useBackendStatus({
    autoCheck: true,
  });

  // 处理质量评估
  const handleQualityAnalysis = async () => {
    if (!conversationFile) return;
    
    setAnalysisType('quality');
    try {
      await runQualityEvaluation(conversationFile, 10);
    } catch (err) {
      console.error('质量评估失败:', err);
    }
  };

  // 处理流程分析
  const handleFlowAnalysis = async () => {
    if (!conversationFile) return;
    
    setAnalysisType('flow');
    try {
      await runFlowAnalysis(conversationFile);
    } catch (err) {
      console.error('流程分析失败:', err);
    }
  };

  // 后端状态检查
  if (isChecking) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader className="w-8 h-8 animate-spin text-primary" />
        <span className="ml-3 text-gray-600 dark:text-gray-400">
          正在连接后端...
        </span>
      </div>
    );
  }

  if (!isHealthy || backendError) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
        <div className="flex items-start space-x-3">
          <XCircle className="w-6 h-6 text-red-600 dark:text-red-400 mt-0.5" />
          <div>
            <h3 className="font-semibold text-red-800 dark:text-red-200 text-lg">
              后端连接失败
            </h3>
            <p className="text-sm text-red-700 dark:text-red-300 mt-2">
              {backendError || '无法连接到 ConveVisAna 后端服务器'}
            </p>
            <p className="text-xs text-red-600 dark:text-red-400 mt-3">
              请确保后端服务已启动 (python backend/start_server.py)
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!conversationFile) {
    return (
      <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6">
        <div className="flex items-start space-x-3">
          <AlertCircle className="w-6 h-6 text-yellow-600 dark:text-yellow-400 mt-0.5" />
          <div>
            <h3 className="font-semibold text-yellow-800 dark:text-yellow-200">
              请先上传对话文件
            </h3>
            <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
              深度分析需要先上传 conversations.json 文件
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 后端连接成功提示 */}
      <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 mt-0.5" />
          <div>
            <h3 className="font-semibold text-green-800 dark:text-green-200">
              后端连接正常
            </h3>
            <p className="text-sm text-green-700 dark:text-green-300 mt-1">
              可以使用深度分析功能
            </p>
          </div>
        </div>
      </div>

      {/* 隐私提示 */}
      <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mt-0.5" />
          <div>
            <h3 className="font-semibold text-yellow-800 dark:text-yellow-200">
              深度分析需要上传数据
            </h3>
            <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
              深度分析功能将上传您的对话数据到后端服务器进行处理。
              我们仅用于分析目的，不会永久存储您的数据。
            </p>
          </div>
        </div>
      </div>

      {/* 分析选项 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-shadow">
          <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">
            质量评估
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            使用 DeepEval 评估对话质量，包括相关性、有用性、连贯性、毒性和偏见。
          </p>
          <Button 
            onClick={handleQualityAnalysis}
            disabled={qualityStatus === 'loading'}
            className="w-full"
          >
            {qualityStatus === 'loading' && analysisType === 'quality' ? (
              <>
                <Loader className="w-4 h-4 mr-2 animate-spin" /> 
                分析中...
              </>
            ) : (
              '开始质量评估'
            )}
          </Button>
          {qualityStatus === 'success' && (
            <p className="text-xs text-green-600 dark:text-green-400 mt-2 text-center">
              ✓ 评估完成
            </p>
          )}
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-shadow">
          <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">
            流程分析
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            使用 LLM 分析对话流程，识别问题类型、轮次模式和对话路径。
          </p>
          <Button 
            onClick={handleFlowAnalysis}
            disabled={flowStatus === 'loading'}
            className="w-full"
            variant="secondary"
          >
            {flowStatus === 'loading' && analysisType === 'flow' ? (
              <>
                <Loader className="w-4 h-4 mr-2 animate-spin" /> 
                分析中...
              </>
            ) : (
              '开始流程分析'
            )}
          </Button>
          {flowStatus === 'success' && (
            <p className="text-xs text-green-600 dark:text-green-400 mt-2 text-center">
              ✓ 分析完成
            </p>
          )}
        </div>
      </div>

      {/* 错误提示 */}
      {(qualityError || flowError) && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-800 dark:text-red-200 font-semibold">
            {qualityError || flowError}
          </p>
        </div>
      )}

      {/* 结果展示 */}
      {qualityResult && (
        <QualityMetricsCard data={qualityResult} />
      )}

      {flowResult && (
        <FlowAnalysisSection data={flowResult} />
      )}
    </div>
  );
}
