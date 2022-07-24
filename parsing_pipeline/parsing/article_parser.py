from bs4 import BeautifulSoup
import ftfy
import re
from requests import HTTPError
from copy import copy

from .requests_wrapper import RequestsWrapper


class ArticleParser:
    # Значение можно заменять только при наследовании
    _url_field_name: str = "url"

    def __init__(self):
        self.requests = RequestsWrapper(fake_success=False)

    def __call__(self, url):
        result = {self._url_field_name: url}
        try:
            soup = self._get_soup(url)
            result["success"] = True
        except HTTPError:
            result["success"] = False
        else:
            result["title"] = self._get_title(soup)
            result["text"] = self._get_text(soup)
            extra_fields = self._get_extra_fields(soup)
            result.update(extra_fields)
        finally:
            return result

    @classmethod
    def get_url_field_name(cls):
        return copy(cls._url_field_name)

    def _get_extra_fields(self, soup: BeautifulSoup):
        return {}

    def _get_title(self, soup: BeautifulSoup):
        title = soup.title.text
        return self._clean_title(title)

    def _clean_title(self, title: str):
        return self._clean_text(title)

    def _get_text(self, soup: BeautifulSoup):
        paragraphs = self._get_paragraphs(soup)
        clean_paragraphs = [self._clean_paragraph(p) for p in paragraphs]
        return "\n".join([p for p in clean_paragraphs if p.strip()])

    def _clean_paragraph(self, paragraph: str):
        return self._clean_text(paragraph)

    def _get_paragraphs(self, soup):
        return [i.text for i in soup.findAll("p")]

    def _clean_text(self, text):
        text = ftfy.fix_text(text).strip()
        return re.sub("\s+", " ", text)

    def _get_soup(self, url):
        html = self.requests.get_html(url)
        return BeautifulSoup(html)

    @property
    def url_field_name(self):
        return self._url_field_name


class KremlinArticleParser(ArticleParser):
    def _clean_title(self, title: str):
        title = title.split("•")[0]
        return super()._clean_title(title)

    def _get_paragraphs(self, soup: BeautifulSoup):
        all_paragraphs = [
            p.text for p in soup.find(class_="read__internal_content").findAll("p")
        ]
        rubbish_paragraphs = set(
            [p.text for p in soup.find(class_="read__bottommeta").findAll("p")]
        )
        return [p for p in all_paragraphs if p not in rubbish_paragraphs]

    def _get_extra_fields(self, soup: BeautifulSoup):
        tags = soup.find(class_="read__place").text
        return {"tags": tags}
