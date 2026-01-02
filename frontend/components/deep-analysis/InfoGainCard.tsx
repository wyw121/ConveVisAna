/**
 * 信息增益（IG）展示卡片：IG(P,Q) = DKL(P||Q) × R × C
 * @module components/deep-analysis/InfoGainCard
 */

'use client'

import React, { useMemo } from 'react';
import GlassCard from '@/components/cards/GlassCard';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { Sigma } from 'lucide-react';
import type { FlowAnalysisResult, QualityEvaluationResult } from '@/types/deepAnalysis';

interface InfoGainCardProps {
  flow: FlowAnalysisResult;
  quality: QualityEvaluationResult;
}

// 计算 KL 散度：DKL(P||Q) = Σ P_i * log(P_i / Q_i)
function dkl(P: Record<string, number>, Q: Record<string, number>): number {
  const epsilon = 1e-9;
  const keys = Array.from(new Set([...Object.keys(P), ...Object.keys(Q)]));
  let sum = 0;
  keys.forEach((k) => {
    const p = Math.max(P[k] || 0, 0);
    const q = Math.max(Q[k] || 0, 0);
    if (p > 0) {
      const ratio = (p + epsilon) / (q + epsilon);
      sum += p * Math.log(ratio);
    }
  });
  return sum;
}

// 归一化到概率分布
function normalize(counts: Record<string, number>): Record<string, number> {
  const total = Object.values(counts).reduce((a, b) => a + (Number(b) || 0), 0) || 1;
  const out: Record<string, number> = {};
  for (const [k, v] of Object.entries(counts)) {
    out[k] = (Number(v) || 0) / total;
  }
  return out;
}

export default function InfoGainCard({ flow, quality }: InfoGainCardProps) {
  const counts = flow.summary?.question_type_counts || {};

  // 基线分布 Q：可设为均匀或轻度偏置（模拟论文中的比较对象）
  const baselineCounts: Record<string, number> = useMemo(() => {
    const keys = Object.keys(counts);
    if (keys.length === 0) return { other: 1 };
    // 轻度偏置：偏向常见的规划/架构/洞察等类型，作为历史平均的近似
    const base: Record<string, number> = {};
    keys.forEach((k) => { base[k] = 1; });
    if (base['planning'] !== undefined) base['planning'] += 0.35;
    if (base['architecture'] !== undefined) base['architecture'] += 0.25;
    if (base['insight'] !== undefined) base['insight'] += 0.2;
    if (base['report'] !== undefined) base['report'] += 0.15;
    if (base['cost'] !== undefined) base['cost'] += 0.1;
    return base;
  }, [counts]);

  const P = normalize(counts);
  const Q = normalize(baselineCounts);
  const dklValue = dkl(P, Q);

  // 关系因子 R 与置信因子 C：取质量评估中的相关性和(1-毒性)作为示例
  const R = Math.max(0, Math.min(1, quality.metrics?.relevancy?.score ?? 0.8));
  const C = Math.max(0, Math.min(1, 1 - (quality.metrics?.toxicity?.score ?? 0.1)));
  const IG = dklValue * R * C;

  const chartData = Object.keys({ ...P, ...Q }).map((k) => ({
    type: k,
    P: Number(P[k] || 0),
    Q: Number(Q[k] || 0),
  }));

  return (
    <GlassCard>
      <div className="space-y-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">信息增益推算</h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">IG(P,Q) = DKL(P∥Q) × R × C，融合分布差异与质量因子</p>
          </div>
          <div className="px-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 text-right">
            <div className="text-xs text-gray-600 dark:text-gray-400">DKL(P∥Q)</div>
            <div className="text-xl font-bold text-gray-900 dark:text-white">{dklValue.toFixed(4)}</div>
          </div>
        </div>

        {/* 公式与参数 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white dark:bg-gray-800/50 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-2 mb-2">
              <Sigma className="w-5 h-5 text-indigo-500" />
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white">公式</h3>
            </div>
            <p className="text-sm text-gray-900 dark:text-white">IG(P,Q) = DKL(P∥Q) × R × C</p>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">其中 DKL 为相对熵，R 为相关性，C 为置信度</p>
          </div>
          <div className="bg-white dark:bg-gray-800/50 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">参数</h3>
            <ul className="text-sm text-gray-700 dark:text-gray-300 space-y-1">
              <li>R（相关性）≈ {R.toFixed(2)}</li>
              <li>C（置信度）≈ {C.toFixed(2)}</li>
              <li>IG（信息增益）≈ <span className="font-bold text-gray-900 dark:text-white">{IG.toFixed(4)}</span></li>
            </ul>
          </div>
          <div className="bg-white dark:bg-gray-800/50 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">解读</h3>
            <p className="text-sm text-gray-700 dark:text-gray-300">
              当 P 与 Q 差异更大（DKL 上升），且对话更相关/更安全（R↑, C↑），则信息增益更高，说明该对话带来了更显著的新信息。
            </p>
          </div>
        </div>

        {/* P vs Q 分布对比 */}
        <div className="bg-white dark:bg-gray-800/50 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">问题类型分布对比（P vs Q）</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="type" tick={{ fill: '#64748b', fontSize: 12 }} />
              <YAxis tick={{ fill: '#64748b', fontSize: 12 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="P" name="P（当前）" fill="#8b5cf6" />
              <Bar dataKey="Q" name="Q（基线）" fill="#22c55e" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* 结论提示 */}
        <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4">
          <h3 className="font-semibold text-amber-800 dark:text-amber-200 mb-2">📈 信息增益洞察</h3>
          <p className="text-sm text-amber-700 dark:text-amber-300">
            当前 IG ≈ {IG.toFixed(4)}。若希望进一步提升，可引导产生与基线分布差异更大的问题类型（如创造/评价类），同时确保回答更相关、更安全。
          </p>
        </div>
      </div>
    </GlassCard>
  );
}
