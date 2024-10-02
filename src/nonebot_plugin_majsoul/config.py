from ssttkkl_nonebot_utils.config_loader import BaseSettings, load_conf


class Config(BaseSettings):
    majsoul_query_timeout: float = 15.0

    majsoul_username: str = ""
    majsoul_password: str = ""

    majsoul_font: str = ""
    majsoul_font_path: str = ""

    majsoul_send_aggregated_message: bool = True

    class Config:
        extra = "ignore"


conf = load_conf(Config)
