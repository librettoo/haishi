#!/usr/bin/env bash

#!/bin/bash

# 遍历当前目录下所有以 '_txt' 结尾的文件夹
for dir in *_txt/; do
    echo "Processing folder: $dir"
    
    # 找到该目录中的第一个 PDF 文件
    pdf=$(ls "$dir"*.pdf 2>/dev/null | head -n 1)
    
    # 检查是否找到 PDF 文件
    if [ -n "$pdf" ]; then
        # 获取 PDF 文件的前缀（不含扩展名）
        prefix=$(basename "$pdf" .pdf)
        echo "Processing PDF: $pdf with prefix $prefix..."
        
        # 使用 pdfseparate 将 PDF 文件逐页拆分，使用 PDF 文件名前缀
        # 页码从 0000 开始
        pdfseparate "$pdf" "$dir/${prefix}_page_%04d.pdf"
        
        # 修改后的方式会从 0000 开始，因此我们需要手动调整 pdfseparate 起始的文件名
        page_number=0
        
        # 遍历拆分出的每个单页 PDF 文件并转换为文本文件，保留原 PDF 前缀并按页码命名
        for i in "$dir/${prefix}_page_"*.pdf; do
            # 格式化页码，确保从0000开始
            formatted_page=$(printf "%04d" "$page_number")
            pdftotext "$i" "${dir}${prefix}_page_${formatted_page}.txt"
            ((page_number++)) # 递增页码
        done
        
        # 删除拆分出的单页 PDF 文件
        rm "$dir/${prefix}_page_"*.pdf
        
        echo "$pdf has been processed into individual text files with prefix $prefix starting from page_0000."
    else
        echo "No PDF files found in $dir"
    fi
done

