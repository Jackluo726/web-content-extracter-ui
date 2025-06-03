import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests
from readability import Document
from bs4 import BeautifulSoup
import html2text
import pyperclip
import re

# 全局字体大小变量
font_size = 11

def fetch_and_display():
    url = entry_url.get().strip()
    if not url:
        messagebox.showwarning("输入错误", "请输入有效的网址。")
        return

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        doc = Document(response.text)

        title = doc.title()
        content_html = doc.summary()

        soup = BeautifulSoup(content_html, 'html.parser')

        # 找出正文内所有大标题 <h1>, <h2>, <h3>（你可以根据需要添加更多）
        headers = []
        for tag_name in ['h1', 'h2', 'h3']:
            for header in soup.find_all(tag_name):
                headers.append(f"\n\n# {header.get_text(strip=True)}")

        # 1. 转换 HTML 为 Markdown（你已有）
        content_markdown = html2text.html2text(str(soup))

        # 2. 清除 Markdown 中的链接格式： [文字](链接) → 文字
        content_cleaned = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content_markdown)

        # 3. 清除加粗、斜体、下划线等标记符
        content_cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', content_cleaned)  # **加粗**
        content_cleaned = re.sub(r'__(.*?)__', r'\1', content_cleaned)  # __下划线__
        content_cleaned = re.sub(r'(?<!\*)\*(?!\*)(.*?)\*(?!\*)', r'\1', content_cleaned)  # *斜体*
        content_cleaned = re.sub(r'_(.*?)_', r'\1', content_cleaned)  # _斜体_

        # 4. 去除多余的标题标记（保留真正的段落）
        # 如果你手动加了一级标题，可以保留 # 开头的一行
        content_cleaned = re.sub(r'(?m)^#{2,6}\s*', '', content_cleaned)  # 去除 h2~h6 标题符号
        # 可选：如果你希望所有 # 开头都去掉（包括 h1），取消注释下面这行
        # content_cleaned = re.sub(r'(?m)^#\s*', '', content_cleaned)

        # 5. 去除多余空行（可选）
        content_cleaned = re.sub(r'\n{3,}', '\n\n', content_cleaned).strip()

        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, content_cleaned)

    except Exception as e:

        messagebox.showerror("抓取失败", f"出错了：{str(e)}")

def copy_to_clipboard():
    selected = output_text.get(tk.SEL_FIRST, tk.SEL_LAST) if output_text.tag_ranges(tk.SEL) else output_text.get(1.0, tk.END)
    pyperclip.copy(selected.strip())
    messagebox.showinfo("已复制", "内容已复制到剪贴板。")

def show_context_menu(event):
    try:
        context_menu.tk_popup(event.x_root, event.y_root)
    finally:
        context_menu.grab_release()

def increase_font():
    global font_size
    font_size += 1
    output_text.configure(font=("Consolas", font_size))

def decrease_font():
    global font_size
    if font_size > 6:
        font_size -= 1
        output_text.configure(font=("Consolas", font_size))

# 创建主窗口
root = tk.Tk()
root.title("网页正文提取器 - 通用增强版")
root.geometry("900x700")

# 输入框区域
frame_input = tk.Frame(root)
frame_input.pack(pady=(15, 5), padx=10, fill='x')

label_url = tk.Label(frame_input, text="网页地址：")
label_url.pack(side='left')

entry_url = tk.Entry(frame_input, width=80)
entry_url.pack(side='left', fill='x', expand=True)

# 按钮区域
frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=(5, 5))

btn_fetch = tk.Button(frame_buttons, text="📥 提取内容", command=fetch_and_display, width=15)
btn_fetch.pack(side='left', padx=10)

btn_copy = tk.Button(frame_buttons, text="📋 复制全部/选中", command=copy_to_clipboard, width=18)
btn_copy.pack(side='left', padx=10)

btn_increase = tk.Button(frame_buttons, text="🔼 字体+", command=increase_font, width=10)
btn_increase.pack(side='left', padx=5)

btn_decrease = tk.Button(frame_buttons, text="🔽 字体-", command=decrease_font, width=10)
btn_decrease.pack(side='left', padx=5)

# 输出文本区域
output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", font_size))
output_text.pack(padx=10, pady=(10, 15), fill='both', expand=True)

# 右键菜单
context_menu = tk.Menu(root, tearoff=0)
context_menu.add_command(label="复制选中内容", command=copy_to_clipboard)
output_text.bind("<Button-3>", show_context_menu)  # macOS/Linux/Windows 右键兼容

root.mainloop()
