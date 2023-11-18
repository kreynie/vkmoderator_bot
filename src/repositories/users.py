from src.database.models.user import User as UserModel
from src.utils.repository import SQLAlchemyRepository


class UsersRepository(SQLAlchemyRepository):
    model = UserModel
