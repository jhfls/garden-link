#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import sys

def diagnose_led_issues():
    print("=== LED灯带问题诊断 ===")
    
    # 检查当前用户和权限
    print(f"\n1. 用户和权限检查:")
    current_user = os.getenv('USER', 'unknown')
    is_root = os.geteuid() == 0
    print(f"   当前用户: {current_user}")
    print(f"   Root权限: {is_root}")
    
    # 检查用户组
    try:
        result = subprocess.run(['groups'], capture_output=True, text=True)
        print(f"   用户组: {result.stdout.strip()}")
    except Exception as e:
        print(f"   组检查失败: {e}")
    
    # 检查GPIO设备权限
    print(f"\n2. GPIO设备权限检查:")
    gpio_devices = ['/dev/gpiomem', '/dev/mem']
    for device in gpio_devices:
        if os.path.exists(device):
            stat = os.stat(device)
            print(f"   {device}: 权限 {oct(stat.st_mode)}, 用户 {stat.st_uid}, 组 {stat.st_gid}")
        else:
            print(f"   {device}: 不存在")
    
    # 检查树莓派识别
    print(f"\n3. 设备类型检查:")
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read().strip()
            print(f"   设备型号: {model}")
            if 'Raspberry Pi' in model:
                print("   ✓ 检测到树莓派")
            else:
                print("   ✗ 非树莓派设备")
    except Exception as e:
        print(f"   设备检测失败: {e}")
    
    # 检查库安装
    print(f"\n4. 库安装检查:")
    try:
        import rpi_ws281x
        print("   ✓ rpi_ws281x 库已安装")
        
        # 测试库功能
        from rpi_ws281x import PixelStrip
        try:
            strip = PixelStrip(1, 18)  # 简单初始化测试
            print("   ✓ rpi_ws281x 库功能正常")
        except Exception as e:
            print(f"   ✗ rpi_ws281x 初始化失败: {e}")
            
    except ImportError as e:
        print(f"   ✗ rpi_ws281x 库未安装: {e}")
        print("   安装命令: sudo pip3 install rpi_ws281x")
    
    # 检查Python路径
    print(f"\n5. Python环境检查:")
    print(f"   Python路径: {sys.executable}")
    print(f"   Python版本: {sys.version}")

if __name__ == '__main__':
    diagnose_led_issues()
