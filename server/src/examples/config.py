import os

from pydantic import BaseModel
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict
from typing_extensions import Type
from configs import SingleTomlMultiEnvSettingsSource


class App(BaseModel):
    id: int
    name: str


class Setting(BaseSettings):
    app: App
    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        case_sensitive=False,
        toml_file="config/app.toml",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # 实例化自定义的单文件多环境 TOML 配置源
        toml_settings = SingleTomlMultiEnvSettingsSource(settings_cls, env=os.getenv('ENV').lower())

        # 保持优先级顺序：
        # 1. 代码初始化参数 (init_settings)
        # 2. 系统环境变量 (env_settings) -> 最高覆盖权
        # 3. 本地 .env 文件 (dotenv_settings)
        # 4. 单文件多环境 TOML 配置 (toml_settings)
        # 5. 模型默认值
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            toml_settings,
            file_secret_settings,
        )
