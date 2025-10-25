#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, send_file, Response
import os
import subprocess
import threading
import time
import socket
import atexit
import sys
import importlib
import cv2
import numpy as np

print("=== 初始化系统核心组件 ===")

app = Flask(__name__)

# 全局摄像头配置
def setup_camera():
    """设置摄像头参数以避免 VIDIOC_QBUF: Invalid argument 错误"""
    try:
        # 尝试不同的摄像头配置
        camera_configs = [
            {'index': 0, 'api': cv2.CAP_V4L2},
            {'index': 0, 'api': cv2.CAP_ANY},
            {'index': 1, 'api': cv2.CAP_V4L2},
            {'index': 1, 'api': cv2.CAP_ANY}
        ]
        
        for config in camera_configs:
            try:
                cap = cv2.VideoCapture(config['index'], config['api'])
                if cap.isOpened():
                    # 设置摄像头参数
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    cap.set(cv2.CAP_PROP_FPS, 30)
                    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 减少缓冲区大小
                    
                    # 测试读取一帧
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        print(f"✓ 摄像头 {config['index']} 初始化成功")
                        return cap
                    else:
                        cap.release()
            except Exception as e:
                print(f"摄像头 {config['index']} 初始化失败: {e}")
                continue
        
        print("✗ 所有摄像头初始化失败，使用模拟模式")
        return None
        
    except Exception as e:
        print(f"摄像头设置失败: {e}")
        return None

# 初始化全局摄像头
global_camera = setup_camera()

# 导入其他功能模块
try:
    from scripts.led_controller import LEDController
    LED_AVAILABLE = True
    print("✓ LED控制器导入成功")
except ImportError as e:
    print(f"✗ LED模块导入失败: {e}")
    LED_AVAILABLE = False
except Exception as e:
    print(f"✗ LED初始化错误: {e}")
    LED_AVAILABLE = False

print("\n=== 初始化智能播报系统 ===")
BROADCAST_AVAILABLE = False
smart_broadcast_instance = None

try:
    # 直接导入SmartBroadcast类
    from scripts.smart_broadcast import SmartBroadcast
    
    # 创建实例
    smart_broadcast_instance = SmartBroadcast()
    print(f"✓ SmartBroadcast 实例创建成功: {type(smart_broadcast_instance)}")
    
    # 检查必要方法
    required_methods = ['get_frame_bytes', 'capture_image', 'start_monitoring', 'get_status']
    missing_methods = []
    
    for method in required_methods:
        if hasattr(smart_broadcast_instance, method):
            print(f"✓ 方法 {method} 存在")
        else:
            print(f"✗ 方法 {method} 不存在")
            missing_methods.append(method)
    
    if not missing_methods:
        BROADCAST_AVAILABLE = True
        # 启动监控
        smart_broadcast_instance.start_monitoring()
        print("✓ 智能播报系统启动成功")
    else:
        print(f"✗ 缺少必要方法: {missing_methods}")
        BROADCAST_AVAILABLE = False
        
except Exception as e:
    print(f"✗ 智能播报系统初始化失败: {e}")
    import traceback
    traceback.print_exc()
    BROADCAST_AVAILABLE = False

# 检票模块
try:
    from scripts.ticket_checker import TicketChecker
    TICKET_CHECKER_AVAILABLE = True
    print("✓ 检票模块导入成功")
except ImportError as e:
    print(f"✗ 检票模块导入失败: {e}")
    TICKET_CHECKER_AVAILABLE = False
except Exception as e:
    print(f"✗ 检票模块初始化错误: {e}")
    TICKET_CHECKER_AVAILABLE = False

# 初始化检票系统
ticket_checker = None
if TICKET_CHECKER_AVAILABLE:
    try:
        ticket_checker = TicketChecker()
        ticket_checker.start_monitoring()
        print("✓ 智能检票系统初始化成功")
    except Exception as e:
        print(f"✗ 智能检票系统初始化失败: {e}")
        TICKET_CHECKER_AVAILABLE = False

# 温湿度模块
try:
    from scripts.temperature_humidity import TemperatureHumiditySensor
    TEMP_SENSOR_AVAILABLE = True
    print("✓ 温湿度模块导入成功")
except ImportError as e:
    print(f"✗ 温湿度模块导入失败: {e}")
    TEMP_SENSOR_AVAILABLE = False
except Exception as e:
    print(f"✗ 温湿度初始化错误: {e}")
    TEMP_SENSOR_AVAILABLE = False

# 初始化温湿度传感器
temp_sensor = None
if TEMP_SENSOR_AVAILABLE:
    try:
        temp_sensor = TemperatureHumiditySensor(gpio_pin=12)
        print("✓ 温湿度传感器初始化成功")
    except Exception as e:
        print(f"✗ 温湿度传感器初始化失败: {e}")
        TEMP_SENSOR_AVAILABLE = False

# 初始化LED控制器
led_controller = None
if LED_AVAILABLE:
    try:
        led_controller = LEDController()
        print("✓ LED控制器初始化成功")
    except Exception as e:
        print(f"✗ LED控制器初始化失败: {e}")
        LED_AVAILABLE = False

# System state variables
system_states = {
    "smart_lighting": False,
    "cloud_effect": False,
    "visitor_feedback": False,
    "holographic_display": False,
    "access_control": False,
    "smart_broadcast": False
}

VIDEO_PATH = "/home/pi/temp/1111.mp4"

# 端口管理函数
def is_port_in_use(port):
    """Check if port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def kill_port(port):
    """Kill processes using the port"""
    try:
        subprocess.run(['fuser', '-k', f'{port}/tcp'], capture_output=True)
    except:
        try:
            result = subprocess.run(['lsof', '-t', '-i', f':{port}'], capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    subprocess.run(['kill', '-9', pid], capture_output=True)
        except:
            pass

# 摄像头清理函数
def cleanup_camera():
    """清理摄像头资源"""
    if global_camera is not None:
        global_camera.release()
        print("摄像头资源已释放")

# 全局清理函数
def cleanup():
    """Cleanup resources"""
    cleanup_camera()
    if LED_AVAILABLE and led_controller:
        led_controller.cleanup()
    if BROADCAST_AVAILABLE and smart_broadcast_instance:
        smart_broadcast_instance.cleanup()
    if TICKET_CHECKER_AVAILABLE and ticket_checker:
        ticket_checker.stop_monitoring()
    print("Backend service stopped")

atexit.register(cleanup)

# ========== Page Routes ==========
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check interface"""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "camera_available": global_camera is not None,
        "broadcast_available": BROADCAST_AVAILABLE,
        "broadcast_type": str(type(smart_broadcast_instance)),
        "ticket_checker_available": TICKET_CHECKER_AVAILABLE,
        "led_available": LED_AVAILABLE,
        "temp_sensor_available": TEMP_SENSOR_AVAILABLE
    })

@app.route('/smart_lighting')
def smart_lighting():
    """Smart lighting page"""
    return render_template('smart_lighting.html')

@app.route('/cloud_effect')
def cloud_effect():
    """Cloud effect page"""
    return render_template('cloud_effect.html')

@app.route('/visitor_feedback')
def visitor_feedback():
    """Visitor feedback page"""
    return render_template('visitor_feedback.html')

@app.route('/holographic_display')
def holographic_display():
    """Holographic display page"""
    return render_template('holographic_display.html')

@app.route('/access_control')
def access_control():
    """Access control page"""
    return render_template('access_control.html')

@app.route('/smart_broadcast')
def smart_broadcast_page():
    """Smart broadcast page"""
    return render_template('smart_broadcast.html')

# ========== API Interfaces ==========
@app.route('/video_feed')
def video_feed():
    """视频流API - 检票系统"""
    if not TICKET_CHECKER_AVAILABLE:
        return "检票系统不可用", 404

    def generate_frames():
        frame_count = 0
        last_time = time.time()
        error_count = 0
        
        while True:
            try:
                frame_bytes = ticket_checker.get_frame_bytes()
                if frame_bytes:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                    
                    frame_count += 1
                    current_time = time.time()
                    if current_time - last_time >= 1.0:
                        fps = frame_count / (current_time - last_time)
                        if frame_count % 30 == 0:
                            print(f"检票视频流FPS: {fps:.1f}")
                        frame_count = 0
                        last_time = current_time
                    
                    time.sleep(0.033)  # ~30fps
                    error_count = 0  # 重置错误计数
                else:
                    error_count += 1
                    if error_count > 10:
                        print("连续获取空帧，可能摄像头出现问题")
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"检票视频流错误: {e}")
                error_count += 1
                if error_count > 5:
                    print("视频流严重错误，尝试恢复...")
                    time.sleep(1)
                else:
                    time.sleep(0.5)

    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/led/control', methods=['POST'])
def control_led():
    """Control LED strip API"""
    if not LED_AVAILABLE:
        return jsonify({"status": "error", "message": "LED function unavailable"})
    data = request.json
    action = data.get('action')
    try:
        if action == 'start':
            led_controller.start_animation()
            return jsonify({"status": "success", "message": "LED animation started"})
        elif action == 'stop':
            led_controller.stop_animation()
            return jsonify({"status": "success", "message": "LED animation stopped"})
        elif action == 'set_color':
            color = data.get('color')
            led_controller.set_color(color)
            return jsonify({"status": "success", "message": "Color set successfully"})
        else:
            return jsonify({"status": "error", "message": "Unknown operation"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/led/status')
def get_led_status():
    """Get LED status"""
    if not LED_AVAILABLE:
        return jsonify({"status": "unavailable"})
    return jsonify({
        "status": "running" if led_controller.is_running else "stopped",
        "brightness": led_controller.brightness,
        "simulation_mode": getattr(led_controller, 'simulation_mode', False)
    })

@app.route('/api/cloud_effect/control', methods=['POST'])
def control_cloud_effect():
    """Control cloud effect API"""
    data = request.json
    action = data.get('action')
    return jsonify({"status": "success", "message": "Cloud effect control interface"})

@app.route('/api/visitor_feedback/submit', methods=['POST'])
def submit_feedback():
    """Submit visitor feedback API"""
    data = request.json
    rating = data.get('rating')
    comment = data.get('comment')
    return jsonify({"status": "success", "message": "Feedback submitted successfully"})

@app.route('/api/access_control/scan', methods=['POST'])
def scan_rfid():
    """RFID scan API"""
    return jsonify({"status": "success", "message": "RFID scan interface"})

@app.route('/api/smart_broadcast/play', methods=['POST'])
def play_broadcast():
    """Play smart broadcast API"""
    data = request.json
    content = data.get('content')
    return jsonify({"status": "success", "message": "Broadcast play interface"})

@app.route('/api/system/states')
def get_states():
    """Get all system states"""
    return jsonify(system_states)

@app.route('/api/system/update_state', methods=['POST'])
def update_state():
    """Update system state"""
    data = request.json
    system_name = data.get('system')
    state = data.get('state')
    if system_name in system_states:
        system_states[system_name] = state
        print(f"System {system_name} state updated to: {state}")
        # Special handling: smart lighting system
        if system_name == "smart_lighting" and LED_AVAILABLE:
            if state:
                led_controller.start_animation()
            else:
                led_controller.stop_animation()
        return jsonify({"status": "success", "system": system_name, "state": state})
    else:
        return jsonify({"status": "error", "message": "Unknown system"})

@app.route('/api/led/set_brightness', methods=['POST'])
def set_led_brightness():
    """Set LED brightness API"""
    if not LED_AVAILABLE:
        return jsonify({"status": "error", "message": "LED function unavailable"})
    data = request.json
    brightness = data.get('brightness')
    try:
        if brightness is not None:
            led_controller.set_brightness(brightness)
            return jsonify({"status": "success", "message": f"Brightness set to {brightness}"})
        else:
            return jsonify({"status": "error", "message": "Brightness parameter required"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/environment/status')
def get_environment_status():
    """获取环境状态API"""
    if not TEMP_SENSOR_AVAILABLE:
        return jsonify({"status": "error", "message": "温湿度传感器不可用"})
    try:
        status = temp_sensor.get_status()
        return jsonify({
            "status": "success",
            "data": status
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/environment/recommendations')
def get_environment_recommendations():
    """获取环境调节建议API"""
    if not TEMP_SENSOR_AVAILABLE:
        return jsonify({"status": "error", "message": "温湿度传感器不可用"})
    try:
        recommendations = temp_sensor.get_recommendations()
        comfort_level = temp_sensor.get_comfort_level()
        return jsonify({
            "status": "success",
            "recommendations": recommendations,
            "comfort_level": comfort_level
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/ticket/status')
def get_ticket_status():
    """获取检票状态API"""
    if not TICKET_CHECKER_AVAILABLE:
        return jsonify({"status": "error", "message": "检票系统不可用"})
    try:
        status = ticket_checker.get_status()
        return jsonify({
            "status": "success",
            "data": status
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/ticket/start')
def start_ticket_checking():
    """开始检票监控API"""
    if not TICKET_CHECKER_AVAILABLE:
        return jsonify({"status": "error", "message": "检票系统不可用"})
    try:
        ticket_checker.start_monitoring()
        return jsonify({"status": "success", "message": "检票监控已启动"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/ticket/stop')
def stop_ticket_checking():
    """停止检票监控API"""
    if not TICKET_CHECKER_AVAILABLE:
        return jsonify({"status": "error", "message": "检票系统不可用"})
    try:
        ticket_checker.stop_monitoring()
        return jsonify({"status": "success", "message": "检票监控已停止"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/broadcast/status')
def get_broadcast_status():
    """获取语音解说状态API"""
    if not BROADCAST_AVAILABLE or smart_broadcast_instance is None:
        return jsonify({"status": "error", "message": "语音解说系统不可用"})
    try:
        status = smart_broadcast_instance.get_status()
        return jsonify({
            "status": "success",
            "data": status
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/broadcast/capture', methods=['POST'])
def capture_broadcast_image():
    """拍摄图片API"""
    if not BROADCAST_AVAILABLE or smart_broadcast_instance is None:
        return jsonify({"status": "error", "message": "语音解说系统不可用"})
    try:
        success, message = smart_broadcast_instance.capture_image()
        return jsonify({
            "status": "success" if success else "error",
            "message": message
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/broadcast_video_feed')
def broadcast_video_feed():
    """语音解说视频流API"""
    print(f"接收到视频流请求 - 播报模块状态: {BROADCAST_AVAILABLE}")
    print(f"智能播报对象类型: {type(smart_broadcast_instance)}")
    
    if not BROADCAST_AVAILABLE or smart_broadcast_instance is None:
        print("语音解说系统不可用")
        return "语音解说系统不可用", 404

    def generate_frames():
        print("开始生成语音解说视频流...")
        frame_count = 0
        last_time = time.time()
        error_count = 0
        
        while True:
            try:
                if smart_broadcast_instance is None:
                    print("smart_broadcast_instance对象为None")
                    time.sleep(1)
                    continue
                    
                if not hasattr(smart_broadcast_instance, 'get_frame_bytes'):
                    print("smart_broadcast_instance没有get_frame_bytes方法")
                    time.sleep(1)
                    continue
                
                frame_bytes = smart_broadcast_instance.get_frame_bytes()
                if frame_bytes:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                    
                    frame_count += 1
                    current_time = time.time()
                    if current_time - last_time >= 2.0:
                        fps = frame_count / (current_time - last_time)
                        print(f"播报视频流FPS: {fps:.1f}")
                        frame_count = 0
                        last_time = current_time
                    
                    time.sleep(0.033)
                    error_count = 0
                else:
                    error_count += 1
                    if error_count > 5:
                        print("连续获取空帧")
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"语音解说视频流错误: {e}")
                error_count += 1
                if "VIDIOC_QBUF" in str(e):
                    print("检测到摄像头缓冲区错误，尝试短暂休息")
                    time.sleep(0.5)
                else:
                    time.sleep(0.1)

    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/led/set_chase_length', methods=['POST'])
def set_led_chase_length():
    """Set LED chase length API"""
    if not LED_AVAILABLE:
        return jsonify({"status": "error", "message": "LED function unavailable"})
    data = request.json
    length = data.get('length')
    try:
        if length is not None:
            led_controller.set_chase_length(length)
            return jsonify({"status": "success", "message": f"Chase length set to {length}"})
        else:
            return jsonify({"status": "error", "message": "Length parameter required"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

def start_backend():
    """Start backend service"""
    # Kill processes using port 5000
    print("Checking port usage...")
    kill_port(5000)
    time.sleep(2)
    
    print("Smart Park Backend Service starting...")
    print(f"Camera status: {'Available' if global_camera else 'Unavailable'}")
    print(f"LED status: {'Available' if LED_AVAILABLE else 'Unavailable'}")
    print(f"Broadcast status: {'Available' if BROADCAST_AVAILABLE else 'Unavailable'}")
    print(f"Ticket checker status: {'Available' if TICKET_CHECKER_AVAILABLE else 'Unavailable'}")
    print(f"Temperature sensor status: {'Available' if TEMP_SENSOR_AVAILABLE else 'Unavailable'}")

    # Start Flask application
    try:
        print("Backend server starting on http://0.0.0.0:5000")
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False, threaded=True)
    except OSError as e:
        if "Address already in use" in str(e):
            print("Port 5000 still in use, trying port 5001...")
            app.run(debug=False, host='0.0.0.0', port=5001, use_reloader=False, threaded=True)
        else:
            raise e

if __name__ == '__main__':
    start_backend()