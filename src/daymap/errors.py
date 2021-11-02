
class DaymapException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    def __int__(self) -> int:
        return 418 # HTTP 418 I'm a teapot (don't instantiate this class)

# exception for when daymap messed up
class ServerFault(DaymapException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    def __int__(self) -> int:
        return 500 # HTTP 500 Server Fault

# something unexpected happened, daymap's api probably changed ;-;


class OurFault(DaymapException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
    
    def __int__(self) -> int:
        return 502 # HTTP 500 Bad Gateway (daymap acting up)

# the user just didn't enter the correct credentials, what can ya do?


class InvalidCredentials(DaymapException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    def __int__(self) -> int:
        return 401 # HTTP 401 Unauthorized (bad credentials)
