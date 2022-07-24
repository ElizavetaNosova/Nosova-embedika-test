from abc import ABC, abstractmethod
from typing import List, Set
import os


class AbstractLinksOutputManager(ABC):
    def __init__(self, output_path: str, extra_known_links: Set[str] = set()):
        self.output_path = output_path
        self.lines = extra_known_links
        self.init_storage()

    @abstractmethod
    def __len__(self):
        raise NotImplementedError()

    @abstractmethod
    def write_batch(self, lines: List[str]):
        raise NotImplementedError()

    @abstractmethod
    def get_unknown_only(self, lines: List[str]) -> List[str]:
        raise NotImplementedError()


class FileLinksOutputManager(AbstractLinksOutputManager):
    def init_storage(self):
        # создаем папки (при не обходимости)
        if self.output_path is None:
            return
        dirname = os.path.abspath(os.path.dirname(self.output_path))
        os.makedirs(dirname, exist_ok=True)
        # Если есть залогированные ссылки, добавляем их
        if os.path.exists(self.output_path):
            with open(self.output_path, "r") as f:
                self.lines.update([line.strip() for line in f.readlines()])

    def __len__(self):
        return len(self.lines)

    def write_batch(self, lines: List[str]):
        with open(self.output_path, "a") as f:
            f.writelines([line + "\n" for line in lines])
        self.lines.update(lines)

    def get_unknown_only(self, lines: List[str]) -> List[str]:
        return [line for line in lines if line not in self.lines]
