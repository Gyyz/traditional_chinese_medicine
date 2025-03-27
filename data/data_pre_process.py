import os
import re
from tqdm import tqdm
import argparse
from zhconv import convert  # 用于繁体转简体
import chardet  # 用于自动检测编码

def detect_and_convert_encoding(text_bytes):
    """
    检测文本编码并尝试转换为UTF-8
    :param text_bytes: 原始字节数据
    :return: 解码后的文本或None(如果失败)
    """
    try:
        # 尝试常见中文编码
        encodings = ['utf-8', 'gbk', 'gb18030', 'big5']
        
        for enc in encodings:
            try:
                return text_bytes.decode(enc)
            except UnicodeDecodeError:
                continue
        
        # 如果常见编码都失败，尝试自动检测
        detected = chardet.detect(text_bytes)
        if detected['confidence'] > 0.7:
            return text_bytes.decode(detected['encoding'])
            
    except Exception as e:
        print(f"编码转换失败: {str(e)}")
    
    return None

def traditional_to_simplified(text):
    """
    将繁体中文转换为简体中文
    :param text: 原始文本
    :return: 简体中文文本
    """
    return convert(text, 'zh-cn')

def clean_chinese_text(text):
    """
    清理中文文本
    :param text: 原始文本
    :return: 清理后的文本
    """
    # 移除不可见字符和多余空白
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 保留中文、英文、数字和常用标点
    text = re.sub(r'[^\w\u4e00-\u9fff，。！？、；："\'《》【】（）…—\-.,;:!?()\[\]{}<>]', '', text)
    
    # 标准化标点符号（可选）
    # text = text.replace(',', '，').replace('.', '。').replace('!', '！').replace('?', '？')
    
    return text

def process_files(input_dir, output_file, file_extension='.txt'):
    """
    处理目录中的所有文本文件
    :param input_dir: 输入目录
    :param output_file: 输出文件路径
    :param file_extension: 文件扩展名
    """
    # 获取所有文本文件
    file_list = [f for f in os.listdir(input_dir) if f.endswith(file_extension)]
    
    if not file_list:
        print(f"在目录 {input_dir} 中没有找到 {file_extension} 文件")
        return
    
    print(f"找到 {len(file_list)} 个文本文件，开始处理...")
    
    # 打开输出文件
    with open(output_file, 'w', encoding='utf-8') as out_f:
        processed_count = 0
        skipped_count = 0
        
        # 使用进度条
        for filename in tqdm(file_list, desc="处理文件中"):
            file_path = os.path.join(input_dir, filename)
            
            try:
                # 以二进制模式读取文件
                with open(file_path, 'rb') as in_f:
                    raw_data = in_f.read()
                
                # 尝试解码文本
                content = detect_and_convert_encoding(raw_data)
                
                if content is None:
                    print(f"无法解码文件: {filename} - 跳过")
                    skipped_count += 1
                    continue
                
                # 繁体转简体
                content = traditional_to_simplified(content)
                
                # 清理文本
                cleaned_content = clean_chinese_text(content)
                
                if cleaned_content:
                    # 写入处理后的内容，每个文件内容用换行分隔
                    out_f.write(cleaned_content + '\n\n')
                    processed_count += 1
                else:
                    skipped_count += 1
                    
            except Exception as e:
                print(f"处理文件 {filename} 时出错: {str(e)}")
                skipped_count += 1
                continue
    
    print(f"\n处理完成！")
    print(f"成功处理文件数: {processed_count}")
    print(f"跳过文件数: {skipped_count}")
    print(f"合并后的文件已保存到: {output_file}")

if __name__ == "__main__":
    # 设置命令行参数
    parser = argparse.ArgumentParser(description="中文TXT文本预处理工具")
    parser.add_argument('--input_dir', type=str, required=True, help='包含TXT文件的输入目录')
    parser.add_argument('--output_file', type=str, required=True, help='输出文件路径')
    args = parser.parse_args()
    
    # 检查输入目录是否存在
    if not os.path.isdir(args.input_dir):
        print(f"错误: 输入目录 {args.input_dir} 不存在")
        exit(1)
    
    # 处理文件
    process_files(
        input_dir=args.input_dir,
        output_file=args.output_file
    )
