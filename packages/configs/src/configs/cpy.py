import os
from typing import Any, Dict, Type, Optional

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

import os
from typing import Any, Dict, Type
from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


# 1. 模拟远程配置中心客户端 SDK/API 接口
def fetch_remote_config(server_url: str, app_id: str, secret_token: str = "") -> Dict[str, Any]:
    """模拟根据本地/环境变量获取到的连接信息，去远程配置中心获取数据"""
    print(f"--> [Remote] Connecting to {server_url} (App: {app_id}, Token: {secret_token})...")

    # 这里是根据连接参数请求远程接口的实际逻辑
    if "nacos" in server_url or "consul" in server_url or "http" in server_url:
        return {
            "app_name": "RemoteApp",
            "db_port": 3306,
            "max_connections": 200,
        }
    return {}


# 2. 自定义远程配置源（依赖本地配置/环境变量）
def _resolve_remote_connection_info() -> tuple[str, str, str]:
    """
    先从环境变量或本地 .env 文件中提取远程连接信息。
    这里使用轻量级的临时 Settings 实例来准确按“环境变量 > .env”获取连接配置。
    """

    class RemoteConnectionConfig(BaseSettings):
        remote_url: str = Field(default="http://localhost:8500", alias="REMOTE_URL")
        app_id: str = Field(default="default_service", alias="APP_ID")
        remote_token: str = Field(default="", alias="REMOTE_TOKEN")

        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore",
        )

    conn_config = RemoteConnectionConfig()
    return conn_config.remote_url, conn_config.app_id, conn_config.remote_token


class RemoteSettingsSource(PydanticBaseSettingsSource):
    """
    自定义远程配置源：
    在内部先解析出连接配置（如 URL/Token），再加载远程数据。
    """

    def __init__(self, settings_cls: Type[BaseSettings]):
        super().__init__(settings_cls)
        # 初始化时，先拉取连接远程配置中心所需的必要参数
        self.remote_url, self.app_id, self.token = _resolve_remote_connection_info()

    def get_field_value(self, field: Any, field_name: str):
        return None, field_name, False

    def __call__(self) -> Dict[str, Any]:
        """执行远程加载逻辑"""
        # 如果没有配置远程 URL，可以降级跳过
        if not self.remote_url:
            return {}

        try:
            return fetch_remote_config(
                server_url=self.remote_url,
                app_id=self.app_id,
                secret_token=self.token,
            )
        except Exception as e:
            print(f"[Warning] 远程配置获取失败, 降级使用本地配置: {e}")
            return {}


# 3. 主配置类
class Settings(BaseSettings):
    server_context_path: Optional[str] = Field(default='', description='服务上下文')
    # --- 远程配置中心的连接参数 (可来自环境变量或 .env) ---
    remote_url: str = Field(default="http://localhost:8500", description="远程配置中心地址")
    app_id: str = Field(default="my_service", description="应用标识")
    remote_token: str = Field(default="", description="访问令牌")

    # --- 业务配置项 ---
    app_name: str = Field(default="DefaultApp", description="应用名称")
    db_host: str = Field(default="localhost", description="数据库主机")
    db_port: int = Field(default="5432", description="数据库端口")
    max_connections: int = Field(default=100, description="最大连接数")

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        case_sensitive=False,
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
        # 1. 实例化远程配置源（它会在内部自动读取环境变量和 .env 获取远程连接参数）
        remote_settings = RemoteSettingsSource(settings_cls)

        # 2. 获取优先级判断标志（从环境变量或默认从 .env）
        remote_first = os.getenv("REMOTE_FIRST", "false").lower() in ("true", "1", "yes")

        # 3. 按指定的优先级顺序返回配置源
        if remote_first:
            # 环境变量 > 远程配置中心 > 本地 .env 文件 > 默认值
            return (
                init_settings,
                env_settings,
                remote_settings,
                dotenv_settings,
                file_secret_settings,
            )
        else:
            # 环境变量 > 本地 .env 文件 > 远程配置中心 > 默认值
            return (
                init_settings,
                env_settings,
                dotenv_settings,
                remote_settings,
                file_secret_settings,
            )


settings = Settings()
