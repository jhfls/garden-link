import Adafruit_DHT
import time

# 设置传感器类型和GPIO引脚
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 12

def read_dht11():
    """读取DHT11传感器数据"""
    try:
        # 读取湿度和温度
        humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
        
        if humidity is not None and temperature is not None:
            print(f"🌡️  温度: {temperature:.1f}°C")
            print(f"💧 湿度: {humidity:.1f}%")
            return temperature, humidity
        else:
            print("❌ 读取传感器失败，请检查接线")
            return None, None
            
    except Exception as e:
        print(f"⚠️ 错误: {e}")
        return None, None

def continuous_monitor(interval=2):
    """连续监测"""
    print("开始连续监测DHT11传感器...")
    print("按 Ctrl+C 停止")
    print("-" * 30)
    
    try:
        while True:
            temp, humidity = read_dht11()
            if temp is not None:
                print(f"温度: {temp:.1f}°C | 湿度: {humidity:.1f}% | {time.strftime('%H:%M:%S')}")
            else:
                print(f"读取失败 | {time.strftime('%H:%M:%S')}")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n👋 监测停止")

if __name__ == "__main__":
    # 单次读取
    print("DHT11传感器测试")
    print("=" * 20)
    read_dht11()
    
    # 连续监测（取消注释来启用）
    # continuous_monitor()
