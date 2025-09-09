import logging
import logging.handlers
from pathlib import Path
from datetime import datetime


def setup_logging(log_level="INFO", log_dir=None):
    if log_dir is None:
        log_dir = Path(__file__).parent.parent / "logs"

    log_dir = Path(log_dir)
    log_dir.mkdir(exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.handlers.clear()


    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)


    log_file = log_dir / f"nutrition_bot_{datetime.now().strftime('%d%m%Y')}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes = 10*1024*1024,  # 10 МБ
        backupCount = 5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


    error_file = log_dir / f"errors_{datetime.now().strftime('%d%m%Y')}.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_file,
        maxBytes=5*1024*1024, # 5 МБ
        backupCount = 3,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    logging.info("Логирование настроено успешно")



