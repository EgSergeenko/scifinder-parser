import os
from pathlib import Path

from storage.base_storage import BaseStorage


class LocalStorage(BaseStorage):
    def __init__(self, config):
        super().__init__(config)
        if not os.path.isdir(config.reactions_dir):
            os.mkdir(config.reactions_dir)

    def save(self, filename, lines):
        filepath = self.get_filepath(filename)
        for dirname in reversed(Path(filepath).parents[:-2]):
            if not os.path.isdir(dirname):
                os.mkdir(dirname)
        with open(filepath, 'w') as output_file:
            for line in lines:
                output_file.write('{line}{newline}'.format(
                        line=line, newline='\n',
                    ),
                )
        return filepath
