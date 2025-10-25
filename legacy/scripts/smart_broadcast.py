#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import threading
import time
import requests
import subprocess
from scripts.camera_manager import camera_manager

class SmartBroadcast:
    """智能语音解说类"""
    
    def __init__(self):
        print("初始化 SmartBroadcast 类...")
        self.is_running = False
        self.current_frame = None
        
        self.camera_available = False
        self.simulation_mode = True
        
        self.api_key = "sk-c8d57c40332a43509e927b3fc22ea04f"
        self.api_url = "https://api.deepseek.com/chat/completions"
        
        self.is_playing_audio = False
        self.broadcast_state = "READY"
        self.captured_image = None
        self.ocr_text = ""
        self.ai_response = ""
        self.last_capture_time = 0
        
        # 帧率优化
        self.last_frame_time = 0
        self.target_fps = 8
        self.frame_interval = 1.0 / self.target_fps
        
        print("✓ SmartBroadcast 类初始化完成")

    def start_monitoring(self):
        """开始监控"""
        print("调用 start_monitoring 方法")
        if self.is_running: 
            print("监控已在运行")
            return
        
        # 使用全局摄像头管理器
        self.cap = camera_manager.get_camera()
        if self.cap is not None:
            self.camera_available = True
            self.simulation_mode = False
            print("✓ 语音解说系统获取摄像头成功")
        else:
            self.camera_available = False
            self.simulation_mode = True
            print("⚠ 语音解说系统使用模拟模式")
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print("✓ 开始智能语音解说监控...")

    def capture_image(self):
        """拍摄图片"""
        print("调用 capture_image 方法")
        if self.broadcast_state != "READY":
            return False, "系统忙，请稍后再试"
        
        try:
            self.broadcast_state = "CAPTURING"
            
            # 获取最新帧
            frame = self.capture_frame()
            if frame is not None:
                self.captured_image = frame.copy()
            
            self.last_capture_time = time.time()
            self.broadcast_state = "PROCESSING"
            
            # 在新线程中处理图片
            processing_thread = threading.Thread(target=self.process_image)
            processing_thread.daemon = True
            processing_thread.start()
            
            return True, "图片拍摄成功，正在分析..."
            
        except Exception as e:
            self.broadcast_state = "READY"
            return False, f"拍摄失败: {str(e)}"

    def get_frame_bytes(self):
        """获取当前帧的字节数据"""
        print("调用 get_frame_bytes 方法")
        try:
            # 如果当前帧为空，先生成一帧
            if self.current_frame is None:
                print("当前帧为空，生成新帧...")
                frame = self.capture_frame()
                if frame is not None:
                    self.current_frame = self.add_status_overlay(frame)
            
            if self.current_frame is not None:
                # 编码为JPEG
                ret, jpeg = cv2.imencode('.jpg', self.current_frame, [
                    cv2.IMWRITE_JPEG_QUALITY, 70
                ])
                if ret:
                    print(f"✓ 成功编码帧，大小: {len(jpeg.tobytes())} 字节")
                    return jpeg.tobytes()
                else:
                    print("✗ JPEG编码失败")
            else:
                print("✗ 当前帧仍然为空")
                
        except Exception as e:
            print(f"✗ get_frame_bytes错误: {e}")
            import traceback
            traceback.print_exc()
        
        # 返回错误帧
        try:
            error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(error_frame, "视频流错误", (200, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            ret, jpeg = cv2.imencode('.jpg', error_frame)
            if ret:
                return jpeg.tobytes()
        except:
            pass
        
        return None

    def get_status(self):
        """获取系统状态"""
        return {
            "broadcast_state": self.broadcast_state,
            "is_playing_audio": self.is_playing_audio,
            "last_capture_time": self.last_capture_time,
            "ocr_text": self.ocr_text,
            "ai_response": self.ai_response,
            "camera_available": self.camera_available,
            "simulation_mode": self.simulation_mode,
            "is_running": self.is_running
        }

    # 其他方法保持不变...
    def stop_monitoring(self):
        """停止监控"""
        self.is_running = False
        camera_manager.release_camera()
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=1.0)
        print("智能语音解说监控已停止")

    def monitor_loop(self):
        """监控循环"""
        frame_count = 0
        last_fps_time = time.time()
        
        while self.is_running:
            current_time = time.time()
            
            if current_time - self.last_frame_time >= self.frame_interval:
                frame = self.capture_frame()
                if frame is not None:
                    self.current_frame = self.add_status_overlay(frame)
                self.last_frame_time = current_time
                frame_count += 1
            
            if current_time - last_fps_time >= 3.0:
                fps = frame_count / (current_time - last_fps_time)
                if frame_count % 15 == 0:
                    print(f"播报处理FPS: {fps:.1f}")
                frame_count = 0
                last_fps_time = current_time
            
            time.sleep(0.01)

    def capture_frame(self):
        """捕获帧"""
        if self.simulation_mode or not self.camera_available:
            return self.generate_simulation_frame()
        
        try:
            ret, frame = camera_manager.read_frame()
            if ret and frame is not None:
                return frame
        except Exception as e:
            print(f"捕获帧错误: {e}")
        
        return self.generate_simulation_frame()

    def generate_simulation_frame(self):
        """生成模拟帧"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        status_color = (0, 255, 0) if self.broadcast_state == "READY" else (255, 255, 0)
        cv2.putText(frame, f"状态: {self.broadcast_state}", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
        cv2.putText(frame, "模拟模式 - 点击拍摄测试", (50, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        return frame

    def add_status_overlay(self, frame):
        """在帧上添加状态信息"""
        status_colors = {
            "READY": (0, 255, 0), "CAPTURING": (255, 255, 0), 
            "PROCESSING": (255, 165, 0), "SPEAKING": (0, 255, 255)
        }
        color = status_colors.get(self.broadcast_state, (255, 255, 255))
        
        cv2.putText(frame, f"状态: {self.broadcast_state}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        mode_text = "模拟模式" if self.simulation_mode else "实时模式"
        cv2.putText(frame, f"模式: {mode_text}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        if self.last_capture_time > 0:
            time_str = time.strftime("%H:%M:%S", time.localtime(self.last_capture_time))
            cv2.putText(frame, f"最后拍摄: {time_str}", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        if self.is_playing_audio:
            cv2.putText(frame, "🔊 播放中...", (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        return frame

    def process_image(self):
        """处理图片"""
        try:
            print("开始处理图片...")
            self.ocr_text = "智能识别到景区场景"
            self.ai_response = "欢迎来到美丽的景区！这里风景优美，历史悠久..."
            self.speak_text(self.ai_response)
            self.broadcast_state = "READY"
        except Exception as e:
            print(f"处理图片错误: {e}")
            self.broadcast_state = "READY"

    def speak_text(self, text):
        """文字转语音"""
        try:
            self.broadcast_state = "SPEAKING"
            self.is_playing_audio = True
            
            clean_text = text[:100]
            cmd = ['espeak', '-v', 'zh', '-s', '150', clean_text]
            subprocess.run(cmd, timeout=30)
        except Exception as e:
            print(f"语音播放错误: {e}")
        finally:
            self.is_playing_audio = False

    def cleanup(self):
        """清理资源"""
        self.stop_monitoring()