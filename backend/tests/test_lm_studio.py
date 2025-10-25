"""测试 LM Studio 连接"""

import openai  # 新增
from config import LM_STUDIO_URL, LM_STUDIO_MODEL


def test_lm_studio_connection():
    """测试 LM Studio 是否正常运行"""
    print(f"正在测试连接到 LM Studio: {LM_STUDIO_URL}")

    # 初始化 OpenAI 客户端
    client = openai.OpenAI(base_url=LM_STUDIO_URL, api_key="lm-studio")

    # 测试简单的文本请求
    payload = {
        "model": LM_STUDIO_MODEL,
        "messages": [{"role": "user", "content": "你好，请回复'连接成功'"}],
        "max_tokens": 50,
    }

    try:
        response = client.chat.completions.create(
            model=payload["model"],
            messages=payload["messages"],
            max_tokens=payload["max_tokens"],
            timeout=10,
        )

        if (
            response
            and response.choices
            and response.choices[0].message
            and response.choices[0].message.content
        ):
            reply = response.choices[0].message.content
            print("✓ 成功连接到 LM Studio")
            print(f"✓ 模型响应：{reply}")
            return True
        else:
            print("❌ LM Studio 返回了无效的响应")
            print(f"   响应内容：{response}")
            return False

    except openai.APIConnectionError:
        print("❌ 无法连接到 LM Studio")
        print("\n故障排除建议：")
        print("1. 确保 LM Studio 正在运行")
        print("2. 确保已启动本地服务器（默认端口 1234）")
        print("3. 检查配置文件中的 URL 是否正确")
        print(f"   当前配置：{LM_STUDIO_URL}")
        return False

    except Exception as e:
        print(f"❌ 发生错误：{e}")
        return False


def test_vision_model():
    """测试视觉模型是否支持"""
    print("\n正在测试视觉模型支持...")

    # 初始化 OpenAI 客户端
    client = openai.OpenAI(base_url=LM_STUDIO_URL, api_key="lm-studio")

    # 创建一个简单的测试图像（1x1 红色像素的 base64）
    test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="

    payload = {
        "model": LM_STUDIO_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "请简单描述这张图片"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{test_image_base64}"
                        },
                    },
                ],
            }
        ],
        "max_tokens": 100,
    }

    try:
        response = client.chat.completions.create(
            model=payload["model"],
            messages=payload["messages"],
            max_tokens=payload["max_tokens"],
            timeout=30,
        )

        if (
            response
            and response.choices
            and response.choices[0].message
            and response.choices[0].message.content
        ):
            reply = response.choices[0].message.content
            print("✓ 视觉模型测试成功")
            print(f"✓ 模型响应：{reply}")
            return True
        else:
            print("❌ 视觉模型测试失败：LM Studio 返回了无效的响应")
            print(f"   响应内容：{response}")
            return False

    except Exception as e:
        print(f"❌ 视觉模型测试失败：{e}")
        print("\n注意：")
        print("1. 确保在 LM Studio 中加载了支持视觉的模型（如 qwen3-vl-8b）")
        print("2. 确保模型已完全加载")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("LM Studio 连接测试")
    print("=" * 60)
    print()

    # 测试基本连接
    if test_lm_studio_connection():
        # 测试视觉功能
        test_vision_model()

    print("\n" + "=" * 60)
