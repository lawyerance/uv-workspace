import copy
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Type, Any

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, TomlConfigSettingsSource, \
    SettingsConfigDict
from pydantic_settings.sources import ConfigFileSourceType, DEFAULT_PATH
from pydantic_settings.sources.utils import InitState


class _LocalSettings(BaseSettings):
    env: str = "local"

    server_context_path: str

    # class Config:
    #     env_file = ".env.local"
    #     toml_file = "config/app.toml"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        toml_file="config/app.toml",
        extra="ignore",
    )


def deep_merge(dict1: dict, dict2: dict) -> dict:
    """
    递归合并两个字典。
    dict2 中的值会覆盖 dict1 中的非字典值；如果是同名字典，则继续递归合并。
    """
    result = dict1.copy()  # 避免修改原字典
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class _SingleTomlMultiEnvSettingsSource(TomlConfigSettingsSource):

    def __init__(self, settings_cls: type[BaseSettings],
                 env_blocks: tuple[str, ...] = ('local', 'sit', 'beta', 'pro'),
                 env: str | None = None,
                 toml_file: ConfigFileSourceType | None = DEFAULT_PATH,
                 toml_table_header: tuple[str, ...] = (), deep_merge: bool = False,
                 _init_state: InitState | None = None):
        self.env: str = env or 'beta'
        self.env_blocks = env_blocks
        super().__init__(settings_cls, toml_file, toml_table_header, deep_merge, _init_state)

    def _read_file(self, file_path: Path | Traversable) -> dict[str, Any]:
        data = super()._read_file(file_path)
        return self.remove_unselected_env_blocks(data)

    def remove_unselected_env_blocks(self, in_data: dict[str, Any]) -> dict[str, Any]:
        toml_data = in_data.copy()
        env_data = toml_data.pop(self.env, {})
        unselected = set(self.env_blocks) - {self.env}
        for key in unselected:
            toml_data.pop(key, None)
        result = deep_merge(toml_data, env_data)
        return result
