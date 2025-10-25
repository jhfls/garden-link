import jsQR from 'jsqr-es6';
import { readonly, ref } from 'vue';

interface UseQRScannerOptions {
  correctCode?: string
}

export function useQRScanner(options: UseQRScannerOptions = {}) {
  const { correctCode = '114514' } = options;

  const isScanning = ref(false);
  const scannedCodes = ref<string[]>([]);
  const lastScannedCode = ref<string | null>(null);
  const scanStatus = ref<'idle' | 'scanning' | 'success' | 'error'>('idle');
  const statusMessage = ref<string>('就绪');

  let animationFrameId: number | null = null;
  let stream: MediaStream | null = null;
  const recentScans = new Set<string>();
  let lastScanTime = 0;
  const SCAN_DEBOUNCE_MS = 500; // 500ms 内重复扫描同一个码视为一次

  async function startScanning(videoElement: HTMLVideoElement) {
    try {
      if (isScanning.value) {
        return;
      }

      scanStatus.value = 'scanning';
      statusMessage.value = '正在启动摄像头...';

      // 请求摄像头权限
      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' },
        audio: false,
      });

      videoElement.srcObject = stream;

      // 等待视频元素加载
      await new Promise((resolve) => {
        videoElement.onloadedmetadata = () => {
          videoElement.play();
          resolve(undefined);
        };
      });

      isScanning.value = true;
      statusMessage.value = '扫描中...';
      recentScans.clear();

      // 创建 Canvas 用于 QR 识别
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');

      if (!context) {
        throw new Error('无法获取 canvas 上下文');
      }

      // 设置 canvas 尺寸
      canvas.width = videoElement.videoWidth;
      canvas.height = videoElement.videoHeight;

      function scanFrame() {
        if (!isScanning.value || !stream || !context) {
          return;
        }

        // 检查视频是否已加载
        if (videoElement.videoWidth === 0 || videoElement.videoHeight === 0) {
          animationFrameId = requestAnimationFrame(scanFrame);
          return;
        }

        // 绘制视频帧到 canvas
        context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

        try {
          // 获取图像数据
          const imageData = context.getImageData(0, 0, canvas.width, canvas.height);

          // 使用 jsQR 扫描二维码
          const code = jsQR(imageData.data, imageData.width, imageData.height, {
            inversionAttempts: 'dontInvert',
          });

          if (code) {
            const scannedValue = code.data.trim();
            const now = Date.now();

            // 防止重复扫描：同一个码在 500ms 内重复出现视为一次
            if (
              lastScannedCode.value !== scannedValue
              || now - lastScanTime > SCAN_DEBOUNCE_MS
            ) {
              lastScanTime = now;
              lastScannedCode.value = scannedValue;

              // 验证码是否正确
              const isValid = scannedValue === correctCode;
              scanStatus.value = isValid ? 'success' : 'error';
              statusMessage.value = isValid
                ? `✓ 有效门票：${scannedValue}`
                : `✗ 无效门票：${scannedValue}`;

              // 添加到扫描历史
              scannedCodes.value.push(scannedValue);
            }
          }
        } catch (error) {
          // 继续扫描，不中断
          console.error('QR 扫描错误：', error);
        }

        animationFrameId = requestAnimationFrame(scanFrame);
      }

      // 开始扫描循环
      animationFrameId = requestAnimationFrame(scanFrame);
    } catch (error) {
      isScanning.value = false;
      scanStatus.value = 'error';
      statusMessage.value = `摄像头启动失败：${(error as Error).message}`;
      console.error('启动扫描失败：', error);
    }
  }

  function stopScanning() {
    if (animationFrameId !== null) {
      cancelAnimationFrame(animationFrameId);
      animationFrameId = null;
    }

    if (stream) {
      stream.getTracks().forEach((track) => {
        track.stop();
      });
      stream = null;
    }

    isScanning.value = false;
    scanStatus.value = 'idle';
    statusMessage.value = '已停止扫描';
    recentScans.clear();
  }

  function clearScannedCodes() {
    scannedCodes.value = [];
    lastScannedCode.value = null;
    scanStatus.value = 'idle';
    statusMessage.value = '结果已清空';
    recentScans.clear();
  }

  return {
    isScanning: readonly(isScanning),
    scannedCodes: readonly(scannedCodes),
    lastScannedCode: readonly(lastScannedCode),
    scanStatus: readonly(scanStatus),
    statusMessage: readonly(statusMessage),
    startScanning,
    stopScanning,
    clearScannedCodes,
  };
}
