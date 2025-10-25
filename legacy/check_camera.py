#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import os

def check_camera_devices():
    print("=== 摄像头设备诊断 ===")
    
    # 检查视频设备
    print("\n1. 检查视频设备:")
    try:
        result = subprocess.run(['ls', '-la', '/dev/video*'], capture_output=True, text=True)
        if result.returncode == 0:
            print("找到视频设备:")
            print(result.stdout)
        else:
            print("未找到 /dev/video* 设备")
    except Exception as e:
        print(f"检查设备失败: {e}")
    
    # 检查USB设备
    print("\n2. 检查USB设备:")
    try:
        result = subprocess.run(['lsusb'], capture_output=True, text=True)
        print("USB设备列表:")
        print(result.stdout)
    except Exception as e:
        print(f"检查USB失败: {e}")
    
    # 检查内核模块
    print("\n3. 检查摄像头驱动:")
    try:
        result = subprocess.run(['lsmod'], capture_output=True, text=True)
        if 'uvcvideo' in result.stdout:
            print("✓ 找到UVC摄像头驱动")
        else:
            print("✗ 未找到UVC摄像头驱动")
    except Exception as e:
        print(f"检查驱动失败: {e}")

def test_camera_with_cv():
    print("\n=== OpenCV摄像头测试 ===")
    import cv2
    
    for i in range(3):
        print(f"\n测试摄像头 {i}:")
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                print(f"  ✓ 摄像头 {i} 可以打开")
                ret, frame = cap.read()
                if ret:
                    print(f"  ✓ 摄像头 {i} 可以读取帧 - 分辨率: {frame.shape[1]}x{frame.shape[0]}")
                else:
                    print(f"  ✗ 摄像头 {i} 可打开但无法读取帧")
                cap.release()
            else:
                print(f"  ✗ 摄像头 {i} 无法打开")
        except Exception as e:
            print(f"  ✗ 测试摄像头 {i} 时出错: {e}")

if __name__ == '__main__':
    check_camera_devices()
    test_camera_with_cv()
