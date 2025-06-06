import logging
import sys

from app.core.config import settings


def setup_logging() -> None:
    """Set up logging configuration."""
    if logging.getLogger().hasHandlers():  # 检查是否已配置
        return
    format_string = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    logging.basicConfig(
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
        format=format_string,
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)