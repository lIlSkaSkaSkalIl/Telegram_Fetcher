import os
import json

CONFIG_PATH = "/content/colab_fetcher/config/credentials.json"

def load_credentials():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Credential file not found at {CONFIG_PATH}")

    with open(CONFIG_PATH, "r") as file:
        return json.load(file)
