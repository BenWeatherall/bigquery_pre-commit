from __future__ import annotations

import argparse
import os
import traceback
from typing import Sequence

from google.cloud import bigquery

# Setup Template string replace
TEMPLATE_FIND = r"__DATE_FILTER__"
TEMPLATE_REPLACE = '= CURRENT_DATE("Australia/Sydney")'

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
    def performDryRun(self, filename):
        # OPEN FILE
        query_text = ""
        try:
            with open(filename, 'r') as fi:
                query_text = fi.read()
                # perform replace
                query_text = query_text.replace(TEMPLATE_FIND, TEMPLATE_REPLACE)

        except SyntaxError:
            print(f'{filename} - Could not load query file')
            print()
            print('\t' + traceback.format_exc().replace('\n', '\n\t'))
            print()
            return 1

        # BUILD QUERY
        query_job = self.client.query(
            query=query_text, job_config=bq.config
        )  # API request

        if query_job.errors or query_job.error_result:
            print(f'{filename} - Dry run failed.')
            print()
            print('\t' + traceback.format_exc().replace('\n', '\n\t'))
            print()
            return 1

        # A dry run query completes immediately.
        if 'total_bytes_processed' in query_job:
            return 0

        return 1


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*", help="Filenames to run")
    args = parser.parse_args(argv)

    # Set Up Big Query
    project = os.environ.get("PROJECT_DEV")
    location = os.environ.get("REGION")
    bigQuery = bq(project, location)

    # Perform Check
    retv = 0
    for filename in args.filenames:
        retv |= bigQuery.performDryRun(filename)
    return retv


if __name__ == "__main__":
    raise SystemExit(main())
