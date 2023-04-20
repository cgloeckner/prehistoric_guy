import pathlib


class DataPath(object):
    def __init__(self, root: pathlib.Path = pathlib.Path.cwd()):
        self.root = root = root / 'data'
        self._ensure(self.levels())

    @staticmethod
    def _ensure(directory: pathlib.Path):
        if not directory.exists():
            directory.mkdir()

    def levels(self, filename: str = '') -> pathlib.Path:
        path = self.root / 'levels'
        if filename != '':
            path /= f'{filename}.xml'
        return path
