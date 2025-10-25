#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import time

def test_video_stream():
    print("=== 测试视频流生成 ===")
    
    # 测试帧生成
    frame_count = 0
    start_time = time.time()
    
    while frame_count < 10:  # 测试10帧
        try:
            # 生成测试帧
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            
            # 添加动态内容
            cv2.putText(frame, f"测试帧 {frame_count}", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, f"时间: {time.time():.2f}", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # 添加移动的圆
            x = int(320 + 200 * np.sin(frame_count * 0.5))
            y = int(240 + 150 * np.cos(frame_count * 0.3))
            cv2.circle(frame, (x, y), 30, (0, 0, 255), -1)
            
            # 编码为JPEG
            ret, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            
            if ret:
                frame_size = len(jpeg.tobytes())
                print(f"✓ 帧 {frame_count}: 编码成功 - 大小: {frame_size} 字节")
            else:
                print(f"✗ 帧 {frame_count}: 编码失败")
            
            frame_count += 1
            time.sleep(0.1)
            
        except Exception as e:
            print(f"✗ 帧 {frame_count}: 生成失败 - {e}")
            break
    
    elapsed = time.time() - start_time
    print(f"\n测试完成: {frame_count} 帧, 耗时: {elapsed:.2f}秒")

if __name__ == '__main__':
    test_video_stream()
