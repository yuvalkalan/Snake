class Error(Exception):
    """Base class for other exceptions"""
    pass


class EscPressed(Error):
    """Raised when the user press esc"""
    pass


class QuitPressed(Error):
    """Raised when the user close the pygame window"""
    pass


class UserDsq(Error):
    """Raised when the game end"""
    pass


class SettingsChanged(Error):
    """Raised when the user change the settings"""
    pass


class LoginError(Error):
    """Raised when the user login details are wrong"""
