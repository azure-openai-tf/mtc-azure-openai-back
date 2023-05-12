"""
@created_by ayaan
@created_at 2023.05.12
"""


class APIException(Exception):
    """Common Exception"""

    def __init__(self, code: int, message: str, error: str = ""):
        self.message = message
        self.code = code
        self.error = error
