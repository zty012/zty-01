import json

try:
    _fp = open("settings.json", "r", encoding="u8")
    text = _fp.read()
    _fp.close()
except OSError:
    text = "{}"
    _fp = open("settings.json", "w", encoding="u8")
    _fp.write(text)
    _fp.close()
settings: dict = json.loads(text) if text.startswith("{") else {}


def save_settings():
    global settings
    fp = open("settings.json", "w", encoding="u8")
    fp.write(json.dumps(settings))
    fp.close()
