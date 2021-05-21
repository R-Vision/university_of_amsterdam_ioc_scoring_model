import json
import pathlib
import time
import datetime
from os.path import join
from typing import Tuple, List, Dict, Any

import pytest
from pandas import DataFrame

try:
    from src.amsterdam_model.helpers import io
    from src.amsterdam_model.helpers.howlong import howlong_flush_stat, HowLong
    from src.amsterdam_model.scoring_engine import (
        get_single_feed_ioc_score,
        _calculate_iocs_score,
    )
except ImportError:
    from helpers import io
    from helpers.howlong import howlong_flush_stat, HowLong
    from scoring_engine import get_single_feed_ioc_score, _calculate_iocs_score

FIXTURES_DIR = join(pathlib.Path(__file__).parent.absolute(), "fixtures")

DATASET_NAME = "dataset_04_mid"
DATASET_DIR = join(FIXTURES_DIR, DATASET_NAME)


def str2timestamp(date_iso: str) -> float:
    dt = datetime.datetime.fromisoformat(date_iso)
    return time.mktime(dt.timetuple())


@pytest.fixture(scope="class")
def fixtures() -> Tuple[List[Dict[str, Any]], Any, DataFrame, DataFrame, float]:
    now = str2timestamp("2021-03-07")

    with HowLong("fixtures"):
        cti_feeds_path = join(DATASET_DIR, "feeds")

        cti_feeds = io.load_feeds(cti_feeds_path)
        lookup_df = io.load_whole_feeds(cti_feeds_path)

        cti_feeds_path = join(DATASET_DIR, "stat")
        iocs_stats = io.load_iocs_statistics(cti_feeds_path, "iocs.csv")
        feeds_stats = io.load_feed_statistics(cti_feeds_path, "feeds.csv")

    return cti_feeds, lookup_df, iocs_stats, feeds_stats, now


@pytest.fixture(scope="session", autouse=True)
def howlong_flush():
    yield
    howlong_flush_stat()


class TestStatisticCalculation:
    def test_get_single_feed_ioc_score(self):
        now = str2timestamp("2021-03-07")
        last_seen = str2timestamp("2021-01-02")

        score = get_single_feed_ioc_score(10, last_seen, now, 0.5, 90)
        assert score == 4.9

    def _test_dump_iocs_score(self, fixtures):
        cti_feeds, lookup_df, iocs_stats, feeds_stats, now = fixtures
        with HowLong("calculating overall"):
            scores = _calculate_iocs_score(
                cti_feeds, lookup_df, iocs_stats, feeds_stats, now
            )

        with open(join(DATASET_DIR, "stat", "scores.json"), "w") as f:
            json.dump(scores, f, indent=2)

    def test_calculate_iocs_score(self, fixtures):
        cti_feeds, lookup_df, iocs_stats, feeds_stats, now = fixtures
        with HowLong("calculating overall"):
            scores = _calculate_iocs_score(
                cti_feeds, lookup_df, iocs_stats, feeds_stats, now
            )

        with open(join(DATASET_DIR, "stat", "scores.json")) as f:
            scores_original = json.load(f)

        # TODO fix freeze on big data
        assert scores_original == scores
