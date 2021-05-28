import time
from datetime import datetime
from typing import List, Dict, Union, Any
from random import randint

from pandas import DataFrame, Series

import functions
from helpers import io, lookups, stats
from helpers.howlong import HowLong
from helpers.integrity_checker import is_modified

DECAY_RATE: float = 0.5
DECAY_TTL: int = 10


def get_tqdm_instance(use_tqdm: bool):
    if use_tqdm:
        from tqdm import tqdm

        return tqdm
    else:
        return lambda x: x


def get_extensiveness_coef(cti_feed: DataFrame) -> float:
    """
    Function calculates the extensiveness
    for the specified feed

        Parameters:

            cti_feed (pandas.DataFrame) — CTI feed as pandas.DataFrame

        Returns:

            Extensiveness coefficient (float, 0..1)
    """
    EXTENSIVENESS_PARAM_COUNT: int = 3  # Extensiveness parameters count
    feed_len: int = len(cti_feed.index)
    sum_extensiveness: float = 0

    for row in cti_feed.itertuples(index=False):
        has_last_seen = 1 if row.last_seen else 0
        has_relationships = 1 if row.relationship_count > 0 else 0
        has_detections_count = 1 if row.detections_count > 0 else 0
        sum_extensiveness += functions.ioc_extensiveness(
            EXTENSIVENESS_PARAM_COUNT,
            has_last_seen,
            has_relationships,
            has_detections_count,
        )
    return functions.extensiveness(sum_extensiveness, feed_len)


def get_completeness_coef(iocs_per_feed: int, total_iocs: int) -> float:
    """
    This function wrapper is intended for
    calculate feed completeness factor

        Parameters:

            iocs_per_feed: int — Number of IoCs in the CTI feed
            total_iocs: int — Number of IoCs across all CTI feeds

        Returns:

            Completeness coefficient (float, 0..1)
    """
    return functions.completeness(iocs_per_feed, total_iocs)


def get_timeliness_coef(cti_feed: DataFrame, iocs_min_date) -> float:
    """
    Function calculates timeliness factor
    for given pandas dataframe

        Parameters:

            cti_feed (pandas.DataFrame) — CTI feed as pandas.DataFrame

        Returns:

            Timeliness coefficient (float, 0..1)
    """
    sigma: float = 0
    curr_feed_len: int = 0
    curr_first_seen: int = 0
    min_first_seen: int = 0

    for row in cti_feed.itertuples(index=False):
        curr_feed_len = len(cti_feed.index)
        curr_first_seen = row.first_seen
        min_first_seen = iocs_min_date[row.value]

        sigma = functions.calculate_timeliness_sigma(
            sigma, min_first_seen, curr_first_seen
        )

    return functions.timeliness(sigma, curr_feed_len)


def get_whitelist_overlap_coef(cti_feed: DataFrame) -> float:
    """
    Function calculates whitelist overlapping ratio
    The higher ratio = the better feed quality

    NOTE: THIS FUNCTION IS A MOCK NOW, JUST FOR
    TESTING REASONS

    TODO: Make working version of function.
    Params: dataframe with CTIfeed, dataframe
    with WL feed.

    Function calculates overlap between CTI & WL
    feeds, calculates CTI feed lenght -> send this
    calcutaions as parameters to

    Returns: functions.whitelist_overlap_score()
    """

    feed_iocs_count: int = len(cti_feed.index)

    wl_iocs: int = randint(
        0, round(feed_iocs_count * 0.1)
    )  # NOTE: Randomly generate WL iocs (max 10% of feed), real WL overlap not implemented yet

    return functions.whitelist_overlap_score(wl_iocs, feed_iocs_count)


def get_source_confidence(
    extensiveness: float,
    completeness: float,
    timeliness: float,
    wl_overlap_coef: float,
):
    """
    Function wrapper calculates source confidence for the specified params

        Parameters:

            cti_feed (dict) — CTI feed packed in pandas dataframe
            cti_feeds_stats — overall CTI feeds stats

        Returns:

            Source confidence (float, 0..1)
    """
    return functions.source_confidence(
        extensiveness,
        timeliness,
        completeness,
        wl_overlap_coef,
    )


def get_multiple_feeds_iocs_score(
    ioc_value: str, last_seens_meta: Dict[str, List[int]], now: float
) -> List[float]:
    """
    Function aggregates individual feed scores
    for the specified IoC
    """
    scores = []
    last_seens = last_seens_meta[ioc_value]

    for last_seen in last_seens:
        scores.append(get_single_feed_ioc_score(None, last_seen, now))

    return scores


def get_single_feed_ioc_score(
    ioc_score: Union[int, None],
    ioc_last_seen: float,
    date_now: float,
    decay_rate=DECAY_RATE,
    decay_ttl=DECAY_TTL,
):
    """
    Function calculates score for the single feed
    """
    last_seen = ioc_last_seen or date_now

    ioc_decay_coef = functions.calculate_decay_coef(
        decay_rate=decay_rate,
        decay_ttl=decay_ttl,
        last_seen=last_seen,
        date_now=date_now or time.mktime(datetime.now().timetuple()),
    )

    return functions.single_feed_ioc_score(ioc_score, ioc_decay_coef)


def calculate_iocs_score(
    cti_feeds_path: str,
    skip_is_modified=False,
    dt_now=time.mktime(datetime.now().timetuple()),
):
    """
    Function initializes and loads statistics dataframes,
    if statistics in not exists recalculates them

        Parameters:

            cti_feeds_path (str) — path to the directory with the CTI feeds
            skip_is_modified (bool) — used to avoid statistics recalculating,
            just for testing reasons.
            dt_now (float) - unixtime means current time, just for testing
            purposes (don't use it if u don't understand why u want use it)

        Returns:

            Calculated iocs scores for each feed in given dataset
    """
    cti_feeds = io.load_feeds(cti_feeds_path)
    lookup_df = io.load_whole_feeds(cti_feeds_path)

    if not skip_is_modified and is_modified(cti_feeds_path):
        statistics = stats.calculate_all_statistics(cti_feeds)
        io.write_statistics(cti_feeds_path, **statistics)

    iocs_stats = io.load_iocs_statistics(cti_feeds_path)
    feeds_stats = io.load_feed_statistics(cti_feeds_path)

    return _calculate_iocs_score(
        cti_feeds, lookup_df, iocs_stats, feeds_stats, dt_now=dt_now
    )


def _calculate_iocs_score(
    cti_feeds: List[Dict[str, Any]],
    lookup_df: Union[DataFrame, Series],
    iocs_stats: DataFrame,
    feeds_stats: DataFrame,
    dt_now: float = time.mktime(datetime.now().timetuple()),
    use_tqdm=False,
):
    """
    Function calculates the final score of IoCs
    """
    all_scores: List = []
    tqdm_instance = get_tqdm_instance(use_tqdm)

    last_seens_meta: Dict[str, List[int]] = {}
    for row in lookup_df.itertuples(index=False):
        if row.value in last_seens_meta:
            last_seens_meta[row.value].append(row.last_seen)
        else:
            last_seens_meta[row.value] = [row.last_seen]

    feed_confidence_dict = {}
    for feed in feeds_stats.itertuples():
        feed_confidence_dict[feed.Index] = feed.feed_source_confidence

    for feed in tqdm_instance(cti_feeds):
        feed_scores: List = []
        for row in feed["df"].itertuples(index=True):
            source_confidences = []
            ioc_value = row.value

            with HowLong("feeds_ioc_mentioned"):
                # Find all feed names where the IoC mentioned in
                feeds_ioc_mentioned = lookups.find_feeds_name_ioc_mentioned_in(
                    ioc_value, iocs_stats
                )

            with HowLong("feed_name in feeds_ioc_mentioned"):
                # Get all source_confidence metrics for this feeds
                for feed_name in feeds_ioc_mentioned:
                    source_confidences.append(feed_confidence_dict[feed_name])

            mentioned_in_count = len(source_confidences)

            with HowLong("feeds_scores"):
                # Get individual feeds scores for each feed the IoC has been mentioned in
                feeds_scores = get_multiple_feeds_iocs_score(
                    ioc_value, last_seens_meta, dt_now
                )

            with HowLong("final_score"):
                # Culmination: calculate the final score
                final_score = functions.score(
                    source_confidences, feeds_scores, mentioned_in_count
                )
            feed_scores.append(
                {
                    "value": ioc_value,
                    "score": final_score,
                    "first_seen": datetime.fromtimestamp(row.first_seen).strftime(
                        "%Y-%m-%d"
                    ),
                    "last_seen": datetime.fromtimestamp(row.last_seen).strftime(
                        "%Y-%m-%d"
                    ),
                    "ioc_mentions": len(feeds_ioc_mentioned)
                    if feeds_ioc_mentioned
                    else 0,
                    "source_confidences": source_confidences,
                    "feeds_scores": [round(r * 100) for r in feeds_scores],
                }
            )

        all_scores.append({"feed_name": feed["name"], "score_data": feed_scores})

    return all_scores
