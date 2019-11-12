#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
    多尺度图像处理(1)
    :keyword multi-scale, image process

    updated:
    ------------------------
    1. [BUGFIX] 解决中文乱码问题
    ------------------------
    1. [BUGFIX]删除doc的tag时增加判断
    ------------------------
    1. 增加简单的hash缓存
    2. 去除folder，path这两个无用的tag
    3. xml输出使用utf-8

"""

import cv2
import os
import numpy as np
from xml.dom import minidom

__author__ = r"Hafrans<hafrans@163.com>, "
__all__: []  # pending...

INTERPOLATION = cv2.INTER_AREA
__xml_tpl__ = None
rect_list = []
img_cache = {}

"""
+----------+----------+
|          |    |     |
|          |----|-----|
|          |    |     |
+----------+----------+
|----|     |          |
|————|-----|          |
|    |-----|          |
+----------+----------+

"""


#
# def shrink_by_ratio(img, scale_basis, shrink_ratio, interpolation=cv2.INTER_NEAREST):
#     return cv2.resize(img, None,
#                       fx=scale_basis/shrink_ratio,
#                       fy=scale_basis/shrink_ratio,
#                       interpolation=cv2.INTER_CUBIC)


def shrink_by_half_of_paint(img, paint):
    """
    缩小图片
    :param img:
    :param paint:
    :return:
    """
    if img_cache.get(paint.shape[1] / 2, None) is None:
        im = cv2.resize(img, tuple(np.array(np.array([paint.shape[1], paint.shape[0]]) / 2, dtype=np.int)),
                        interpolation=INTERPOLATION)
        img_cache[paint.shape[1] / 2] = im
        return im
    else:
        return img_cache[paint.shape[1] / 2]


def get_origin_object_rect(doc):
    """
    获取图片初始rect区域
    ！！！A！！！
    该方法的工作方式就是获取xml中第一个object的位置信息，如果先对xml使用generate_object_doc
    进行修改，则第一个object的位置信息会被覆盖掉，从而造成数据丢失。
    :param doc:
    :return:
    """
    target = doc.getElementsByTagName("object")[0]
    xmin = int(target.getElementsByTagName("xmin")[0].childNodes[0].data)
    ymin = int(target.getElementsByTagName("ymin")[0].childNodes[0].data)
    xmax = int(target.getElementsByTagName("xmax")[0].childNodes[0].data)
    ymax = int(target.getElementsByTagName("ymax")[0].childNodes[0].data)
    return {
        "xbase": 0,
        "ybase": 0,
        "xmin": xmin,
        "ymin": ymin,
        "xmax": xmax,
        "ymax": ymax,
    }


def generate_object_doc(doc, rect, data=None):
    """
    生成object的xml Element对象
    ！！ATTENTION！！！（BUG）
    该函数使用外部xml_tpl作为基础对象存储以及后续添加新Element的模板
    无法同时对多个doc进行生成操作！
    对一个新doc进行操作时，要确保变量__xml_tpl__为空
    :param doc: minidom对象
    :param rect: rect区域
    :param data: 标签名称
    :return: minidom对象
    """
    global __xml_tpl__
    need_append = True
    if __xml_tpl__ is None:
        target = doc.getElementsByTagName("object")[0]
        __xml_tpl__ = doc.getElementsByTagName("object")[0].cloneNode(deep=True)
        need_append = False
    else:
        target = __xml_tpl__.cloneNode(deep=True)
    if data is not None:
        target.getElementsByTagName("name")[0].childNodes[0].data = data
    target.getElementsByTagName("xmin")[0].childNodes[0].data = rect["xmin"]
    target.getElementsByTagName("ymin")[0].childNodes[0].data = rect["ymin"]
    target.getElementsByTagName("xmax")[0].childNodes[0].data = rect["xmax"]
    target.getElementsByTagName("ymax")[0].childNodes[0].data = rect["ymax"]
    if need_append:
        doc.documentElement.appendChild(target)
    return doc


def generate_image(paint, img, rect, doc):
    """
    图像生成 + rect重定位
    退出递归条件：存在w或h<25px,
    :param paint: 空白画布， 要求与目标图片同样的shape
    :param img:   目标图片
    :param rect:  初始rect区域
    :param doc:   minidom对象
    :return:  最终生成的图片
    """
    if paint is None:
        raise ValueError("paint is invalid!")
    # if paint.shape[0] < 25 or paint.shape[1] < 25:
    if np.max([(rect["ymax"] - rect["ymin"]) / 1, (rect["xmax"] - rect["xmin"]) / 1]) < 32:
        rect_list.append(rect)
        # print("rect",str([(rect["ymax"] - rect["ymin"]) / 2, (rect["xmax"] -rect["xmin"]) /2]))
        paint[0:paint.shape[0], 0:paint.shape[1]] = cv2.resize(img, (paint.shape[1], paint.shape[0]),
                                                               interpolation=INTERPOLATION)
        return
    shrunken_imag = shrink_by_half_of_paint(img, paint)
    h, w, d = shrunken_imag.shape

    rect_x = int((rect["xmin"] - rect["xbase"]) / 2)
    rect_y = int((rect["ymin"] - rect["ybase"]) / 2)
    rect_w = int((rect["xmax"] - rect["xmin"]) / 2)
    rect_h = int((rect["ymax"] - rect["ymin"]) / 2)

    rect_left_top = rect.copy()
    rect_left_top["xmin"] = rect["xbase"] + rect_x
    rect_left_top["ymin"] = rect["ybase"] + rect_y
    rect_left_top["xmax"] = rect_left_top["xmin"] + rect_w
    rect_left_top["ymax"] = rect_left_top["ymin"] + rect_h

    rect_right_down = rect.copy()
    rect_right_down["xbase"] = rect["xbase"] + w
    rect_right_down["ybase"] = rect["ybase"] + h
    rect_right_down["xmin"] = rect_right_down["xbase"] + w - rect_x - rect_w
    rect_right_down["ymin"] = rect_right_down["ybase"] + rect_y
    rect_right_down["xmax"] = rect_right_down["xmin"] + rect_w
    rect_right_down["ymax"] = rect_right_down["ymin"] + rect_h

    # 写入图片
    # print("paint size" + str(paint.shape) + "s size:" + str(shrunken_imag.shape))
    # print("paint size" + str(paint[0:w, 0:h].shape) + "s size:" + str(shrunken_imag.shape))
    # print("paint size" + str(paint[w:2 * w, h:2 * h].shape) + "s size:" + str(shrunken_imag.shape))
    # 测试图片大小是否合适
    paint[0:h, 0:w] = shrunken_imag
    paint[h:2 * h, w:2 * w] = cv2.flip(shrunken_imag, 1)

    doc = generate_object_doc(doc, rect_left_top)
    rect_list.append(rect_left_top)
    doc = generate_object_doc(doc, rect_right_down)
    rect_list.append(rect_right_down)

    rect_lt = rect_left_top.copy()
    rect_rd = rect_left_top.copy()

    # rect slip
    rect_lt["xbase"] += w
    rect_lt["xmin"] += w
    rect_lt["xmax"] += w
    # rect slip
    rect_rd["ybase"] += h
    rect_rd["ymin"] += h
    rect_rd["ymax"] += h

    generate_image(paint[h:2 * h, 0:w], img, rect_lt, doc)
    generate_image(paint[0:h, w:2 * w], img, rect_rd, doc)

    return paint


if __name__ == '__main__':
    SRC_PATH = "./uav"
    DST_PATH = "./nav_dst"

    if not os.path.exists(DST_PATH):
        os.mkdir(DST_PATH)
    images = list(filter(lambda x: x.split(".")[1] == "jpg", [i for i in os.listdir(SRC_PATH)]))

    for i in images:
        # init
        __xml_tpl__ = None
        rect_list.clear()
        img_cache.clear()
        # init end
        filename = i.split(".")[0]
        image_file = filename + ".jpg"
        desc_file = filename + ".xml"
        # load
        doc = minidom.parse(os.path.join(SRC_PATH, desc_file))
        # 删除两大毒瘤
        if len(doc.getElementsByTagName("folder")) > 0:  # 一般只有一个
            doc.documentElement.removeChild(doc.getElementsByTagName("folder")[0])
        if len(doc.getElementsByTagName("path")) > 0:
            doc.documentElement.removeChild(doc.getElementsByTagName("path")[0])
        img = cv2.imread(os.path.join(SRC_PATH, image_file), cv2.IMREAD_UNCHANGED)
        # generate new paint
        paint = np.ones(img.shape, dtype=img.dtype) * 255  # white background (default)
        rect = get_origin_object_rect(doc)  # init rect
        result_img = generate_image(paint, img, rect, doc)  # generate result img
        # generate xml
        for j in rect_list:
            generate_object_doc(doc, j)
        # store
        cv2.imwrite(os.path.join(DST_PATH, image_file), result_img)
        with bopen(os.path.join(DST_PATH, desc_file), "w+") as f:
            f.write(doc.toxml(encoding="utf-8"))
        # DEBUG
        # 去掉下面的注释将产生示例图片（有rect），可以按回车继续
        # for k in rect_list:
        #     cv2.rectangle(result_img, (k["xmin"], k["ymin"]), (k["xmax"], k["ymax"]), (255, 0, 0), 1)
        # cv2.imshow(filename, result_img)
        # cv2.waitKey(0)
        print("PROCESSING:" + filename, "OK!")
