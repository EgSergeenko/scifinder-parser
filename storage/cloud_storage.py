import os
from pathlib import Path

import yadisk

from storage.base_storage import BaseStorage


class CloudStorage(BaseStorage):
    def __init__(self, config):
        super().__init__(config)
        self.storage = yadisk.YaDisk(token=config.storage_token)
        if not self.storage.is_dir(self.reactions_dir):
            self.storage.mkdir(self.reactions_dir)

    def upload(self, src_filepath):
        filename = os.path.basename(src_filepath)
        dst_filepath = self.get_filepath(filename)
        for dirname in reversed(Path(dst_filepath).parents[:-2]):
            if not self.storage.is_dir(dirname):
                self.storage.mkdir(dirname)
        if self.storage.is_file(dst_filepath):
            self.storage.remove(dst_filepath)
        self.storage.upload(src_filepath, dst_filepath)
        return dst_filepath
