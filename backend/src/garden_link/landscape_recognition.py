from . import config, utils
from typing import Generator


PROMPT = f"""请仔细观察这张图片，判断其中是否包含自然景观（如山川、河流、湖泊、森林等）或人文景观（如古建筑、园林、名胜古迹等）。

如果图中包含景观：
1. 输出一句与该景观相关的中国古代文学作品名句（诗词、散文、赋等）
2. 简要说明该名句的出处、作者和背景
3. 或者描述与该景观相关的文学事件或典故

如果图中不包含景观或无法识别出明确的景观，请只输出：{utils.NULL_TEXT}

请直接给出至多一个答案，不需要额外的解释说明。"""


def _analyze_image(base64: str) -> Generator[str, None, None]:
    response = utils.ai.chat.completions.create(
        model=config.LANDSCAPE_RECOGNITION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64}",
                        },
                    },
                ],
            }
        ],
        temperature=config.MODEL_TEMPERATURE,
        max_tokens=config.MODEL_MAX_TOKENS,
        timeout=config.MODEL_TIMEOUT,
        stream=True,
    )
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            yield content


def capture():
    frame = utils.take_photo(config.CAMERA_INDEX)
    image_base64 = utils.image_to_base64(frame)
    for chunk in _analyze_image(image_base64):
        if chunk != utils.NULL_TEXT:
            print(chunk, end="")
    print()
