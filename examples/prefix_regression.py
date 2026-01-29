#!/usr/bin/env python3
import argparse
from collections import defaultdict

import pm4py
from pm4py.util import xes_constants
from sklearn.ensemble import RandomForestRegressor
from math import sqrt

from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split


def build_prefix_onehot_remaining_time(log, activity_key, timestamp_key):
    activities = sorted(
        {event[activity_key] for trace in log for event in trace if activity_key in event}
    )
    activity_to_index = {activity: idx for idx, activity in enumerate(activities)}

    feature = []
    target = []
    case_ids = []

    for trace_index, trace in enumerate(log):
        if len(trace) < 2:
            continue
        if timestamp_key not in trace[-1]:
            continue
        end_time = trace[-1][timestamp_key]
        trace_id = trace.attributes.get(
            xes_constants.DEFAULT_TRACEID_KEY, trace_index
        )
        seen = set()
        for idx, event in enumerate(trace):
            if activity_key not in event:
                continue
            activity = event[activity_key]
            if idx == 0:
                seen.add(activity)
                continue
            if timestamp_key not in event:
                seen.add(activity)
                continue
            row = [0] * len(activities)
            for seen_activity in seen:
                row[activity_to_index[seen_activity]] = 1
            remaining = (end_time - event[timestamp_key]).total_seconds()
            feature.append(row)
            target.append(remaining)
            case_ids.append(trace_id)
            seen.add(activity)

    return feature, target, case_ids, activities, activity_to_index


def main():
    parser = argparse.ArgumentParser(
        description=(
            "One-hot encode every prefix (length >= 2) of each trace using the "
            "activities up to the penultimate event, with remaining time to case end as target."
        )
    )
    parser.add_argument(
        "log_path",
        nargs="?",
        default="../tests/input_data/receipt.xes",
        help="Path to the XES log (default: tests/input_data/receipt.xes)",
    )
    parser.add_argument(
        "--activity-key",
        default=xes_constants.DEFAULT_NAME_KEY,
        help=f"Event attribute to use as activity (default: {xes_constants.DEFAULT_NAME_KEY})",
    )
    parser.add_argument(
        "--timestamp-key",
        default=xes_constants.DEFAULT_TIMESTAMP_KEY,
        help=f"Event attribute to use as timestamp (default: {xes_constants.DEFAULT_TIMESTAMP_KEY})",
    )
    parser.add_argument(
        "--show-sample",
        action="store_true",
        help="Print the first 5 feature rows and targets",
    )
    args = parser.parse_args()

    log = pm4py.read_xes(args.log_path, return_legacy_log_object=True)
    feature, target, case_ids, activities, activity_to_index = build_prefix_onehot_remaining_time(
        log, args.activity_key, args.timestamp_key
    )
    if not feature:
        raise SystemExit("No prefixes of length >= 2 with timestamps found in the log.")

    X_train, X_test, y_train, y_test, case_train, case_test = train_test_split(
        feature, target, case_ids, test_size=0.2, random_state=42
    )
    reg = RandomForestRegressor(
        n_estimators=300, random_state=42, n_jobs=-1
    )
    reg.fit(X_train, y_train)
    y_pred = reg.predict(X_test)

    abs_errors = [abs(y_true - y_hat) for y_true, y_hat in zip(y_test, y_pred)]
    sq_errors = [(y_true - y_hat) ** 2 for y_true, y_hat in zip(y_test, y_pred)]

    per_case_abs = defaultdict(list)
    per_case_sq = defaultdict(list)
    for case_id, ae, se in zip(case_test, abs_errors, sq_errors):
        per_case_abs[case_id].append(ae)
        per_case_sq[case_id].append(se)

    case_mae_values = [sum(vals) / len(vals) for vals in per_case_abs.values()]
    case_rmse_values = [sqrt(sum(vals) / len(vals)) for vals in per_case_sq.values()]

    mae = sum(case_mae_values) / len(case_mae_values)
    rmse = sum(case_rmse_values) / len(case_rmse_values)

    mae_hours = mae / 3600.0
    rmse_hours = rmse / 3600.0
    r2 = r2_score(y_test, y_pred)

    print(f"Log path: {args.log_path}")
    print(f"Activity key: {args.activity_key}")
    print(f"Timestamp key: {args.timestamp_key}")
    print(f"Activities: {len(activities)}")
    print(f"Samples (prefixes): {len(feature)}")
    print(f"Feature dimension: {len(activities)}")
    print(f"Train size: {len(X_train)}")
    print(f"Test size: {len(X_test)}")
    print(f"Per-case MAE (hours): {mae_hours:.4f}")
    print(f"Per-case RMSE (hours): {rmse_hours:.4f}")
    print(f"R2: {r2:.4f}")

    if args.show_sample:
        print("Sample features (first 5 rows):")
        for row in feature[:5]:
            print(row)
        print("Sample targets (first 5):")
        print(target[:5])


if __name__ == "__main__":
    main()
