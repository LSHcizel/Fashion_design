"""
精简版工具函数，只包含fashion.py需要的功能
"""
import re


def extract_prompt(text, word):
    """
    从文本中提取指定标记之间的内容
    :param text: 输入文本
    :param word: 标记词
    :return: 提取的内容
    """
    code_block_pattern = rf"```{word}(.*?)```"
    code_blocks = re.findall(code_block_pattern, text, re.DOTALL)
    extracted_code = "\n".join(code_blocks).strip()
    return extracted_code

