import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from transformers import BertTokenizer, BertModel
from faiss import IndexFlatL2
from numpy import array  # 只导入 numpy.array
from torch import no_grad

# Step 1: 加载预训练模型和分词器 (HFL-Anthology)
tokenizer = BertTokenizer.from_pretrained("hfl/chinese-roberta-wwm-ext")
model = BertModel.from_pretrained("hfl/chinese-roberta-wwm-ext")

# 所有目录的根目录 (包含多个 PDF 对应的子目录，每个子目录包含多个 txt 文件)
root_directory = '/Users/MacBook/Desktop/广东海事局'

# Step 2: 批量读取每个目录中的 .txt 文件
def load_txt_from_multiple_directories(root_directory):
    file_texts = []
    file_paths = []  # 记录文件的路径 (用于关联结果)
    
    # 遍历每个子目录 (每个子目录对应一个 PDF)
    for subdir, _, files in os.walk(root_directory):
        for file in files:
            if file.endswith("merged.txt"):
                file_path = os.path.join(subdir, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    file_texts.append(file_content)
                    file_paths.append(file_path)  # 保存文件路径
    
    return file_texts, file_paths

# Step 3: 加载所有的 .txt 文件
texts, file_paths = load_txt_from_multiple_directories(root_directory)

# Step 4: 文本向量化
def encode_texts(texts):
    inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=128)
    with no_grad():
        outputs = model(**inputs)
    # 使用 [CLS] token 的向量作为句子向量
    sentence_embeddings = outputs.last_hidden_state[:, 0, :].numpy()
    return sentence_embeddings

# 将文本转换为向量
sentence_embeddings = encode_texts(texts)
print(sentence_embeddings)

# Step 5: 构建 FAISS 向量数据库
d = sentence_embeddings.shape[1]  # 向量的维度 (BERT 输出的维度)
index = IndexFlatL2(d)  # 使用欧氏距离 (L2) 构建索引

# 向 FAISS 索引中添加所有的文本向量
index.add(array(sentence_embeddings))

# 打印索引中已存储的向量数量
print(f"已添加的向量数量: {index.ntotal}")
# Step 6: 实现关键词查询功能
def search_related_txt_files(query_text, top_n):
    # 将查询关键词转换为向量
    query_vector = encode_texts([query_text])
    print(query_vector)
    # 使用 FAISS 索引进行搜索，返回前 top_n 个最相似的文件
    D, I = index.search(array(query_vector), top_n)
    
    # 输出查询结果：相似的文件及其对应的距离
    print("查询关键词: ", query_text)
    print("找到的相似文件: ")
    for idx, distance in zip(I[0], D[0]):
        print(f"文件路径: {file_paths[idx]}, 距离: {distance}")

# 示例查询
search_related_txt_files("政府法令", 5)
