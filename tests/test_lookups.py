import pathlib
from os.path import join
from typing import Any, Dict, List, Tuple

import pytest
from pandas import DataFrame

from helpers import io, lookups


FIXTURES_DIR = join(pathlib.Path(__file__).parent.absolute(), "fixtures")

DATASET_NAME = "dataset_04_mid"
DATASET_DIR = join(FIXTURES_DIR, DATASET_NAME)


@pytest.fixture(scope="class")
def fixtures() -> Tuple[List[Dict[str, Any]], Any, DataFrame, DataFrame]:
    cti_feeds_path = join(DATASET_DIR, "feeds")

    cti_feeds = io.load_feeds(cti_feeds_path)
    lookup_df = io.load_whole_feeds(cti_feeds_path)

    cti_feeds_path = join(DATASET_DIR, "stat")
    iocs_stats = io.load_iocs_statistics(cti_feeds_path, "iocs.csv")
    feeds_stats = io.load_feed_statistics(cti_feeds_path, "feeds.csv")

    return cti_feeds, lookup_df, iocs_stats, feeds_stats


class TestLookups:
    def test_find_feed_ioc_mentioned_in(self, fixtures):
        cti_feeds, lookup_df, iocs_stats, feeds_stats = fixtures

        result = lookups.find_feeds_name_ioc_mentioned_in("65.42.162.18", iocs_stats)
        if result:
            assert result == ["feed_2.csv"]
        else:
            assert result == []

    def test_number_of_feeds_ioc_mentioned_in(self, fixtures):
        cti_feeds, _, _, _ = fixtures
        result = lookups.number_of_feeds_ioc_mentioned_in("65.42.162.18", cti_feeds)
        assert result == 1

    def test_overall_ioc_count(self, fixtures):
        cti_feeds, _, _, _ = fixtures
        result = lookups.overall_ioc_count(cti_feeds)
        assert result == 3382

    def test_find_feeds_name_ioc_mentioned_in(self, fixtures):
        _, _, iocs_stats, _ = fixtures
        result = lookups.find_feeds_name_ioc_mentioned_in("65.42.162.18", iocs_stats)
        assert result == ["feed_2.csv"]

    def test_get_feed_source_confidence(self, fixtures):
        _, _, _, feeds_stats = fixtures
        result = lookups.get_feed_source_confidence("feed_2.csv", feeds_stats)
        assert result == 0.634

    def test_find_min_date(self, fixtures):
        cti_feeds, _, _, _ = fixtures
        result = lookups.find_min_date("65.42.162.18", cti_feeds)
        assert int(result) == 1608508800
