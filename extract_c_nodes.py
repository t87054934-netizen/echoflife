import re
import pandas as pd
import os

def parse_pstxnet_file(file_path):
    """
    解析pstxnet.dat文件，按NET_NAME分段
    """
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # 首先找到所有NET_NAME的位置
    net_pattern = r"NET_NAME\s*\n\s*'([^']+)'"
    net_matches = list(re.finditer(net_pattern, content))
    
    net_sections = []
    
    for i, match in enumerate(net_matches):
        net_name = match.group(1)
        start_pos = match.start()
        
        # 确定段落的结束位置
        if i < len(net_matches) - 1:
            end_pos = net_matches[i + 1].start()
        else:
            end_pos = len(content)
        
        section = content[start_pos:end_pos]
        net_sections.append((net_name, section))
    
    return net_sections

def extract_c_nodes(section_content):
    """
    从段落中提取NODE_NAME后面是C开头的条目
    """
    c_nodes = []
    
    # 查找所有NODE_NAME行
    lines = section_content.split('\n')
    for line in lines:
        line = line.strip()
        # 匹配NODE_NAME后面是C开头的
        # 格式: NODE_NAME  C416 1
        match = re.search(r'NODE_NAME\s+(C\S+)', line)
        if match:
            node_name = match.group(1)
            c_nodes.append(node_name)
    
    return c_nodes

def main():
    # 文件路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(base_dir, 'pstxnet.dat')
    output_file = os.path.join(base_dir, '结果.xlsx')
    
    # 检查文件是否存在
    if not os.path.exists(input_file):
        print(f"错误: 文件 {input_file} 不存在")
        return
    
    # 解析pstxnet.dat文件
    print(f"正在解析文件: {input_file}")
    net_sections = parse_pstxnet_file(input_file)
    print(f"找到 {len(net_sections)} 个NET_NAME段落")
    
    # 查找包含+3.3V_LCD的段落
    target_net_name = '+3.3V_LCD'
    target_section = None
    
    for net_name, section in net_sections:
        if net_name == target_net_name:
            target_section = section
            print(f"\n找到目标NET_NAME: {net_name}")
            break
    
    if target_section is None:
        print(f"\n错误: 未找到NET_NAME为 {target_net_name} 的段落")
        print("包含'3.3'或'LCD'的NET_NAME:")
        for net_name, _ in net_sections:
            if '3.3' in net_name or 'LCD' in net_name:
                print(f"  - {net_name}")
        return
    
    # 提取C开头的NODE_NAME
    c_nodes = extract_c_nodes(target_section)
    print(f"找到 {len(c_nodes)} 个C开头的NODE_NAME")
    
    # 显示所有找到的节点
    if c_nodes:
        print("\n所有C开头的NODE_NAME:")
        for i, node in enumerate(c_nodes):
            print(f"  {i+1}. {node}")
    
    # 创建结果DataFrame
    # 第一行写+3.3V_LCD，接下来的行写所有符合的NODE_NAME
    result_data = [[target_net_name]]  # 第一行
    for node in c_nodes:
        result_data.append([node])  # 接下来的每一行
    
    result_df = pd.DataFrame(result_data, columns=['NODE_NAME'])
    
    # 保存到Excel文件
    result_df.to_excel(output_file, index=False, header=False)
    print(f"\n结果已保存到: {output_file}")
    print(f"总共 {len(result_data)} 行数据")

if __name__ == '__main__':
    main()
