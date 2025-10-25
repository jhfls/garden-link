#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_smart_broadcast():
    print("=== 测试 SmartBroadcast 类 ===")
    
    # 测试导入
    try:
        from scripts.smart_broadcast import SmartBroadcast
        print("✓ 导入成功")
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return
    
    # 测试实例化
    try:
        broadcast = SmartBroadcast()
        print(f"✓ 实例化成功，类型: {type(broadcast)}")
    except Exception as e:
        print(f"✗ 实例化失败: {e}")
        return
    
    # 测试方法
    methods_to_test = ['start_monitoring', 'capture_image', 'get_frame_bytes', 'get_status']
    
    for method_name in methods_to_test:
        if hasattr(broadcast, method_name):
            method = getattr(broadcast, method_name)
            print(f"✓ 方法 {method_name} 存在，类型: {type(method)}")
        else:
            print(f"✗ 方法 {method_name} 不存在")
    
    # 测试具体方法调用
    try:
        status = broadcast.get_status()
        print(f"✓ get_status() 调用成功: {status}")
    except Exception as e:
        print(f"✗ get_status() 调用失败: {e}")
    
    # 清理
    try:
        broadcast.cleanup()
        print("✓ 清理成功")
    except:
        print("✗ 清理失败")

if __name__ == '__main__':
    test_smart_broadcast()
