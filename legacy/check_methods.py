#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_methods():
    print("检查智能播报模块的方法...")
    
    try:
        from scripts.smart_broadcast import SmartBroadcast
        
        # 创建实例
        broadcast = SmartBroadcast()
        print("✓ SmartBroadcast实例创建成功")
        
        # 检查方法是否存在
        methods_to_check = [
            'get_frame_bytes',
            'start_monitoring', 
            'stop_monitoring',
            'capture_image',
            'get_status'
        ]
        
        for method in methods_to_check:
            if hasattr(broadcast, method):
                print(f"✓ 方法存在: {method}")
            else:
                print(f"✗ 方法不存在: {method}")
        
        # 检查方法是否可调用
        if hasattr(broadcast, 'get_frame_bytes'):
            print("测试调用 get_frame_bytes...")
            try:
                result = broadcast.get_frame_bytes()
                if result:
                    print(f"✓ get_frame_bytes 调用成功，返回数据大小: {len(result)}")
                else:
                    print("⚠ get_frame_bytes 返回 None")
            except Exception as e:
                print(f"✗ get_frame_bytes 调用失败: {e}")
        
    except Exception as e:
        print(f"检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_methods()
