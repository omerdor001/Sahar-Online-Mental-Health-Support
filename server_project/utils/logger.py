import glob
import logging
import os
import re
import time
import threading
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler

from utils.config_util import ConfigUtil


class Logger:
    def __init__(self):
        log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        log_handler = TimedRotatingFileHandler(
            "logs/app.log",
            when="midnight",
            interval=1,
            backupCount=ConfigUtil().get_config_attribute("maxLogFile")
        )
        log_handler.setFormatter(log_formatter)

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(log_handler)

        self._start_cleanup_thread()

    def _start_cleanup_thread(self):
        self.cleanup_thread_2 = threading.Thread(target=self.clean_conversation_log)
        self.cleanup_thread_2.daemon = True
        self.cleanup_thread_2.start()

    def clean_conversation_log(self):
        while True:
            try:
                time.sleep(
                    int(ConfigUtil().get_config_attribute("deleteThreadLogsInterval")))  # Sleep for configured interval
            except ValueError as e:
                logging.error(f"Error in sleep interval: {e}")
                time.sleep(60 * 60 * 24)  # Sleep for 24 hours if there's an exception

            try:
                logging.info(f"Start cleaning conversations log")

                cutoff_date = datetime.now() - timedelta(
                    seconds=int(ConfigUtil().get_config_attribute("maxCacheLogAge")))

                # Get all log files in the logs directory
                log_files = glob.glob("logs/*.xlsx*")

                # Iterate over all log files
                for file_path in log_files:
                    try:
                        # Extract the date from the filename
                        filename = os.path.basename(file_path)
                        date_part = filename.split('_')[2:5]
                        date_str = '_'.join(date_part).replace(".xlsx", '')
                        file_date = datetime.strptime(date_str, "%m_%d_%y")

                        # If the file is older than the cutoff date, delete it
                        if file_date < cutoff_date:
                            os.remove(file_path)
                            logging.info(f"Removed old log file: {file_path}")
                    except Exception as e:
                        logging.error(f"Error removing conversation log file: {e}")

                logging.info("Cleaned old log cache data successfully")

            except FileNotFoundError:
                logging.error("Log directory not found when trying to clean old cache log data")
            except OSError as e:
                logging.error(f"Failed to clean old cache log data: {e}")
            except Exception as e:
                logging.error(f"Unexpected error while cleaning cache old log data: {e}")
