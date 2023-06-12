from datetime import date
from uuid import UUID

from ninja import Schema


class DepartmentIn(Schema):
    title: str


class DepartmentOut(Schema):
    id: UUID
    title: str


class EmployeeIn(Schema):
    first_name: str
    last_name: str
    department_id: UUID = None
    birthdate: date = None


class EmployeeOut(Schema):
    id: UUID
    first_name: str
    last_name: str
    department_id: UUID = None
    department: DepartmentOut = None
    birthdate: date = None
