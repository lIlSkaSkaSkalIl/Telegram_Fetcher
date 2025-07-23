import json
from pathlib import Path

STATE_FILE = Path(__file__).resolve().parent.parent / "config/user_state.json"
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_user_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user_state(state_dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state_dict, f, indent=4)

def set_user_state(user_id, state):
    state_dict = load_user_state()
    state_dict[str(user_id)] = state
    save_user_state(state_dict)

def get_user_state(user_id):
    return load_user_state().get(str(user_id), None)

def clear_user_state(user_id):
    state_dict = load_user_state()
    if str(user_id) in state_dict:
        del state_dict[str(user_id)]
        save_user_state(state_dict)
