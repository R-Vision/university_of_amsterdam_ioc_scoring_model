from datetime import date, datetime, timedelta
import time
import random
from uuid import uuid4
from typing import Optional, Union

digits = "0123456789"
hexdigits_lower = digits + "abcdef"


class FakeGenerators:
    """
    Methods for generate some fake data for tests
    """

    def generate_uuid4(self) -> str:
        return str(uuid4())

    def generate_random_value(self) -> Optional[Union[str, int]]:
        ioc_type: str = random.choice(("hash", "ipv4", "ipv6"))
        if ioc_type == "hash":
            return self.generate_hash()
        elif ioc_type == "ipv4":
            return self.generate_ipv4()
        elif ioc_type == "ipv6":
            return self.generate_ipv6()

    def generate_hash(self) -> str:
        hash_type: str = random.choice(("md5", "sha1", "sha256"))
        if hash_type == "md5":
            return self.generate_md5()
        elif hash_type == "sha1":
            return self.generate_sha1()
        elif hash_type == "sha256":
            return self.generate_sha256()
        else:
            return self.generate_md5()

    def generate_md5(self) -> str:
        return "".join(random.choice(hexdigits_lower) for _ in range(32))

    def generate_sha1(self) -> str:
        return "".join(random.choice(hexdigits_lower) for _ in range(40))

    def generate_sha256(self) -> str:
        return "".join(random.choice(hexdigits_lower) for _ in range(64))

    def generate_ipv4(self) -> str:
        return ".".join(str(random.randint(0, 255)) for _ in range(4))

    def generate_ipv6(self) -> str:
        return ":".join("{:x}".format(random.randint(0, 2 ** 16 - 1)) for i in range(8))

    def generate_timestamp(self) -> int:
        ts = random.randint(1, int(time.time()))
        return ts

    def generate_random_date(self) -> str:
        # TODO: Add optional `%H:%M:%S %d-%m-%Y` and `%Y-%m-%Y` formats
        dt = random.randint(10, int(time.time()))
        return datetime.fromtimestamp(dt).strftime("%Y-%m-%d")

    def generate_date_between_dates(
        self,
        start_date: date = date(2020, 12, 1),
        end_date: date = datetime.now().date(),
    ) -> str:
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_date = (start_date + timedelta(days=random_number_of_days)).strftime(
            "%Y-%m-%d"
        )
        return random_date

    def generate_last_seen_date(self, first_seen: str) -> str:
        """
        Generate `last_seen` timestamp
        between `first_seen` and current date
        """
        fs = datetime.strptime(first_seen, "%Y-%m-%d").date()
        end_date = datetime.now().date()
        last_seen = self.generate_date_between_dates(start_date=fs, end_date=end_date)
        return last_seen

    def generate_bool(self) -> bool:
        random_bool: int = random.getrandbits(1)
        if random_bool == 0:
            return False
        else:
            return True

    def generate_random_int(self, min: int = 0, max: int = 1000) -> int:
        return random.randint(min, max)
