from core.repositories.variable import VariableRepository
from core.repositories.variable_value import VariableValueRepository
from core.services.variable import VariableService


# Put it to separate file to prevent from circular imports
def get_variable_service() -> VariableService:
    variable_value_repo = VariableValueRepository()
    variable_repo = VariableRepository()

    variable_service = VariableService(
        variable_value_repo=variable_value_repo,
        variable_repo=variable_repo
    )
    return variable_service
