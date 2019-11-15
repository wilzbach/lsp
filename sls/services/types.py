# -*- coding: utf-8 -*-
from storyhub.sdk.service.output import (
    OutputAny,
    OutputBase,
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


class TypeMappings:
    @classmethod
    def get_type_string(cls, ty):
        """
        Maps a type class from the hub SDK to its corresponding TypeClass
        in the compiler.
        """
        assert isinstance(ty, OutputBase), ty
        if isinstance(ty, OutputBoolean):
            return "boolean"
        if isinstance(ty, OutputInt):
            return "int"
        if isinstance(ty, OutputFloat):
            return "float"
        if isinstance(ty, OutputString):
            return "string"
        if isinstance(ty, OutputAny):
            return "any"
        if isinstance(ty, OutputObject):
            return "object"
        if isinstance(ty, OutputList):
            elements = cls.get_type_string(ty.elements())
            return f"List[{elements}]"
        if isinstance(ty, OutputNone):
            return "none"
        if isinstance(ty, OutputRegex):
            return "regex"
        if isinstance(ty, OutputEnum):
            return "enum"

        assert isinstance(ty, OutputMap), f"Unknown Hub Type: {ty!r}"
        keys = cls.get_type_string(ty.keys())
        values = cls.get_type_string(ty.values())
        return f"Map[{keys},{values}]"
