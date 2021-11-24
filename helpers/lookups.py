from typing import List, Optional
import pandas as pd
from helpers.parse_array import parse_array


def feeds_ioc_mentioned_in(ioc_value: str, df) -> List[str]:
    """Return feed names where specified IOC was mentioned in"""
    feeds: List[str] = []
    for feed in df:
        is_ioc_exist = feed["df"].loc[feed["df"]["value"] == ioc_value]
        if not is_ioc_exist.empty:
            feeds.append(feed["name"])
    return feeds


def number_of_feeds_ioc_mentioned_in(ioc_value: str, dataframe) -> int:
    """Return number of feed specified ioc mentioned in"""
    df = pd.concat(feed["df"] for feed in dataframe)
    mentioned_in = df.loc[df["value"] == ioc_value]
    return len(mentioned_in.index)


def overall_ioc_count(dataframe) -> int:
    """Return total number of iocs across all feeds (non-distinct)"""
    return sum(feed["df"].shape[0] for feed in dataframe)


def find_feeds_ioc_mentioned_in(ioc_value: str, df) -> int:
    result = df.at[ioc_value, "mentioned_in_count"]
    return result


def find_feeds_name_ioc_mentioned_in(ioc_value: str, df) -> Optional[List[str]]:
    result: str = df.at[ioc_value, "feeds_ioc_mentioned_in"]
    names = parse_array(result)
    return names


def get_feed_source_confidence(feed_name: str, df):
    source_confidence = df.at[feed_name, "feed_source_confidence"]
    return source_confidence


def find_min_date(ioc_value: str, df) -> str:
    """Return min `first_seen` for the specified IoC"""
    df = pd.concat(feed["df"] for feed in df)
    selected = df.loc[df["value"] == ioc_value]
    return str(selected["first_seen"].min())
