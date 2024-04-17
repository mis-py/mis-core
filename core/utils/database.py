from enum import Enum


class SettingType(str, Enum):
    str = "str"
    int = "int"
    float = "float"
    bool = "bool"


