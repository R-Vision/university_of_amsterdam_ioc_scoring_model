import sys
import pandas as pd
import plotly.express as px
from typing import Any, Dict, List

sys.path.append("../..")
import time
from datetime import datetime, timedelta

import functions

last_seen = datetime.now() - timedelta(days=7)
EPOCH_DAY = 86000


def decayed_score_timeline(
    ttl: int, decay_rate: float, ioc_last_seen: int, init_score: int = 100
):
    days_coef: List[Dict[str, Any]] = []

    for day in range(1, ttl):
        rolling_day = time.mktime(datetime.now().timetuple()) + (EPOCH_DAY * day)
        coefficient: float = functions.calculate_decay_coef(
            decay_rate=decay_rate,
            decay_ttl=ttl,
            last_seen=ioc_last_seen,
            date_now=rolling_day,
        )
        days_coef.append(
            {"decay_ratio": coefficient, "day": day, "decay_ratio_value": decay_rate}
        )

    return days_coef


def plot(score_timeline_arr):
    df = pd.DataFrame(score_timeline_arr)
    fig = px.line(
        df,
        x="day",
        y="decay_ratio",
        title="IoC score decay timeline",
        line_group="decay_ratio_value",
        color="decay_ratio_value",
        log_x=False,
        log_y=False,
    )
    fig.show()