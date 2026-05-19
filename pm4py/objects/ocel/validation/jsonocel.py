import importlib.util
from pm4py.objects.ocel.util import compression


def apply(input_path, validation_path, parameters=None):
    if not importlib.util.find_spec("jsonschema"):
        raise Exception(
            "please install jsonschema in order to validate a JSONOCEL file."
        )

    import json
    import jsonschema
    from jsonschema import validate

    if parameters is None:
        parameters = {}

    with compression.open_text(input_path, "rt", encoding="utf-8") as F:
        file_content = json.load(F)
    with open(validation_path, "rb") as F:
        schema_content = json.load(F)
    try:
        validate(instance=file_content, schema=schema_content)
        return True
    except jsonschema.exceptions.ValidationError as err:
        return False
