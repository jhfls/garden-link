from . import config, utils
from typing import Generator


PROMPT_TEMPLATE = """拙政园是江南古典园林的代表作之一，始建于明代，由王献臣建造。园林分为东、中、西三部分，拥有远香堂、香洲、见山楼、梧竹幽居、玉兰堂等众多景点。园林设计体现了文人园林的精髓，蕴含着丰富的文化内涵。

来了一位游客，其背景信息是：
- 对拙政园的了解：{prior_knowledge}
- 可游览时间：{duration}
{preferences_text}

请根据以上信息，制定游览计划。你的回答应包括：
1. 推荐游览的景点（按顺序列出，使用数字序号）
2. 每个景点的简要介绍、选择理由、停留时间
3. 对“文旅中的文学印记”主题的体现，但不直接提及该词汇

切忌：
1. 写标题、欢迎语
2. 重复提示词中的内容
3. 强行升华或拉近距离

请以日常、清晰的语气回答。"""


def _generate_plan(
    prior_knowledge: str, duration: str, preferences: list[str] = []
) -> Generator[str, None, None]:
    preferences_text = ""
    if preferences:
        preferences_text = f"- 游览偏好：{', '.join(preferences)}"
    
    response = utils.ai.chat.completions.create(
        model=config.LANDSCAPE_RECOGNITION_MODEL,
        messages=[
            {
                "role": "user",
                "content": PROMPT_TEMPLATE.format(
                    prior_knowledge=prior_knowledge,
                    duration=duration,
                    preferences_text=preferences_text,
                ),
            }
        ],
        temperature=config.MODEL_TEMPERATURE,
        max_tokens=config.MODEL_MAX_TOKENS * 3,
        timeout=config.MODEL_TIMEOUT,
        stream=True,
    )

    for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            yield content


def ask():
    prior_knowledge = input(
        "您对拙政园有什么了解？可以随便说说您知道的内容："
    )
    if not prior_knowledge:
        prior_knowledge = "没有特别了解"
    duration = ""
    while not duration:
        duration = input("您预计在拙政园逗留多长时间：")
    
    # CLI 模式下也可以询问偏好
    preferences_input = input("您有什么游览偏好吗？（可选）")
    preferences = [p.strip() for p in preferences_input.split("，") if p.strip()] if preferences_input else []
    
    print()
    for chunk in _generate_plan(prior_knowledge, duration, preferences):
        print(chunk, end="", flush=True)
    print()
