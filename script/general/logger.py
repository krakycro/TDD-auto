#import logging

#from logging.handlers import TimedRotatingFileHandler

##############################################################################

TEMP_DATA_DIR = "temp_data"
IGNORE_ERROR = False

##############################################################################


def log_error(*str_list, error=Exception):
    """
    Info: raise an error with message

    Return: None
    """
    string = " ".join(str_list)
    if IGNORE_ERROR is not True:
        raise error(string)

    else:
        print(string)


##############################################################################
# class Logger(object):
#     instance = None

#     def __new__(cls):
#         if not Logger.instance:
#             Logger.instance = Logger.__Logger()
#         return Logger.instance

#     ########################################################################
#     class __Logger:
#         # LOGGING

#         CRITICAL = 50
#         FATAL = CRITICAL
#         ERROR = 40
#         WARNING = 30
#         WARN = WARNING
#         INFO = 20
#         DEBUG = 10
#         NOTSET = 0

#         _levelToName = {
#             CRITICAL: 'CRITICAL',
#             ERROR: 'ERROR',
#             WARNING: 'WARNING',
#             INFO: 'INFO',
#             DEBUG: 'DEBUG',
#             NOTSET: 'NOTSET',
#         }

#         _nameToLevel = {
#             'CRITICAL': CRITICAL,
#             'FATAL': FATAL,
#             'ERROR': ERROR,
#             'WARN': WARNING,
#             'WARNING': WARNING,
#             'INFO': INFO,
#             'DEBUG': DEBUG,
#             'NOTSET': NOTSET,
#         }

#         LOG_LEVEL = 20
#         FILE_NAME = TEMP_DATA_DIR+'/rotator.log'
#         logger = None

#         def set_logging(self, log_level, file_name=FILE_NAME):
#             global LOG_LEVEL
#             global logger
#             LOG_LEVEL = self._nameToLevel[log_level]
#             self.logger = logging.getLogger("Rotating Log")
#             self.logger.setLevel(LOG_LEVEL)


#             handler = TimedRotatingFileHandler(
#                 file_name, when="s" ,interval=3600 ,backupCount=10
#                 )

#             formatter = logging.Formatter(
#                 'T:%(asctime)s   LL:%(levelname)s'
#                 '   F:%(funcName)s        M:%(message)s'
#                 )
#             handler.setFormatter(formatter)
#             self.logger.addHandler(handler)

#         def get_logger(self):
#             return self.logger

#         def log_message(self, message):
#             self.logger.log(self.logger.level, message)

##############################################################################
##############################################################################
