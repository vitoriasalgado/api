class DomainError(Exception):
    code: str = "DOMAIN_ERROR"

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NotFoundError(DomainError):
    code = "NOT_FOUND"


class ConflictError(DomainError):
    code = "CONFLICT"


class BusinessRuleError(DomainError):
    code = "BUSINESS_RULE_VIOLATION"
