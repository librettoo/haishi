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

def split_text_by_empty_lines(text):
    """
    根据空行分割文本，返回段落列表。
    空行被认为是段落之间的分隔符。
    """
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]  # 使用双换行符分割段落，去除多余空格
    return paragraphs


def encode_paragraphs(paragraphs):
    """
    对分割后的段落进行向量化，返回段落的嵌入向量。
    """
    inputs = tokenizer(paragraphs, return_tensors="pt", padding=True, truncation=True, max_length=128).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
    paragraph_embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
    return paragraph_embeddings

def build_paragraph_faiss_index(paragraph_embeddings):
    """
    构建 FAISS 索引用于段落的相似度搜索。
    """
    d = paragraph_embeddings.shape[1]
    faiss_index = IndexFlatL2(d)
    faiss_index.add(array(paragraph_embeddings))
    return faiss_index

def search_relevant_paragraph_in_document(text, query_text):
    """
    在文档中基于段落搜索最相关的内容。
    """
    # 基于空行分割文档为段落
    paragraphs = split_text_by_empty_lines(text)
    
    # 对段落向量化
    paragraph_embeddings = encode_paragraphs(paragraphs)
    
    # 构建段落的 FAISS 索引
    faiss_index = build_paragraph_faiss_index(paragraph_embeddings)
    
    # 将查询向量化
    query_embedding = encode_texts([query_text])
    
    # 搜索最相关的段落
    D, I = faiss_index.search(array(query_embedding), 1)  # 找到最相关的段落
    return paragraphs[I[0][0]]  # 返回最相关的段落


# 执行快速搜索功能
def quick_search_files(query_text, top_n=5):
    current_directory = os.getcwd()  # 获取当前工作目录
    root_directory = os.path.join(current_directory, 'data')  # 构建绝对路径

    texts, file_paths = load_quick_txt_files(root_directory)
    faiss_index = build_faiss_index(texts)

    # 查询
    query_vector = encode_texts([query_text])
    D, I = faiss_index.search(array(query_vector), top_n)
    
    results = []
    for idx, distance in zip(I[0], D[0]):
        txt_path = file_paths[idx]
        pdf_path = txt_path.replace(".merged.txt", ".pdf").replace(".merged","")

        relevant_paragraph = search_relevant_paragraph_in_document(texts[idx], query_text)

        results.append({
            "file_name": os.path.basename(pdf_path).replace(".pdf", ""),
            "summary": relevant_paragraph,
            "pdf_path": pdf_path,
        })
    return results