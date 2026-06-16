from enum import Enum
from typing import Optional, Dict, Any, List
import json

import pandas as pd

from pm4py.objects.ocel import constants
from pm4py.objects.ocel.exporter.util import clean_dataframes
from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.ocel.util import filtering_utils, ocel_consistency
from pm4py.util import exec_utils, constants as pm4_constants, pandas_utils


class Parameters(Enum):
    EVENT_ID = constants.PARAM_EVENT_ID
    EVENT_ACTIVITY = constants.PARAM_EVENT_ACTIVITY
    EVENT_TIMESTAMP = constants.PARAM_EVENT_TIMESTAMP
    OBJECT_ID = constants.PARAM_OBJECT_ID
    OBJECT_TYPE = constants.PARAM_OBJECT_TYPE
    QUALIFIER = constants.PARAM_QUALIFIER
    CHANGED_FIELD = constants.PARAM_CHNGD_FIELD
    ENCODING = "encoding"
    OBJECT_TYPE_PREFIX = "object_type_prefix"
    O2O_ACTIVITY = "o2o_activity"
    CSV_EVENT_ID = "csv_event_id"
    CSV_EVENT_ACTIVITY = "csv_event_activity"
    CSV_EVENT_TIMESTAMP = "csv_event_timestamp"


def _is_null(value) -> bool:
    return clean_dataframes.is_null(value)


def _format_timestamp(value) -> str:
    if _is_null(value):
        return ""
    try:
        timestamp = pd.Timestamp(value)
        if timestamp.tzinfo is not None:
            return timestamp.strftime("%Y-%m-%dT%H:%M:%S%z")
        return timestamp.isoformat()
    except BaseException:
        return str(value)


def _json_dumps(attrs: Dict[str, Any]) -> str:
    normalized = {
        key: clean_dataframes.normalize_value(value)
        for key, value in attrs.items()
        if not _is_null(value)
    }
    if not normalized:
        return ""
    return json.dumps(normalized, ensure_ascii=False, separators=(",", ":"))


def _format_reference(object_id: Any, qualifier: Any = None, attrs: Optional[Dict[str, Any]] = None) -> str:
    value = str(clean_dataframes.normalize_value(object_id))
    if not _is_null(qualifier) and str(qualifier) != "":
        value += "#" + str(clean_dataframes.normalize_value(qualifier))
    if attrs:
        value += _json_dumps(attrs)
    return value


def _non_ocel_attribute_columns(df: pd.DataFrame, reserved: List[str]) -> List[str]:
    return [
        column
        for column in df.columns
        if column not in reserved and not str(column).startswith("ocel:")
    ]


def apply(
    ocel: OCEL,
    output_path: str,
    objects_path=None,
    parameters: Optional[Dict[Any, Any]] = None,
):
    """
    Exports an OCEL 2.0 object-centric event log to the compact CSV format.
    """
    if parameters is None:
        parameters = {}

    encoding = exec_utils.get_param_value(
        Parameters.ENCODING, parameters, pm4_constants.DEFAULT_ENCODING
    )
    event_id_column = exec_utils.get_param_value(
        Parameters.EVENT_ID, parameters, ocel.event_id_column
    )
    event_activity_column = exec_utils.get_param_value(
        Parameters.EVENT_ACTIVITY, parameters, ocel.event_activity
    )
    event_timestamp_column = exec_utils.get_param_value(
        Parameters.EVENT_TIMESTAMP, parameters, ocel.event_timestamp
    )
    object_id_column = exec_utils.get_param_value(
        Parameters.OBJECT_ID, parameters, ocel.object_id_column
    )
    object_type_column = exec_utils.get_param_value(
        Parameters.OBJECT_TYPE, parameters, ocel.object_type_column
    )
    qualifier_column = exec_utils.get_param_value(
        Parameters.QUALIFIER, parameters, ocel.qualifier
    )
    changed_field_column = exec_utils.get_param_value(
        Parameters.CHANGED_FIELD, parameters, ocel.changed_field
    )
    object_type_prefix = exec_utils.get_param_value(
        Parameters.OBJECT_TYPE_PREFIX, parameters, "ot:"
    )
    o2o_activity = exec_utils.get_param_value(
        Parameters.O2O_ACTIVITY, parameters, "o2o"
    )
    csv_event_id = exec_utils.get_param_value(
        Parameters.CSV_EVENT_ID, parameters, "id"
    )
    csv_event_activity = exec_utils.get_param_value(
        Parameters.CSV_EVENT_ACTIVITY, parameters, "activity"
    )
    csv_event_timestamp = exec_utils.get_param_value(
        Parameters.CSV_EVENT_TIMESTAMP, parameters, "timestamp"
    )

    ocel = ocel_consistency.apply(ocel, parameters=parameters)
    ocel = filtering_utils.propagate_relations_filtering(ocel, parameters=parameters)

    object_types = sorted(
        str(x)
        for x in pandas_utils.format_unique(ocel.objects[object_type_column].dropna().unique())
    )
    object_type_columns = [object_type_prefix + object_type for object_type in object_types]

    event_attribute_columns = _non_ocel_attribute_columns(
        ocel.events, [event_id_column, event_activity_column, event_timestamp_column]
    )
    object_attribute_columns = _non_ocel_attribute_columns(
        ocel.objects, [object_id_column, object_type_column]
    )

    object_type = (
        ocel.objects[[object_id_column, object_type_column]]
        .drop_duplicates(subset=[object_id_column])
        .set_index(object_id_column)[object_type_column]
        .to_dict()
    )

    object_attrs = {}
    for record in ocel.objects.to_dict("records"):
        attrs = {}
        for column in object_attribute_columns:
            value = record.get(column)
            if not _is_null(value):
                attrs[column] = value
        if attrs:
            object_attrs[record[object_id_column]] = attrs

    attrs_emitted = set()
    event_relations = {}
    for record in ocel.relations.to_dict("records"):
        event_relations.setdefault(record[event_id_column], []).append(record)

    rows = []
    header = [csv_event_id, csv_event_activity, csv_event_timestamp] + event_attribute_columns + object_type_columns

    for event in ocel.events.to_dict("records"):
        row = {column: "" for column in header}
        event_id = event[event_id_column]
        row[csv_event_id] = event_id
        row[csv_event_activity] = event[event_activity_column]
        row[csv_event_timestamp] = _format_timestamp(event[event_timestamp_column])

        for column in event_attribute_columns:
            value = event.get(column)
            if not _is_null(value):
                row[column] = clean_dataframes.normalize_value(value)

        entries = {object_type: [] for object_type in object_types}
        for relation in event_relations.get(event_id, []):
            oid = relation[object_id_column]
            ot = relation.get(object_type_column, object_type.get(oid))
            if _is_null(ot):
                continue
            attrs = object_attrs.get(oid, {}) if oid not in attrs_emitted else {}
            if attrs:
                attrs_emitted.add(oid)
            entries.setdefault(str(ot), []).append(
                _format_reference(oid, relation.get(qualifier_column), attrs)
            )

        for ot, values in entries.items():
            if values:
                row[object_type_prefix + ot] = "/".join(values)
        rows.append(row)

    o2o_entries = {}
    for record in ocel.o2o.to_dict("records"):
        source_id = record.get(object_id_column)
        target_id = record.get(object_id_column + "_2")
        target_type = object_type.get(target_id)
        if _is_null(source_id) or _is_null(target_id) or _is_null(target_type):
            continue
        o2o_entries.setdefault(source_id, {}).setdefault(str(target_type), []).append(
            _format_reference(target_id, record.get(qualifier_column))
        )

    for source_id, entries in o2o_entries.items():
        row = {column: "" for column in header}
        row[csv_event_id] = source_id
        row[csv_event_activity] = o2o_activity
        for ot, values in entries.items():
            row[object_type_prefix + ot] = "/".join(values)
        rows.append(row)

    change_groups = {}
    for record in ocel.object_changes.to_dict("records"):
        oid = record.get(object_id_column)
        ot = record.get(object_type_column, object_type.get(oid))
        timestamp = record.get(event_timestamp_column)
        changed_field = record.get(changed_field_column)
        if _is_null(oid) or _is_null(ot) or _is_null(timestamp) or _is_null(changed_field):
            continue
        key = (_format_timestamp(timestamp), str(ot), oid)
        change_groups.setdefault(key, {})[changed_field] = record.get(changed_field)

    for (timestamp, ot, oid), attrs in sorted(change_groups.items(), key=lambda item: item[0]):
        row = {column: "" for column in header}
        row[csv_event_timestamp] = timestamp
        row[object_type_prefix + ot] = _format_reference(oid, attrs=attrs)
        rows.append(row)

    dataframe = pandas_utils.instantiate_dataframe(rows)
    if len(dataframe) == 0:
        dataframe = pandas_utils.instantiate_dataframe({column: [] for column in header})
    else:
        dataframe = dataframe[header]
    dataframe.to_csv(output_path, index=False, na_rep="", encoding=encoding)

    if objects_path is not None:
        ocel.objects.to_csv(objects_path, index=False, na_rep="", encoding=encoding)
