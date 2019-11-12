# 图片预处理以及文件名称整理
# preprocess images and format file name

updated: Nov 12 2019

## 各个脚本提供的功能
### 1. picture_first_filter.py
 **功能**: 将目标文件夹内的图片进行筛选，去除掉损坏的、size过小的文件，并导出到exported_2文件夹内。
### 2. scale_process.py
**功能**: 将目标文件夹中的文件进行多种尺度的缩放并绘制在一张图上，并根据原标签生成与组合图响应的标签。
### 3. sortFileName.py
**功能**： 将目标文件夹内的图像文件以及标签文件（xml）进行批量重命名，并将其复制到output文件夹中。

## 安装依赖
```python
pip install -r requirements.txt
``` 

## Functions provided by each script.
### 1. picture_first_filter.py
 **functional specification**: filter all image files to eliminate very small & corrupted images. 
### 2. scale_process.py
**functional specification**: scale images in multiple scales and draw them onto one picture and generate corresponded label file.
### 3. sortFileName.py
**functional specification**： rename images and description files and copy to 'output'. 

## Install Requirements
```python
pip install -r requirements.txt
``` 




