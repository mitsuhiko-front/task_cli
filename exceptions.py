class TaskNotFoundError(Exception):
    pass

class UserNotFoundError(Exception):
    pass

class HeaderNotFoundError(Exception):
    pass

class AlreadyDeletedError(Exception):
    pass

class NotDeletedError(Exception):
    pass

class AutorizationError(Exception):
    pass
class AuthenticationError(Exception):
    pass