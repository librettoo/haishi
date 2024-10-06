import os
from transformers import BertTokenizer, BertModel
from faiss import IndexFlatL2
from numpy import array
import torch

# 加载预训练模型和分词器
device = torch.device("cpu")
tokenizer = BertTokenizer.from_pretrained("hfl/chinese-roberta-wwm-ext")
model = BertModel.from_pretrained("hfl/chinese-roberta-wwm-ext").to(device)

# 快速搜索，返回 PDF 文件的路径
def quick_search_for_pdfs(root_directory, top_n=5):
    file_texts = []
    file_paths = []

    for subdir, _, files in os.walk(root_directory):
        for file in files:
            if file.endswith("merged.txt"):  # 快速搜索基于完整的 .txt 文件
                file_path = os.path.join(subdir, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    file_texts.append(file_content)
                    file_paths.append(file_path)

    return file_texts, file_paths

# 将文本向量化
def encode_texts(texts):
    inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=128).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
    sentence_embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
    return sentence_embeddings

# 构建向量数据库
def build_faiss_index(texts):
    sentence_embeddings = encode_texts(texts)
    d = sentence_embeddings.shape[1]
    faiss_index = IndexFlatL2(d)
    faiss_index.add(array(sentence_embeddings))
    return faiss_index

# 在精确搜索中查找 PDF 文件，并为每个 PDF 构建单独的向量库
def precise_search(query_text, root_directory, top_n=5):
    # 1. 执行快速搜索以获取 PDF 文件列表
    texts, file_paths = quick_search_for_pdfs(root_directory)
    faiss_index = build_faiss_index(texts)

    # 查询并获取 top_n 个相关的 PDF 文件
    query_vector = encode_texts([query_text])
    D, I = faiss_index.search(array(query_vector), top_n)
    
    selected_pdfs = []
    for idx in I[0]:
        pdf_path = file_paths[idx].replace("merged.txt", "pdf").replace(".merged","")
        selected_pdfs.append(pdf_path)

    # 2. 针对每个 PDF 文件的页面构建独立的向量库
    precise_results = []
    for pdf in selected_pdfs:
        pdf_directory = os.path.dirname(pdf)  # 动态设置新的 root_directory 为 PDF 文件所在的目录
        page_texts, page_files = load_pages_for_pdf(pdf_directory)

        # 构建每个 PDF 的向量库
        faiss_index = build_faiss_index(page_texts)

        # 在每个 PDF 的页面中执行搜索
        D, I = faiss_index.search(array(query_vector), len(page_files))
        for idx, distance in zip(I[0], D[0]):
            page_file = page_files[idx]
            page_num = page_file.split("_page_")[1].replace(".txt", "")
            precise_results.append({
                "pdf_name": os.path.basename(pdf),
                "page_num": page_num,
                "distance": distance,
                "pdf_path": pdf
            })
    
    return precise_results

# 加载每个 PDF 的页面 .txt 文件
def load_pages_for_pdf(pdf_directory):
    page_texts = []
    page_files = []
    
    for subdir, _, files in os.walk(pdf_directory):
        for file in files:
            if "_page_" in file and file.endswith(".txt"):
                file_path = os.path.join(subdir, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    page_texts.append(file_content)
                    page_files.append(file_path)

    return page_texts, page_files
