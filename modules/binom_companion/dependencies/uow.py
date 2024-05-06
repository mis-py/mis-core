from typing import Annotated

from fastapi import Depends

from ..unit_of_work import IUnitOfWork, unit_of_work_factory

UnitOfWorkDep = Annotated[IUnitOfWork, Depends(unit_of_work_factory)]
