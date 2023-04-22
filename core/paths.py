import pathlib
from typing import List


class DataPath(object):
    def __init__(self, root: pathlib.Path):
        self.root = root

        self.level_ext = 'xml'
        self.language_ext = 'ini'
        self.tile_ext = 'png'
        self.sprite_ext = 'png'
        self.background_ext = 'png'

        self._ensure(self.level())
        self._ensure(self.language())
        self._ensure(self.tile())
        self._ensure(self.sprite())
        self._ensure(self.background())

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
        return self._combine('levels', filename, self.level_ext)

    def language(self, filename: str = '') -> pathlib.Path:
        return self._combine('language', filename, self.language_ext)

    def tile(self, filename: str = '') -> pathlib.Path:
        return self._combine('tiles', filename, self.tile_ext)

    def sprite(self, filename: str = '') -> pathlib.Path:
        return self._combine('sprites', filename, self.sprite_ext)

    def background(self, filename: str = '') -> pathlib.Path:
        return self._combine('backgrounds', filename, self.background_ext)

    def __call__(self, filename: str, ext: str) -> pathlib.Path:
        return self.root / f'{filename}.{ext}'

    @staticmethod
    def get_files(base: pathlib.Path, ext: str) -> List[str]:
        return sorted([file.stem for file in base.glob(f'*.{ext}') if file.is_file()])

    def all_levels(self) -> List[str]:
        return DataPath.get_files(self.level(), self.level_ext)

    def all_languages(self) -> List[str]:
        return DataPath.get_files(self.language(), self.language_ext)

    def all_tiles(self) -> List[str]:
        return DataPath.get_files(self.tile(), self.tile_ext)

    def all_sprites(self) -> List[str]:
        return DataPath.get_files(self.sprite(), self.sprite_ext)

    def all_backgrounds(self) -> List[str]:
        return DataPath.get_files(self.background(), self.background_ext)
