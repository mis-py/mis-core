from packaging.specifiers import SpecifierSet
from pydantic import BaseModel, Field, field_validator


class ModuleDependency(BaseModel):
    module: str
    version: str  # PEP 440 specifiers example: '==2.1.3' or '<=2.1.3,>=2.0.0'

    @field_validator('version')
    @classmethod
    def validate_version(cls, value: str) -> str:
        SpecifierSet(value)  # it raises ValueError if the version is invalid
        return value


class ModuleManifest(BaseModel):
    name: str
    display_name: str
    description: str
    version: str
    author: str
    category: str
    permissions: dict = Field(default_factory=dict)
    dependencies: list[ModuleDependency] = Field(default_factory=list)
    auth_disabled: bool
    extra: dict = Field(default_factory=dict)
