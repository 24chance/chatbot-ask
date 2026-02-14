import time, os
from huggingface_hub import InferenceClient
from gradio_client import Client


import requests

SPACE_URL = "https://chanceown-chatbot.hf.space/run/predict"

def ask_model_via_api(prompt):
    try:
        response = requests.post(
            SPACE_URL,
            json={"data": [prompt]},
            timeout=120
        )
        print(response)

        client = Client("chanceown/chatbot")
        result = client.predict(
            question=prompt,
            api_name="/predict"
        )
        print(result)
        return result

    except Exception as e:
        print("SPACE ERROR:", e)
        return "AI server is busy. Try again."