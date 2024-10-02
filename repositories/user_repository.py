from sqlalchemy.orm import Session
from models.user_model import User
from typing import Optional


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Fetch a user based on user_id.
        Returns None if no user is found.
        """
        return self.db.query(User).filter(User.user_id == user_id).first()

    def create_user(self, username: Optional[str] = None, first_name: Optional[str] = None, 
                    last_name: Optional[str] = None, language_code: str = 'en') -> User:
        """
        Create and save a new user. Allows username, first_name, and last_name to be None.
        
        If no username is provided, the field will be set to None, and it will not affect the unique constraint.
        """
        new_user = User(
            username=username,  # Can be None
            first_name=first_name,  # Can be None
            last_name=last_name,  # Can be None
            language_code=language_code  # Default is 'en' if not provided
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)  # This will populate the auto-incremented user_id
        return new_user

    def update_user_language(self, user_id: int, language_code: str) -> Optional[User]:
        """
        Update a user's language_code.
        Returns the updated user object or None if the user is not found.
        """
        user = self.get_user_by_id(user_id)

        if not user:
            return None

        user.language_code = language_code
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_language_code(self, user_id: int) -> Optional[str]:
        """
        Fetch the language code for a user by user_id.
        Returns the language code or None if the user is not found.
        """
        user = self.get_user_by_id(user_id)
        return user.language_code if user else None