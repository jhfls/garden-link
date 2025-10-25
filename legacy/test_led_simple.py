#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import sys
import os

def test_led_basic():
    """基础灯带测试"""
    print("=== LED灯带基础测试 ===")
    
    # 检查是否在树莓派上
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read()
            if 'Raspberry Pi' in model:
                print(f"检测到: {model.strip()}")
            else:
                print("非树莓派环境，灯带功能可能受限")
    except:
        print("无法检测设备类型")
    
    # 尝试导入灯带库
    try:
        from rpi_ws281x import PixelStrip, Color
        print("✓ rpi_ws281x 库导入成功")
        led_available = True
    except ImportError as e:
        print(f"✗ rpi_ws281x 库导入失败: {e}")
        print("请安装: sudo pip3 install rpi_ws281x")
        led_available = False
        return
    
    # 灯带配置
    LED_COUNT = 30      # 灯珠数量
    LED_PIN = 18        # GPIO引脚
    LED_FREQ_HZ = 800000
    LED_DMA = 10
    LED_BRIGHTNESS = 50  # 亮度 (0-255)
    LED_INVERT = False
    LED_CHANNEL = 0
    
    try:
        # 初始化灯带
        print("正在初始化灯带...")
        strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, 
                          LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        strip.begin()
        print("✓ 灯带初始化成功")
        
        # 测试1: 全部点亮为白色
        print("\n1. 测试全白点亮")
        for i in range(LED_COUNT):
            strip.setPixelColor(i, Color(255, 255, 255))
        strip.show()
        time.sleep(2)
        
        # 测试2: 全部关闭
        print("2. 测试关闭所有灯")
        for i in range(LED_COUNT):
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
        time.sleep(1)
        
        # 测试3: 单色测试 (红色)
        print("3. 测试红色")
        for i in range(LED_COUNT):
            strip.setPixelColor(i, Color(255, 0, 0))
        strip.show()
        time.sleep(2)
        
        # 测试4: 单色测试 (绿色)
        print("4. 测试绿色")
        for i in range(LED_COUNT):
            strip.setPixelColor(i, Color(0, 255, 0))
        strip.show()
        time.sleep(2)
        
        # 测试5: 单色测试 (蓝色)
        print("5. 测试蓝色")
        for i in range(LED_COUNT):
            strip.setPixelColor(i, Color(0, 0, 255))
        strip.show()
        time.sleep(2)
        
        # 测试6: 彩虹色测试
        print("6. 测试彩虹色")
        colors = [
            (255, 0, 0),    # 红
            (255, 127, 0),  # 橙
            (255, 255, 0),  # 黄
            (0, 255, 0),    # 绿
            (0, 0, 255),    # 蓝
            (75, 0, 130),   # 靛
            (148, 0, 211)   # 紫
        ]
        
        for color in colors:
            for i in range(LED_COUNT):
                strip.setPixelColor(i, Color(*color))
            strip.show()
            time.sleep(0.5)
        
        # 测试7: 流水灯效果
        print("7. 测试流水灯效果")
        for i in range(LED_COUNT * 2):
            # 清除所有灯
            for j in range(LED_COUNT):
                strip.setPixelColor(j, Color(0, 0, 0))
            
            # 设置当前灯
            current_led = i % LED_COUNT
            strip.setPixelColor(current_led, Color(0, 255, 255))
            
            # 设置拖尾效果
            if current_led > 0:
                strip.setPixelColor(current_led - 1, Color(0, 127, 127))
            if current_led > 1:
                strip.setPixelColor(current_led - 2, Color(0, 63, 63))
                
            strip.show()
            time.sleep(0.1)
        
        # 最后关闭所有灯
        print("8. 关闭所有灯")
        for i in range(LED_COUNT):
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
        
        print("\n✓ 所有测试完成！")
        
    except Exception as e:
        print(f"✗ 灯带测试失败: {e}")
        print("可能的原因:")
        print("1. 权限不足 - 尝试使用 sudo 运行")
        print("2. GPIO引脚被占用")
        print("3. 硬件连接问题")
        print("4. DMA通道冲突")

if __name__ == '__main__':
    # 检查是否以root运行
    if os.geteuid() != 0:
        print("警告: 未以root权限运行，灯带可能无法工作")
        print("建议使用: sudo python3 test_led_simple.py")
        response = input("是否继续? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    try:
        test_led_basic()
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
