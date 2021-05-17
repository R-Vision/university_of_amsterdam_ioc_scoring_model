import os

import numpy as np
import pandas as pd
from glob import glob
from typing import Any, List, Dict, Optional, Tuple


def load_single_feed(fullpath: str):
    df = pd.read_csv(fullpath)
    df["first_seen"] = (
        pd.to_datetime(df["first_seen"]).values.astype(np.int64) // 10 ** 9
    )
    df["last_seen"] = pd.to_datetime(df["last_seen"]).values.astype(np.int64) // 10 ** 9

    return df


def load_feeds(path: str) -> List[Dict[str, Any]]:
    """
    Read all feeds from the specified
    directory, you cat get the result
    by using generator expression like
    [x for x in get_feeds()]
    """
    filenames = glob(f"{path}/*.csv")
    return [
        {"name": os.path.basename(df), "df": load_single_feed(df)} for df in filenames
    ]


def load_feed_statistics(path: str, name=".feeds-statistics") -> pd.DataFrame:
    """
    Read feeds statistics from file
    """
    FEEDS_STATS_FILE: str = os.path.join(path, name)
    return pd.read_csv(FEEDS_STATS_FILE, index_col="feed_name")


def load_iocs_statistics(path: str, name=".iocs-statistics") -> pd.DataFrame:
    """
    Read iocs statistics from file
    """
    IOCS_STATS_FILE: str = os.path.join(path, name)
    return pd.read_csv(IOCS_STATS_FILE, index_col="value")


def load_whole_feeds(path: str):
    return pd.concat(feed["df"] for feed in load_feeds(path))


def write_statistics(
    path: Optional[str], **df: Dict[str, Any]
) -> Optional[Tuple[str, str]]:
    if path:
        IOCS_STATS_FILE: str = os.path.join(path, ".iocs-statistics")
        FEEDS_STATS_FILE: str = os.path.join(path, ".feeds-statistics")
        pd.DataFrame(df["iocs"]).to_csv(IOCS_STATS_FILE)
        pd.DataFrame(df["feeds"]).to_csv(FEEDS_STATS_FILE)

        return None

    return pd.DataFrame(df["iocs"]).to_csv(), pd.DataFrame(df["feeds"]).to_csv()
