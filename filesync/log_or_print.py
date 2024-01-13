import logging


def log_or_print(logger, message, level='info'):
    # if the message will show up in the logs, then log it
    # if the message won't show up in the logs, then print it
    level = level.upper()
    if logger.getEffectiveLevel() > getattr(logging, level):
        print(message)
    else:
        logger.log(getattr(logging, level), message)
