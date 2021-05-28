import pathlib
import random
from os.path import join
from typing import Tuple

import pytest
from helpers import io, stats
from helpers.howlong import HowLong, howlong_flush_stat

FIXTURES_DIR = join(pathlib.Path(__file__).parent.absolute(), "fixtures")

DATASET_NAME = "dataset_03_xl"
DATASET_DIR = join(FIXTURES_DIR, DATASET_NAME)

random.seed(1337)


def get_stat(path: str) -> Tuple[str, str]:  # (iocs, feeds)
    with HowLong("overall"):
        cti_feeds = io.load_feeds(path)
        stat = stats.calculate_all_statistics(cti_feeds, use_tqdm=False)

    return io.write_statistics(None, **stat)


@pytest.fixture(scope="class")
def stat_fixture():
    return get_stat(join(DATASET_DIR, "feeds"))


@pytest.fixture(scope="session", autouse=True)
def howlong_flush():
    yield
    howlong_flush_stat()


class TestStatisticCalculation:
    # ! Do not use this for testing purpose !
    def _test_write_stat(self, stat_fixture):
        with open(join(DATASET_DIR, "stat", "iocs.csv"), "w") as f:
            f.writelines(stat_fixture[0])

        with open(join(DATASET_DIR, "stat", "feeds.csv"), "w") as f:
            f.writelines(stat_fixture[1])

    def test_iocs_stat(self, stat_fixture):
        iocs_csv_raw, feeds_csv_raw = stat_fixture
        iocs_csv_raw_lines = iocs_csv_raw.split("\n")

        with open(join(DATASET_DIR, "stat", "iocs.csv")) as original_csv:
            count = 0
            for line in original_csv:
                assert line[:-1] == iocs_csv_raw_lines[count]
                count += 1

    # The test below is not valid because we have
    # randomly-generated whitelist overlap ratio at
    # `scoring_engine`: get_whitelist_overlap_coef()
    #
    # def test_feeds_stat(self, stat_fixture):
    #     iocs_csv_raw, feeds_csv_raw = stat_fixture
    #     feeds_csv_raw_lines = feeds_csv_raw.split("\n")
    #
    #     with open(join(DATASET_DIR, "stat", "feeds.csv")) as original_csv:
    #         count = 0
    #         for line in original_csv:
    #             assert line[:-1] == feeds_csv_raw_lines[count]
    #             count += 1
