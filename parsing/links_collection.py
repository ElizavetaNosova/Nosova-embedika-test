from abc import ABC, abstractmethod
import math
from typing import List
import time
from bs4 import BeautifulSoup

from links_collection_output_manager import FileLinksOutputManager
from menu_page_link_manager import MenuPageLinkManager
from requests_wrapper import RequestsWrupper


class AbstractLinksScrapper(ABC):
    def __init__(self, output_path: str, start_link=None,
                 output_type='file',
                 retry_limit: int = 3,
                 write_limit: int = math.inf,
                 sleeping_time=3):
        if output_type == 'file':
            self.output_manager = FileLinksOutputManager(output_path)
        else:
            raise NotImplementedError()
        self.writing_limit = write_limit
        self.retry_limit = retry_limit
        self.sleeping_time = sleeping_time
        self.done = False

    def run(self):
        while not self.done and len(self.output_manager) < self.writing_limit:
            self.step()

    def step(self):
        html = self.get_next_html()
        links = self.extract_unknown_links(html)
        unknown_links = self.output_manager.get_unknown_only(links)

        num_trials = 0
        while not unknown_links and num_trials < self.retry_limit:
            time.sleep(self.sleeping_time)
            num_trials += 1
            html = self.retry_get_next_html()
            unknown_links = self.extract_unknown_links(html)

        if unknown_links:
            self.output_manager.write_batch(unknown_links)
        else:
            # Если мы не смогли выявить новые ссылки, считаем, что дошли до конца
            self.done = True

    @abstractmethod
    def get_next_html(self) -> str:
        raise NotImplementedError()

    def retry_get_next_html(self) -> str:
        return self.get_next_html()

    @abstractmethod
    def extract_links(self, html: str) -> List[str]:
        raise NotImplementedError()

    def extract_unknown_links(self, html: str) -> List[str]:
        links = self.extract_links(html)
        return self.output_manager.get_unknown_only(links)


class PresidentScrapper(AbstractLinksScrapper):
    first_page_idx = 1

    def __init__(self,
                 output_path: str,
                 output_type='file',
                 retry_limit: int = 3,
                 write_limit: int = math.inf,
                 sleeping_time=3,
                 chapter='events/president/letters'):
        super().__init__(output_path=output_path,
                         output_type=output_type,
                         retry_limit=retry_limit,
                         write_limit=write_limit,
                         sleeping_time=sleeping_time)
        link_template = self.get_link_template(chapter)
        self.chapter = chapter
        self.link_manager = MenuPageLinkManager(link_template,
                                                first_page_idx=self.first_page_idx)
        self.requests_wrapper = RequestsWrupper()

    def get_next_html(self):
        next_link = self.link_manager.get_next_page_link()
        return self.requests_wrapper.get_html(next_link)

    def retry_get_next_html(self):
        # toDo учитывать ситуацию, когда по ошибке запрашивают нулевую страницу вместо первой
        current_link = self.link_manager.get_current_page_link()
        time.sleep(10)
        return self.requests_wrapper.get_html(current_link)

    def extract_links(self, html):
        soup = BeautifulSoup(html)
        href_children = soup.findAll(href=True)
        links = []
        for child in href_children:
            link = child['href']
            if self.chapter in link:
                links.append(link)

        return links

    def get_link_template(self, chapter: str):
        return 'http://kremlin.ru/' + chapter.strip('/') + '/page/{}'