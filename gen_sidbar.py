import os
from pathlib import Path

def generate_markdown_list(root_dir):
    """遍历指定目录，生成Markdown格式的笔记列表"""
    # 规范化路径
    root_path = Path(root_dir).resolve()
    
    # 检查目录是否存在
    if not root_path.is_dir():
        print(f"错误：目录 '{root_dir}' 不存在")
        return
    
    # 存储目录结构的字典
    dir_structure = {}
    
    # 遍历目录中的所有文件
    for item in root_path.rglob('*.md'):
        # 获取相对于根目录的路径
        relative_path = item.relative_to(root_path)
        
        # 分割路径为目录部分和文件名
        parts = list(relative_path.parts)
        
        # 区分根目录文件和子目录文件
        if len(parts) == 1:
            # 根目录下的文件
            dir_structure.setdefault('_files', []).append(parts[0])
        else:
            # 子目录下的文件
            filename = parts.pop()
            current_level = dir_structure
            
            # 构建目录结构
            for part in parts:
                if part not in current_level:
                    current_level[part] = {'_files': []}
                current_level = current_level[part]
            
            # 添加文件到当前目录层级
            current_level['_files'].append(filename)
    
    return dir_structure

def print_markdown_list(structure, pre_fix, level=0, path_parts=None, output_file=None):
    """将目录结构以Markdown列表形式写入文件"""
    if path_parts is None:
        path_parts = []
        
    indent = "  " * level
    
    # 首先处理目录
    for dir_name, content in sorted(structure.items()):
        if dir_name != '_files':
            line = f"{indent}- **{dir_name}**\n"
            output_file.write(line)
            new_path_parts = path_parts + [dir_name]
            print_markdown_list(content, pre_fix, level + 1, new_path_parts, output_file)
    
    # 然后处理文件
    files = structure.get('_files', [])
    for file_name in sorted(files):
        # 正确拼接文件路径
        file_path = '/'.join(path_parts + [file_name]) if path_parts else file_name
        file_path = f"{pre_fix}{file_path}"
        file_path = file_path.replace(" ","%20")
        line = f"{indent}- [{file_name}]({file_path})\n"
        output_file.write(line)

if __name__ == "__main__":
    


    
    top_topics = {  "docs" }
    for subdir in top_topics:
        # 指定要遍历的目录路径
        directory_path = f"./{subdir}"  # 当前目录，可修改为实际路径
        output_path = f"./{subdir}/_sidebar.md"  # 输出文件路径
        pre_fix     = f"{subdir}/"    
        print(f"正在生成Markdown笔记列表并写入 '{output_path}'...")
        structure = generate_markdown_list(directory_path)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Markdown笔记列表\n\n")
            print_markdown_list(structure,pre_fix, output_file=f)
        
        print(f"列表已成功写入 '{output_path}'")    


