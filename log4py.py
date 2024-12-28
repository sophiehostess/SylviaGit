#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging

# Create a logger instance with the module name
logger = logging.getLogger(__name__)
# Set the logging level for the logger to DEBUG (captures all levels)
logger.setLevel(logging.DEBUG)

# Create file handler that writes logs to 'df_log.log'
fh = logging.FileHandler('df_log.log')
# Set file handler to log INFO and above
fh.setLevel(logging.INFO)

# Create console handler for terminal output
ch = logging.StreamHandler()
# Set console handler to log INFO and above
ch.setLevel(logging.INFO)

# Define log message format:
# timestamp - filename - module - function name - log level - message
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(module)s - %(funcName)s - %(levelname)s - %(message)s')
# Apply formatter to both handlers
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# Add both handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


if __name__ == '__main__':
    pass