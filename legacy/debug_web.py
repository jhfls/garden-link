#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

def test_backend_connection():
    """测试后端连接"""
    print("=== 后端服务连接测试 ===")
    
    base_url = "http://localhost:5000"
    
    # 测试健康检查接口
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"健康检查: ✓ (状态码: {response.status_code})")
        print(f"响应内容: {response.json()}")
    except Exception as e:
        print(f"健康检查: ✗ (错误: {e})")
        return False
    
    # 测试LED状态接口
    try:
        response = requests.get(f"{base_url}/api/led/status", timeout=5)
        print(f"LED状态: ✓ (状态码: {response.status_code})")
        print(f"响应内容: {response.json()}")
    except Exception as e:
        print(f"LED状态: ✗ (错误: {e})")
    
    # 测试LED控制接口
    try:
        test_data = {"action": "start"}
        response = requests.post(
            f"{base_url}/api/led/control",
            json=test_data,
            timeout=5
        )
        print(f"LED控制: ✓ (状态码: {response.status_code})")
        print(f"响应内容: {response.json()}")
    except Exception as e:
        print(f"LED控制: ✗ (错误: {e})")
    
    return True

def test_frontend_buttons():
    """模拟前端按钮点击"""
    print("\n=== 模拟前端按钮点击 ===")
    
    base_url = "http://localhost:5000"
    
    # 模拟点击"启动跑马灯"
    test_data = {"action": "start"}
    
    try:
        response = requests.post(
            f"{base_url}/api/led/control",
            json=test_data,
            timeout=10
        )
        
        print(f"请求URL: {base_url}/api/led/control")
        print(f"请求数据: {test_data}")
        print(f"响应状态: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"API响应: {result}")
            
            # 检查LED状态
            time.sleep(1)
            status_response = requests.get(f"{base_url}/api/led/status")
            print(f"LED状态更新: {status_response.json()}")
            
        return True
        
    except Exception as e:
        print(f"请求失败: {e}")
        return False

if __name__ == '__main__':
    print("正在诊断网页端问题...")
    
    if test_backend_connection():
        print("\n连接测试通过，开始模拟按钮点击...")
        test_frontend_buttons()
    else:
        print("\n后端服务连接失败，请检查:")
        print("1. 后端服务是否运行: sudo python app.py")
        print("2. 端口5000是否被占用")
        print("3. 防火墙设置")
