import RPi.GPIO as GPIO
import time

def pwm_control_test():
    """PWM控制测试（如果您的驱动器支持）"""
    PIN = 24
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN, GPIO.OUT)
    
    # 创建PWM实例，频率1kHz
    pwm = GPIO.PWM(PIN, 1000)
    pwm.start(0)  # 初始占空比0%
    
    try:
        print("🎛️  Starting PWM control test...")
        
        # 测试不同占空比
        for duty_cycle in [0, 25, 50, 75, 100, 75, 50, 25, 0]:
            pwm.ChangeDutyCycle(duty_cycle)
            print(f"🔧 Duty cycle: {duty_cycle}%")
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n🛑 PWM test interrupted")
    finally:
        pwm.stop()
        GPIO.cleanup()
        print("🧹 PWM test cleaned up")

# 运行PWM测试（取消注释来测试）
pwm_control_test()