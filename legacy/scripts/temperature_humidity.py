#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import threading
import os

class TemperatureHumiditySensor:
    def __init__(self, gpio_pin=12):
        self.gpio_pin = gpio_pin
        self.temperature = None
        self.humidity = None
        self.simulation_mode = False
        self.sensor = None
        
        # 温湿度舒适范围
        self.comfort_temp_range = (20, 26)  # 舒适温度范围 20-26°C
        self.comfort_humidity_range = (40, 60)  # 舒适湿度范围 40-60%
        
        # 初始化传感器
        self.setup_sensor()
        
        # 启动监控线程
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        print("温湿度传感器初始化完成")

    def setup_sensor(self):
        """初始化DHT11传感器"""
        try:
            # 检查是否在树莓派上
            if not self.is_raspberry_pi():
                print("警告: 不在树莓派环境，使用模拟模式")
                self.simulation_mode = True
                return
            
            import Adafruit_DHT
            self.sensor = Adafruit_DHT.DHT11
            self.simulation_mode = False
            print(f"✓ DHT11传感器初始化成功 (GPIO{self.gpio_pin})")
            
        except ImportError as e:
            print(f"✗ Adafruit_DHT库未安装: {e}")
            print("请安装: sudo pip3 install Adafruit_DHT")
            self.simulation_mode = True
        except Exception as e:
            print(f"✗ 传感器初始化失败: {e}")
            self.simulation_mode = True

    def is_raspberry_pi(self):
        """检查是否在树莓派上"""
        try:
            with open('/proc/device-tree/model', 'r') as f:
                return 'Raspberry Pi' in f.read()
        except:
            return False

    def read_sensor(self):
        """读取传感器数据"""
        if self.simulation_mode:
            # 模拟数据 - 在舒适范围附近随机波动
            import random
            base_temp = 23
            base_humidity = 50
            self.temperature = base_temp + random.uniform(-3, 3)
            self.humidity = base_humidity + random.uniform(-15, 15)
            return True
        else:
            # 读取真实传感器数据
            try:
                import Adafruit_DHT
                humidity, temperature = Adafruit_DHT.read_retry(self.sensor, self.gpio_pin)
                
                if humidity is not None and temperature is not None:
                    self.temperature = temperature
                    self.humidity = humidity
                    return True
                else:
                    print("读取传感器数据失败")
                    return False
                    
            except Exception as e:
                print(f"读取传感器错误: {e}")
                return False

    def get_recommendations(self):
        """根据温湿度给出调节建议"""
        if self.temperature is None or self.humidity is None:
            return ["等待传感器数据..."]
        
        recommendations = []
        
        # 温度建议
        if self.temperature < self.comfort_temp_range[0]:
            recommendations.append("开热空调")
        elif self.temperature > self.comfort_temp_range[1]:
            recommendations.append("开冷空调")
        else:
            recommendations.append("温度适宜")
        
        # 湿度建议
        if self.humidity < self.comfort_humidity_range[0]:
            recommendations.append("开加湿器")
        elif self.humidity > self.comfort_humidity_range[1]:
            recommendations.append("开除湿机")
        else:
            recommendations.append("湿度适宜")
        
        return recommendations

    def get_comfort_level(self):
        """计算舒适度指数 (0-100)"""
        if self.temperature is None or self.humidity is None:
            return 0
        
        temp_score = 0
        humidity_score = 0
        
        # 温度评分
        if self.comfort_temp_range[0] <= self.temperature <= self.comfort_temp_range[1]:
            temp_score = 100
        else:
            temp_diff = min(
                abs(self.temperature - self.comfort_temp_range[0]),
                abs(self.temperature - self.comfort_temp_range[1])
            )
            temp_score = max(0, 100 - temp_diff * 10)
        
        # 湿度评分
        if self.comfort_humidity_range[0] <= self.humidity <= self.comfort_humidity_range[1]:
            humidity_score = 100
        else:
            humidity_diff = min(
                abs(self.humidity - self.comfort_humidity_range[0]),
                abs(self.humidity - self.comfort_humidity_range[1])
            )
            humidity_score = max(0, 100 - humidity_diff * 2)
        
        # 综合舒适度
        comfort_level = (temp_score * 0.6 + humidity_score * 0.4)
        return int(comfort_level)

    def monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            success = self.read_sensor()
            if success:
                # 打印当前状态（调试用）
                comfort = self.get_comfort_level()
                recommendations = self.get_recommendations()
                print(f"温湿度: {self.temperature:.1f}°C, {self.humidity:.1f}% | 舒适度: {comfort}% | 建议: {', '.join(recommendations)}")
            else:
                print("读取传感器数据失败")
            
            time.sleep(5)  # 每5秒读取一次

    def get_status(self):
        """获取当前状态"""
        return {
            "temperature": round(self.temperature, 1) if self.temperature is not None else None,
            "humidity": round(self.humidity, 1) if self.humidity is not None else None,
            "comfort_level": self.get_comfort_level(),
            "recommendations": self.get_recommendations(),
            "simulation_mode": self.simulation_mode,
            "comfort_temp_range": self.comfort_temp_range,
            "comfort_humidity_range": self.comfort_humidity_range
        }

    def cleanup(self):
        """清理资源"""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
        print("温湿度传感器已关闭")
