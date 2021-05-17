import time
import datetime
from typing import List, Union


def timeliness(sigma: float, curr_feed_len: int) -> float:
    return round(sigma / curr_feed_len, 3)


def extensiveness(feed_sum_extensiveness: float, feed_len: int) -> float:
    return round(feed_sum_extensiveness / feed_len, 3)


def completeness(feed_size: int, total_iocs: int) -> float:
    return round(feed_size / total_iocs, 3)


def ioc_extensiveness(
    EXTENSIVENESS_PARAM_COUNT, has_last_seen, has_relationships, has_detections_count
):
    return +round(
        (has_last_seen + has_detections_count + has_relationships)
        / EXTENSIVENESS_PARAM_COUNT,
        2,
    )


def whitelist_overlap_score(
    whitelisted_iocs: int,
    overall_iocs: int,
) -> float:
    """
    Calculates penalty for explicit whitelisted ios

        Constants:

            FP (float) — Threshold. Indicates at which percentage
            of overlap between `whilelisted_iocs` and `overall_iocs`
            will not be considered as trustworth.

            DELTA (float) — Is used to compensate potential inaccuracy:
            source paper assumpt that whitelisted IoC might be malicious
            anyway.

        Parameters:

            whitelisted_iocs (int) — Number of IoC that overlapped with
            well-known non-iocs (aka whitelists), such as MISP Warninglists,
            Alexa Top 1m, etc.

            overall_iocs (int) — CTI feed size (IoCs count).

        Returns:

            Overlapping ratio — quality of feed in relation to whitelists.
    """
    FP: float = 0.1  # Assumption from the paper
    DELTA: float = 0.5  # Assumption from the paper
    return round(max(0, 1 - (whitelisted_iocs / (overall_iocs * FP)) ** (1 / DELTA)), 3)


def source_confidence(
    source_extensiveness: float,
    source_timeliness: float,
    source_completeness: float,
    source_wl_score: float,
) -> float:
    """
    Calculates weighted mean of 4 characteristics

        Parameters:

            source_extensiveness (float, 0..1)
            source_timeliness (float, 0..1)
            source_completeness (float, 0..1)
            source_wl_score (float, 0..1)

        Returns:

            Source confinence (float, 0..1)
    """
    # PARAMS WEIGHTS — you cat tune it
    EXTENSIVENESS_WEIGHT: float = 0.8
    TIMELINESS_WEIGHT: float = 0.6
    COMPLETENESS_WEIGHT: float = 0.5
    WL_OVERLAP_WEIGHT: float = 1

    confidence_score = (
        EXTENSIVENESS_WEIGHT * source_extensiveness
        + TIMELINESS_WEIGHT * source_timeliness
        + COMPLETENESS_WEIGHT * source_completeness
        + WL_OVERLAP_WEIGHT * source_wl_score
    ) / (
        EXTENSIVENESS_WEIGHT
        + TIMELINESS_WEIGHT
        + COMPLETENESS_WEIGHT
        + WL_OVERLAP_WEIGHT
    )
    return round(confidence_score, 3)


def single_feed_ioc_score(
    ioc_score: Union[int, None], decay_coef: float
) -> Union[int, float]:
    """
    Calculates score for the specified feed.
    If feed has not score itself, return 1

        Parameters:

            ioc_score (int) — Source score of IoC from the CTI feed.
            decay_coef (float) — Decay (attenuation) ratio.

        Returns:

            Feed score (float, 0..1) — feed rating (score).

        NOTE: function always apply decay coefficient, but original paper
        propose to use coeff == 1 if there is none score from CTI feed:
        ioc_score * decay_coef if ioc_score else 1
    """

    # TODO ioc_score normalization
    return ioc_score * decay_coef if ioc_score else 1 * decay_coef


def score(
    source_confidence: List[float], score: List[float], mentioned_feeds_count: int
) -> int:
    """
    Function calculates final score for the IoC

        Parameters:

            source_confidence (List[float], 0..1) — a list `source_confindence` of all CTI feeds where the IoC has been mentioned.
            score (List[float], 0..1) — a list `score` of all CTI feeds where the IoC has been mentioned.
            mentioned_feeds_count (int) — count of feeds that mentioned the IoC.

        Returns:

            IoC final score (int, 0..100)
    """
    x: float = 0
    y: float = 0

    for i in range(0, mentioned_feeds_count):
        x += (source_confidence[i] ** 2) * score[i]
        y += source_confidence[i]

    return round(x / y * 100)


def calculate_timeliness_sigma(
    sigma: float, min_first_seen: int, curr_first_seen: int, LAMBDA: int = 604800
) -> float:
    """
    TODO:

    Equation below from original paper is based on LAMBDA contant
    which makes the final score more accurate, but gives high negative
    numbers in cases when we tried to assess old feeds.

    sigma += (min_first_seen - curr_first_seen + LAMBDA) / LAMBDA

    So we might think about how to dymanically calculated LAMBDA,
    for example on overall feeds timestamps statistics,
    e.g LAMBDA(min_first_seen, max_first_seen)
    """
    sigma += min_first_seen / curr_first_seen
    return round(sigma, 3)


def seconds2days(sec: Union[int, float]) -> float:
    return sec / 60.0 / 60.0 / 24.0


def calculate_decay_coef(
    decay_rate: float,
    decay_ttl: int,
    last_seen: float,
    date_now: float = time.mktime(datetime.datetime.now().timetuple()),
) -> float:
    """
    This function is intended for
    calculate decay rate (attenuation)
    for the indicator of compromise

        Parameters:

            decay_rate (float, 0..1): represents the time it takes
            for an IoC to become invalid after its last sighting.
            decay_ttl (int, min 1): determines at which x value f(x) is equal to 0
            last_seen (datetime): date that IoC last seen

        Returns:

            Decay coefficient (float, 0..1)
    """

    if decay_rate <= 0:
        decay_rate = 0.1
    elif decay_rate > 1:
        decay_rate = 1

    delta = seconds2days(date_now - last_seen)

    d = (delta / decay_ttl) ** (1 / decay_rate)
    return round(max(0, 1 - d), 2)
