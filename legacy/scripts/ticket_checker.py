#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import threading
import time
import os
from pyzbar import pyzbar
from scripts.camera_manager import camera_manager

class TicketChecker:
    def __init__(self):
        self.is_running = False
        self.current_frame = None
        self.last_qr_data = None
        self.face_detected = False
        self.qr_detected = False
        self.welcome_message = ""
        
        self.camera_available = False
        self.simulation_mode = True
        
        self.checking_state = "WAITING"
        self.face_detection_time = None
        self.qr_verification_time = None
        self.expected_qr_content = "Hello,World!"
        
        self.face_timeout = 10
        self.completion_timeout = 5
        
        # 帧率优化
        self.frame_queue = []
        self.max_queue_size = 2
        self.last_frame_time = 0
        self.target_fps = 10
        self.frame_interval = 1.0 / self.target_fps
        
        self.setup_face_detector()
        print("智能检票系统初始化完成")

    def setup_face_detector(self):
        self.face_cascade = None
        file_path = "scripts/haarcascade_frontalface_default.xml"
        if os.path.exists(file_path):
            try:
                self.face_cascade = cv2.CascadeClassifier(file_path)
                if not self.face_cascade.empty():
                    print("✓ 人脸检测器加载成功")
            except: pass

    def start_monitoring(self):
        if self.is_running: return
        
        self.cap = camera_manager.get_camera()
        if self.cap is not None:
            self.camera_available = True
            self.simulation_mode = False
        
        self.is_running = True
        self.process_thread = threading.Thread(target=self.process_frames)
        self.process_thread.daemon = True
        self.process_thread.start()
        print("开始智能检票监控...")

    def stop_monitoring(self):
        self.is_running = False
        camera_manager.release_camera()
        if hasattr(self, 'process_thread'):
            self.process_thread.join(timeout=1.0)
        print("智能检票监控已停止")

    def capture_frame(self):
        if self.simulation_mode or not self.camera_available:
            return self.generate_simulation_frame()
        
        try:
            ret, frame = camera_manager.read_frame()
            if ret and frame is not None:
                if len(self.frame_queue) >= self.max_queue_size:
                    self.frame_queue.pop(0)
                self.frame_queue.append(frame)
                return frame
        except: pass
        return self.generate_simulation_frame()

    def process_frames(self):
        frame_count = 0
        last_fps_time = time.time()
        
        while self.is_running:
            current_time = time.time()
            
            # 控制帧率
            if current_time - self.last_frame_time >= self.frame_interval:
                frame = self.capture_frame()
                if frame is not None:
                    processed_frame = self.process_single_frame(frame)
                    if processed_frame is not None:
                        self.current_frame = processed_frame
                self.last_frame_time = current_time
                frame_count += 1
            
            # FPS监控
            if current_time - last_fps_time >= 2.0:
                fps = frame_count / (current_time - last_fps_time)
                if frame_count % 10 == 0:
                    print(f"检票处理FPS: {fps:.1f}")
                frame_count = 0
                last_fps_time = current_time
            
            time.sleep(0.01)

    def process_single_frame(self, frame):
        try:
            # 快速处理 - 降低分辨率
            small_frame = cv2.resize(frame, (320, 240))
            
            # 条件检测 - 只在需要时检测
            faces = []
            if self.face_cascade and self.checking_state in ["WAITING", "FACE_DETECTED"]:
                faces = self.detect_faces(small_frame)
            
            qr_codes = []
            if self.checking_state in ["FACE_DETECTED", "QR_CHECKING"]:
                qr_codes = self.detect_qr_codes(small_frame)
            
            self.face_detected = len(faces) > 0
            self.qr_detected = len(qr_codes) > 0
            self.update_checking_state(faces, qr_codes)
            self.update_welcome_message()
            
            return self.draw_detections(frame, faces, qr_codes)
        except: return frame

    def detect_faces(self, frame):
        if self.face_cascade is None: return []
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return self.face_cascade.detectMultiScale(gray, 1.2, 3, minSize=(30, 30))
        except: return []

    def detect_qr_codes(self, frame):
        try:
            decoded_objects = pyzbar.decode(frame)
            return [{'data': obj.data.decode('utf-8'), 'polygon': obj.polygon, 'rect': obj.rect} 
                   for obj in decoded_objects if obj.data]
        except: return []

    def update_checking_state(self, faces, qr_codes):
        current_time = time.time()
        
        if self.checking_state == "WAITING":
            if len(faces) > 0:
                self.checking_state = "FACE_DETECTED"
                self.face_detection_time = current_time
        
        elif self.checking_state == "FACE_DETECTED":
            if current_time - self.face_detection_time > self.face_timeout:
                self.checking_state = "WAITING"
            elif len(qr_codes) > 0:
                self.checking_state = "QR_CHECKING"
        
        elif self.checking_state == "QR_CHECKING":
            valid_qr_found = any(qr['data'] == self.expected_qr_content for qr in qr_codes)
            if valid_qr_found:
                self.checking_state = "COMPLETED"
                self.qr_verification_time = current_time
            elif len(qr_codes) == 0:
                self.checking_state = "COMPLETED"
        
        elif self.checking_state == "COMPLETED":
            if current_time - self.qr_verification_time > self.completion_timeout:
                self.checking_state = "WAITING"

    def update_welcome_message(self):
        if self.checking_state == "WAITING":
            self.welcome_message = "等待游客..."
        elif self.checking_state == "FACE_DETECTED":
            remaining = self.face_timeout - (time.time() - self.face_detection_time)
            self.welcome_message = f"请出示二维码 ({int(remaining)}秒)"
        elif self.checking_state == "QR_CHECKING":
            self.welcome_message = "正在验证二维码..."
        elif self.checking_state == "COMPLETED":
            self.welcome_message = "欢迎光临！验证成功"

    def draw_detections(self, frame, faces, qr_codes):
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        for qr in qr_codes:
            points = qr['polygon']
            if len(points) > 4:
                hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                cv2.polylines(frame, [hull.astype(int)], True, (255, 0, 0), 2)
        
        cv2.putText(frame, f'State: {self.checking_state}', (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        if self.welcome_message:
            text_size = cv2.getTextSize(self.welcome_message, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
            text_x = (frame.shape[1] - text_size[0]) // 2
            cv2.putText(frame, self.welcome_message, (text_x, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        return frame

    def generate_simulation_frame(self):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(frame, f"状态: {self.checking_state}", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, "模拟模式", (50, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        return frame

    def get_frame_bytes(self):
        try:
            if self.current_frame is not None:
                ret, jpeg = cv2.imencode('.jpg', self.current_frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                if ret: return jpeg.tobytes()
        except: pass
        return None

    def get_status(self):
        return {
            "checking_state": self.checking_state,
            "face_detected": self.face_detected,
            "qr_detected": self.qr_detected,
            "welcome_message": self.welcome_message,
            "last_qr_data": self.last_qr_data,
            "simulation_mode": self.simulation_mode,
            "camera_available": self.camera_available,
            "is_running": self.is_running
        }

    def cleanup(self):
        self.stop_monitoring()