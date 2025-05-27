import os
import json
import re

def parse_filename(filename):
    """
    解析文件名，返回id和src
    文件名格式: id 000001,src 000000,time 34,execs 318,op inf,pos 0,+cov
    """
    m = re.match(r'^(.*?)time', filename)
    arr = m.group(1).split(',')

    if len(arr) == 3:
        return arr[0], arr[1]
    elif len(arr) == 2:
        return arr[0], '000000'
    return None

def build_tree(queue_dir):
    """
    读取queue目录下所有文件，构建树结构
    """
    nodes = {}
    children_map = {}
    fid = ''

    # 遍历queue目录下所有文件
    for fname in os.listdir(queue_dir):
        fpath = os.path.join(queue_dir, fname)
        if not os.path.isfile(fpath):
            continue
        id_val, src_val = parse_filename(fname)
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # 获取id_val最后不为0的几位
        # fid = re.search(r'([1-9]\d*)0*$', id_val)
        # fid = fid.group(1) if fid else id_val
        numbers1 = re.findall(r'\d+', id_val)
        if numbers1[0] == '000000':
            fid = '0'
        else:
            fid = re.search(r'([1-9]\d*)0*$', id_val)
            fid = fid.group(1) if fid else id_val

        numbers2 = re.findall(r'\d+', src_val)
        if numbers2[0] == '000000':
            fsrc = '0'
        else:
            fsrc = re.search(r'([1-9]\d*)0*$', src_val)
            fsrc = fsrc.group(1) if fid else src_val
        
        node = {
            "name": fid,
            "intro": content,
            "children": []
        }
        nodes[fid] = node

        # 记录父子关系
        if fsrc not in children_map:
            children_map[fsrc] = []
        if fid == '0':
            continue
        children_map[fsrc].append(fid)

    # 构建children
    for parent_id, child_ids in children_map.items():
        # print(parent_id, child_ids)
        if parent_id in nodes:
            nodes[parent_id]["children"].extend([nodes[cid] for cid in child_ids if cid in nodes])
    return nodes
            
# 2025.5.26 22：11 做到这里了，上面都改好了，src为000000的情况也写好了

    # # 找到根节点（src为000000且id不为000000）
    # root_candidates = [nid for nid in nodes if any(src == '000000' and nid == cid for src, cids in children_map.items() for cid in cids)]
    # # root_candidates = '0';

    # if not root_candidates:
    #     # fallback: 选id最小的
    #     root_id = min(nodes.keys())
    # else:
    #     root_id = root_candidates[0]
    # return nodes[root_id]

def has_cycle(node, visited=None):
    if visited is None:
        visited = set()
    
    node_id = node['name']
    if node_id in visited:
        return True
    visited.add(node_id)
    for child in node['children']:
        if has_cycle(child, visited.copy()):
            return True
    return False


if __name__ == "__main__":
    queue_dir = r"Q:\Aa-Capstone\NodeTree\src\components\queue"  # 假设queue目录和本脚本同级
    tree = build_tree(queue_dir)
    # 1. 生成 links 列表
    tmp_dir = r"Q:\Aa-Capstone\NodeTree\src\components\tmp"  # 修改为你的tmp目录实际路径
    links = []

    for fname in os.listdir(tmp_dir):
        fpath = os.path.join(tmp_dir, fname)
        if not os.path.isfile(fpath):
            continue
        # 解析文件名
        id_val, src_val = parse_filename(fname)
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        # 只保留数字部分（和nodes处理方式一致）
        numbers1 = re.findall(r'\d+', id_val)
        if numbers1[0] == '000000':
            tid = '0'
        else:
            tid = re.search(r'([1-9]\d*)0*$', id_val)
            tid = tid.group(1) if tid else id_val

        numbers2 = re.findall(r'\d+', src_val)
        if numbers2[0] == '000000':
            sid = '0'
        else:
            sid = re.search(r'([1-9]\d*)0*$', src_val)
            sid = sid.group(1) if sid else src_val

        links.append({
            "source": sid,
            "target": tid,
            "content": content
        })

    # 2. 导出时加上 links 字段
    with open("b.json", "w", encoding="utf-8") as f:
        json.dump({"nodes": list(tree.values()), "links": links}, f, ensure_ascii=False, indent=2)