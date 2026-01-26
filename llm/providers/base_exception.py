class LLMException(Exception):
    """Base exception for all LLM-related failures"""
    pass

class LLMQuotaExceeded(Exception):
    """Raised when an LLM provider exhausts its free quota."""
    pass
class InvalidRequestError(LLMException):
    """Bad prompt or invalid parameters"""
    pass
class LLMModelUnavailable(Exception):
    pass
class LLMTransientError(Exception):
    pass
