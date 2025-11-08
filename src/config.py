import json

_fp = open("config.json", "r", encoding="u8")
text = _fp.read()
_fp.close()
config: dict = json.loads(text) if text.startswith("{") else {}


def save_config():
    global config
    fp = open("config.json", "w", encoding="u8")
    fp.write(json.dumps(config))
    fp.close()
