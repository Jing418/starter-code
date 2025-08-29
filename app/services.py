from typing import Annotated, List, Optional

from fastapi import Depends
from sqlalchemy import Sequence, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import Classroom, School, UserAccount, Assignment
from app.dependencies import get_database
from app.exceptions import ServiceException
from app.schemas import (
    ClassroomPostModel,
    ClassroomUpdateModel,
    SchoolPostModel,
    SchoolUpdateModel,
    UserAccountPostModel,
    UserAccountUpdateModel,
    AssignmentPostModel,
    AssignmentUpdateModel,
)


class BaseService:
    def __init__(self, database: Session) -> None:
        self.database = database


class SchoolService(BaseService):
    def get(self, id: int) -> Optional[School]:
        stmt = select(School).where(School.id == id)
        return self.database.scalar(stmt)

    def get_list(self, ids: Optional[List[int]] = None) -> Sequence[School]:
        stmt = select(School)
        if ids:
            stmt = stmt.where(School.id.in_(ids))

        return self.database.scalars(stmt).all()

    def create(self, data: SchoolPostModel) -> School:
        school = School(name=data.name)
        try:
            self.database.add(school)
            self.database.commit()
        except IntegrityError:
            self.database.rollback()
            raise ServiceException(f"Could not Create {data.name}")
        self.database.refresh(school)
        return school

    def update(self, id: int, data: SchoolUpdateModel) -> Optional[School]:
        if school := self.database.scalar(select(School).where(School.id == id)):
            if data.name:
                school.name = data.name
            if data.classrooms:
                classrooms = self.database.scalars(
                    select(Classroom).where(Classroom.id.in_(data.classrooms))
                ).all()
                school.classrooms = classrooms
            if data.user_accounts:
                user_accounts = self.database.scalars(
                    select(UserAccount).where(UserAccount.id.in_(data.user_accounts))
                ).all()
                school.user_accounts = user_accounts

            try:
                self.database.commit()
            except IntegrityError:
                self.database.rollback()
                raise ServiceException(f"Could not Update {school.name}")
            return school

        return None

    def delete(self, id: int) -> None:
        if school := self.database.scalar(select(School).where(School.id == id)):
            try:
                self.database.delete(school)
                self.database.commit()
            except IntegrityError:
                self.database.rollback()
                raise ServiceException(f"Failed to delete {school.name}")

        return None


class ClassroomService(BaseService):
    def get(self, id: int) -> Optional[Classroom]:
        stmt = select(Classroom).where(Classroom.id == id)
        return self.database.scalar(stmt)

    def get_list(self, ids: Optional[List[int]] = None) -> Sequence[Classroom]:
        stmt = select(Classroom)
        if ids:
            stmt = stmt.where(Classroom.id.in_(ids))

        return self.database.scalars(stmt).all()

    def create(self, data: ClassroomPostModel) -> Classroom:
        classroom = Classroom(name=data.name, school_id=data.school_id)
        try:
            self.database.add(classroom)
            self.database.commit()
        except IntegrityError:
            self.database.rollback()
            raise ServiceException(f"Could not Create {data.name}")

        self.database.refresh(classroom)
        return classroom

    def update(self, id: int, data: ClassroomUpdateModel) -> Optional[Classroom]:
        if classroom := self.database.scalar(
            select(Classroom).where(Classroom.id == id)
        ):
            if data.name:
                classroom.name = data.name
            if data.user_accounts:
                user_accounts = self.database.scalars(
                    select(UserAccount).where(UserAccount.id.in_(data.user_accounts))
                ).all()
                classroom.user_accounts = user_accounts

            try:
                self.database.commit()
            except IntegrityError:
                self.database.rollback()
                raise ServiceException(f"Could not Update {classroom.name}")
            return classroom

        return None

    def delete(self, id: int) -> None:
        if classroom := self.database.scalar(
            select(Classroom).where(Classroom.id == id)
        ):
            try:
                self.database.delete(classroom)
                self.database.commit()
            except IntegrityError:
                self.database.rollback()
                raise ServiceException(f"Failed to delete {classroom.name}")

        return None


class UserAccountService(BaseService):
    def get(self, id: int) -> Optional[UserAccount]:
        stmt = select(UserAccount).where(UserAccount.id == id)
        return self.database.scalar(stmt)

    def get_list(self, ids: Optional[List[int]] = None) -> Sequence[UserAccount]:
        stmt = select(UserAccount)
        if ids:
            stmt = stmt.where(UserAccount.id.in_(ids))

        return self.database.scalars(stmt).all()

    def create(self, data: UserAccountPostModel) -> UserAccount:
        # Guard classrooms selection when not provided or empty
        classrooms: List[Classroom] = []
        if data.classrooms:
            classrooms = self.database.scalars(
                select(Classroom).where(Classroom.id.in_(data.classrooms))
            ).all()

        # Validate school exists
        school = None
        if data.school_id is not None:
            school = self.database.scalar(select(School).where(School.id == data.school_id))
            if not school:
                raise ServiceException("School does not exist")
        user_account = UserAccount(
            name=data.name,
            email=data.email,
            is_student=data.is_student,
            school_id=data.school_id,
            classrooms=classrooms,
        )
        try:
            self.database.add(user_account)
            self.database.commit()
        except IntegrityError:
            self.database.rollback()
            raise ServiceException(f"Could not create {data.name}")

        self.database.refresh(user_account)

        return user_account

    def update(self, id: int, data: UserAccountUpdateModel) -> Optional[UserAccount]:
        if user_account := self.database.scalar(
            select(UserAccount).where(UserAccount.id == id)
        ):
            if data.name:
                user_account.name = data.name
            if data.email:
                user_account.email = data.email
            if data.is_student is not None:
                user_account.is_student = data.is_student

            try:
                self.database.commit()
            except IntegrityError:
                self.database.rollback()
                raise ServiceException(f"Could not Update {user_account.name}")
            return user_account

        return None

    def delete(self, id: int) -> None:
        if user_account := self.database.scalar(
            select(UserAccount).where(UserAccount.id == id)
        ):
            try:
                self.database.delete(user_account)
                self.database.commit()
            except IntegrityError:
                self.database.rollback()
                raise ServiceException(f"Failed to delete {user_account.name}")

        return None


class AssignmentService(BaseService):
    def get(self, id: int) -> Optional[Assignment]:
        stmt = select(Assignment).where(Assignment.id == id)
        return self.database.scalar(stmt)

    def get_list(
        self,
        classroom_name: Optional[str] = None,
        student_name: Optional[str] = None,
        classroom_id: Optional[int] = None,
        student_id: Optional[int] = None,
    ) -> Sequence[Assignment]:
        stmt = select(Assignment)
        if classroom_id is not None:
            stmt = stmt.where(Assignment.classroom_id == classroom_id)
        if student_id is not None:
            stmt = stmt.where(Assignment.student_id == student_id)
        if classroom_name:
            stmt = stmt.join(Assignment.classroom).where(
                Classroom.name.ilike(f"%{classroom_name}%")
            )
        if student_name:
            stmt = stmt.join(Assignment.student).where(
                UserAccount.name.ilike(f"%{student_name}%")
            )
        return self.database.scalars(stmt).all()

    def create(self, data: AssignmentPostModel) -> Assignment:
        classroom = self.database.scalar(
            select(Classroom).where(Classroom.id == data.classroom_id)
        )
        if not classroom:
            raise ServiceException("Classroom does not exist")

        student = self.database.scalar(
            select(UserAccount).where(UserAccount.id == data.student_id)
        )
        if not student:
            raise ServiceException("Student does not exist")
        if not student.is_student:
            raise ServiceException("User must be a student")

        assignment = Assignment(
            title=data.title,
            body=data.body,
            submission_date=data.submission_date,
            classroom_id=data.classroom_id,
            student_id=data.student_id,
        )

        try:
            self.database.add(assignment)
            self.database.commit()
        except IntegrityError:
            self.database.rollback()
            raise ServiceException("Could not create assignment")

        self.database.refresh(assignment)
        return assignment

    def update(self, id: int, data: AssignmentUpdateModel) -> Optional[Assignment]:
        if assignment := self.database.scalar(
            select(Assignment).where(Assignment.id == id)
        ):
            if data.title is not None:
                assignment.title = data.title
            if data.body is not None:
                assignment.body = data.body
            if data.submission_date is not None:
                assignment.submission_date = data.submission_date
            if data.classroom_id is not None:
                classroom = self.database.scalar(
                    select(Classroom).where(Classroom.id == data.classroom_id)
                )
                if not classroom:
                    raise ServiceException("Classroom does not exist")
                assignment.classroom_id = data.classroom_id
            if data.student_id is not None:
                student = self.database.scalar(
                    select(UserAccount).where(UserAccount.id == data.student_id)
                )
                if not student:
                    raise ServiceException("Student does not exist")
                if not student.is_student:
                    raise ServiceException("User must be a student")
                assignment.student_id = data.student_id

            try:
                self.database.commit()
            except IntegrityError:
                self.database.rollback()
                raise ServiceException("Could not update assignment")
            return assignment

        return None

    def delete(self, id: int) -> None:
        if assignment := self.database.scalar(
            select(Assignment).where(Assignment.id == id)
        ):
            try:
                self.database.delete(assignment)
                self.database.commit()
            except IntegrityError:
                self.database.rollback()
                raise ServiceException("Failed to delete assignment")

        return None


class ServiceDependency:
    def __init__(self, class_name: str):
        self.service_class = globals().get(class_name)

    def __call__(self, db: Annotated[Session, Depends(get_database)]):
        return self.service_class(db)
