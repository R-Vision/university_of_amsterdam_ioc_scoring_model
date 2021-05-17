import os
import json
from argparse import ArgumentParser
import scoring_engine as engine

argparser = ArgumentParser()

argparser.add_argument(
    "path",
    help="Path the directory with the CTI feeds",
)
argparser.add_argument(
    "--file",
    action="store_true",
    dest="file",
    default=None,
    help="Dump output to the file",
)


args = argparser.parse_args()
FEED_PATH: str = os.path.abspath(os.path.join(os.getcwd(), args.path))

print("Calculate iocs score for", FEED_PATH)
result = engine.calculate_iocs_score(FEED_PATH)
print("\n", result, "\n")

if args.file:
    workdir: str = os.path.abspath(os.getcwd())
    filename: str = os.path.basename(FEED_PATH) + ".json"
    with open(
        os.path.join(workdir, filename),
        "w",
    ) as file:
        file.write(json.dumps(result))
