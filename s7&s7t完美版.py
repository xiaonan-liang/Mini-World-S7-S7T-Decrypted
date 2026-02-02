import os
import hashlib
import math
from datetime import datetime

# S7编码表
S7_TABLE = "Vg21WQ5KdRt0yNpcr9m4O3PoHaZvsLeCY8FjSwiTkUbuEBIJlAG7fqXM6xDnzh-;"

def s7encode(input_str: str) -> str:
    """S7编码"""
    if not input_str:
        return ""
    
    s64_list = []
    index = 0
    
    while len(input_str) >= index + 1:
        buf = 0
        bytes_num = 0
        
        for i in range(3):
            buf = buf * 256
            if len(input_str) >= index + 1:
                buf += ord(input_str[index])
                bytes_num += 1
                index += 1
        
        for i in range(bytes_num + 1):
            b64char = int(math.floor(buf / 262144)) % 64
            s64_list.append(S7_TABLE[b64char])
            buf = buf * 64
        
        for i in range(3 - bytes_num):
            s64_list.append('_')
    
    return ''.join(s64_list)

def s7decode(encoded_str: str) -> str:
    """S7解码"""
    encoded_str = encoded_str.rstrip('_')
    data = bytearray()
    index = 0
    
    while index < len(encoded_str):
        chunk = encoded_str[index:index+4]
        indices = [S7_TABLE.index(c) for c in chunk]
        
        if len(chunk) == 4:
            num = (indices[0] << 18) | (indices[1] << 12) | (indices[2] << 6) | indices[3]
            data.append((num >> 16) & 0xFF)
            data.append((num >> 8) & 0xFF)
            data.append(num & 0xFF)
        elif len(chunk) == 3:
            num = (indices[0] << 12) | (indices[1] << 6) | indices[2]
            data.append((num >> 10) & 0xFF)
            data.append((num >> 2) & 0xFF)
        elif len(chunk) == 2:
            num = (indices[0] << 6) | indices[1]
            data.append((num >> 4) & 0xFF)
        
        index += len(chunk)
    
    return data.decode('utf-8', errors='replace')

def generate_s7t(s7_string: str) -> str:
    """生成S7T值（原始算法）"""
    combined = 's7' + s7_string
    md5_hash = hashlib.md5(combined.encode('utf-8')).hexdigest()
    return md5_hash[6:11]

def get_original_s7t(decoded_str: str) -> str:
    """通过明文重新编码计算原始S7T"""
    re_encoded = s7encode(decoded_str)
    return generate_s7t(re_encoded)

def main():
    print("=== S7加解密工具（修复S7T计算）===")
    print("1. 加密\n2. 解密")
    choice = input("请选择操作(1/2): ").strip()
    text = input("输入文本: ").strip()
    
    try:
        if choice == '1':
            encoded = s7encode(text)
            s7t_value = generate_s7t(encoded)
            print(f"\n加密结果:\n{encoded}")
            print(f"S7T值: {s7t_value}")
            result = f"{encoded}\nS7T: {s7t_value}"
        elif choice == '2':
            decoded = s7decode(text)
            # 关键修复：通过重新编码明文获取原始S7T
            original_s7t = get_original_s7t(decoded)
            print(f"\n解密结果:\n{decoded}")
            print(f"原始S7T值: {original_s7t}")
            result = f"{decoded}\n原始S7T: {original_s7t}"
        else:
            print("无效选择")
            return
        
        os.makedirs('s7_results', exist_ok=True)
        filename = f"s7_results/{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"操作: {'加密' if choice == '1' else '解密'}\n")
            f.write(f"输入: {text}\n")
            f.write(f"输出: {result}\n")
        print(f"\n结果已保存到: {filename}")
    except Exception as e:
        print(f"\n处理出错: {str(e)}")

if __name__ == "__main__":
    # 验证测试
    test_str = "act=get_map_list_info&fn_list=94704518559841&playable=1&time=1754799757&auth=6e9bb93f2f6cb96c4ac65bfb1f4024a6&s2t=1754799721&uin=1783042094&ver=1.48.0&apiid=1&lang=0&country=CN&s7e=1"
    print("运行验证测试...")
    
    encoded = s7encode(test_str)
    s7t_value = generate_s7t(encoded)
    print(f"加密结果: {encoded[:50]}... (共{len(encoded)}字符)")
    print(f"S7T值: {s7t_value}")
    
    decoded = s7decode(encoded)
    original_s7t = get_original_s7t(decoded)
    print(f"解密验证: {'成功' if decoded == test_str else '失败'}")
    print(f"原始S7T值: {original_s7t}")
    
    print("="*50)
    main()