import os
from flask import Flask, request, render_template, send_from_directory
from quick_search import quick_search_files
from precise_search import precise_search

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/quick_search', methods=['GET'])
# 快速搜索路由
def quick_search():
    query = request.args.get('query')
    if not query:
        return render_template('index.html', quick_results=None, query=query)

    # 调用搜索函数
    quick_results = quick_search_files(query)

    # 对PDF文件路径进行处理，确保是相对路径，并提取文件名
    for result in quick_results:
        # 将绝对路径转换为相对路径
        result['pdf_path'] = os.path.relpath(result['pdf_path'], start=os.path.join(app.root_path, 'data'))
        # 提取文件名，不带扩展名，移除所有的 .merged
        result['file_name'] = os.path.basename(result['pdf_path']).replace(".merged", "").replace(".pdf", "")

    # 渲染模板，将结果传递到HTML页面
    return render_template('index.html', quick_results=quick_results)


# 精确搜索路由
@app.route('/precise_search', methods=['GET'])
def precise_search_route():
    query = request.args.get('query')
    if not query:
        return render_template('index.html', precise_results=None)

    # 设置根目录路径
    root_directory = '/Users/MacBook/Desktop/广东海事局/data'
    
    # 执行精确搜索
    precise_results = precise_search(query, root_directory)
    
    for result in precise_results:
        # 将绝对路径转换为相对路径
        result['pdf_path'] = os.path.relpath(result['pdf_path'], start=os.path.join(app.root_path, 'data'))
        # 提取文件名，不带扩展名，移除所有的 .merged
        result['file_name'] = os.path.basename(result['pdf_path']).replace(".merged", "").replace(".pdf", "")

    return render_template('index.html', precise_results=precise_results)

# 提供下载或打开 PDF 文件
@app.route('/pdf/<path:subpath>/<filename>')
def download_pdf(subpath, filename):
    # 构建相对路径，包含子目录和文件名
    directory = os.path.join(app.root_path, 'data', subpath)  # 构建路径，将子目录添加到 'data'
    # 确保文件在指定的目录下，返回文件
    return send_from_directory(directory, filename)

if __name__ == '__main__':
    app.run(debug=True)
