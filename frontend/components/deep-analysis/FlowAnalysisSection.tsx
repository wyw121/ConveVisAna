/**
 * 流程分析结果展示组件
 * @module components/deep-analysis/FlowAnalysisSection
 */

'use client'

import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts';
import GlassCard from '@/components/cards/GlassCard';
import { MessageCircle, TrendingUp, Clock, Hash } from 'lucide-react';
import { FlowAnalysisResult } from '@/types/deepAnalysis';

interface FlowAnalysisSectionProps {
  data: FlowAnalysisResult;
}

export default function FlowAnalysisSection({ data }: FlowAnalysisSectionProps) {
  const { summary, turns, cached } = data;

  // 问题类型饼图数据
  const questionTypeData = Object.entries(summary.question_type_counts).map(([type, count]) => ({
    name: getQuestionTypeLabel(type),
    value: count,
  }));

  // 问题类型颜色
  const COLORS = ['#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6', '#ef4444'];

  // 对话轮次时间线数据
  const timelineData = turns.map((turn, index) => ({
    turn: index + 1,
    questionLength: turn.question?.length || 0,
    responseLength: turn.answer?.length || 0,
    type: turn.question_type,
  }));

  function getQuestionTypeLabel(type: string): string {
    const labels: Record<string, string> = {
      'informational': '信息查询',
      'technical': '技术问题',
      'procedural': '操作流程',
      'clarification': '澄清确认',
      'feedback': '反馈意见',
      'other': '其他',
    };
    return labels[type] || type;
  }

  return (
    <GlassCard>
      <div className="space-y-6">
        {/* 标题与统计 */}
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              对话流程分析
            </h2>
            <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
              <span>共 {summary.total_turns} 轮对话</span>
              {cached && (
                <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded text-xs">
                  已缓存
                </span>
              )}
            </div>
          </div>
        </div>

        {/* 关键指标卡片 */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-2 mb-2">
              <Hash className="w-5 h-5 text-purple-500" />
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
                总轮次
              </h3>
            </div>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {summary.total_turns}
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-2 mb-2">
              <MessageCircle className="w-5 h-5 text-blue-500" />
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
                平均问题长度
              </h3>
            </div>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {summary.avg_question_length.toFixed(0)}
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-2 mb-2">
              <TrendingUp className="w-5 h-5 text-green-500" />
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
                平均回复长度
              </h3>
            </div>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {summary.avg_response_length.toFixed(0)}
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-2 mb-2">
              <Clock className="w-5 h-5 text-orange-500" />
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
                问题类型
              </h3>
            </div>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {Object.keys(summary.question_type_counts).length}
            </p>
          </div>
        </div>

        {/* 图表网格 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 问题类型分布饼图 */}
          <div className="bg-white dark:bg-gray-800/50 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
              问题类型分布
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={questionTypeData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {questionTypeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value: number) => value}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* 对话长度趋势折线图 */}
          <div className="bg-white dark:bg-gray-800/50 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
              对话长度趋势
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={timelineData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis 
                  dataKey="turn" 
                  label={{ value: '对话轮次', position: 'insideBottom', offset: -5 }}
                  tick={{ fill: '#64748b', fontSize: 12 }}
                />
                <YAxis 
                  label={{ value: '字符数', angle: -90, position: 'insideLeft' }}
                  tick={{ fill: '#64748b', fontSize: 12 }}
                />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                  }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="questionLength" 
                  stroke="#8b5cf6" 
                  name="问题长度" 
                  strokeWidth={2}
                />
                <Line 
                  type="monotone" 
                  dataKey="responseLength" 
                  stroke="#ec4899" 
                  name="回复长度" 
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 对话详情表格 */}
        <div className="bg-white dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              对话轮次详情
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    轮次
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    问题类型
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    问题
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    回复
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {turns.slice(0, 10).map((turn, index) => (
                  <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                      {index + 1}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className="px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded text-xs">
                        {getQuestionTypeLabel(turn.question_type)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900 dark:text-white max-w-md truncate">
                      {turn.question}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700 dark:text-gray-300 max-w-md truncate">
                      {turn.answer}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {turns.length > 10 && (
            <div className="px-6 py-3 bg-gray-50 dark:bg-gray-800 text-center text-sm text-gray-500 dark:text-gray-400">
              显示前 10 条，共 {turns.length} 条对话记录
            </div>
          )}
        </div>

        {/* 洞察建议 */}
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
          <h3 className="font-semibold text-green-800 dark:text-green-200 mb-2">
            🔍 流程洞察
          </h3>
          <ul className="text-sm text-green-700 dark:text-green-300 space-y-1 list-disc list-inside">
            <li>
              对话共 {summary.total_turns} 轮，
              {summary.avg_question_length > 100 
                ? '用户问题较详细，表明需求明确' 
                : '用户问题较简洁，可能需要引导'}
            </li>
            <li>
              平均回复长度 {summary.avg_response_length.toFixed(0)} 字符，
              {summary.avg_response_length > 200 
                ? '回复较详尽' 
                : '回复相对简洁'}
            </li>
            <li>
              主要问题类型：{Object.entries(summary.question_type_counts)
                .sort(([, a], [, b]) => (b as number) - (a as number))
                .slice(0, 2)
                .map(([type]) => getQuestionTypeLabel(type))
                .join('、')}
            </li>
          </ul>
        </div>
      </div>
    </GlassCard>
  );
}
