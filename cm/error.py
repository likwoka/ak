from quixote.errors import AccessError, TraversalError, SessionError

from psycopg import ProgrammingError  


class AKAccessError(AccessError):
    def __str__(self):
        return self.private_msg or self.public_msg \
               or self.description or "AKAccessError" 

class NotLoggedInError(AKAccessError):
    title = "Not Logged In Error"
    description = "You have attempted to reach a resource that " \
                  "is only available after you log in."

class NotEnoughDataError(AKAccessError):
    title = "Not Enough Data Error"
    description = "There is not enough data to complete your " \
                  "request."

class AccessNotAllowedError(AKAccessError):
    title = "Access Not Allowed Error"
    description = "You do not have access to this resource."


