import configparser
from typing import Optional


class BaseSection:
    def __init__(self, parent: str):
        self.parent = parent

    def __getattr__(self, attr: str) -> str:
        # parent was invalid, hence this one is invalid too
        return f'{self.parent.upper()}.{attr.upper()}'


class Section(BaseSection):
    def __init__(self, parent: str, section: configparser.SectionProxy):
        super().__init__(parent)
        self.section = section

    def __getattr__(self, attr: str) -> str:
        try:
            return self.section[attr]
        except KeyError:
            # FIXME: log this error
            # parent was valid, but this one isn't
            return f'{self.parent}.{attr.upper()}'


class Match:
    def __init__(self, config: Optional[configparser.ConfigParser] = None):
        if config is None:
            self.config = configparser.ConfigParser
        else:
            self.config = config

    def __getattr__(self, attr: str) -> BaseSection:
        try:
            value = self.config[attr]
        except KeyError:
            # FIXME: log this error
            return BaseSection(attr)
        else:
            return Section(attr, value)

    def load_from_file(self, filename: str) -> None:
        self.config = configparser.ConfigParser()
        self.config.read(filename)
