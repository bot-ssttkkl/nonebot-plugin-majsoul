from ssttkkl_nonebot_utils.config_loader import (
    BaseSettings,
    load_conf
)


class Config(BaseSettings):

    majsoul_query_timeout: float = 15.0

    majsoul_username: str = ""
    majsoul_password: str = ""

    majsoul_font: str = ""
    majsoul_font_path: str = ""

    majsoul_send_aggregated_message: bool = True

    majsoul_send_link: bool = False

    # Paifuya player_records API key. Loaded from
    # MAJSOUL_PAIFUYA_API_KEY in the NoneBot .env file.
    majsoul_paifuya_api_key: str = ""

    # AI锐评

    majsoul_ai_comment: bool = True

    majsoul_ai_api_base: str = ""

    majsoul_ai_api_key: str = ""

    majsoul_ai_model: str = ""

    majsoul_ai_timeout: int = 60
    

    class Config:
        extra = "ignore"


conf = load_conf(Config)
