import os
import random
import argparse
from typing import Any, Dict, List

import pandas as pd

from generators import FakeGenerators

fake = FakeGenerators()
feed = pd.DataFrame()
argparser = argparse.ArgumentParser()

FEED_PATH: str = os.path.join(os.getcwd(), "data/dataset_04_large")


def generate_random_feed(ioc_quatity: int) -> pd.DataFrame:
    # TODO: add feed uniqueness %
    ioc: Dict[str, Any] = {}
    feed: List[Dict[str, Any]] = []

    for _ in range(ioc_quatity):
        first_seen = fake.generate_date_between_dates()
        last_seen = fake.generate_last_seen_date(first_seen)
        ioc = {
            "id": fake.generate_uuid4(),
            "value": fake.generate_random_value(),
            "first_seen": first_seen,
            "last_seen": last_seen,
            "relationship_count": fake.generate_random_int(),
            "detections_count": fake.generate_random_int(0, 5),
        }
        feed.append(ioc.copy())

    return pd.DataFrame(feed)


def write_feed(filename: str, data: pd.DataFrame) -> None:
    filepath: str = os.path.join(FEED_PATH, os.path.basename(filename) + ".csv")

    if not os.path.exists(FEED_PATH):
        os.makedirs(FEED_PATH)

    data.to_csv(filepath)
    print(f"[INFO] Wrote feed at: {filepath}")


argparser.add_argument(
    "--feeds_count",
    action="store",
    dest="feeds_count",
    default=None,
    type=int,
    required=True,
    help="Number of feeds have to be generated",
)
args = argparser.parse_args()

if args.feeds_count:
    for item in range(args.feeds_count):
        filename: str = f"feed_{item}"
        feed: pd.DataFrame = generate_random_feed(random.randint(5, 10))
        write_feed(filename=filename, data=feed)
