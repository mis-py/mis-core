import dataclasses


@dataclasses.dataclass
class ModuleDependency:
    module_name: str
    module_version: str
