from . import config, utils

PROMPT = f"""请仔细观察这张图片中的所有人脸。
1. 识别每个人的表情（例如：非常开心、开心、平静、不开心、非常不开心）。
2. 根据以下规则为每个表情打分：
    - 非常开心/大笑：5
    - 开心/微笑：4
    - 平静/没有表情：3
    - 不开心/伤心：2
    - 非常不开心/愤怒：1
3. 为图中的每一个人脸输出一个对应的分数。
4. 将所有分数以逗号分隔（例如：4,5,3）。
5. 只输出最终以逗号分隔的整数结果。不要任何额外的文字、解释或标点符号。如果无法识别任何人脸，请只输出：{utils.NULL_TEXT}"""


def _analyze_image(base64: str) -> str:
    response = (
        utils.ai.chat.completions.create(
            model=config.SATISFACTION_SURVEY_VISUAL_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64}"},
                        },
                    ],
                }
            ],
            temperature=config.MODEL_TEMPERATURE,
            max_tokens=config.MODEL_MAX_TOKENS,
            timeout=config.MODEL_TIMEOUT,
        )
        .choices[0]
        .message
    )
    if response.content:
        return response.content
    raise utils.UnexpectedResponseError(response)


def capture_expressions():
    frame = utils.take_photo(config.CAMERA_INDEX)
    base64 = utils.image_to_base64(frame)
    res = _analyze_image(base64)

    scores = []
    if res == utils.NULL_TEXT:
        return
    for r in res.strip().split(","):
        s = r.strip()
        if s.isdigit():
            x = int(s)
            if 1 <= x <= 5:
                scores.append(str(x))
        else:
            raise utils.UnexpectedResponseError(res)
    print(f"= {'+'.join(scores)}")
