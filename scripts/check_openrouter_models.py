from openai import OpenAI
import json

client = OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1"
)

try:
    response = client.models.list()
    # List all free models
    free_models = [m.id for m in response.data if ':free' in m.id]
    print("Available FREE models on OpenRouter:")
    for m_id in sorted(free_models):
        print(f"- {m_id}")
    
    # Also list anthropic models specifically
    anthropic_models = [m.id for m in response.data if 'anthropic' in m.id]
    print("\nAvailable Anthropic models on OpenRouter:")
    for m_id in sorted(anthropic_models):
        print(f"- {m_id}")
except Exception as e:
    print(f"Error listing models: {e}")
