class BucketUtilsError(Exception):
    """Base class for all bucket utility errors."""
    pass


class AuthError(BucketUtilsError):
    """Problems with credentials / tokens."""
    pass


class FileNotFoundError(BucketUtilsError):
    """Remote object does not exist."""
    pass
