from ast import literal_eval

import pytest
from random import randint
from datetime import datetime


try:
    from src.amsterdam_model.helpers.parse_array import parse_array
    from src.amsterdam_model import functions
    from src.amsterdam_model.helpers import stats
    from src.amsterdam_model.feed_generator.generators import FakeGenerators
except ImportError:
    import functions
    from helpers import stats
    from helpers.parse_array import parse_array
    from feed_generator.generators import FakeGenerators

fake = FakeGenerators()
EPOCH_DAY: int = 86400  # Milliseconds format


class TestFunctions:
    def test_timeliness(self):
        sigma = 0
        timeliness = 0
        feed_size = randint(10, 100)  # Feed size emulation

        for _ in range(feed_size):
            min_fs = fake.generate_date_between_dates()
            curr_fs = stats.date_to_unixtime(fake.generate_last_seen_date(min_fs))
            min_fs_unix = stats.date_to_unixtime(min_fs)
            sigma = functions.calculate_timeliness_sigma(sigma, min_fs_unix, curr_fs)

        timeliness = functions.timeliness(sigma=sigma, curr_feed_len=feed_size)
        assert 0 <= timeliness <= 1

    def test_negative_decay_rate(self):
        last_seen = datetime.now().timestamp() - (EPOCH_DAY * 7)
        result = functions.calculate_decay_coef(
            decay_rate=-1.0, decay_ttl=10, last_seen=last_seen
        )
        assert result == 0.97

    def test_min_decay_rate(self):
        last_seen = datetime.now().timestamp() - (EPOCH_DAY * 7)
        result = functions.calculate_decay_coef(
            decay_rate=0, decay_ttl=10, last_seen=last_seen
        )
        assert result == 0.97

    def test_max_decay_rate(self):
        last_seen = datetime.now().timestamp() - (EPOCH_DAY * 7)
        result = functions.calculate_decay_coef(
            decay_rate=1.0, decay_ttl=10, last_seen=last_seen
        )
        assert result == 0.3

    def test_negative_decay_ttl(self):
        last_seen = datetime.now().timestamp() * 1000
        with pytest.raises(Exception) as e:
            functions.calculate_decay_coef(
                decay_rate=0.3, decay_ttl=-1, last_seen=last_seen
            )
            assert "should be greater or equal" in str(e)

    def test_non_int_type(self):
        with pytest.raises(Exception) as e:
            functions.calculate_decay_coef(
                decay_rate=1.0, decay_ttl=1, last_seen="28.01.2021"
            )
            assert "`last_seen` arg must be of" in str(e)

    def test_get_extensiveness_coef(self):
        result = functions.extensiveness(feed_sum_extensiveness=50, feed_len=100)
        assert result == 0.5

    def test_completeness(self):
        result = functions.completeness(feed_size=50, total_iocs=100)
        assert result == 0.5

    def test_whitelist_overlap_score(self):
        must_be_zero = functions.whitelist_overlap_score(100, 1000)
        must_be_non_zero = functions.whitelist_overlap_score(
            whitelisted_iocs=50, overall_iocs=1000
        )
        assert must_be_zero == 0
        assert 0 <= must_be_non_zero <= 1

    def test_source_confidence(self):
        result = functions.source_confidence(
            source_extensiveness=0.8,
            source_timeliness=0.9,
            source_completeness=0.8,
            source_wl_score=0.1,
        )
        assert result == 0.579

    def test_singe_feed_score(self):
        must_be_float = round(functions.single_feed_ioc_score(56, 0.55), 2)
        must_be_half_a_zero = functions.single_feed_ioc_score(None, 0.5)
        assert must_be_float == 30.80
        assert must_be_half_a_zero == 0.5

    def test_score(self):
        source_confidence = [0.25, 0.5, 0.75, 1]
        score = [0.25, 0.5, 0.75, 1]
        count = 4
        result = functions.score(source_confidence, score, count)
        assert result == 62

    def test_score_v2(self):
        source_confidence = [0.653, 0.653]
        score = [1, 0.5]
        count = 1
        result = functions.score(source_confidence, score, count)
        assert result == 65

    def test_parse_array_base(self):
        str_arr = "['feed_1.csv', 'feed_2.csv']"
        python_way = literal_eval(str_arr)
        out_way = parse_array(str_arr)

        assert out_way == python_way

    def test_parse_array_hard(self):
        str_arr = "['feed,_1.csv', 'feed_2.csv']"
        python_way = literal_eval(str_arr)
        out_way = parse_array(str_arr)

        assert out_way == python_way

    def test_parse_array_empty(self):
        str_arr = "[]"
        python_way = literal_eval(str_arr)
        out_way = parse_array(str_arr)

        assert out_way == python_way
