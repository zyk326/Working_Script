import os

def delete_empty_folders(path):
    # 遍历路径下的所有文件夹
    for root, dirs, files in os.walk(path, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            # 检查文件夹是否为空
            if not os.listdir(dir_path):
                try:
                    os.rmdir(dir_path)  # 删除空文件夹
                    print(f"已删除空文件夹: {dir_path}")
                except OSError as e:
                    print(f"无法删除文件夹 {dir_path}: {e}")

if __name__ == "__main__":
    # 输入路径
    folder_path = r"Y:\2_标注数据\2025-06-24立讯 吉安  国产手机充电器 Cos AOI\1015\异色1014"  # 替换为你要操作的路径
    delete_empty_folders(folder_path)
