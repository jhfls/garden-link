#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import subprocess

class CameraManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._camera = None
            self._users = 0
            self.camera_index = 1  # 默认使用摄像头1
            self.camera_available = False
            self.simulation_frame_count = 0
            print("CameraManager 单例初始化完成")
    
    def get_camera(self):
        if self._camera is None:
            self._camera = self._initialize_camera()
        self._users += 1
        print(f"摄像头用户数: {self._users}")
        return self._camera
    
    def release_camera(self):
        self._users -= 1
        print(f"摄像头用户数: {self._users}")
        if self._users <= 0 and self._camera is not None:
            print("释放摄像头资源")
            self._camera.release()
            self._camera = None
    
    def _initialize_camera(self):
        print("初始化共享摄像头...")
        
        # 优先尝试摄像头1
        for camera_index in [1, 0, 2]:
            try:
                print(f"尝试打开摄像头 {camera_index}...")
                cap = cv2.VideoCapture(camera_index)
                
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        cap.set(cv2.CAP_PROP_FPS, 15)
                        
                        self.camera_index = camera_index
                        self.camera_available = True
                        print(f"✓ 摄像头 {camera_index} 初始化成功")
                        return cap
                    else:
                        cap.release()
                else:
                    print(f"摄像头 {camera_index} 不可用")
                    
            except Exception as e:
                print(f"摄像头 {camera_index} 初始化失败: {e}")
                if 'cap' in locals():
                    cap.release()
        
        print("所有摄像头都不可用，使用模拟模式")
        return None
    
    def read_frame(self):
        if self._camera is None:
            return False, None
        
        try:
            return self._camera.read()
        except:
            return False, None
    
    def generate_simulation_frame(self, width=640, height=480):
        self.simulation_frame_count += 1
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # 渐变背景
        for i in range(height):
            color = int(128 + 127 * np.sin(i / 50 + self.simulation_frame_count / 30))
            frame[i, :, 0] = color
            frame[i, :, 1] = int(128 + 127 * np.sin(i / 40 + self.simulation_frame_count / 25))
            frame[i, :, 2] = int(128 + 127 * np.sin(i / 60 + self.simulation_frame_count / 35))
        
        cv2.putText(frame, "模拟摄像头模式", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"帧: {self.simulation_frame_count}", (50, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame

# 全局单例实例
camera_manager = CameraManager()