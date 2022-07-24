import luigi
import os
import shutil
import json
import time
import random

import pandas as pd

from .parsing import KremlinArticleParser, KremlinScrapper
from .create_dataset import create_ner_dataset
from .parsing_state_control import KremlinParsingFileStateManager

CURRENT_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_DATA_DIRECTORY = os.path.abspath(os.path.join(CURRENT_FILE_DIR, "..", "data"))


class MakeDirectoryTask(luigi.Task):
    data_directory_path = luigi.Parameter()

    def run(self):
        if not os.path.exists(self.data_directory_path):
            os.makedirs(self.data_directory_path)

    def output(self):
        return luigi.LocalTarget(self.data_directory_path)


class CollectKremlinUrlsTask(luigi.Task):
    parsing_state_manager = luigi.Parameter()
    update_mode = luigi.Parameter()

    def run(self):
        try:
            known_links = (
                self.parsing_state_manager.get_all_processed_links()
                if self.update_mode
                else set()
            )
            scraper = KremlinScrapper(
                # записываем результат во временный файл,
                #  чтобы при прерывании процесса не было выполнено условие готовност
                output_path=self.parsing_state_manager.temp_links_collection_output_file_path,
                scrapping_log_file_path=self.parsing_state_manager.page_log_file_path,
                update_mode=self.update_mode,
                known_links=known_links,
            )
            scraper.run()
        # при update_mode=False ошибка может возникнуть уже при инициализации,
        # если при предыдущем запуске итерация завершилась,
        # а копирование файла - нет
        except StopIteration:
            pass

        # ошибка SameFileError исключена, так как при наличии выходного файла задание не запустится
        shutil.copy(
            self.parsing_state_manager.temp_links_collection_output_file_path,
            self.parsing_state_manager.links_collection_output_file_path,
        )

    def output(self):
        return luigi.LocalTarget(
            self.parsing_state_manager.links_collection_output_file_path
        )

    def requires(self):
        return [
            MakeDirectoryTask(
                os.path.dirname(self.parsing_state_manager.temp_child_directory_path)
            )
        ]


class ParseKremlinArticleTask(luigi.Task):
    content_url = luigi.Parameter()
    output_file_path = luigi.Parameter()

    def run(self):
        parser = KremlinArticleParser()
        parsing_result = parser(self.content_url)
        save_path = self.output_file_path
        with open(save_path, "w") as f:
            json.dump(parsing_result, f, ensure_ascii=False)
        time.sleep(random.randint(1, 3))

    def requires(self):
        return [MakeDirectoryTask(os.path.dirname(self.output_file_path))]

    def output(self):
        return luigi.LocalTarget(self.output_file_path)


class AllArticlesAreParsed(luigi.Target):
    def __init__(self, parsing_state_manager):
        self.parsing_state_manager = parsing_state_manager

    def exists(self):
        if not os.path.exists(
            self.parsing_state_manager.links_collection_output_file_path
        ):
            return False
        urls = self.parsing_state_manager.get_scrapped_links()
        if all(
            [
                os.path.exists(
                    self.parsing_state_manager.get_path_to_save_parsing_output(url)
                )
                for url in urls
            ]
        ):
            return True
        return False


class CollectDataTask(luigi.Task):
    parsing_state_manager = luigi.Parameter()
    update_mode = luigi.Parameter()

    def run(self):
        urls = self.parsing_state_manager.get_scrapped_links()
        yield [
            ParseKremlinArticleTask(
                content_url=url,
                output_file_path=self.parsing_state_manager.get_path_to_save_parsing_output(
                    url
                ),
            )
            for url in urls
        ]

    def requires(self):
        return CollectKremlinUrlsTask(
            parsing_state_manager=self.parsing_state_manager,
            update_mode=self.update_mode,
        )

    def output(self):
        return AllArticlesAreParsed(self.parsing_state_manager)


class ContainsLatestArticleTarget(luigi.target.Target):
    def __init__(self, parsing_manager: KremlinParsingFileStateManager):
        super().__init__()
        self.parsing_manager = parsing_manager

    def exists(self):
        if not self.parsing_manager.prev_parsing_output_exists():
            return False
        if self.parsing_manager.new_links_exist():
            return False
        return True


class CreateOrUpdateNerDatasetTask(luigi.Task):
    data_directory = luigi.Parameter(default=DEFAULT_DATA_DIRECTORY)

    def __init__(self):
        super().__init__()
        self.parsing_state_manager = KremlinParsingFileStateManager(self.data_directory)
        self.update_mode = self.parsing_state_manager.prev_parsing_output_exists()

    def run(self):
        df = create_ner_dataset(self.parsing_state_manager.temp_child_directory_path)
        if self.update_mode:
            prev_df = pd.read_csv(self.parsing_state_manager.output_file_path)
            df = pd.concat([prev_df, df])
        df.to_csv(self.parsing_state_manager.output_file_path)

    def output(self):
        return ContainsLatestArticleTarget(self.parsing_state_manager)

    def requires(self):
        return [
            MakeDirectoryTask(self.parsing_state_manager.data_directory),
            MakeDirectoryTask(self.parsing_state_manager.temp_child_directory_path),
            CollectDataTask(
                parsing_state_manager=self.parsing_state_manager,
                update_mode=self.update_mode,
            ),
        ]
