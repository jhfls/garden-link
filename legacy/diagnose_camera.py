#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import os
import subprocess

def diagnose_camera():
    print("=== 摄像头问题诊断 ===")
    
    # 检查摄像头设备
    print("\n1. 检查摄像头设备:")
    try:
        # 检查/dev/video*设备
        result = subprocess.run(['ls', '/dev/video*'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   找到视频设备: {result.stdout.strip()}")
        else:
            print("   未找到视频设备")
    except Exception as e:
        print(f"   检查设备失败: {e}")
    
    # 检查用户权限
    print(f"\n2. 检查用户权限:")
    current_user = os.getenv('USER', 'unknown')
    is_root = os.geteuid() == 0
    print(f"   当前用户: {current_user}")
    print(f"   Root权限: {is_root}")
    
    # 检查video组
    try:
        result = subprocess.run(['groups'], capture_output=True, text=True)
        groups = result.stdout.strip().split()
        if 'video' in groups:
            print("   ✓ 用户在video组中")
        else:
            print("   ✗ 用户不在video组中")
    except Exception as e:
        print(f"   检查用户组失败: {e}")
    
    # 测试OpenCV
    print(f"\n3. 测试OpenCV:")
    try:
        print(f"   OpenCV版本: {cv2.__version__}")
        
        # 测试摄像头访问
        print("   测试摄像头访问...")
        for i in range(3):  # 测试前3个摄像头索引
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    print(f"   ✓ 摄像头 {i} 可用 - 分辨率: {frame.shape[1]}x{frame.shape[0]}")
                else:
                    print(f"   ✗ 摄像头 {i} 可打开但无法读取帧")
                cap.release()
            else:
                print(f"   ✗ 摄像头 {i} 不可用")
                
    except Exception as e:
        print(f"   OpenCV测试失败: {e}")
    
    # 检查pyzbar
    print(f"\n4. 检查二维码库:")
    try:
        from pyzbar import pyzbar
        print("   ✓ pyzbar库可用")
    except ImportError as e:
        print(f"   ✗ pyzbar库不可用: {e}")

if __name__ == '__main__':
    diagnose_camera()
