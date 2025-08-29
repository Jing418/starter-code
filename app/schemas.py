from typing import Any, List, Optional
from datetime import datetime

from pydantic import BaseModel, field_validator, ConfigDict


class SchoolPostModel(BaseModel):
    name: str


class SchoolModel(SchoolPostModel):
    id: int
    classrooms: Optional[List[int]] = None
    user_accounts: Optional[List[int]] = None
    model_config = ConfigDict(from_attributes=True)

    @field_validator("classrooms", "user_accounts", mode="before")
    @classmethod
    def get_id(cls, value: Any) -> Optional[List[int]]:
        if value:
            return [item.id for item in value]
        return None


class SchoolUpdateModel(BaseModel):
    name: Optional[str] = None
    classrooms: Optional[List[int]] = None
    user_accounts: Optional[List[int]] = None


class ClassroomPostModel(BaseModel):
    name: str
    school_id: int


class ClassroomModel(ClassroomPostModel):
    id: int
    user_accounts: Optional[List[int]] = None
    model_config = ConfigDict(from_attributes=True)

    @field_validator("user_accounts", mode="before")
    @classmethod
    def get_id(cls, value: Any) -> Optional[List[int]]:
        if value:
            return [item.id for item in value]
        return None


class ClassroomUpdateModel(BaseModel):
    name: Optional[str] = None
    user_accounts: Optional[List[int]] = None


class UserAccountPostModel(BaseModel):
    name: str
    email: str
    is_student: Optional[bool] = True
    school_id: int
    classrooms: Optional[List[int]] = None


class UserAccountModel(UserAccountPostModel):
    id: int
    model_config = ConfigDict(from_attributes=True)

    @field_validator("classrooms", mode="before")
    @classmethod
    def get_id(cls, value: Any) -> Optional[List[int]]:
        if value:
            return [item.id for item in value]
        return None


class UserAccountUpdateModel(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    is_student: Optional[bool] = None


class AssignmentPostModel(BaseModel):
    title: str
    body: str
    submission_date: datetime
    classroom_id: int
    student_id: int


class AssignmentModel(AssignmentPostModel):
    id: int
    model_config = ConfigDict(from_attributes=True)


class AssignmentUpdateModel(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    submission_date: Optional[datetime] = None
    classroom_id: Optional[int] = None
    student_id: Optional[int] = None
