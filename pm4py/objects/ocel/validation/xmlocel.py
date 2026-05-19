import importlib.util
from pm4py.objects.ocel.util import compression


def apply(input_path, validation_path, parameters=None):
    if not importlib.util.find_spec("lxml"):
        raise Exception(
            "please install lxml in order to validate an XMLOCEL file."
        )

    import lxml.etree

    if parameters is None:
        parameters = {}

    with compression.open_binary(input_path, "rb") as F:
        xml_file = lxml.etree.parse(F)
    xml_validator = lxml.etree.XMLSchema(file=validation_path)
    is_valid = xml_validator.validate(xml_file)
    return is_valid
