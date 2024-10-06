import os
from transformers import BertTokenizer, BertModel
from faiss import IndexFlatL2
from numpy import array
import torch

# 加载预训练模型和分词器
device = torch.device("cpu")
tokenizer = BertTokenizer.from_pretrained("hfl/chinese-roberta-wwm-ext")
model = BertModel.from_pretrained("hfl/chinese-roberta-wwm-ext").to(device)

# 快速搜索加载 txt 文件
def load_quick_txt_files(root_directory):
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

root_directory = '/Users/MacBook/Desktop/广东海事局/data'
texts, file_paths = load_quick_txt_files(root_directory)
faiss_index = build_faiss_index(texts)

# 执行快速搜索功能
def quick_search_files(query_text, top_n=5):
    
    # 查询
    query_vector = encode_texts([query_text])
    D, I = faiss_index.search(array(query_vector), top_n)
    
    results = []
    for idx, distance in zip(I[0], D[0]):
        txt_path = file_paths[idx]
        pdf_path = txt_path.replace(".merged.txt", ".pdf").replace(".merged","")
        results.append({
            "file_name": os.path.basename(pdf_path).replace(".pdf", ""),
            "pdf_path": pdf_path,
            "distance": distance
        })
    return results
    
