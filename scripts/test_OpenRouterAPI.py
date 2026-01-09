from openai import OpenAI

# 使用 OpenRouter 的 API 端点和密钥
client = OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1"
)

try:
    response = client.chat.completions.create(
        model="xiaomi/mimo-v2-flash:free", #  anthropic/claude-3.5-haiku
        max_tokens=1000,
        temperature=0,
        messages=[
            {"role": "system", "content": "你是一个乐于助人且简洁的AI助手。"},
            {"role": "user", "content": "请用一句话解释天空为什么是蓝色的。"}
        ]
    )
    print(response.choices[0].message.content)
except Exception as e:
    print(f"出错了: {e}")