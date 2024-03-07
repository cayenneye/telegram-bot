import json
import pathlib
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from zoneinfo import ZoneInfo

__all__ = (
    'LoggingConfig',
    'RedisConfig',
    'SentryConfig',
    'Config',
    'load_config_from_file_path',
    'load_commands_from_file',
    'parse_config',
    'load_role_play_actions_from_file',
)

from aiogram.types import BotCommand
from pydantic import TypeAdapter

from models import RolePlayAction


@dataclass(frozen=True, slots=True)
class LoggingConfig:
    level: int


@dataclass(frozen=True, slots=True)
class RedisConfig:
    host: str
    port: int
    db: int


@dataclass(frozen=True, slots=True)
class SentryConfig:
    is_enabled: bool
    dsn: str
    traces_sample_rate: float


@dataclass(frozen=True, slots=True)
class CloudinaryConfig:
    cloud_name: str
    api_key: str
    api_secret: str


@dataclass(frozen=True, slots=True)
class Config:
    logging: LoggingConfig
    cloudinary: CloudinaryConfig
    telegram_bot_token: str
    redis: RedisConfig
    sentry: SentryConfig
    server_api_base_url: str
    main_chat_id: int | str
    timezone: ZoneInfo


def parse_config(config: Mapping) -> Config:
    return Config(
        logging=LoggingConfig(
            level=config['logging']['level'],
        ),
        cloudinary=CloudinaryConfig(
            cloud_name=config['cloudinary']['cloud_name'],
            api_key=config['cloudinary']['api_key'],
            api_secret=config['cloudinary']['api_secret'],
        ),
        telegram_bot_token=config['telegram_bot']['token'],
        redis=RedisConfig(
            host=config['redis']['host'],
            port=config['redis']['port'],
            db=config['redis']['db'],
        ),
        sentry=SentryConfig(
            is_enabled=config['sentry']['is_enabled'],
            dsn=config['sentry']['dsn'],
            traces_sample_rate=config['sentry']['traces_sample_rate'],
        ),
        server_api_base_url=config['server_api']['base_url'],
        main_chat_id=config['main_chat_id'],
        timezone=ZoneInfo(config['timezone']),
    )


def load_config_from_file_path(file_path: pathlib.Path) -> Config:
    config_text = file_path.read_text(encoding='utf-8')
    config = tomllib.loads(config_text)
    return parse_config(config)


def load_commands_from_file(file_path: pathlib.Path) -> list[BotCommand]:
    commands_text = file_path.read_text(encoding='utf-8')
    commands = json.loads(commands_text)
    type_adapter = TypeAdapter(list[BotCommand])
    return type_adapter.validate_python(commands)


def load_role_play_actions_from_file(
        file_path: pathlib.Path,
) -> list[RolePlayAction]:
    actions_text = file_path.read_text(encoding='utf-8')
    type_adapter = TypeAdapter(list[RolePlayAction])
    return type_adapter.validate_json(actions_text)
