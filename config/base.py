from pydantic import BaseSettings


class BaseConfig(BaseSettings):
    class Config:
        env_file = '.env'
