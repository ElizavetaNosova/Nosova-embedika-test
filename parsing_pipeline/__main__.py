import luigi
from .luigi_tasks import CreateOrUpdateNerDatasetTask


if __name__ == "__main__":
    luigi.run()
