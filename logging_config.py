from typing import Optional
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logging(app) -> None:
    """
    Configure logging for the Flask application.

    Args:
        app: Flask application instance
    """
    # Always configure console output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        )
    )
    console_handler.setLevel(logging.INFO)

    # Add console handler to app logger
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)

    # Add console handler to root logger as well
    logging.getLogger().addHandler(console_handler)
    logging.getLogger().setLevel(logging.INFO)

    # Only create log file in non-debug mode
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists("logs"):
            os.mkdir("logs")

        # Configure file handler with rotation
        file_handler = RotatingFileHandler(
            "logs/coi.log", maxBytes=10240, backupCount=10
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)

        # Add handler to app logger
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)

        # Also configure root logger for consistency
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]",
            handlers=[
                RotatingFileHandler("logs/coi.log", maxBytes=10240, backupCount=10),
                logging.StreamHandler(),  # Also log to console in production
            ],
        )

        app.logger.info("Application logging setup complete")
    else:
        # In debug mode, also configure basic logging to console
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]",
            handlers=[logging.StreamHandler()],  # Only console in debug mode
        )
        app.logger.info("Application logging setup complete (debug mode)")


def get_logger(name: Optional[str]) -> logging.Logger:
    """
    Get a logger instance for use in modules.

    Args:
        name: Name of the logger (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
