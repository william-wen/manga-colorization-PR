"""
General Error Handler where the purpose of the error can be specified by
the error-type field.
"""

class Error(Exception):
    def __init__(self, error_type, message, status_code):
        self.error_type = error_type
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        rv = {
            "error_type": self.error_type,
            "message": self.message,
            "status_code": self.status_code,
        }
        return rv
    
