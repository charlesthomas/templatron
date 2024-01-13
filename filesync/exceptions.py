class FilesyncException(Exception):
    pass


class AmbiguousOrgConfigError(FilesyncException):
    pass


class DirtyRepoError(FilesyncException):
    pass


class GitConfigError(FilesyncException):
    pass


class HookFailure(FilesyncException):
    pass


class MissingRequiredConfigError(FilesyncException):
    pass


class TemplateConfigMissingError(FilesyncException):
    pass


class UnrecognizableBaseBranchError(FilesyncException):
    pass


class UnrecognizedRepoConfigError(FilesyncException):
    pass
