import fitz  # 导入 PyMuPDF
import os

# 遍历当前目录下所有以 '_txt' 结尾的文件夹
for dir in os.listdir('.'):
    if dir.endswith('_txt') and os.path.isdir(dir):
        print(f"Processing folder: {dir}")

        # 找到该目录中的第一个 PDF 文件
        pdf_files = [f for f in os.listdir(dir) if f.endswith('.pdf')]
        
        if pdf_files:
            pdf_path = os.path.join(dir, pdf_files[0])  # 获取第一个 PDF 文件的路径
            prefix = os.path.splitext(pdf_files[0])[0]  # 获取 PDF 文件的前缀
            print(f"Processing PDF: {pdf_path} with prefix {prefix}...")

            # 打开 PDF 文件
            pdf_document = fitz.open(pdf_path)

            # 创建以 PDF 文件名为基础的 merged.txt 文件
            merged_filename = os.path.join(dir, f"{prefix}.merged.txt")
            with open(merged_filename, 'w', encoding='utf-8') as merged_file:
                # 遍历每一页
                for page_number in range(len(pdf_document)):
                    page = pdf_document[page_number]  # 获取当前页
                    text = page.get_text()  # 提取文本
                    
                    # 格式化页码，确保从 0000 开始
                    formatted_page = f"{page_number:04d}"
                    
                    # 保存当前页的文本
                    page_filename = os.path.join(dir, f"{prefix}_page_{formatted_page}.txt")
                    with open(page_filename, 'w', encoding='utf-8') as page_file:
                        page_file.write(text)  # 写入当前页文本
                        
                    # 将当前页文本写入 merged.txt
                    merged_file.write(text + "\n" + "="*40 + "\n")  # 添加分隔符
                
            pdf_document.close()  # 关闭 PDF 文件
            print(f"{pdf_path} has been processed into individual text files and merged into {merged_filename}.")
        else:
            print(f"No PDF files found in {dir}.")
