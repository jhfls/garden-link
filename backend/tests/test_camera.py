"""测试摄像头是否正常工作"""

import cv2


def test_camera(camera_index=0):
    """测试指定索引的摄像头"""
    print(f"正在测试摄像头 {camera_index}...")

    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print(f"❌ 无法打开摄像头 {camera_index}")
        return False

    print(f"✓ 成功打开摄像头 {camera_index}")

    # 读取一帧图像
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("❌ 无法读取图像")
        return False

    height, width, channels = frame.shape
    print("✓ 成功读取图像")
    print(f"  - 分辨率：{width}x{height}")
    print(f"  - 通道数：{channels}")

    # 可选：保存测试图像
    cv2.imwrite("test_capture.jpg", frame)
    print("✓ 测试图像已保存到 test_capture.jpg")

    return True


def find_available_cameras(max_index=5):
    """查找所有可用的摄像头"""
    print(f"正在搜索摄像头（索引 0-{max_index}）...\n")
    available = []

    for i in range(max_index + 1):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available.append(i)
            cap.release()
            print(f"✓ 找到摄像头 {i}")
        else:
            print(f"✗ 摄像头 {i} 不可用")

    return available


if __name__ == "__main__":
    print("=" * 60)
    print("摄像头测试工具")
    print("=" * 60)
    print()

    # 查找所有可用摄像头
    available = find_available_cameras()

    print()
    print("=" * 60)

    if available:
        print(f"\n找到 {len(available)} 个可用摄像头：{available}")
        print(f"\n测试第一个可用摄像头 ({available[0]}):\n")
        test_camera(available[0])
    else:
        print("\n❌ 没有找到可用的摄像头")
        print("\n故障排除建议：")
        print("1. 确保 USB 摄像头已正确连接")
        print("2. 检查摄像头权限：ls -l /dev/video*")
        print("3. 确保当前用户在 video 组：groups")
        print("4. 尝试安装 v4l-utils: sudo apt-get install v4l-utils")
        print("5. 查看可用设备：v4l2-ctl --list-devices")

    print("\n" + "=" * 60)
