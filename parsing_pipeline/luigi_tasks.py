import luigi
import os
import shutil
import re
import json
import time
import random

from parsing import KremlinArticleParser, KremlinScrapper
from create_dataset import create_ner_dataset

CURRENT_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_DATA_DIRECTORY = os.path.abspath(os.path.join(CURRENT_FILE_DIR,"..", "data"))
DEFAULT_TEMP_DATA_DIRECTORY = os.path.join(DEFAULT_DATA_DIRECTORY, 'temp')


class MakeDirectoryTask(luigi.Task):
    data_directory_path = luigi.Parameter(default=DEFAULT_TEMP_DATA_DIRECTORY)

    def run(self):
        if not os.path.exists(self.data_directory_path):
            os.makedirs(self.data_directory_path)

    def output(self):
        return luigi.LocalTarget(self.data_directory_path)



class CollectKremlinUrlsTask(luigi.Task):
    output_file_path = luigi.Parameter(default=os.path.join(DEFAULT_TEMP_DATA_DIRECTORY, 'kremlin_urls.txt'))

    def run(self):
        filepath_without_extention, extention = os.path.splitext(self.output_file_path)
        temp_output_filepath = filepath_without_extention+'_temp'+extention
        try:
            scraper = KremlinScrapper(output_path=temp_output_filepath)
            scraper.run()
        # если предыдущий запуск собрал все ссылки, но процесс упал раньше перемещения файла
        except StopIteration:
            pass

        try:
            shutil.copy(temp_output_filepath, self.output_file_path)
        except shutil.SameFileError:
            pass

    def output(self):
        return luigi.LocalTarget(self.output_file_path)

    def requires(self):
        return [MakeDirectoryTask(os.path.dirname(self.output_file_path))]



class ParseKremlinArticleTask(luigi.Task):
    data_directory_path = luigi.Parameter(default=DEFAULT_TEMP_DATA_DIRECTORY)
    content_url = luigi.Parameter()

    def __init__(self, data_directory_path, content_url):
        super().__init__(data_directory_path=data_directory_path, content_url=content_url)
        base_file_name = re.sub('/', '_',
            re.sub(re.escape('http://'), '', self.content_url)
        )
        self.output_file_path = os.path.join(self.data_directory_path, base_file_name+'.json')


    def run(self):
        parser = KremlinArticleParser()
        parsing_result = parser(self.content_url)
        with open(self.output_file_path, 'w') as f:
            json.dump(parsing_result, f, ensure_ascii=False)
        time.sleep(random.randint(1,3))


    def requires(self):
        return [MakeDirectoryTask(self.data_directory_path)]

    def output(self):
        return luigi.LocalTarget(self.output_file_path)

class CreateNerDataset(luigi.Task):
    json_directory = luigi.Parameter()
    output_path = luigi.Parameter()

    def run(self):
        df = create_ner_dataset(self.json_directory)
        df.to_csv(self.output_path, index=False)

    def output(self):
        return luigi.LocalTarget(self.output_path)

    def requires(self):
        return [MakeDirectoryTask(os.path.dirname(self.output_path))]


class ParsingTask(luigi.WrapperTask):
    data_path = luigi.Parameter(default=DEFAULT_DATA_DIRECTORY)

    def requires(self):
        temp_data_path = os.path.join(self.data_path, 'temp')
        link_collection_output_path = os.path.join(temp_data_path, 'kremlin_urls.txt')

        yield CollectKremlinUrlsTask(link_collection_output_path)
        with open(link_collection_output_path) as f:
            urls = [i.strip() for i in f.readlines() if i.strip()]
        yield [ParseKremlinArticleTask(content_url=url, data_directory_path=temp_data_path) for url in urls]
        ner_dataset_path = os.path.join(self.data_path, 'kremlin_ner_dataset.csv')
        yield CreateNerDataset(json_directory=temp_data_path, output_path=ner_dataset_path)


if __name__ == '__main__':
    luigi.run()




