from common.enums import CustomEnum


class RoleEnum(CustomEnum):
    Admin = 'Admin'
    Student = "Student"
    SuperAdmin = "SuperAdmin"


class BulkStatusEnum(CustomEnum):
    Started = "Started"
    Completed = "Completed"


TOKEN_TYPE = (
    ('LoginToken', 'LoginToken'),
)
