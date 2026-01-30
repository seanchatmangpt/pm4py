#!/usr/bin/env python3
import argparse
import random
from collections import Counter

import pm4py
from pm4py.util import xes_constants
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

from prefix_feature_extraction import build_prefix_features_next_activity


def select_components_by_cumulative_variance(
    explained_variance_ratio, threshold=0.93
):
    cumulative = 0.0
    for idx, ratio in enumerate(explained_variance_ratio):
        cumulative += ratio
        if cumulative >= threshold:
            return idx + 1
    return len(explained_variance_ratio)


def fit_pca_with_variance_threshold(features, threshold=0.93):
    if not features:
        raise ValueError("No features provided for PCA fitting.")
    max_components = min(len(features), len(features[0]))
    if max_components <= 1:
        pca = PCA(n_components=1)
        pca.fit(features)
        return 1, pca
    pca_full = PCA(n_components=max_components, random_state=42)
    pca_full.fit(features)
    n_components = select_components_by_cumulative_variance(
        pca_full.explained_variance_ratio_.tolist(), threshold=threshold
    )
    pca = PCA(n_components=n_components, random_state=42)
    pca.fit(features)
    return n_components, pca


def sample_training_data(features, targets, percentage, rng):
    if percentage >= 100:
        return features, targets
    sample_size = max(1, int(round(len(features) * (percentage / 100.0))))
    indices = rng.sample(range(len(features)), sample_size)
    sampled_features = [features[i] for i in indices]
    sampled_targets = [targets[i] for i in indices]
    return sampled_features, sampled_targets


def train_classifier_random_forest(features, targets):
    clf = RandomForestClassifier(
        n_estimators=300, random_state=42, n_jobs=-1, class_weight="balanced"
    )
    clf.fit(features, targets)
    return clf


def train_pca_knn_classifier(features, targets):
    n_components, pca = fit_pca_with_variance_threshold(features, threshold=0.93)
    reduced = pca.transform(features)
    knn = KNeighborsClassifier(n_neighbors=1)
    knn.fit(reduced, targets)
    return {"pca": pca, "model": knn, "n_components": n_components}


def evaluate_classifier_random_forest(model, features, targets):
    predictions = model.predict(features)
    return accuracy_score(targets, predictions)


def evaluate_pca_knn_classifier(model_bundle, features, targets):
    reduced = model_bundle["pca"].transform(features)
    predictions = model_bundle["model"].predict(reduced)
    return accuracy_score(targets, predictions)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Encode every prefix of each trace using the activities and paths up to the "
            "penultimate event, plus time-based features, with the next event as class."
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
    (
        feature,
        target,
        activities,
        activity_to_index,
        paths,
        _,
    ) = build_prefix_features_next_activity(
        log, args.activity_key, args.timestamp_key
    )
    if not feature:
        raise SystemExit("No prefixes found in the log.")

    candidate_percentages = [5, 20, 100]

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

    print(f"Log path: {args.log_path}")
    print(f"Activity key: {args.activity_key}")
    print(f"Activities: {len(activities)}")
    print(f"Paths: {len(paths)}")
    print(f"Samples (prefixes): {len(feature)}")
    print(f"Feature dimension: {len(activities) + len(paths) + 3}")
    print(f"Target classes: {len(activity_to_index)}")
    print(f"Train size: {len(X_train)}")
    print(f"Test size: {len(X_test)}")

    rng = random.Random(42)
    for percentage in candidate_percentages:
        X_sampled, y_sampled = sample_training_data(
            X_train, y_train, percentage, rng
        )
        clf = train_classifier_random_forest(X_sampled, y_sampled)
        accuracy = evaluate_classifier_random_forest(clf, X_test, y_test)
        pca_knn = train_pca_knn_classifier(X_sampled, y_sampled)
        pca_accuracy = evaluate_pca_knn_classifier(pca_knn, X_test, y_test)
        print(f"Training sample %: {percentage}")
        print(f"Train size (sampled): {len(X_sampled)}")
        print(f"RF test accuracy: {accuracy:.4f}")
        print(
            f"PCA+kNN (k=1) test accuracy: {pca_accuracy:.4f} "
            f"(components: {pca_knn['n_components']})"
        )

    if args.show_sample:
        print("Sample features (first 5 rows):")
        for row in feature[:5]:
            print(row)
        print("Sample targets (first 5):")
        print(target[:5])


if __name__ == "__main__":
    main()
