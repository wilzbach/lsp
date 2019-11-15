from pytest import mark

from sls.services.types import TypeMappings

from storyhub.sdk.service.output import (
    OutputAny,
    OutputBoolean,
    OutputEnum,
    OutputFloat,
    OutputInt,
    OutputList,
    OutputMap,
    OutputNone,
    OutputObject,
    OutputRegex,
    OutputString,
)


@mark.parametrize(
    "ty,output",
    [
        (OutputAny(data=None), "any"),
        (OutputBoolean(data=None), "boolean"),
        (OutputEnum(data=None), "enum"),
        (OutputFloat(data=None), "float"),
        (OutputInt(data=None), "int"),
        (OutputList(OutputFloat(data=None), data=None), "List[float]"),
        (
            OutputMap(
                OutputInt(data=None), OutputString(data=None), data=None
            ),
            "Map[int,string]",
        ),
        (OutputNone(data=None), "none"),
        (OutputObject(properties={}, data=None), "object"),
        (OutputRegex(data=None), "regex"),
        (OutputString(data=None), "string"),
    ],
)
def test_get_type_string(ty, output):
    assert TypeMappings.get_type_string(ty) == output
