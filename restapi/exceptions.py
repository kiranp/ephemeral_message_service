from functools import wraps
from django.db import IntegrityError, DatabaseError, DataError
from django_redis.exceptions import ConnectionInterrumped

class EphemeralMessageError(Exception):

    """Base class for Local Listings exceptions"""
    pass


def handle_api_exceptions(f):
    """
    API exceptions decorator.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ConnectionInterrumped as conn_error:
            raise EphemeralMessageError("Unable to connect to data store {0}".format(conn_error))
        except IntegrityError:
            raise EphemeralMessageError("Data integrity error")
        except DataError:
            raise EphemeralMessageError("Data error")
        except DatabaseError:
            raise EphemeralMessageError("Database error")

    return wrapper
