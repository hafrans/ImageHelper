#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
    理顺当前文件夹文件名称，并且理顺xml的filename
    :author "Hafrans"<hafrans@163.com>
    :version 0.0.1

"""
import logging
import os
from shutil import copyfile, rmtree
from xml.dom import minidom
from time import sleep

# load basic configuration
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M', )

if __name__ == '__main__':
    print("=======文件理顺工具=======")
    print("功能：理顺文件名称，修改相关xml的filename, 将jpeg改为jpg")
    print("您当前运行此脚本的文件夹是：", os.getcwd())
    print("请您确保该文件夹内没有除output以外的任何子文件夹！(程序输出在output文件夹内，重复运行会被删除)")
    print("请输入目标文件夹(可以相对路径),默认为当前路径：")
    target = input(">>>>")
    if len(target) == 0:
        target = "."
    print("请输入作为起始的文件名称，要求数字（例如：100000），默认为10000")
    start = input(">>>")
    if len(start) == 0:
        start = 10000
    try:
        start = int(start)
    except Exception as e:
        print("您输入的是非数字，程序正在退出")
        exit(-1)
    # go to target folder
    os.chdir(os.path.join(os.getcwd(), target))
    input("您输入的起始文件名是：" + str(start) + "，输出至output文件夹，按任意键程序开始运行")


    def generate_next_filename():
        global start
        while True:
            yield str(start)
            start += 1


    counter = generate_next_filename()
    # check output
    if not os.path.exists("output"):
        logging.info("create output folder ...")
        os.mkdir("output")
    else:
        logging.info("deleting and recreate output folder ...")
        rmtree("output")
        sleep(1)
        os.mkdir("output")

    # check dir
    # 要确保所有的jpg都有xml对应，否则程序没法运行
    all_files = sorted(os.listdir())
    all_images = filter(lambda x: x.split(".")[-1] in ("jpeg", "jpg"), all_files)
    for i in all_images:
        # 这里假设文件名为x.y
        filename, ext = i.split(".")
        new_name = next(counter)
        try:
            doc = minidom.parse(filename + ".xml")
            doc.getElementsByTagName("filename")[0].childNodes[0].data = new_name + ".jpg"
            # 删除两大毒瘤
            if len(doc.getElementsByTagName("folder")) > 0:  # 一般只有一个
                doc.documentElement.removeChild(doc.getElementsByTagName("folder")[0])
            if len(doc.getElementsByTagName("path")) > 0 :
                doc.documentElement.removeChild(doc.getElementsByTagName("path")[0])

            # write
            with open("./output/" + new_name + ".xml", 'wb') as f:
                f.write(doc.toxml(encoding="utf-8"))
            copyfile(i, "./output/" + new_name + ".jpg")
            logging.info(i + ">>>>> output/" + new_name + ".jpg")
        except Exception as e:
            logging.warning("image " + i + " desc file is corrupted. wont output it.")
            raise e
