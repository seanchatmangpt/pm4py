#!/usr/bin/env python3
import argparse

import pm4py
from pm4py.util import xes_constants
from collections import Counter
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


def build_prefix_onehot(log, activity_key):
    activities = sorted(
        {event[activity_key] for trace in log for event in trace if activity_key in event}
    )
    activity_to_index = {activity: idx for idx, activity in enumerate(activities)}

    feature = []
    target = []

    for trace in log:
        if len(trace) < 2:
            continue
        seen = set()
        for idx, event in enumerate(trace):
            if activity_key not in event:
                continue
            activity = event[activity_key]
            if idx == 0:
                seen.add(activity)
                continue
            row = [0] * len(activities)
            for seen_activity in seen:
                row[activity_to_index[seen_activity]] = 1
            feature.append(row)
            target.append(activity_to_index[activity])
            seen.add(activity)

    return feature, target, activities, activity_to_index


def main():
    parser = argparse.ArgumentParser(
        description=(
            "One-hot encode every prefix (length >= 2) of each trace using the "
            "activities up to the penultimate event, with the last event as class."
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
        "--show-sample",
        action="store_true",
        help="Print the first 5 feature rows and targets",
    )
    args = parser.parse_args()

    log = pm4py.read_xes(args.log_path, return_legacy_log_object=True)
    feature, target, activities, activity_to_index = build_prefix_onehot(
        log, args.activity_key
    )
    if not feature:
        raise SystemExit("No prefixes of length >= 2 found in the log.")

    class_counts = Counter(target)
    min_class = min(class_counts.values()) if class_counts else 0
    stratify = target if min_class >= 2 else None
    if stratify is None:
        print(
            "Warning: some classes have < 2 samples; "
            "disabling stratified split."
        )
    X_train, X_test, y_train, y_test = train_test_split(
        feature, target, test_size=0.2, random_state=42, stratify=stratify
    )
    clf = RandomForestClassifier(
        n_estimators=300, random_state=42, n_jobs=-1, class_weight="balanced"
    )
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"Log path: {args.log_path}")
    print(f"Activity key: {args.activity_key}")
    print(f"Activities: {len(activities)}")
    print(f"Samples (prefixes): {len(feature)}")
    print(f"Feature dimension: {len(activities)}")
    print(f"Target classes: {len(activity_to_index)}")
    print(f"Train size: {len(X_train)}")
    print(f"Test size: {len(X_test)}")
    print(f"Test accuracy: {accuracy:.4f}")

    if args.show_sample:
        print("Sample features (first 5 rows):")
        for row in feature[:5]:
            print(row)
        print("Sample targets (first 5):")
        print(target[:5])


if __name__ == "__main__":
    main()
