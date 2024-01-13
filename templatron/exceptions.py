class TemplatronException(Exception):
    pass


class AmbiguousOrgConfigError(TemplatronException):
    pass


class DirtyRepoError(TemplatronException):
    pass


class GitConfigError(TemplatronException):
    pass


class HookFailure(TemplatronException):
    pass


class MissingRequiredConfigError(TemplatronException):
    pass


class TemplateConfigMissingError(TemplatronException):
    pass


class UnrecognizableBaseBranchError(TemplatronException):
    pass


class UnrecognizedRepoConfigError(TemplatronException):
    pass
