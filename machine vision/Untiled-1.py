import cv2
import numpy as np

# 定义棋盘格的行数和列数
ROWS = 23
COLS = 17

# 定义世界坐标系中的棋盘格角点
objp = np.zeros((ROWS * COLS, 3), np.float32)
objp[:, :2] = np.mgrid[0:COLS, 0:ROWS].T.reshape(-1, 2)

# 存储所有图像中的对象点和图像点
objpoints = []  # 3D points in real world space
imgpoints = []  # 2D points in image plane

# 加载图像
images = [
    'F:/Source-code-management-repository/MyHome/Machine vision/Data/1.bmp',
    'F:/Source-code-management-repository/MyHome/Machine vision/Data/2.bmp',
    'F:/Source-code-management-repository/MyHome/Machine vision/Data/3.bmp',
    'F:/Source-code-management-repository/MyHome/Machine vision/Data/4.bmp',
    'F:/Source-code-management-repository/MyHome/Machine vision/Data/5.bmp',
    'F:/Source-code-management-repository/MyHome/Machine vision/Data/6.bmp',
    'F:/Source-code-management-repository/MyHome/Machine vision/Data/7.bmp',
    'F:/Source-code-management-repository/MyHome/Machine vision/Data/8.bmp',
    'F:/Source-code-management-repository/MyHome/Machine vision/Data/9.bmp',
    'F:/Source-code-management-repository/MyHome/Machine vision/Data/10.bmp',
    'F:/Source-code-management-repository/MyHome/Machine vision/Data/11.bmp',
    'F:/Source-code-management-repository/MyHome/Machine vision/Data/12.bmp',
    'F:/Source-code-management-repository/MyHome/Machine vision/Data/13.bmp',
    'F:/Source-code-management-repository/MyHome/Machine vision/Data/14.bmp',
    'F:/Source-code-management-repository/MyHome/Machine vision/Data/15.bmp',
    'F:/Source-code-management-repository/MyHome/Machine vision/Data/16.bmp',
    'F:/Source-code-management-repository/MyHome/Machine vision/Data/17.bmp'
]

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 查找棋盘格角点
    ret, corners = cv2.findChessboardCorners(gray, (COLS, ROWS), None)

    if ret:
        objpoints.append(objp)
        imgpoints.append(corners)

        # 绘制角点
        cv2.drawChessboardCorners(img, (COLS, ROWS), corners, ret)
        cv2.imshow('img', img)
        cv2.waitKey(500)

cv2.destroyAllWindows()

# 标定相机
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

print("相机矩阵:")
print(mtx)
print("\n畸变系数:")
print(dist)

# ============== 新增：图像矫正部分 ==============

if ret:
    # 选择一张图像进行矫正，例如第一张图像
    image_to_undistort_path = images[6]
    img_to_undistort = cv2.imread(image_to_undistort_path)
    if img_to_undistort is None:
        print("错误：无法读取矫正图像。")
    else:
        h, w = img_to_undistort.shape[:2]

        # 计算新的最优相机矩阵，alpha=1 表示保留所有像素，可能会有黑边
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

        # 执行图像矫正
        dst = cv2.undistort(img_to_undistort, mtx, dist, None, newcameramtx)

        # 根据ROI裁剪图像，去除黑边
        x, y, w_roi, h_roi = roi
        dst = dst[y:y+h_roi, x:x+w_roi]
        img_to_undistort_cropped = img_to_undistort[y:y+h_roi, x:x+w_roi]  # 对原始图像做相同裁剪，以便对比

        # 显示矫正前后的对比
        # 将两张图片水平拼接
        combined = np.hstack((img_to_undistort_cropped, dst))
        cv2.imshow('矫正前后对比 - 左: 原始图像 | 右: 矫正后图像', combined)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # 分析结果
        print("\n图像矫正分析：")
        print("1. 从对比图可以看出，矫正后的图像（右侧）的直线边缘（如棋盘格的格线）变得更加平直，有效地修正了镜头的桶形或枕形畸变。")
        print("2. 矫正过程可能会在图像边缘产生一些黑边，这是为了保证图像不失真而进行的裁剪。")
        print("3. 整体图像的几何形状更加符合真实世界的物理结构。")
else:
    print("标定失败，无法进行图像矫正。")


