from openai import OpenAI

# 使用 OpenRouter 的 API 端点和密钥
client = OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1"
)

try:
    response = client.chat.completions.create(
        model="meta-llama/llama-3.2-3b-instruct:free",  # 使用另一个免费模型进行最终验证
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


# List Anthropic-managed Skills
skills = client.beta.skills.list(
    source="anthropic",
    betas=["skills-2025-10-02"]
)

for skill in skills.data:
    print(f"{skill.id}: {skill.display_title}")