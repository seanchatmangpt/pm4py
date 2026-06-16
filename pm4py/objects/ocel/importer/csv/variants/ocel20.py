from enum import Enum
from typing import Optional, Dict, Any, List, Tuple
import json

import pandas as pd

from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.ocel import constants
from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.ocel.util import filtering_utils, ocel_consistency
from pm4py.util import exec_utils, constants as pm4_constants, pandas_utils


class Parameters(Enum):
    EVENT_ID = constants.PARAM_EVENT_ID
    EVENT_ACTIVITY = constants.PARAM_EVENT_ACTIVITY
    EVENT_TIMESTAMP = constants.PARAM_EVENT_TIMESTAMP
    OBJECT_ID = constants.PARAM_OBJECT_ID
    OBJECT_TYPE = constants.PARAM_OBJECT_TYPE
    INTERNAL_INDEX = constants.PARAM_INTERNAL_INDEX
    QUALIFIER = constants.PARAM_QUALIFIER
    CHANGED_FIELD = constants.PARAM_CHNGD_FIELD
    ENCODING = "encoding"
    OBJECT_TYPE_PREFIX = "object_type_prefix"
    O2O_ACTIVITY = "o2o_activity"
    CSV_EVENT_ID = "csv_event_id"
    CSV_EVENT_ACTIVITY = "csv_event_activity"
    CSV_EVENT_TIMESTAMP = "csv_event_timestamp"


def _is_empty(value) -> bool:
    if value is None:
        return True
    try:
        if pd.isna(value):
            return True
    except BaseException:
        pass
    return str(value) == ""


def _split_entries(value: Any) -> List[str]:
    if _is_empty(value):
        return []

    value = str(value)
    entries = []
    current = []
    in_string = False
    escape = False
    json_depth = 0

    for char in value:
        if escape:
            current.append(char)
            escape = False
            continue
        if char == "\\":
            current.append(char)
            if in_string:
                escape = True
            continue
        if char == '"':
            current.append(char)
            if json_depth > 0:
                in_string = not in_string
            continue
        if not in_string:
            if char == "{":
                json_depth += 1
            elif char == "}" and json_depth > 0:
                json_depth -= 1
            elif char == "/" and json_depth == 0:
                entry = "".join(current)
                if entry:
                    entries.append(entry)
                current = []
                continue
        current.append(char)

    entry = "".join(current)
    if entry:
        entries.append(entry)
    return entries


def _split_reference(value: str) -> Tuple[str, Optional[str], Dict[str, Any]]:
    attrs = {}
    value = value.strip()

    if value.endswith("}"):
        json_start = value.find("{")
        if json_start >= 0:
            json_part = value[json_start:]
            value = value[:json_start]
            if json_part:
                attrs = json.loads(json_part)

    if "#" in value:
        object_id, qualifier = value.split("#", 1)
    else:
        object_id, qualifier = value, None

    return object_id, qualifier, attrs


def _instantiate_dataframe(records: List[Dict[str, Any]], columns: List[str]):
    if records:
        return pandas_utils.instantiate_dataframe(records)
    return pandas_utils.instantiate_dataframe({column: [] for column in columns})


def _normalize_timestamp_columns(df, timestamp_column):
    if len(df) == 0 or timestamp_column not in df.columns:
        return df
    return dataframe_utils.convert_timestamp_columns_in_df(
        df,
        timest_format=pm4_constants.DEFAULT_TIMESTAMP_PARSE_FORMAT,
        timest_columns=[timestamp_column],
    )


def _collect_object_attribute(
    object_attributes: Dict[Tuple[str, str], List[Tuple[int, Any, Any]]],
    object_id: str,
    attribute: str,
    timestamp: Any,
    value: Any,
    index: int,
):
    object_attributes.setdefault((object_id, attribute), []).append((index, timestamp, value))


def apply(
    file_path: str,
    objects_path: str = None,
    parameters: Optional[Dict[Any, Any]] = None,
) -> OCEL:
    """
    Imports an OCEL 2.0 object-centric event log from the compact CSV format.
    """
    if parameters is None:
        parameters = {}

    encoding = exec_utils.get_param_value(
        Parameters.ENCODING, parameters, pm4_constants.DEFAULT_ENCODING
    )
    event_id_column = exec_utils.get_param_value(
        Parameters.EVENT_ID, parameters, constants.DEFAULT_EVENT_ID
    )
    event_activity_column = exec_utils.get_param_value(
        Parameters.EVENT_ACTIVITY, parameters, constants.DEFAULT_EVENT_ACTIVITY
    )
    event_timestamp_column = exec_utils.get_param_value(
        Parameters.EVENT_TIMESTAMP, parameters, constants.DEFAULT_EVENT_TIMESTAMP
    )
    object_id_column = exec_utils.get_param_value(
        Parameters.OBJECT_ID, parameters, constants.DEFAULT_OBJECT_ID
    )
    object_type_column = exec_utils.get_param_value(
        Parameters.OBJECT_TYPE, parameters, constants.DEFAULT_OBJECT_TYPE
    )
    internal_index_column = exec_utils.get_param_value(
        Parameters.INTERNAL_INDEX, parameters, constants.DEFAULT_INTERNAL_INDEX
    )
    qualifier_column = exec_utils.get_param_value(
        Parameters.QUALIFIER, parameters, constants.DEFAULT_QUALIFIER
    )
    changed_field_column = exec_utils.get_param_value(
        Parameters.CHANGED_FIELD, parameters, constants.DEFAULT_CHNGD_FIELD
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

    table = pandas_utils.read_csv(file_path, index_col=False, encoding=encoding, dtype=str)
    table = table.fillna("")
    object_type_columns = [
        column for column in table.columns if str(column).startswith(object_type_prefix)
    ]
    event_attribute_columns = [
        column
        for column in table.columns
        if column not in {csv_event_id, csv_event_activity, csv_event_timestamp}
        and column not in object_type_columns
    ]

    events = []
    relations = []
    o2o = []
    object_id_type = {}
    object_attributes = {}
    object_source_ids = set()

    for index, row in table.iterrows():
        row_id = row.get(csv_event_id, "")
        row_activity = row.get(csv_event_activity, "")
        row_timestamp = row.get(csv_event_timestamp, "")

        is_o2o_row = row_activity == o2o_activity and not row_timestamp
        is_object_attribute_row = not row_id and not row_activity and bool(row_timestamp)
        is_event_row = bool(row_id) and bool(row_activity) and bool(row_timestamp) and not is_o2o_row

        if is_event_row:
            event = {
                event_id_column: row_id,
                event_activity_column: row_activity,
                event_timestamp_column: row_timestamp,
            }
            for column in event_attribute_columns:
                if not _is_empty(row.get(column, "")):
                    event[column] = row[column]
            events.append(event)

        if is_o2o_row:
            object_source_ids.add(row_id)

        for column in object_type_columns:
            object_type = str(column)[len(object_type_prefix):]
            for entry in _split_entries(row.get(column, "")):
                object_id, qualifier, attrs = _split_reference(entry)
                if not object_id:
                    continue

                object_id_type[object_id] = object_type

                if is_event_row:
                    relations.append(
                        {
                            event_id_column: row_id,
                            event_activity_column: row_activity,
                            event_timestamp_column: row_timestamp,
                            object_id_column: object_id,
                            object_type_column: object_type,
                            qualifier_column: "" if qualifier is None else qualifier,
                        }
                    )
                    for attr, value in attrs.items():
                        _collect_object_attribute(
                            object_attributes, object_id, attr, row_timestamp, value, index
                        )
                elif is_o2o_row:
                    o2o.append(
                        {
                            object_id_column: row_id,
                            object_id_column + "_2": object_id,
                            qualifier_column: "" if qualifier is None else qualifier,
                        }
                    )
                    for attr, value in attrs.items():
                        _collect_object_attribute(
                            object_attributes, object_id, attr, None, value, index
                        )
                elif is_object_attribute_row:
                    for attr, value in attrs.items():
                        _collect_object_attribute(
                            object_attributes, object_id, attr, row_timestamp, value, index
                        )

    for source_id in object_source_ids:
        object_id_type.setdefault(source_id, None)

    events_df = _instantiate_dataframe(
        events, [event_id_column, event_activity_column, event_timestamp_column]
    )
    relations_df = _instantiate_dataframe(
        relations,
        [
            event_id_column,
            event_activity_column,
            event_timestamp_column,
            object_id_column,
            object_type_column,
            qualifier_column,
        ],
    )
    o2o_df = _instantiate_dataframe(
        o2o, [object_id_column, object_id_column + "_2", qualifier_column]
    )

    events_df = _normalize_timestamp_columns(events_df, event_timestamp_column)
    relations_df = _normalize_timestamp_columns(relations_df, event_timestamp_column)

    if object_id_type:
        object_records = []
        for object_id, object_type in object_id_type.items():
            object_records.append(
                {object_id_column: object_id, object_type_column: object_type}
            )
    else:
        object_records = []

    object_changes = []
    object_records_by_id = {record[object_id_column]: record for record in object_records}

    for (object_id, attr), values in object_attributes.items():
        values = sorted(values, key=lambda item: (str(item[1]) if item[1] is not None else "", item[0]))
        object_type = object_id_type.get(object_id)
        if object_id not in object_records_by_id:
            object_records_by_id[object_id] = {
                object_id_column: object_id,
                object_type_column: object_type,
            }

        _, first_timestamp, first_value = values[0]
        object_records_by_id[object_id][attr] = first_value

        for _, timestamp, value in values[1:]:
            change = {
                object_id_column: object_id,
                object_type_column: object_type,
                event_timestamp_column: timestamp,
                changed_field_column: attr,
                attr: value,
            }
            object_changes.append(change)

    objects_df = _instantiate_dataframe(
        list(object_records_by_id.values()), [object_id_column, object_type_column]
    )
    object_changes_df = _instantiate_dataframe(
        object_changes,
        [object_id_column, object_type_column, event_timestamp_column, changed_field_column],
    )
    object_changes_df = _normalize_timestamp_columns(object_changes_df, event_timestamp_column)

    if len(events_df) > 0:
        events_df[internal_index_column] = events_df.index
        events_df = events_df.sort_values([event_timestamp_column, internal_index_column])
        del events_df[internal_index_column]

    if len(relations_df) > 0:
        relations_df[internal_index_column] = relations_df.index
        relations_df = relations_df.sort_values([event_timestamp_column, internal_index_column])
        del relations_df[internal_index_column]

    if len(object_changes_df) > 0:
        object_changes_df[internal_index_column] = object_changes_df.index
        object_changes_df = object_changes_df.sort_values(
            [event_timestamp_column, internal_index_column]
        )
        del object_changes_df[internal_index_column]

    ocel = OCEL(
        events=events_df,
        objects=objects_df,
        relations=relations_df,
        o2o=o2o_df,
        object_changes=object_changes_df,
        parameters=parameters,
    )
    ocel = ocel_consistency.apply(ocel, parameters=parameters)
    ocel = filtering_utils.propagate_relations_filtering(ocel, parameters=parameters)

    return ocel
