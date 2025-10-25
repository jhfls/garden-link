#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
from pyzbar import pyzbar

def test_qr_detection():
    print("=== 测试二维码检测功能 ===")
    
    # 创建一个包含二维码的测试图像
    def create_test_qr_image():
        # 创建一个空白图像
        img = np.ones((400, 400, 3), dtype=np.uint8) * 255
        
        # 添加测试文本
        cv2.putText(img, "测试二维码图像", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(img, "请扫描包含 'Hello World' 的二维码", (20, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        # 添加一个模拟的二维码框（实际使用时需要真实二维码）
        cv2.rectangle(img, (100, 150), (300, 350), (0, 0, 255), 2)
        cv2.putText(img, "二维码区域", (120, 140), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        return img
    
    # 测试二维码检测
    test_image = create_test_qr_image()
    
    try:
        # 检测二维码
        decoded_objects = pyzbar.decode(test_image)
        
        if decoded_objects:
            print("✓ 二维码检测功能正常")
            for obj in decoded_objects:
                try:
                    data = obj.data.decode('utf-8')
                    print(f"  检测到二维码: {data}")
                    print(f"  类型: {obj.type}")
                except:
                    print("  检测到二维码但无法解码内容")
        else:
            print("⚠ 未检测到二维码（这是正常的，因为没有真实二维码）")
            print("  请使用手机生成包含 'Hello World' 的二维码进行测试")
        
        # 显示测试图像
        cv2.imshow('QR Code Test', test_image)
        print("按任意键关闭窗口...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    except Exception as e:
        print(f"✗ 二维码检测失败: {e}")

if __name__ == '__main__':
    test_qr_detection()
