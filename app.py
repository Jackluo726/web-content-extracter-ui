from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

def clean_text(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # 去掉 markdown 粗体标识
    text = re.sub(r'http[s]?://\S+', '', text)    # 去掉链接
    text = re.sub(r'#', '', text)                 # 去掉多余的 #
    return text.strip()

def extract_main_content(url):
    try:
        resp = requests.get(url, timeout=10)
        resp.encoding = resp.apparent_encoding
        soup = BeautifulSoup(resp.text, 'html.parser')

        title = soup.title.string.strip() if soup.title else ''
        paragraphs = soup.find_all(['p', 'article'])
        content = '\n\n'.join(clean_text(p.get_text()) for p in paragraphs if len(p.get_text().strip()) > 30)
        return title, content
    except Exception as e:
        return '', f"❌ 提取出错：{str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    title = content = ''
    if request.method == 'POST':
        url = request.form['url']
        title, content = extract_main_content(url)
    return render_template('index.html', title=title, content=content)

if __name__ == '__main__':
    app.run(debug=True)
