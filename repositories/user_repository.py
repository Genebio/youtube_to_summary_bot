from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.user_model import User
from typing import Optional, List
from utils.logger import logger

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Fetch a user based on username.
        Returns None if no user is found.
        """
        try:
            user = self.db.query(User).filter(User.username == username).first()
            if user:
                logger.info(f"Retrieved user with username '{username}'")
            else:
                logger.info(f"No user found with username '{username}'")
            return user
        except SQLAlchemyError as e:
            logger.error(f"Error fetching user by username: {str(e)}")
            return None

    def create_user(self, username: str, first_name: str = None, last_name: str = None, language_code: str = 'en') -> Optional[User]:
        """
        Create and save a new user. Requires a username and can take optional first/last name and language_code.
        """
        try:
            new_user = User(
                username=username,
                first_name=first_name,
                last_name=last_name,
                language_code=language_code
            )
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            logger.info(f"Created new user with username '{username}'")
            return new_user
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            return None

    def get_or_create_user(self, username: str, first_name: str = None, last_name: str = None,
                           language_code: str = 'en') -> Optional[User]:
        """
        Fetch a user by username. If the user doesn't exist, create a new one.
        """
        user = self.get_user_by_username(username)
        if not user:
            user = self.create_user(username, first_name, last_name, language_code)
        return user

    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """
        Update an existing user's information.
        """
        try:
            user = self.db.query(User).filter(User.user_id == user_id).first()
            if user:
                for key, value in kwargs.items():
                    setattr(user, key, value)
                self.db.commit()
                self.db.refresh(user)
                logger.info(f"Updated user with ID {user_id}")
                return user
            else:
                logger.warning(f"User with ID {user_id} not found")
                return None
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating user: {str(e)}")
            return None

    def delete_user(self, user_id: int) -> bool:
        """
        Delete a user by their ID.
        """
        try:
            user = self.db.query(User).filter(User.user_id == user_id).first()
            if user:
                self.db.delete(user)
                self.db.commit()
                logger.info(f"Deleted user with ID {user_id}")
                return True
            else:
                logger.warning(f"User with ID {user_id} not found")
                return False
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting user: {str(e)}")
            return False

    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """
        Fetch a list of all users with pagination.
        """
        try:
            users = self.db.query(User).order_by(User.created_at.desc()).limit(limit).offset(offset).all()
            logger.info(f"Retrieved {len(users)} users")
            return users
        except SQLAlchemyError as e:
            logger.error(f"Error fetching all users: {str(e)}")
            return []

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Fetch a user by their ID.
        """
        try:
            user = self.db.query(User).filter(User.user_id == user_id).first()
            if user:
                logger.info(f"Retrieved user with ID {user_id}")
            else:
                logger.info(f"No user found with ID {user_id}")
            return user
        except SQLAlchemyError as e:
            logger.error(f"Error fetching user by ID: {str(e)}")
            return None

    def update_user_language(self, user_id: int, language_code: str) -> Optional[User]:
        """
        Update a user's language code.
        """
        return self.update_user(user_id, language_code=language_code)

    def toggle_user_subscription(self, user_id: int) -> Optional[User]:
        """
        Toggle a user's subscription status.
        """
        try:
            user = self.get_user_by_id(user_id)
            if user:
                user.subscription = not user.subscription
                self.db.commit()
                self.db.refresh(user)
                logger.info(f"Toggled subscription for user with ID {user_id}")
                return user
            else:
                logger.warning(f"User with ID {user_id} not found")
                return None
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error toggling user subscription: {str(e)}")
            return None