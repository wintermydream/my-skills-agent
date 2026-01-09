import anthropic
import os

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

try:
    print(dir(client))
    # Check if 'models' attribute exists
    if hasattr(client, 'models'):
        print("Models attribute found, attempting to list...")
        models = client.models.list()
        for model in models.data:
            print(f"- {model.id}")
    else:
        print("Models attribute NOT found")
except Exception as e:
    print(f"Error: {e}")
