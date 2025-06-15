import yaml

def load_config(config_path="config.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_order_mode(config_path="config.yaml"):
    config = load_config(config_path)
    return config.get("order", {}).get("mode", "dummy").lower()
