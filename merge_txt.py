import os
import re

# 定义根目录路径
root_directory = '/Users/MacBook/Desktop/广东海事局'

# 正则表达式匹配 _page_ 后面跟着四个数字的文件名
page_pattern = re.compile(r'_page_\d{4}\.txt$')

# 遍历根目录及其所有子目录
for dirpath, dirnames, filenames in os.walk(root_directory):
    # 存储当前目录下需要排序和合并的txt文件
    txt_files_to_merge = []

    # 存储当前目录下无需排序和合并的文件
    other_files = []

    # 分类文件
    for file in filenames:
        if file.endswith('.txt'):
            if page_pattern.search(file):  # 判断文件名是否符合_page_后跟四位数字
                txt_files_to_merge.append(file)
            else:
                other_files.append(file)

    # 处理需要排序和合并的文件
    if txt_files_to_merge:
        # 假设所有需要合并的文件的前缀是相同的，提取前缀部分
        first_file = txt_files_to_merge[0]
        prefix = first_file.split('_page_')[0]  # 根据文件名的规则提取前缀
        
        # 设置输出文件路径，合并后的文件命名为 {prefix}.merged.txt
        output_file_path = os.path.join(dirpath, f"{prefix}.merged.txt")
        
        # 按文件名中的最后四位数字进行排序，如果不符合_page_格式，则不使用数字排序
        txt_files_to_merge.sort(key=lambda x: int(x[-8:-4]) if '_page_' in x and x[-8:-4].isdigit() else float('inf'))
        
        # 打开一个新的txt文件进行写入
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            for file in txt_files_to_merge:
                file_path = os.path.join(dirpath, file)
                
                # 使用逐行读取来避免超时问题
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        for line in infile:
                            outfile.write(line)
                        outfile.write("\n")  # 每个文件之间加个换行以区分
                except TimeoutError:
                    print(f"读取文件 {file_path} 时超时")

        print(f"已将 {dirpath} 中的文件合并到 {output_file_path}")

    # 处理不需要排序和合并的文件
    for file in other_files:
        file_path = os.path.join(dirpath, file)
        
        # 构造新的文件名，将 .txt 改为 .merged.txt
        new_file_path = os.path.join(dirpath, file.replace('.txt', '.merged.txt'))
        
        # 重命名文件
        os.rename(file_path, new_file_path)
        print(f"文件 {file_path} 已重命名为 {new_file_path}")
