import pathlib


class DataPath(object):
    def __init__(self, root: pathlib.Path):
        self.root = root
        self._ensure(self.level())
        self._ensure(self.language())

    @staticmethod
    def _ensure(directory: pathlib.Path):
        if not directory.exists():
            directory.mkdir()

    def _combine(self, directory: str, filename: str, extension: str) -> pathlib.Path:
        path = self.root / directory
        if filename != '':
            path /= f'{filename}.{extension}'
        return path

    def level(self, filename: str = '') -> pathlib.Path:
        return self._combine('levels', filename, 'xml')

    def language(self, filename: str = '') -> pathlib.Path:
        return self._combine('language', filename, 'ini')
