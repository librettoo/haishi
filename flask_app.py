import os
from transformers import BertTokenizer, BertModel
from faiss import IndexFlatL2
from numpy import array
import torch
from flask import Flask, request, render_template

app = Flask(__name__)

# 加载预训练模型和分词器
device = torch.device("cpu")
tokenizer = BertTokenizer.from_pretrained("hfl/chinese-roberta-wwm-ext")
model = BertModel.from_pretrained("hfl/chinese-roberta-wwm-ext").to(device)

# 加载所有文本文件
def load_txt_from_multiple_directories(root_directory):
    file_texts = []
    file_paths = []

    for subdir, _, files in os.walk(root_directory):
        for file in files:
            if file.endswith("merged.txt"):
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
    faiss_index = IndexFlatL2(d)  # 避免命名冲突
    faiss_index.add(array(sentence_embeddings))
    return faiss_index, sentence_embeddings

# 设置你的根目录路径，包含多个txt文件
root_directory = '/Users/MacBook/Desktop/广东海事局'
texts, file_paths = load_txt_from_multiple_directories(root_directory)
faiss_index, sentence_embeddings = build_faiss_index(texts)

# 实现关键词查询功能
def search_related_txt_files(query_text, top_n=5):
    query_vector = encode_texts([query_text])
    D, I = faiss_index.search(array(query_vector), top_n)  # 使用 faiss_index
    results = []
    for idx, distance in zip(I[0], D[0]):
        results.append({
            "file_path": file_paths[idx],
            "distance": distance
        })
    return results

# Flask 路由，处理搜索请求并返回HTML页面
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return render_template('index.html', results=None, query=query)

    # 调用搜索函数
    results = search_related_txt_files(query)

    # 渲染模板，将结果传递到HTML页面
    return render_template('index.html', results=results, query=query)

if __name__ == '__main__':
    app.run(debug=True)
