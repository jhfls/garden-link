#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2

def test_camera():
    print("简单摄像头测试")

    for i in range(3):
        print(f"\n测试摄像头 {i}:")
        cap = cv2.VideoCapture(0)

        if cap.isOpened():
            print(f"✓ 摄像头 {i} 可以打开")

            # 尝试读取一帧
            ret, frame = cap.read()
            if ret:
                print(f"✓ 可以读取帧 - 分辨率: {frame.shape[1]}x{frame.shape[0]}")

                # 显示帧信息
                cv2.imshow(f'Camera {i}', frame)
                print("按任意键关闭窗口...")
                cv2.waitKey(0)
                cv2.destroyAllWindows()

            else:
                print("✗ 可以打开但无法读取帧")

            cap.release()
        else:
            print(f"✗ 摄像头 {i} 无法打开")

if __name__ == '__main__':
    test_camera()