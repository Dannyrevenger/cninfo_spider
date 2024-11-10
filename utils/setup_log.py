import logging
from logging.handlers import TimedRotatingFileHandler
from colorama import Fore, Style, init
import os
from datetime import datetime

# Initialize colorama for cross-platform support
init(autoreset=True)

# Define a custom logging level for "SUCCESS"
SUCCESS_LEVEL_NUM = 25  # Define success level, between INFO (20) and WARNING (30)
logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")


# Define a logg success method
def success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kwargs)


# Add the success method to the logger
logging.Logger.success = success


# Custom formatter to apply colors to different log levels
class CustomFormatter(logging.Formatter):
    # Define colors for each log level
    COLORS = {
        logging.DEBUG: Style.DIM + Fore.WHITE,
        logging.INFO: Fore.CYAN,
        SUCCESS_LEVEL_NUM: Fore.LIGHTGREEN_EX,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Style.BRIGHT + Fore.RED,
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelno, Fore.WHITE)
        formatter = logging.Formatter(f'{log_color}%(asctime)s - %(levelname)s - %(message)s{Style.RESET_ALL}')
        return formatter.format(record)


# Setup logger function
def setup_logger(log_file_path):
    """
    Sets up the logger to write log messages to a file and console, with colored output for the console.
    """
    logger = logging.getLogger('my_logger')
    logger.setLevel(logging.DEBUG)

    # File handler to write to the log file
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Console handler for colored output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(CustomFormatter())

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# 创建日志文件目录
log_directory = "./log"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# 获取当前日期，并格式化为日志文件名的一部分
current_date = datetime.now().strftime("%Y-%m-%d")
log_file = os.path.join(log_directory, f"{current_date}.log")
# 创建日志记录器，并设置日志级别
logger = logging.getLogger("cninfo_logger")
logger.setLevel(logging.DEBUG)

# 设置日志文件按天轮换，并保留30天的日志文件
handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=30, encoding="utf-8")
handler.suffix = "%Y-%m-%d"  # 确保文件名按日期格式化
handler.setLevel(logging.DEBUG)

# 创建日志格式
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# 将处理器添加到日志记录器
logger.addHandler(handler)
logger = setup_logger(log_file)


