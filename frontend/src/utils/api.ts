const storedBackendUrl = localStorage.getItem('backendUrl');
const API_BASE_URL = storedBackendUrl || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8908';

/**
 * 景观识别 - 触发后端摄像头拍照并分析，返回古代文学作品名句
 * @param onChunk 可选的回调函数，用于处理流式返回的每个文本块
 */
export async function analyzeLandscape(onChunk?: (chunk: string) => void): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/api/landscape-recognition`, {
    method: 'POST',
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '请求失败' }));
    throw new Error(error.detail || '景观识别失败');
  }

  // 流式读取响应
  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('无法读取响应');
  }

  const decoder = new TextDecoder();
  let result = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done)
      break;
    const chunk = decoder.decode(value, { stream: true });
    result += chunk;
    onChunk?.(chunk);
  }

  return result;
}

/**
 * 行程定制 - 生成个性化游览计划
 */
export async function customizePlan(
  priorKnowledge: string,
  duration: string,
  preferences: string[],
  onChunk?: (chunk: string) => void,
): Promise<string> {
  const body = {
    prior_knowledge: priorKnowledge,
    duration,
    preferences,
  };

  const response = await fetch(`${API_BASE_URL}/api/plan-customizing`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '请求失败' }));
    throw new Error(error.detail || '行程定制失败');
  }

  // 流式读取响应
  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('无法读取响应');
  }

  const decoder = new TextDecoder();
  let result = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done)
      break;
    const chunk = decoder.decode(value, { stream: true });
    result += chunk;
    onChunk?.(chunk);
  }

  return result;
}

/**
 * 满意度调查 - 触发后端摄像头拍照并分析人脸表情，返回评分
 */
export interface SatisfactionResult {
  scores: number[]
  total: number
  average: number
  count: number
  message?: string
}

export async function analyzeSatisfaction(): Promise<SatisfactionResult> {
  const response = await fetch(`${API_BASE_URL}/api/satisfaction-survey`, {
    method: 'POST',
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '请求失败' }));
    throw new Error(error.detail || '满意度分析失败');
  }

  return await response.json();
}
