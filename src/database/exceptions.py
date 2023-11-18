class DatabaseException(Exception):
    pass


class EntityAlreadyExists(DatabaseException):
    pass


class EntityDoesNotExist(DatabaseException):
    pass


class MultipleEntityFound(DatabaseException):
    pass
