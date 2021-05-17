import os
from dirhash import dirhash


def is_modified(cti_feeds_path: str):
    CURR_CHECKSUM = dirhash(cti_feeds_path, "md5", match=["*.csv"])
    CHKSUM_FILE: str = os.path.join(cti_feeds_path, ".checksum")

    def write_chksum(chksum_file: str, chksum) -> None:
        with open(chksum_file, "w") as file:
            file.write(chksum)
        print("[FEEDS] Checksum file has not found, generated a new one.")

    if os.path.isfile(CHKSUM_FILE):
        with open(CHKSUM_FILE, "r") as file:
            previous_chksum = file.read()

        if previous_chksum != CURR_CHECKSUM:
            print(
                "[FEEDS] Feeds have been modified. Started statistics recalculating..."
            )
            write_chksum(CHKSUM_FILE, CURR_CHECKSUM)
            return True
    else:
        write_chksum(CHKSUM_FILE, CURR_CHECKSUM)
        return True
