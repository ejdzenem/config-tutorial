import os
from pathlib import Path

import yaml
from string import Template
from typing import Type, Tuple, Dict, Any
from pydantic import Field, BaseModel, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource


def _substitute_env_variables(template: str) -> str:
    try:
        substitute = Template(template).substitute(os.environ)
        return substitute
    except KeyError as e:
        raise KeyError(f"Missing env var for template: {e.args[0]}")
    except Exception as e:
        raise RuntimeError(f"Template substitution error: {e}")


# def _deep_merge(self, base: Dict[Any, Any], override: Dict[Any, Any]) -> Dict[Any, Any]:
#     result = base.copy()
#     for key, value in override.items():
#         if isinstance(value, dict) and key in result and isinstance(result[key], dict):
#             result[key] = self._deep_merge(result[key], value)
#         else:
#             result[key] = value
#     return result


def yaml_config_settings_source() -> dict:
    """
    Loads configuration from a YAML file as a fallback source.
    The YAML file path can itself be set via an environment variable.
    """
    app_dir_dir = Path(__file__).parent.parent
    config_path = app_dir_dir / os.getenv("CONFIG_PATH", "config/default_conf.yaml")
    try:
        with open(config_path, 'r') as f:
            raw = f.read()
        substituted = _substitute_env_variables(raw)
        return yaml.safe_load(substituted)
    except FileNotFoundError:
        raise FileNotFoundError(f"Missing config file: {config_path}")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"YAML parsing error: {e}")
    except Exception as e:
        raise RuntimeError(f"Error loading config: {e}")


class App(BaseModel):
    name: str
    environment: str


class Database(BaseModel):
    host: str
    port: int
    username: str
    password: str
    db_name: str
    driver: str = "postgresql"
    connection_str: str = Field(default="", init=False)  # set upon initialization

    def __init__(self, **data):
        super().__init__(**data)
        self.connection_str = f"{self.driver}://{self.username}:{self.password}@{self.host}:{self.port}/{self.db_name}"


class TableNames(BaseModel):
    input_table: str
    output_table: str


class DataPaths(BaseModel):
    input_path: str
    output_path: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter='__',
        env_file=f"{Path(__file__).parent.parent}/.env" # this is ugly make it better
    )  # this sets the delimiter for nested env vars

    app: App
    database: Database
    table_names: TableNames
    data_paths: DataPaths
    filter_values: list[str]

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: Type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple:  # in here you can define the settings sources, i.e. change the default order and add custom sources
        return (
            init_settings,  # dont know what this does
            env_settings,  # if you want dotenv here, just add it
            dotenv_settings,
            yaml_config_settings_source  # this is custom source we defined - i.e. read from the file
        )


def load_settings() -> Settings:
    """
    Loads and validates configuration by instantiating the Config class.
    Environment variables with the proper prefixes (e.g., DATABASE__HOST, TABLE_NAMES__OUTPUT_TABLE, etc.)
    will override values from the YAML configuration.
    """
    try:
        config = Settings()
        return config
    except ValidationError as e:
        raise RuntimeError(f"Configuration validation error: {e}")
