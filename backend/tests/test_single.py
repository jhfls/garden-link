#!/usr/bin/env python3
"""
简化版示例 - 单次识别测试

这个脚本用于快速测试整个流程，执行一次图像捕获和识别。
适合用于调试和验证系统是否正常工作。
"""

import base64
from io import BytesIO

import cv2
import requests
from PIL import Image

from config import (
    API_MAX_TOKENS,
    API_TEMPERATURE,
    API_TIMEOUT,
    CAMERA_INDEX,
    IMAGE_QUALITY,
    LM_STUDIO_MODEL,
    LM_STUDIO_URL,
)


def quick_test():
    """执行一次完整的识别流程测试"""
    print("=" * 60)
    print("单次识别测试")
    print("=" * 60)
    print()

    # 1. 捕获图像
    print(f"1. 正在从摄像头 {CAMERA_INDEX} 捕获图像...")
    try:
        cap = cv2.VideoCapture(CAMERA_INDEX)
        if not cap.isOpened():
            print(f"❌ 无法打开摄像头 {CAMERA_INDEX}")
            return False

        ret, frame = cap.read()
        cap.release()

        if not ret:
            print("❌ 无法读取图像")
            return False

        height, width = frame.shape[:2]
        print(f"   ✓ 成功捕获图像 ({width}x{height})")
    except Exception as e:
        print(f"❌ 摄像头错误：{e}")
        return False

    # 2. 编码图像
    print("\n2. 正在编码图像...")
    try:
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        buffered = BytesIO()
        pil_image.save(buffered, format="JPEG", quality=IMAGE_QUALITY)
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        print(f"   ✓ 图像已编码 (大小：{len(img_base64)} 字符)")
    except Exception as e:
        print(f"❌ 编码错误：{e}")
        return False

    # 3. 发送到 LM Studio
    print(f"\n3. 正在发送到 LM Studio ({LM_STUDIO_URL})...")
    prompt = """请仔细观察这张图片，判断其中是否包含自然景观（如山川、河流、湖泊、森林、田园、日出日落、云雾等）或人文景观（如古建筑、园林、名胜古迹等）。

如果图中包含景观：
1. 输出一句与该景观相关的中国古代文学作品名句（诗词、散文、赋等）
2. 简要说明该名句的出处、作者和背景
3. 或者描述与该景观相关的文学事件或典故

如果图中不包含景观或无法识别出明确的景观，请只输出：Ø

请直接给出答案，不需要额外的解释说明。"""

    payload = {
        "model": LM_STUDIO_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                    },
                ],
            }
        ],
        "temperature": API_TEMPERATURE,
        "max_tokens": API_MAX_TOKENS,
    }

    try:
        response = requests.post(LM_STUDIO_URL, json=payload, timeout=API_TIMEOUT)
        response.raise_for_status()
        result = response.json()
        reply = result["choices"][0]["message"]["content"].strip()
        print("   ✓ 成功获取响应")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到 LM Studio")
        print("   请确保 LM Studio 正在运行并启动了服务器")
        return False
    except Exception as e:
        print(f"❌ API 错误：{e}")
        return False

    # 4. 显示结果
    print("\n" + "=" * 60)
    print("识别结果：")
    print("=" * 60)
    print()
    print(reply)
    print()
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = quick_test()

    if success:
        print("\n✓ 测试成功！系统工作正常。")
        print("\n现在可以运行 'python main.py' 并输入 'sbjg' 开始连续识别。")
    else:
        print("\n✗ 测试失败，请检查上面的错误信息。")
        print("\n调试建议：")
        print("- 运行 'python test_camera.py' 测试摄像头")
        print("- 运行 'python test_lm_studio.py' 测试 LM Studio")
