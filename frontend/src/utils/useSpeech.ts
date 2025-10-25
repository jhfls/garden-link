import type { Ref } from 'vue';
import { ref } from 'vue';

export interface UseSpeechOptions {
  lang?: string
  rate?: number
}

export interface UseSpeechReturn {
  isSpeaking: Ref<boolean>
  isSpeechEnabled: Ref<boolean>
  speechQueue: Ref<string>
  queueSpeech: (text: string) => void
  toggleSpeech: () => void
  stopSpeech: () => void
  setGenerating: (generating: boolean) => void
}

/**
 * Web Speech API 朗读管理 Hook
 * 用于实时朗读生成的文本，支持智能分句和队列管理
 *
 * @param options 配置选项
 * @param options.lang 语言代码，默认为 'zh-CN'
 * @param options.rate 播放速度，默认为 0.9
 * @returns 朗读管理接口
 *
 * @example
 * ```ts
 * const { isSpeaking, isSpeechEnabled, queueSpeech, toggleSpeech, stopSpeech } = useSpeech();
 *
 * // 监听 API 流式返回
 * await customizePlan(
 *   priorKnowledge,
 *   duration,
 *   preferences,
 *   (chunk) => {
 *     result.value += chunk;
 *     queueSpeech(chunk);  // 自动开始朗读
 *   }
 * );
 * ```
 */
export function useSpeech(options: UseSpeechOptions = {}): UseSpeechReturn {
  const { lang = 'zh-CN', rate = 0.9 } = options;

  const isSpeaking = ref(false);
  const isSpeechEnabled = ref(true);
  const speechQueue = ref('');
  const synth = typeof window !== 'undefined' ? window.speechSynthesis : null;
  let isGenerating = false;

  /**
   * 获取下一句可朗读的文本
   * 按以下优先级分割：
   * 1. 按句号、感叹号、问号分割
   * 2. 按换行符分割
   * 3. 超过指定长度的文本按字符限制分割
   * 4. 如果正在生成，等待更多文本
   * 5. 生成完成，返回剩余文本
   */
  function getNextSentence(): string {
    const queue = speechQueue.value;
    if (!queue)
      return '';

    // 尝试按句号、叹号、问号分割
    const sentenceMatch = queue.match(/^[^。！？\n]+[。！？]|^[^\n]+\n/);

    if (sentenceMatch) {
      const sentence = sentenceMatch[0];
      speechQueue.value = queue.slice(sentence.length);
      return sentence.trim();
    }

    // 如果没有标点，返回前 50 个字符
    if (queue.length > 50) {
      const text = queue.slice(0, 50);
      speechQueue.value = queue.slice(50);
      return text;
    }

    // 如果正在生成，返回空（等待更多文本）
    if (isGenerating)
      return '';

    // 生成完成，返回剩余文本
    speechQueue.value = '';
    return queue;
  }

  /**
   * 开始朗读队列中的文本
   */
  function speakQueued() {
    if (!synth || !isSpeechEnabled.value || speechQueue.value.length === 0)
      return;

    // 如果正在说话，等待回调处理
    if (isSpeaking.value)
      return;

    // 获取可朗读的文本块
    const textToSpeak = getNextSentence();
    if (!textToSpeak)
      return;

    isSpeaking.value = true;
    const utterance = new SpeechSynthesisUtterance(textToSpeak);
    utterance.lang = lang;
    utterance.rate = rate;

    utterance.onend = () => {
      isSpeaking.value = false;
      // 继续说下一句
      speakQueued();
    };

    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event);
      isSpeaking.value = false;
    };

    synth.speak(utterance);
  }

  /**
   * 将文本添加到朗读队列并自动开始朗读
   */
  function queueSpeech(text: string) {
    if (!synth || !isSpeechEnabled.value)
      return;

    // 将文本添加到队列
    speechQueue.value += text;

    // 尝试开始朗读
    speakQueued();
  }

  /**
   * 停止朗读并清空队列
   */
  function stopSpeech() {
    if (!synth)
      return;
    synth.cancel();
    isSpeaking.value = false;
    speechQueue.value = '';
  }

  /**
   * 切换朗读状态（播放/暂停）
   */
  function toggleSpeech() {
    if (!synth) {
      console.error('浏览器不支持 Web Speech API');
      return false;
    }

    if (isSpeaking.value) {
      synth.pause();
    } else if (speechQueue.value.length > 0) {
      synth.resume();
      speakQueued();
    }

    return true;
  }

  /**
   * 设置是否正在生成文本的状态
   * 这影响文本分割逻辑
   */
  function setGenerating(generating: boolean) {
    isGenerating = generating;
  }

  return {
    isSpeaking,
    isSpeechEnabled,
    speechQueue,
    queueSpeech,
    toggleSpeech,
    stopSpeech,
    setGenerating,
  };
}

/**
 * 创建一个 useSpeech 实例用于指定的完整文本朗读
 * 适合用于朗读已完整获取的文本（非流式）
 */
export function createSpeechReader(text: string, options: UseSpeechOptions = {}) {
  const { lang = 'zh-CN', rate = 0.9 } = options;
  const synth = typeof window !== 'undefined' ? window.speechSynthesis : null;

  return {
    read: () => {
      if (!synth) {
        console.error('浏览器不支持 Web Speech API');
        return;
      }

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = lang;
      utterance.rate = rate;
      synth.speak(utterance);
    },
    stop: () => {
      if (!synth)
        return;
      synth.cancel();
    },
    pause: () => {
      if (!synth)
        return;
      synth.pause();
    },
    resume: () => {
      if (!synth)
        return;
      synth.resume();
    },
  };
}
