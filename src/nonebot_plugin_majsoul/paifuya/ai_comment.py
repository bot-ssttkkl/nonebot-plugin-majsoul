from openai import AsyncOpenAI

from ..config import conf


client = AsyncOpenAI(
    base_url=conf.majsoul_ai_api_base,
    api_key=conf.majsoul_ai_api_key,
    timeout=conf.majsoul_ai_timeout
)


async def generate_ai_comment(stats_text: str):

    if not conf.majsoul_ai_comment:
        return ""

    if not conf.majsoul_ai_api_key:
        return ""

    prompt = f"""
你是一个雀魂猫娘。

你需要根据玩家的雀魂统计数据进行锐评。

要求：

- 说话要像猫娘一样
- 客观分析数据
- 有节目效果
- 可以玩梗
- 不要太长
- 80字以内
- 不要回复很多换行符
- 禁止markdown+富文本
- 禁止使用**加粗文本
- 不要辱骂群友
- 重点分析打法问题
- 要给出问题的解决方案

以下是玩家数据：

{stats_text}
"""

    try:

        response = await client.chat.completions.create(
            model=conf.majsoul_ai_model,
            messages=[
                {
                    "role": "system",
                    "content": "你是雀魂锐评机器人"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=1.3,
            max_tokens=1000
        )

        content = response.choices[0].message.content

        if not content:
            return ""

        return content.strip()

    except Exception as e:
        return f"AI锐评失败：{e}"