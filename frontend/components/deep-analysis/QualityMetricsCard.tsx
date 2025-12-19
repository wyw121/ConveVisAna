/**
 * 质量评估结果展示卡片
 * @module components/deep-analysis/QualityMetricsCard
 */

'use client'

import React from 'react';
import { 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  Radar, 
  ResponsiveContainer,
  Tooltip 
} from 'recharts';
import GlassCard from '@/components/cards/GlassCard';
import { CheckCircle, XCircle, TrendingUp, AlertTriangle } from 'lucide-react';
import { QualityEvaluationResult } from '@/types/deepAnalysis';

interface QualityMetricsCardProps {
  data: QualityEvaluationResult;
}

export default function QualityMetricsCard({ data }: QualityMetricsCardProps) {
  const { metrics, pairs_evaluated, average_score, cached } = data;

  // 安全获取指标分数，处理失败或缺失的情况
  const getMetricScore = (metric: any): number => {
    if (!metric || typeof metric.score !== 'number') return 0;
    return metric.score;
  };

  // 雷达图数据
  const radarData = [
    { 
      metric: 'Relevancy', 
      value: getMetricScore(metrics?.relevancy) * 100,
      fullMark: 100 
    },
    { 
      metric: 'Helpfulness', 
      value: getMetricScore(metrics?.helpfulness) * 100,
      fullMark: 100 
    },
    { 
      metric: 'Coherence', 
      value: getMetricScore(metrics?.coherence) * 100,
      fullMark: 100 
    },
    { 
      metric: 'Low Toxicity', 
      value: (1 - getMetricScore(metrics?.toxicity)) * 100,
      fullMark: 100 
    },
    { 
      metric: 'Low Bias', 
      value: (1 - getMetricScore(metrics?.bias)) * 100,
      fullMark: 100 
    },
  ];

  // 计算整体得分
  const overallScore = average_score || 
    (getMetricScore(metrics?.relevancy) + 
     getMetricScore(metrics?.helpfulness) + 
     getMetricScore(metrics?.coherence) + 
     (1 - getMetricScore(metrics?.toxicity)) + 
     (1 - getMetricScore(metrics?.bias))) / 5;

  // 获取等级和颜色
  const getScoreLevel = (score: number) => {
    if (score >= 0.9) return { label: '优秀', color: 'text-green-600 dark:text-green-400', bg: 'bg-green-50 dark:bg-green-900/20' };
    if (score >= 0.7) return { label: '良好', color: 'text-blue-600 dark:text-blue-400', bg: 'bg-blue-50 dark:bg-blue-900/20' };
    if (score >= 0.5) return { label: '一般', color: 'text-yellow-600 dark:text-yellow-400', bg: 'bg-yellow-50 dark:bg-yellow-900/20' };
    return { label: '需改进', color: 'text-red-600 dark:text-red-400', bg: 'bg-red-50 dark:bg-red-900/20' };
  };

  const scoreLevel = getScoreLevel(overallScore);

  // 指标配置
  const metricsConfig = [
    { key: 'relevancy', label: '相关性', icon: CheckCircle },
    { key: 'helpfulness', label: '有用性', icon: TrendingUp },
    { key: 'coherence', label: '连贯性', icon: CheckCircle },
    { key: 'toxicity', label: '毒性', icon: AlertTriangle, inverse: true },
    { key: 'bias', label: '偏见', icon: AlertTriangle, inverse: true },
  ];

  return (
    <GlassCard>
      <div className="space-y-6">
        {/* 标题与统计 */}
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              质量评估结果
            </h2>
            <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
              <span>已评估 {pairs_evaluated} 对问答</span>
              {cached && (
                <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded text-xs">
                  已缓存
                </span>
              )}
            </div>
          </div>
          
          {/* 整体得分 */}
          <div className={`px-6 py-4 rounded-lg ${scoreLevel.bg} text-center`}>
            <div className={`text-4xl font-bold ${scoreLevel.color}`}>
              {(overallScore * 100).toFixed(1)}
            </div>
            <div className={`text-sm font-medium ${scoreLevel.color} mt-1`}>
              {scoreLevel.label}
            </div>
          </div>
        </div>

        {/* 雷达图 */}
        <div className="bg-white dark:bg-gray-800/50 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
            综合评分可视化
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#94a3b8" />
              <PolarAngleAxis 
                dataKey="metric" 
                tick={{ fill: '#64748b', fontSize: 12 }}
              />
              <PolarRadiusAxis 
                angle={90} 
                domain={[0, 100]} 
                tick={{ fill: '#64748b', fontSize: 10 }}
              />
              <Radar 
                name="Quality Score" 
                dataKey="value" 
                stroke="#8b5cf6" 
                fill="#8b5cf6" 
                fillOpacity={0.6} 
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                }}
                formatter={(value: number) => `${value.toFixed(1)}%`}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* 指标卡片网格 */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {metricsConfig.map(({ key, label, icon: Icon, inverse }) => {
            const metric = metrics?.[key as keyof typeof metrics];
            
            // 安全检查：如果指标不存在或评估失败
            if (!metric || typeof metric.score !== 'number') {
              return (
                <div 
                  key={key}
                  className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700"
                >
                  <div className="flex items-center space-x-2 mb-2">
                    <Icon className="w-5 h-5 text-gray-400" />
                    <h3 className="font-semibold text-gray-900 dark:text-white">
                      {label}
                    </h3>
                  </div>
                  <p className="text-sm text-yellow-600 dark:text-yellow-400">
                    评估失败或数据缺失
                  </p>
                  {metric?.error && (
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                      {metric.error}
                    </p>
                  )}
                </div>
              );
            }
            
            const displayScore = inverse ? (1 - metric.score) : metric.score;
            const passed = metric.passed;
            
            return (
              <div 
                key={key}
                className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <Icon className={`w-5 h-5 ${passed ? 'text-green-500' : 'text-red-500'}`} />
                    <h3 className="font-semibold text-gray-900 dark:text-white">
                      {label}
                    </h3>
                  </div>
                  {passed ? (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-500" />
                  )}
                </div>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">
                  {(displayScore * 100).toFixed(1)}%
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  阈值: {(metric.threshold * 100)}%
                </p>
                {metric.reason && (
                  <p className="text-xs text-gray-600 dark:text-gray-400 mt-2 italic">
                    {metric.reason}
                  </p>
                )}
              </div>
            );
          })}
        </div>

        {/* 详细建议（防御性处理缺失/失败的指标） */}
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <h3 className="font-semibold text-blue-800 dark:text-blue-200 mb-2">
            💡 改进建议
          </h3>
          {(() => {
            const safeMetrics = metrics || {} as any;
            const isPassed = (m: any) => m?.passed ?? false;
            const anyMetric = Object.keys(safeMetrics).length > 0;
            const allPassed = anyMetric && Object.values(safeMetrics).every((m: any) => m?.passed === true);

            return (
              <ul className="text-sm text-blue-700 dark:text-blue-300 space-y-1 list-disc list-inside">
                {!isPassed(safeMetrics.relevancy) && (
                  <li>提高回答与问题的相关性，确保直接回应用户需求</li>
                )}
                {!isPassed(safeMetrics.helpfulness) && (
                  <li>提供更具操作性和实用价值的建议</li>
                )}
                {!isPassed(safeMetrics.coherence) && (
                  <li>增强回答的逻辑性和结构性</li>
                )}
                {!isPassed(safeMetrics.toxicity) && (
                  <li>避免使用可能冒犯或伤害用户的语言</li>
                )}
                {!isPassed(safeMetrics.bias) && (
                  <li>保持中立客观，避免歧视性或偏见性表达</li>
                )}
                {anyMetric && allPassed && (
                  <li>当前质量表现优秀，继续保持！</li>
                )}
                {!anyMetric && (
                  <li>尚未获取有效指标，请稍后重试或更换模型。</li>
                )}
              </ul>
            );
          })()}
        </div>
      </div>
    </GlassCard>
  );
}
