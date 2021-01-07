class CommandInvokeError(Exception):
    pass

class MissingRequiredArgument(CommandInvokeError):
    pass

class TooManyArguments(CommandInvokeError):
    pass