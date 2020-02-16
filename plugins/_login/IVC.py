# coding=utf-8
from PIL import Image
import math
from io import BytesIO
from .IdentificationData import *


def identificationVerificationCode(img_raw):
    img_matrix = np.array(Image.open(BytesIO(img_raw)).convert("L"))  # 灰度处理并创建二维矩阵
    rows, cols = img_matrix.shape  # 获取矩阵（图像）的长宽
    for i in range(rows):
        for j in range(cols):
            if img_matrix[i, j] <= 128:  # 与阈值比较
                img_matrix[i, j] = 0  # 设为灰度最小值
            else:
                img_matrix[i, j] = 1  # 设为灰度最大值
    rows_max = np.min(img_matrix, axis=1)  # 每行最小值
    rows_start = np.argmin(rows_max)  # 找到第一个有图像的行
    rows_end = np.argmin(np.flip(rows_max, 0))  # 找到最后一个有图像的行
    img_matrix = img_matrix[rows_start:-rows_end, :]  # 只取有图像的行
    codes = [0] * 4
    for i in range(4):
        img_matrix_split = img_matrix[:, 19 * i:19 * (i + 1)]  # 切片
        cols_max = np.min(img_matrix_split, axis=0)
        cols_start = np.argmin(cols_max)
        cols_end = np.argmin(np.flip(cols_max, 0))
        width = cols_max.shape[0] - (cols_start + cols_end)  # 图像宽度
        width = 9 - width  # 宽度扩宽到 9 像素
        cols_start -= int(math.ceil(width / 2.0))  # 左边界
        cols_end -= int(math.floor(width / 2.0))  # 右边界
        img_matrix_split = img_matrix_split[:, cols_start:-cols_end]  # 裁剪为 9 像素宽的图像
        res = [''] * 10
        x = img_matrix_split.flatten()  # 展开成一维
        for j in range(10):
            y = identification_data[j]  # 一次取字库中标准数据
            res[j] = np.sum(x ^ y)  # 通过异或计算不同元素的数量
            # Lx = np.sqrt(x.dot(x))
            # Ly = np.sqrt(y.dot(y))
            # cos_angle = x.dot(y) / (Lx * Ly)
            # res[j] = cos_angle
        # plt.figure("lena")
        # plt.imshow(img_matrix_split, cmap='gray')
        # plt.axis('off')
        # plt.show()
        codes[i] = str(np.argmin(res))  # 取差异最小的下标
    return ''.join(codes)
