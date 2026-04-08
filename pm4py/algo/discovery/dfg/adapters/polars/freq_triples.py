"""
PM4Py – A Process Mining Library for Python
Copyright (C) 2024 Process Intelligence Solutions

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
"""



from typing import Dict, Tuple

import polars as pl


def get_freq_triples(
    df: pl.LazyFrame,
    activity_key: str = "concept:name",
    case_id_glue: str = "case:concept:name",
    timestamp_key: str = "time:timestamp",
    sort_caseid_required: bool = True,
    sort_timestamp_along_case_id: bool = True,
) -> Dict[Tuple[str, str, str], int]:
    """Compute frequency triples directly on a Polars LazyFrame."""

    if sort_caseid_required:
        if sort_timestamp_along_case_id:
            df = df.sort([case_id_glue, timestamp_key])
        else:
            df = df.sort(case_id_glue)

    triples = df.with_columns(
        [
            pl.col(activity_key)
            .shift(-1)
            .over(case_id_glue)
            .alias(activity_key + "_2"),
            pl.col(activity_key)
            .shift(-2)
            .over(case_id_glue)
            .alias(activity_key + "_3"),
        ]
    )

    triples = triples.filter(
        pl.col(activity_key + "_2").is_not_null()
        & pl.col(activity_key + "_3").is_not_null()
    )

    grouped = (
        triples.group_by(
            [activity_key, activity_key + "_2", activity_key + "_3"]
        )
        .agg(pl.len().alias("count"))
        .collect()
    )

    return {
        (
            row[activity_key],
            row[activity_key + "_2"],
            row[activity_key + "_3"],
        ): row["count"]
        for row in grouped.iter_rows(named=True)
    }
