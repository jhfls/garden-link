import base64
from io import BytesIO
import cv2
from PIL import Image
from . import config
import openai


NULL_TEXT = "Ø"


ai = openai.OpenAI(base_url=config.LM_STUDIO_URL, api_key="")


class UnexpectedResponseError(Exception):
    def __init__(self, response: object) -> None:
        super().__init__(f"未知响应：{response}")


def take_photo(camera_index=config.CAMERA_INDEX):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError("无法打开摄像头")
    ret, frame = cap.read()
    cap.release()
    if not ret:
        raise RuntimeError("无法读取摄像头图像")
    return frame


def image_to_base64(image: cv2.typing.MatLike) -> str:
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image_rgb)
    buffered = BytesIO()
    pil_image.save(buffered, format="JPEG", quality=config.IMAGE_QUALITY)
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_base64
