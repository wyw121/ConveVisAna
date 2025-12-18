/**
 * Token pricing utilities
 * Provides simple cost lookup and calculation helpers.
 */

export interface Pricing {
  inputCost: number; // cost per 1K input tokens (USD)
  outputCost: number; // cost per 1K output tokens (USD)
}

// Basic pricing table covering common models; defaults to zero if unknown.
const PRICING_TABLE: Record<string, Pricing> = {
  // OpenAI
  'gpt-4o': { inputCost: 0.0025, outputCost: 0.01 },
  'gpt-4o-mini': { inputCost: 0.00015, outputCost: 0.0006 },
  'gpt-4': { inputCost: 0.03, outputCost: 0.06 },
  'gpt-3.5-turbo': { inputCost: 0.0005, outputCost: 0.0015 },
  'gpt-3.5-turbo-0125': { inputCost: 0.0005, outputCost: 0.0015 },
  'chatgpt-4o-latest': { inputCost: 0.005, outputCost: 0.015 },
  // Anthropic
  'claude-3-opus': { inputCost: 0.015, outputCost: 0.075 },
  'claude-3-sonnet': { inputCost: 0.003, outputCost: 0.015 },
  'claude-3-haiku': { inputCost: 0.00025, outputCost: 0.00125 },
  // DeepSeek
  'deepseek-chat': { inputCost: 0.00014, outputCost: 0.00028 },
  'deepseek-coder': { inputCost: 0.00014, outputCost: 0.00028 },
};

function normalizeModel(model: string): string {
  return model?.toLowerCase() || '';
}

export function getPricing(modelName: string): Pricing {
  const key = normalizeModel(modelName);
  return PRICING_TABLE[key] || { inputCost: 0, outputCost: 0 };
}

export function calculateCost(tokens: number, costPerThousand: number): number {
  if (!tokens || !costPerThousand) return 0;
  return (tokens / 1000) * costPerThousand;
}

export const pricingTable = PRICING_TABLE;
