import logging
import logging.config
import yaml
import pathlib
import functools

with open(pathlib.Path(__file__).parent.absolute() / "logging-config.yaml", 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)


def log_init(func, logger: logging.Logger):
    """
    log initialization of a class

    Use this method as a decorator to the __init__ - function of a class

    Parameters
    ----------
    logger: logging.Logger
        logging-instance

    Returns
    -------
    Callable
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f'Start initialize {args[0].__repr__()}')
        value = func(*args, **kwargs)
        if logger.level == logging.DEBUG and args[0].__str__() is not object.__str__:
            logger.debug(f'{args[0].__str__()}')
        else:
            logger.info(f'Finished {args[0].__repr__()}')
        return value

    return wrapper


def log_return(func, logger: logging.Logger):
    """
    log what a decorated function returns

    Use this method as a decorator of the function you want to log

    Parameters
    ----------
    logger: logging.Logger
        logging-instance

    Returns
    -------
    Callable
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        value = func(*args, **kwargs)
        logger.debug(f'{func.__qualname__}: {value}')
        return value

    return wrapper
