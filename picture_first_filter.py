#!/usr/bin/env python3
# -*- coding:utf8 -*-

"""
  Processing  Kite Image for ML
  筛选垃圾

  :author Hafrans <hafrans@163.com>
  :keyword image kite

"""

import logging
import os
from shutil import copyfile

import dhash
from PIL import Image

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M', )

# Global Variables
_G_SRC_DIR = "./kite/"  # the folder which containing kite image.
_G_DST_DIR = "./exported_1/"  # exported stage 1 (eliminate damaged images)
_G_P_DIR = "./exported_2/"  # exported stage 2 (eliminate duplicated images)
_G_D_HASH_THRESHOLD = 0  # deprecated.
_G_ENABLE_RENAME = False

# filter
it = 10000  # init the iterator to rename for image.

# pool for dhash
pool = []

if not os.path.exists(_G_DST_DIR) or _G_ENABLE_RENAME:
    start = it
    if not os.path.exists(_G_DST_DIR):
        os.mkdir(_G_DST_DIR)
        logging.info("make a dir named " + _G_DST_DIR + ". ")

    for i in os.listdir(_G_SRC_DIR):
        ext = i.split(".")[1]
        if os.stat(_G_SRC_DIR + i).st_size <= 10:  # try to find damaged image.
            logging.debug(i + " will be omitted because of its damaged status.")
            continue
        copyfile(_G_SRC_DIR + i, _G_DST_DIR + "{0}.{1}".format(start, ext))
        logging.info(_G_SRC_DIR + i + " will be copied to " + _G_DST_DIR + "{0}.{1}".format(start, ext))
        start += 1


def d_hash_compute(file):
    """
    Compute dhash with a file name, size is 16
    :param file: string filename
    :return: string dhash hex
    """
    image = Image.open(file)
    return dhash.dhash_int(image, size=32)


if not os.path.exists(_G_P_DIR):
    os.mkdir(_G_P_DIR)
    logging.info("make a dir named " + _G_P_DIR + ". ")
    logging.info("script will filter same image..")
    for i in os.listdir(_G_DST_DIR):
        logging.warning("Image Pool Size: "+str(len(pool)))
        dshash = d_hash_compute(_G_DST_DIR + i)
        try:
            if pool.index(dshash) >= 0:
                logging.warning(i + " will be omitted because of duplication")
        except ValueError as e:
            pool.append(dshash)
            copyfile(_G_DST_DIR + i, _G_P_DIR + i)
            logging.info(i + " is ok")

###############################################################

if __name__ == '__main__':  # 开始干正事
    print("Process Image....")
    pass
