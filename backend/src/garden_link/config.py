# 配置文件

LM_STUDIO_URL = "http://192.168.0.167:1234/v1"
CAMERA_INDEX = 0  # USB 摄像头索引，通常为 0，如果有多个摄像头则尝试 1、2 等
IMAGE_QUALITY = 85  # JPEG 压缩质量（1-100）

MODEL_TIMEOUT = 30  # API 请求超时时间（秒）
MODEL_TEMPERATURE = 0.7  # 模型温度参数
MODEL_MAX_TOKENS = 500  # 最大返回 token 数

LANDSCAPE_RECOGNITION_MODEL = "qwen3-vl-8b"
SATISFACTION_SURVEY_VISUAL_MODEL = "qwen3-vl-8b"
