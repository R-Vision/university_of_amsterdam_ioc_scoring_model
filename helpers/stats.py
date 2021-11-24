import calendar
from typing import Any, Dict, List, Tuple, Union

import pandas as pd
from dateutil import parser
import scoring_engine as engine

from helpers import lookups
from helpers.howlong import HowLong


def date_to_unixtime(time: str) -> int:
    return calendar.timegm(parser.parse(time).timetuple())


def get_tqdm_instance(use_tqdm: bool):
    if use_tqdm:
        from tqdm import tqdm

        return tqdm
    else:
        return lambda x: x


def _calculate_iocs_statistics(
    feed_list,
    iocs_min_date: Dict[str, str],
    iocs_feed_names: Dict[str, List[str]],
    use_tqdm=True,
):
    """
    Function is intended for calculating overall iocs
    statistics, that will be needed for IoC scoring calculation.

        Params:

            feed_list — CTI feeds dict with it names and dataframes.

        Returns:

            Calculated iocs statistics
    """
    tqdm_instance = get_tqdm_instance(use_tqdm)

    iocs_stats: List[Any] = []

    print("[STATISTICS] Started CTI iocs statistics recalculating...")

    for feed in tqdm_instance(feed_list):
        for row in feed["df"].itertuples(index=False):
            value = row.value
            iocs_stats.append(
                (
                    row.id,
                    value,
                    iocs_min_date[value],
                    len(iocs_feed_names[value]),
                    iocs_feed_names[value],
                )
            )

    print("[STATISTICS] IoCs statistics recalculated")

    return pd.DataFrame(
        iocs_stats,
        columns=[
            "id",
            "value",
            "min_first_seen",
            "mentioned_in_count",
            "feeds_ioc_mentioned_in",
        ],
    ).drop_duplicates(subset=["value"])


def _calculate_feeds_statistics(
    feed_list: List[Dict[str, Union[str, pd.DataFrame]]],
    iocs_min_date,
    use_tqdm=True,
) -> pd.DataFrame:
    """
    Function is intended for calculating overall feeds
    statistics, that will be needed for IoC scoring calculation.

        Params:

            feed_list — CTI feeds dict with it names and dataframes.

        Returns:

            Calculated feeds statistics
    """
    tqdm_instance = get_tqdm_instance(use_tqdm)

    overall_iocs: int = lookups.overall_ioc_count(feed_list)
    feeds_stats: List[Any] = []

    print("[STATISTICS] Started CTI feeds statistics recalculating...")

    for feed in tqdm_instance(feed_list):
        feed_iocs_count = len(feed["df"].index)

        extensiveness: float = engine.get_extensiveness_coef(feed["df"])
        completeness: float = engine.get_completeness_coef(
            feed_iocs_count, overall_iocs
        )
        timeliness: float = engine.get_timeliness_coef(feed["df"], iocs_min_date)
        wl_overlap_coef: float = engine.get_whitelist_overlap_coef(feed["df"])
        source_confidence: float = engine.get_source_confidence(
            extensiveness, completeness, timeliness, wl_overlap_coef
        )

        feed_stats: Dict[str, Any] = {
            "feed_name": feed["name"],
            "feed_extensiveness": extensiveness,
            "feed_completeness": completeness,
            "feed_timeliness": timeliness,
            "feed_wl_overlap": wl_overlap_coef,
            "feed_source_confidence": source_confidence,
            "feed_size": feed_iocs_count,
        }

        feeds_stats.append(feed_stats)

    print("[STATISTICS] CTI feeds statistics recalculated")

    return pd.DataFrame(feeds_stats)


def _get_meta_data(cti_feeds, use_tqdm=True) -> Tuple[Any, Any]:
    tqdm_instance = get_tqdm_instance(use_tqdm)

    iocs_min_date: Dict[str, str] = dict()
    iocs_feed_names: Dict[str, List[str]] = dict()

    for feed in tqdm_instance(cti_feeds):
        for row in feed["df"].itertuples(index=False):
            value = row.value
            if value in iocs_min_date:
                iocs_min_date[value] = min(iocs_min_date[value], row.first_seen)
            else:
                iocs_min_date[value] = row.first_seen

            if value in iocs_feed_names:
                iocs_feed_names[value].append(feed["name"])
            else:
                iocs_feed_names[value] = [feed["name"]]

    return iocs_min_date, iocs_feed_names


def calculate_all_statistics(
    cti_feeds: List[Dict[str, Any]], use_tqdm=True
) -> Dict[str, Any]:
    """
    Wrapper for start calculating feeds and iocs stats simultaneosly
    and write results into the files

    TODO: Force recalculate stats in case when `functions.py` has
    been modified (formulas, constants, etc)
    """
    result: Dict[str, Any] = {}

    try:
        with HowLong("prepare of metadata"):
            iocs_min_date, iocs_feed_names = _get_meta_data(cti_feeds, use_tqdm)
        with HowLong("result['iocs']"):
            result["iocs"] = _calculate_iocs_statistics(
                cti_feeds, iocs_min_date, iocs_feed_names, use_tqdm=use_tqdm
            )
        with HowLong("result['feeds']"):
            result["feeds"] = _calculate_feeds_statistics(
                cti_feeds, iocs_min_date, use_tqdm=use_tqdm
            )

        return result
    except Exception as e:
        raise e
