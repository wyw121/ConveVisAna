/**
 * 后端状态检查 Hook
 * @module hooks/useBackendStatus
 */

import { useState, useEffect, useCallback } from 'react';
import { BackendHealthResponse } from '@/types/deepAnalysis';
import { apiClient } from '@/utils/apiClient';

interface UseBackendStatusReturn {
  isHealthy: boolean;
  isChecking: boolean;
  error: string | null;
  healthData: BackendHealthResponse | null;
  checkHealth: () => Promise<void>;
  isConfigured: boolean;
}

interface UseBackendStatusOptions {
  autoCheck?: boolean; // 是否自动检查
  checkInterval?: number; // 定期检查间隔（毫秒），0 表示不定期检查
}

/**
 * 后端状态检查 Hook
 */
export function useBackendStatus(
  options: UseBackendStatusOptions = {}
): UseBackendStatusReturn {
  const { autoCheck = true, checkInterval = 0 } = options;

  const [isHealthy, setIsHealthy] = useState(false);
  const [isChecking, setIsChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [healthData, setHealthData] = useState<BackendHealthResponse | null>(null);
  const [isConfigured] = useState(() => apiClient.isConfigured());

  /**
   * 执行健康检查
   */
  const checkHealth = useCallback(async () => {
    // 如果未配置后端，跳过检查
    if (!apiClient.isConfigured()) {
      setError('后端未配置');
      setIsHealthy(false);
      return;
    }

    setIsChecking(true);
    setError(null);

    try {
      const data = await apiClient.checkHealth();
      setHealthData(data);
      setIsHealthy(data.status === 'healthy');
      
      // 如果没有 API 密钥，设置警告
      if (!data.has_api_key) {
        setError('后端未配置 API 密钥');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '后端连接失败';
      setError(errorMessage);
      setIsHealthy(false);
      setHealthData(null);
    } finally {
      setIsChecking(false);
    }
  }, []);

  // 自动检查（组件挂载时）
  useEffect(() => {
    if (autoCheck && isConfigured) {
      checkHealth();
    }
  }, [autoCheck, isConfigured, checkHealth]);

  // 定期检查
  useEffect(() => {
    if (checkInterval > 0 && isConfigured) {
      const intervalId = setInterval(checkHealth, checkInterval);
      return () => clearInterval(intervalId);
    }
  }, [checkInterval, isConfigured, checkHealth]);

  return {
    isHealthy,
    isChecking,
    error,
    healthData,
    checkHealth,
    isConfigured,
  };
}
