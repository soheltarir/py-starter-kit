from pydantic import EmailStr


class UserAlreadyExistsError(Exception):
    """Exception raised when trying to create a user that already exists."""

    def __init__(self, email: EmailStr):
        self.email = email
        super().__init__(f"User with email {email} already exists")


class UserNotFoundError(Exception):
    """Exception raised when a user is not found."""

    def __init__(self, user_id=None, email=None):
        if user_id:
            message = f"User with id {user_id} not found"
        elif email:
            message = f"User with email {email} not found"
        else:
            message = "User not found"
        super().__init__(message)
