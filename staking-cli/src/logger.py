import logging
from re import A
from rich.logging import RichHandler

def init_logging(log_level):
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    log = logging.getLogger("rich")
    return log
