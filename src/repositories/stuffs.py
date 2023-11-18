from src.database.models.stuff import Stuff as StuffModel
from src.utils.repository import SQLAlchemyRepository


class StuffsRepository(SQLAlchemyRepository):
    model = StuffModel
