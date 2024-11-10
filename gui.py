import tkinter as tk
from tkinter import filedialog, messagebox
import os
from datetime import datetime, timedelta
from main import *


def select_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)


def select_output_path():
    output_path = filedialog.askdirectory()
    if output_path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, output_path)


def execute_search():
    keyword = keyword_entry.get()
    file_path = file_entry.get()
    output_path = output_entry.get()
    # Get today's date
    today = datetime.today()
    # Calculate tomorrow's date by adding one day
    tomorrow = today + timedelta(days=1)

    # Format the date as YYYY-MM-DD
    start_date = today.strftime('%Y-%m-%d')
    end_date = tomorrow.strftime('%Y-%m-%d')

    # File path to the uploaded .docx file
    file_path = file_path

    # Step 1: Read the document
    doc = read_docx(file_path)

    # Step 2: Get tables from the document
    tables = get_tables(doc)

    # Step 3: Extract numbers from the tables
    company_codes = extract_contents_from_tables(tables)

    cninfo_links = defaultdict(dict)
    sina_links = defaultdict(dict)
    cninfo_failed_contents = defaultdict(dict)
    sina_failed_contents = defaultdict(dict)
    cninfo_links, cninfo_failed_codes, sina_links, sina_failed_codes = asyncio.run(start_main(company_codes, start_date, end_date, keyword))
    # cninfo_links, cninfo_failed_codes = asyncio.run(start_main(company_codes, start_date, end_date, keyword))

    while len(cninfo_failed_codes) > 0:
        cninfo_failed_contents = convert_failed_codes_to_contents(cninfo_failed_codes, company_codes)
        _e_cninfo_links, cninfo_failed_codes = asyncio.run(scratch_cninfo(cninfo_failed_contents, start_date, end_date))
        cninfo_links.update(_e_cninfo_links)

    while len(sina_failed_codes) > 0:
        sina_failed_contents = convert_failed_codes_to_contents(sina_failed_codes, company_codes)
        _e_sina_links, sina_failed_codes = asyncio.run(scratch_sina(sina_failed_contents, start_date, keyword))
        sina_links.update(_e_sina_links)

    doc = Doc(cninfo_links, sina_links, fr"{output_path}/{start_date}.docx")
    asyncio.run(doc.add_beginnings_to_docx())
    asyncio.run(doc.write_announce_to_docx())
    asyncio.run(doc.write_news_to_docx())
    asyncio.run(doc.change_font())
    messagebox.showinfo("Search Complete")


# 创建主窗口
root = tk.Tk()
root.title("国枫律师事务所")

# 关键词输入
tk.Label(root, text="输入需要剔除的关键词:").grid(row=0, column=0, padx=10, pady=10)
keyword_entry = tk.Entry(root, width=28)
keyword_entry.grid(row=0, column=1, padx=10, pady=10)

# 文件选择
tk.Label(root, text="选择查询文件:").grid(row=1, column=0, padx=10, pady=10)
file_entry = tk.Entry(root, width=28)
file_entry.grid(row=1, column=1, padx=10, pady=10)
file_button = tk.Button(root, text="浏览", command=select_file, height=2, font=("Arial", 10))
file_button.grid(row=1, column=2, padx=5, pady=5)

# 输出路径选择
tk.Label(root, text="选择输出路径:").grid(row=2, column=0, padx=10, pady=10)
output_entry = tk.Entry(root, width=28)
output_entry.grid(row=2, column=1, padx=10, pady=10)
output_button = tk.Button(root, text="浏览", command=select_output_path, height=2, font=("Arial", 10))
output_button.grid(row=2, column=2, padx=5, pady=5)

# 执行按钮
execute_button = tk.Button(root, text="执行程序", command=execute_search, height=2, font=("Arial", 10))
execute_button.grid(row=3, column=1, padx=5, pady=5)

# 启动主循环
root.mainloop()
