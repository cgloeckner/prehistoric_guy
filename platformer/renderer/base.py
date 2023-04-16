from abc import ABC, abstractmethod


class Renderer(ABC):
    @abstractmethod
    def update(self, elapsed_ms: int) -> None:
        ...

    @abstractmethod
    def draw(self) -> None:
        ...
