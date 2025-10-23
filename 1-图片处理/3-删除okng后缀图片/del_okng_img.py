import os

def delete_corresponding_images(path):
    # 获取路径下的所有文件
    files = os.listdir(path)
    # 用来存储已处理过的图片文件的基名（去掉 "_OK" 或 "_NG"）
    seen_basenames = set()

    for file in files:
        if file.endswith('.jpg'):
            # 提取文件名中的基名 (如: F1_20251015074646505_1)
            base_name = "_".join(file.split("_")[:-1])
            
            # 如果基名已经处理过，跳过
            if base_name in seen_basenames:
                continue

            # 检查是否有对应的 "OK" 或 "NG" 图片
            ok_file = base_name + "_OK.jpg"
            ng_file = base_name + "_NG.jpg"
            
            # 删除对应的 OK 或 NG 图片（如果存在）
            if ok_file in files:
                try:
                    os.remove(os.path.join(path, ok_file))
                    print(f"已删除文件: {os.path.join(path, ok_file)}")
                except OSError as e:
                    print(f"无法删除文件 {os.path.join(path, ok_file)}: {e}")
            if ng_file in files:
                try:
                    os.remove(os.path.join(path, ng_file))
                    print(f"已删除文件: {os.path.join(path, ng_file)}")
                except OSError as e:
                    print(f"无法删除文件 {os.path.join(path, ng_file)}: {e}")
            
            # 将当前的基名添加到已处理列表中
            seen_basenames.add(base_name)

if __name__ == "__main__":
    # 输入路径
    folder_path = r"C:\Users\Administrator\Documents\WXWork\1688858172661254\Cache\File\2025-10\NG\NG\CutAIImage"  # 替换为你的图片文件夹路径
    delete_corresponding_images(folder_path)
