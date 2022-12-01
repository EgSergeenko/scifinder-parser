from config.base import BaseConfig


class BaseStorageConfig(BaseConfig):
    reactions_dir: str = 'reactions'
    main_dir_step = 10000
    subdir_step = 100


class LocalStorageConfig(BaseStorageConfig):
    pass


class CloudStorageConfig(BaseStorageConfig):
    reactions_dir: str = '/reactions'
    storage_token: str


class StorageConfig(BaseConfig):
    local_storage_config: LocalStorageConfig
    cloud_storage_config: CloudStorageConfig


def get_storage_config():
    return StorageConfig(
        local_storage_config=LocalStorageConfig(),
        cloud_storage_config=CloudStorageConfig(),
    )
