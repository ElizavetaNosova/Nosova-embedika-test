import os
from abc import ABC, abstractmethod
from typing import List
import pandas as pd
from copy import copy
import re

from .parsing import KremlinArticleParser, KremlinScrapper

class ParsingStateManager(ABC):

    @abstractmethod
    def scrapping_was_aborted(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def new_links_exist(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_all_processed_links(self) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def prev_parsing_output_exists(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_scrapped_links(self) -> List[str]:
        raise NotImplementedError


class ParsingFileStateManager(ParsingStateManager):

   # @property
   # @abstractmethod
    def _output_file_path(self):
        raise NotImplementedError

    def prev_parsing_output_exists(self) -> bool:
        return os.path.exists(self.output_file_path)

    def get_output_file_path(self):
        return copy(self.output_file_path)


class KremlinParsingFileStateManager(ParsingFileStateManager):
    def __init__(self,
                 data_directory,
                 output_filename='kremlin_ner_dataset.csv',
                 temp_child_directory='temp',
                 page_log_filename = 'menu_mage_progress_log.txt',
                 links_collection_output_filename='kremlin_urls.txt',
                 end_scrapping_log='END',
                 url_column = KremlinArticleParser.get_url_field_name()):
        self.data_directory = os.path.abspath(data_directory)
        # файл с собранным датасетом
        self.output_file_path = os.path.join(self.data_directory, output_filename)
        # папка для данных, с использованием которых собирается датасет
        self.temp_child_directory_path = os.path.join(self.data_directory, temp_child_directory)
        # логи истории посещений страниц меню
        self.page_log_file_path = os.path.join(self.temp_child_directory_path, page_log_filename)
        # тэг, обозначающий, что скрапинг доработал до конца, а не прервался
        self.end_scrapping_log = end_scrapping_log.strip()
        # колонка ссылки на текст в датасете
        self.url_column = url_column

        # путь к окончательной версии списка собранных новых ссылок, служит таргетом
        self.links_collection_output_file_path = os.path.join(self.temp_child_directory_path,
                                                              links_collection_output_filename)
        filepath_without_extention, extention = os.path.splitext(self.links_collection_output_file_path)
        # файл, куда записываются ссылки в процессе сбора
        self.temp_links_collection_output_file_path = filepath_without_extention+'_temp'+extention



    def scrapping_was_aborted(self)->bool:
        # если не начинали писать логи или закончили парсинг и удалили файл с логами
        if not os.path.exists(self.page_log_file_path):
            return False
        # если файл с логами заканчивается логом завершения скрапинга
        with open(self.page_log_file_path) as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        if lines and lines[-1] == self.end_scrapping_log:
            return False
        return True

    def get_all_processed_links(self)->List[str]:
        if not self.prev_parsing_output_exists():
            return []

        # если файлы перемещались,
        # время создания может быть больше времени модификации
        last_modification_time = max([
            os.path.getmtime(self.output_file_path),
            os.path.getctime(self.output_file_path)
        ])

        # если список ссылок еще не считывали
        # или после последнего считывания что-то изменилось,
        # считываем заново
        if not hasattr(self, '__read_file_modification_time') \
                or self.__read_file_modification_time != last_modification_time:

            df = pd.read_csv(self.output_file_path)
            self._known_links = set(df[self.url_column])
            self.__read_file_modification_time = last_modification_time
        return self._known_links

    def get_scrapped_links(self):
        if not os.path.exists(self.links_collection_output_file_path):
            raise RuntimeError('asking for scrapping result before scrapping')
        with open(self.links_collection_output_file_path) as f:
            return [i.strip() for i in f.readlines() if i.strip() and i.strip() != self.end_scrapping_log]


    def new_links_exist(self) -> bool:
        known_links = self.get_all_processed_links()
        scrapper = KremlinScrapper(known_links=known_links,
                                   # при проверке, есть ли новые ссылки,
                                   # не требуется логировать состояние
                                   output_path=None,
                                   update_mode=True)
        unknown_start_page_links = scrapper.get_unknown_start_page_links()
        print('новые ссылки', unknown_start_page_links)
        return bool(unknown_start_page_links)

    def get_path_to_save_parsing_output(self, content_url):
        base_file_name = re.sub('/', '_', re.sub(re.escape('http://'), '', content_url))
        filepath = os.path.join(self.data_directory, base_file_name) +'.json'
        return filepath