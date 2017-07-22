#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('df_log.log') # file handler
fh.setLevel(logging.INFO)

ch = logging.StreamHandler() #stream handler
ch.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(filename)s - %(module)s - %(funcName)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)


if __name__ == '__main__':
    pass