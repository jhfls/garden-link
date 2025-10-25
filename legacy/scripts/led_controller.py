#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import time
import atexit
import os

class LEDController:
    def __init__(self):
        # LED配置
        self.LED_COUNT = 30
        self.LED_PIN = 18
        self.LED_FREQ_HZ = 800000
        self.LED_DMA = 10
        self.LED_BRIGHTNESS = 50
        self.LED_INVERT = False
        self.LED_CHANNEL = 0
        
        # 控制变量
        self.animation_thread = None
        self.is_running = False
        self.brightness = 50
        self.chase_length = 5
        self.simulation_mode = False
        self.strip = None
        
        # 尝试初始化物理灯带
        self.setup_led_strip()
        
        # 注册清理函数
        atexit.register(self.cleanup)
        
        print(f"LED控制器初始化完成 - 模式: {'模拟' if self.simulation_mode else '物理'}")

    def setup_led_strip(self):
        """设置LED灯带"""
        try:
            # 检查是否在树莓派上
            if not self.is_raspberry_pi():
                print("警告: 不在树莓派环境，使用模拟模式")
                self.simulation_mode = True
                return
            
            # 检查权限
            if os.geteuid() != 0:
                print("警告: 未以root权限运行，使用模拟模式")
                print("请使用: sudo python app.py")
                self.simulation_mode = True
                return
            
            from rpi_ws281x import PixelStrip
            
            print("正在初始化物理灯带...")
            self.strip = PixelStrip(
                self.LED_COUNT, 
                self.LED_PIN, 
                self.LED_FREQ_HZ, 
                self.LED_DMA, 
                self.LED_INVERT, 
                self.LED_BRIGHTNESS, 
                self.LED_CHANNEL
            )
            self.strip.begin()
            self.simulation_mode = False
            print("✓ 物理灯带初始化成功")
            
        except Exception as e:
            print(f"✗ 物理灯带初始化失败: {e}")
            print("切换到模拟模式")
            self.simulation_mode = True
            self.strip = None

    def is_raspberry_pi(self):
        """检查是否在树莓派上"""
        try:
            with open('/proc/device-tree/model', 'r') as f:
                model = f.read()
                is_pi = 'Raspberry Pi' in model
                if is_pi:
                    print(f"检测到树莓派: {model.strip()}")
                return is_pi
        except:
            print("无法读取设备信息，可能不是树莓派")
            return False

    def cleanup(self):
        """清理资源"""
        self.stop_animation()
        if not self.simulation_mode and self.strip:
            self.clear_leds()
            print("灯带资源已清理")

    def clear_leds(self):
        """关闭所有LED"""
        if self.simulation_mode:
            print("模拟: 关闭所有LED")
            return
        
        try:
            for i in range(self.LED_COUNT):
                self.strip.setPixelColor(i, 0)
            self.strip.show()
            print("物理: 所有LED已关闭")
        except Exception as e:
            print(f"清除LED失败: {e}")

    def pastel_wheel(self, pos):
        """生成柔和的颜色"""
        pos = pos % 256
        if pos < 64:
            return (80, 60, 100)  # 淡紫色
        elif pos < 128:
            return (60, 80, 100)  # 淡蓝色
        elif pos < 192:
            return (80, 100, 60)  # 淡绿色
        else:
            return (100, 80, 60)  # 淡粉色

    def chase_animation(self):
        """跑马灯动画"""
        print(f"开始跑马灯动画 - 亮度: {self.brightness}, 长度: {self.chase_length}")
        frame_count = 0
        
        while self.is_running:
            try:
                for i in range(self.LED_COUNT):
                    if not self.is_running:
                        break
                    
                    if not self.simulation_mode and self.strip:
                        # 物理灯带控制
                        from rpi_ws281x import Color
                        
                        # 清除所有LED
                        for j in range(self.LED_COUNT):
                            self.strip.setPixelColor(j, 0)
                        
                        # 设置当前LED和拖尾效果
                        for j in range(-self.chase_length + 1, 1):
                            led_index = (i + j) % self.LED_COUNT
                            if 0 <= led_index < self.LED_COUNT:
                                # 计算亮度
                                brightness_factor = max(0, 1 - abs(j) * (1.0 / self.chase_length))
                                color = self.pastel_wheel(i * 8)
                                r = int(color[0] * brightness_factor)
                                g = int(color[1] * brightness_factor)
                                b = int(color[2] * brightness_factor)
                                self.strip.setPixelColor(led_index, Color(r, g, b))
                        
                        self.strip.show()
                        
                    else:
                        # 模拟模式
                        if frame_count % 20 == 0:  # 每20帧打印一次
                            print(f"模拟: 跑马灯位置 {i}, 长度 {self.chase_length}, 亮度 {self.brightness}")
                    
                    time.sleep(0.1)
                    frame_count += 1
                    
            except Exception as e:
                print(f"动画错误: {e}")
                break
        
        self.clear_leds()
        print("跑马灯动画结束")

    def start_animation(self):
        """启动动画"""
        if self.is_running:
            print("动画已在运行")
            return
        
        self.is_running = True
        self.animation_thread = threading.Thread(target=self.chase_animation)
        self.animation_thread.daemon = True
        self.animation_thread.start()
        
        mode = "模拟" if self.simulation_mode else "物理"
        print(f"{mode}跑马灯已启动 - 亮度: {self.brightness}, 长度: {self.chase_length}")

    def stop_animation(self):
        """停止动画"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.animation_thread and self.animation_thread.is_alive():
            self.animation_thread.join(timeout=2)
        self.clear_leds()
        print("跑马灯已停止")

    def set_brightness(self, brightness):
        """设置亮度"""
        self.brightness = max(0, min(255, brightness))
        
        if not self.simulation_mode and self.strip:
            self.strip.setBrightness(self.brightness)
            if self.is_running:
                self.strip.show()  # 立即更新
        
        print(f"亮度设置为: {self.brightness}")

    def set_chase_length(self, length):
        """设置跑马灯长度"""
        self.chase_length = max(1, min(30, length))
        print(f"跑马灯长度设置为: {self.chase_length}")

    def get_status(self):
        """获取状态"""
        return {
            "is_running": self.is_running,
            "brightness": self.brightness,
            "chase_length": self.chase_length,
            "simulation_mode": self.simulation_mode,
            "led_count": self.LED_COUNT
        }