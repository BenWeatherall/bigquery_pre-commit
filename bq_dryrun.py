from __future__ import annotations

import argparse
import re
import traceback
from typing import Sequence

from google.cloud import bigquery


class bq:
    config = bigquery.QueryJobConfig(
        use_legacy_sql=False, use_query_cache=False, dry_run=True
    )

    def __init__(self, project, location):
        self.client = bigquery.Client(
            project=project,
            location=location,
        )

    # Functions
    def performDryRun(self, filename, replacement_pairs):
        # OPEN FILE
        query_text = ""
        try:
            with open(filename, "r") as fi:
                query_text = fi.read()
                # perform replace
                for pair in replacement_pairs:
                    query_text = query_text.replace(pair[0], pair[1])

        except SyntaxError:
            print(f"{filename} - Could not load query file")
            print()
            print("\t" + traceback.format_exc().replace("\n", "\n\t"))
            print()
            return 1

        # BUILD QUERY
        query_job = self.client.query(
            query=query_text, job_config=bq.config
        )  # API request

        if query_job.errors or query_job.error_result:
            print(f"{filename} - Dry run failed.")
            print()
            print("\t" + traceback.format_exc().replace("\n", "\n\t"))
            print()
            return 1

        # A dry run query completes immediately.
        if "total_bytes_processed" in query_job:
            return 0

        return 1

def findReplacePairs(args):
    pairs = []
    for arg in args:
        matches = re.findall(r'^([^"=]+|"(?:\\.|[^"])*")=([^"=]+|"(?:\\.|[^"])*")$', arg)
        if len(matches) == 2:
            pairs.append((matches[0], matches[1]))
        else:
            print("Malformed Pairs")

    return pairs

def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*", help="Filenames to run")
    parser.add_argument("--project", nargs="?", help="bq project",required=True)
    parser.add_argument("--region", nargs="?", help="bq region",required=True)
    parser.add_argument("--replace",
                        metavar="FIND=REPLACE",
                        nargs='+',
                        help="Set a number of find and replace statements"
                             "(if either value includes a space, define "
                             "it with double quotes: "
                             'replaceMe="replace Me". Note that '
                             "values are always treated as strings.")
    args = parser.parse_args(argv)

    # Set Up Big Query
    replacement_pairs = findReplacePairs(args.replace)
    big_query = bq(args.project, args.region)

    # Perform Check
    retv = 0
    for filename in args.filenames:
        retv |= big_query.performDryRun(filename, replacement_pairs)
    return retv


if __name__ == "__main__":
    raise SystemExit(main())
