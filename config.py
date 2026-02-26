import json

from classes import DbConfig
from logger import get_logger


logger = get_logger(__name__)

data_file = "stat-data.json"

with open(data_file, "r", encoding="utf-8") as f:
    config_data = json.load(f)

db_data = DbConfig(
    admin=config_data["database"]["admin"],
    password=config_data["database"]["password"],
    host=config_data["database"]["host"],
    port=int(config_data["database"]["port"]),
    db_name=config_data["database"]["db_name"],
)

bot_token = config_data["bot_token"]
admin = config_data["admin_id"]