import logging
import logging.config
import yaml
import pathlib
import functools

with open(pathlib.Path(__file__).parent.absolute() / "logging-config.yaml", "r") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)


def get_keyword_arguments(kwargs):
    arguments = [f"{k}={v}" for k, v in kwargs.items()]
    return f'({", ".join(arguments)})'


class LoggerMethods:
    """
    provides some methods to support logging

    .. versionadded:: 0.2.0

    The idea is to initialize this class within a module.
    It allows then to log for example the initialization of
    a class using :py:meth:`~m_n_kappa.log.LoggerMethods.init` as
    decorator.
    Or the result of a method by using :py:meth:`~m_n_kappa.log.LoggerMethods.result`
    as decoration of this specific function.

    Furthermore, the basic logging functions
    :py:meth:`~m_n_kappa.log.LoggerMethods.debug`,
    :py:meth:`~m_n_kappa.log.LoggerMethods.info`,
    :py:meth:`~m_n_kappa.log.LoggerMethods.warning`,
    :py:meth:`~m_n_kappa.log.LoggerMethods.error`,
    :py:meth:`~m_n_kappa.log.LoggerMethods.exception` and
    :py:meth:`~m_n_kappa.log.LoggerMethods.critical` are implemented to reduce
    the need for further imports.
    """
    def __init__(self, logger_name):
        """
        Parameters
        ----------
        logger_name : str
            name of the logger, ofter ``__name__`` on module-level
        """
        self._logger_name = logger_name
        self._logger = logging.getLogger(self.logger_name)

    @property
    def logger_name(self) -> str:
        """name of the logger"""
        return self._logger_name

    @property
    def logger(self):
        """logger"""
        return self._logger

    def init(self, func):
        """
        log initialization of a class

        Use this method as a decorator to the __init__ - function of a class

        Parameters
        ----------
        func : method
            method to log, here __init__

        Returns
        -------
        Callable
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            init_index = func.__qualname__.find(".__init__")
            is_calling_class = func.__qualname__[:init_index] == args[0].__class__.__name__
            if is_calling_class:
                self.logger.info(
                    f'Start initialize {args[0].__class__.__name__}{get_keyword_arguments(kwargs)}'
                )

            value = func(*args, **kwargs)

            if is_calling_class:
                if (
                        self.logger.level == logging.DEBUG
                        and args[0].__str__() is not object.__str__
                ):
                    self.debug(f"{args[0].__str__()}")
                else:
                    self.info(f"Finished {args[0].__repr__()}")

            return value

        return wrapper

    def result(self, func):
        """
        log what a decorated function returns

        Use this method as a decorator of the function you want to log

        Parameters
        ----------
        func : method
            method to log results

        Returns
        -------
        Callable
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            value = func(*args, **kwargs)
            self.debug(f"{func.__qualname__}{get_keyword_arguments(kwargs)}: -> {value}")
            return value

        return wrapper

    def debug(self, msg, *args, **kwargs):
        """copy of the ``logging.debug`` method"""
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """copy of the ``logging.info`` method"""
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """copy of the ``logging.warning`` method"""
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """copy of the ``logging.error`` method"""
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """copy of the ``logging.critical`` method"""
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        """copy of the ``logging.exception`` method"""
        self.logger.exception(msg, *args, **kwargs)

