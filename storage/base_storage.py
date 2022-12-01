import os


class BaseStorage(object):
    def __init__(self, config):
        self.reactions_dir = config.reactions_dir
        self.main_dir_step = config.main_dir_step
        self.subdir_step = config.subdir_step

    def get_filepath(self, filename):
        page, extension = filename.split('.')
        main_dir = self.get_dir(int(page), self.main_dir_step)
        subdir = self.get_dir(int(page), self.subdir_step)
        return os.path.join(
            self.reactions_dir,
            main_dir,
            subdir,
            filename,
        )

    def get_dir(self, number, step):
        lower_bound = 1 if number <= step else (number - 1) // step * step + 1
        upper_bound = step if number <= step else lower_bound + step - 1
        return '{0}-{1}'.format(lower_bound, upper_bound)
