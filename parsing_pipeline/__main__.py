import luigi
from .luigi_tasks import CreateNerDataset


if __name__ == '__main__':
    luigi.run()