"""
Tests for the apply() method implementations in pm4py case filter variants.

Covers:
- pandas variant: pm4py.algo.filtering.pandas.cases.case_filter
- log variant:    pm4py.algo.filtering.log.cases.case_filter
"""
import pandas as pd
import pytest

from pm4py.algo.filtering.pandas.cases import case_filter as pandas_case_filter
from pm4py.algo.filtering.log.cases import case_filter as log_case_filter
from pm4py.objects.log.obj import Event, EventLog, Trace


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_df():
    """Return a DataFrame with two distinct cases (3 events each)."""
    return pd.DataFrame(
        {
            "case:concept:name": ["A", "A", "A", "B", "B", "B"],
            "concept:name": ["start", "mid", "end"] * 2,
            "time:timestamp": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-03",
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-03",
                ]
            ),
        }
    )


def _make_log():
    """Return an EventLog with two traces ('case1' and 'case2')."""
    log = EventLog()
    for cid in ["case1", "case2"]:
        trace = Trace()
        trace.attributes["concept:name"] = cid
        for act in ["A", "B"]:
            event = Event({"concept:name": act})
            trace.append(event)
        log.append(trace)
    return log


# ---------------------------------------------------------------------------
# Pandas variant tests
# ---------------------------------------------------------------------------

class TestPandasCaseFilterApply:
    def test_keep_one_case(self):
        df = _make_df()
        result = pandas_case_filter.apply(df, ["A"])
        assert len(result) == 3
        assert set(result["case:concept:name"].unique()) == {"A"}

    def test_keep_other_case(self):
        df = _make_df()
        result = pandas_case_filter.apply(df, ["B"])
        assert len(result) == 3
        assert set(result["case:concept:name"].unique()) == {"B"}

    def test_keep_both_cases(self):
        df = _make_df()
        result = pandas_case_filter.apply(df, ["A", "B"])
        assert len(result) == 6

    def test_keep_no_cases(self):
        df = _make_df()
        result = pandas_case_filter.apply(df, [])
        assert len(result) == 0

    def test_keep_nonexistent_case(self):
        df = _make_df()
        result = pandas_case_filter.apply(df, ["X"])
        assert len(result) == 0

    def test_none_admitted_values(self):
        df = _make_df()
        result = pandas_case_filter.apply(df, None)
        assert len(result) == 0

    def test_attrs_preserved(self):
        df = _make_df()
        df.attrs["source"] = "test"
        result = pandas_case_filter.apply(df, ["A"])
        assert result.attrs.get("source") == "test"

    def test_custom_case_id_key(self):
        df = pd.DataFrame(
            {
                "my_case": ["X", "X", "Y"],
                "concept:name": ["A", "B", "A"],
            }
        )
        from pm4py.algo.filtering.pandas.cases.case_filter import Parameters
        result = pandas_case_filter.apply(
            df, ["X"], parameters={Parameters.CASE_ID_KEY: "my_case"}
        )
        assert len(result) == 2
        assert set(result["my_case"].unique()) == {"X"}


# ---------------------------------------------------------------------------
# Log (EventLog) variant tests
# ---------------------------------------------------------------------------

class TestLogCaseFilterApply:
    def test_keep_one_trace(self):
        log = _make_log()
        result = log_case_filter.apply(log, ["case1"])
        assert len(result) == 1
        assert result[0].attributes["concept:name"] == "case1"

    def test_keep_other_trace(self):
        log = _make_log()
        result = log_case_filter.apply(log, ["case2"])
        assert len(result) == 1
        assert result[0].attributes["concept:name"] == "case2"

    def test_keep_both_traces(self):
        log = _make_log()
        result = log_case_filter.apply(log, ["case1", "case2"])
        assert len(result) == 2

    def test_keep_no_traces(self):
        log = _make_log()
        result = log_case_filter.apply(log, [])
        assert len(result) == 0

    def test_keep_nonexistent_trace(self):
        log = _make_log()
        result = log_case_filter.apply(log, ["case999"])
        assert len(result) == 0

    def test_none_admitted_values(self):
        log = _make_log()
        result = log_case_filter.apply(log, None)
        assert len(result) == 0

    def test_result_is_event_log(self):
        log = _make_log()
        result = log_case_filter.apply(log, ["case1"])
        assert isinstance(result, EventLog)
