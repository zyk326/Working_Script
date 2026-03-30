import cv2
import numpy as np
import os

# =============================
# 配置区域
# =============================
folder = r"C:\\Users\\Administrator\\Desktop\\part\\Cut"  # 👉 修改为你的文件夹路径
output_path = os.path.join(folder, "merged.jpg")

# =============================
# 读取图像
# =============================
images = []
for i in range(1, 7):
    img_path = os.path.join(folder, f"{i}.jpg")
    if not os.path.exists(img_path):
        raise FileNotFoundError(f"未找到文件: {img_path}")
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError(f"无法读取图像: {img_path}")
    images.append(img)

# =============================
# 检查尺寸并统一大小
# =============================
# 以第一张图片为基准统一尺寸
h, w = images[0].shape[:2]
images = [cv2.resize(img, (w, h)) for img in images]

# =============================
# 拼接操作
# =============================
row1 = np.hstack((images[0], images[1]))
row2 = np.hstack((images[2], images[3]))
row3 = np.hstack((images[4], images[5]))
merged = np.vstack((row1, row2, row3))

# =============================
# 保存与显示
# =============================
cv2.imwrite(output_path, merged)
print(f"拼接完成，输出文件: {output_path}")

# 如果你想显示结果
# cv2.imshow("Merged", merged)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
