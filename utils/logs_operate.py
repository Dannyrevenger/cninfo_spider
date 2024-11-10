import re


def extract_codes_with_error(log_content):
    codes = []
    current_code = None
    error_found = False

    # 按行分割日志
    log_lines = log_content.splitlines()

    # 逐行处理日志
    for line in log_lines:
        # 检查 "尝试打开cninfo" 行并提取 {code}
        if "尝试打开cninfo" in line:
            # 提取 {code}
            start_idx = line.find("[-]") + 3
            end_idx = line.find("尝试打开cninfo")
            current_code = line[start_idx:end_idx].strip()
            error_found = False  # 重置 error 标志

        # 检查是否存在 ERROR
        if "ERROR" in line:
            error_found = True

        # 检查 "暂无新公告" 行
        if "暂无新公告" in line and current_code and error_found:
            # 如果之前发现了 ERROR，则记录代码
            codes.append(current_code)
            # 记录要删除的块的开始和结束行
            current_code = None  # 重置 current_code 以便于下次处理
        # 删除日志块
    filtered_log_lines = []

    return codes


def clear_log_file(log_file_path):
    # 以写入模式打开文件，写入空字符串即可清空文件内容
    with open(log_file_path, 'w') as file:
        file.write("")

