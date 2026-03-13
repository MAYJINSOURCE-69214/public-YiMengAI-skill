#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电商商品标题生成器 v2.0
三段式结构：产品类型 + 材质描述 / 高权重词 / 产品名
适用于淘宝、抖音、小红书等平台的天然水晶类商品
"""

import argparse
import random
from typing import List, Tuple, Optional

# 产品类型列表
PRODUCT_TYPES = ["手链", "手镯", "项链", "吊坠", "手串", "戒指", "耳环", "首饰"]

# 第一段模板：产品类型 + 材质/描述混合
FIRST_SEGMENT_TEMPLATES = [
    "{type}设计{material}{type}",
    "{type}轻奢{material}女款",
    "{type}转运{material}女",
    "{type}高级感{material}女手工",
    "{type}双圈{material}手串转运",
    "{type}天然{material}设计款",
    "{type}精致{material}女饰品",
    "{type}百搭{material}转运款",
]

# 第二段：高权重词组合（10-12 字）
SECOND_SEGMENTS = [
    "轻奢气质女款高级转运饰品",
    "招财转运高级感百搭饰品",
    "轻奢精致高级感百搭气质饰品",
    "招财轻奢百搭转运旺运首饰",
    "轻奢高级女款百搭首饰",
    "温柔精致小众设计感饰品",
    "优雅百搭高级感转运饰品",
    "时尚简约元气满满精致饰品",
    "高级感轻奢气质女款饰品",
    "小众设计温柔精致感饰品",
    "转运提升优雅气质款饰品",
    "静心舒缓高级感百搭饰品",
]

# 材质简化映射（去除"天然"前缀用于部分模板）
MATERIAL_SHORT_MAP = {
    "天然黄水晶": "黄水晶",
    "天然白水晶": "白水晶",
    "天然紫水晶": "紫水晶",
    "天然粉水晶": "粉水晶",
    "天然绿幽灵": "绿幽灵",
    "天然发晶": "发晶",
    "天然黑曜石": "黑曜石",
    "天然碧玺": "碧玺",
    "天然石榴石": "石榴石",
    "天然海蓝宝": "海蓝宝",
    "天然月光石": "月光石",
    "天然太阳石": "太阳石",
}


def extract_product_type(product_name: str) -> Optional[str]:
    """从产品名中提取产品类型"""
    for ptype in PRODUCT_TYPES:
        if product_name.endswith(ptype):
            return ptype
    return None


def get_short_material(material: str) -> str:
    """获取简化材质名"""
    return MATERIAL_SHORT_MAP.get(material, material)


def calculate_chars(text: str) -> int:
    """计算字符数：中文=2，空格=1，英文=1"""
    count = 0
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            count += 2
        else:
            count += 1
    return count


def remove_duplicate_type(first_segment: str, product_name: str, product_type: Optional[str]) -> str:
    """移除产品名中重复的类型词"""
    if not product_type:
        return product_name
    
    # 如果第一段已经包含产品类型，从产品名末尾移除
    if product_type in first_segment and product_name.endswith(product_type):
        return product_name[:-len(product_type)]
    
    return product_name


def generate_first_segment(product_type: str, material: str, template: str) -> str:
    """生成第一段"""
    short_material = get_short_material(material)
    
    # 随机选择使用完整材质名还是简化版
    if random.random() > 0.5:
        used_material = material
    else:
        used_material = short_material
    
    return template.format(type=product_type, material=used_material)


def generate_title(product_type: str, material: str, product_name: str, 
                   first_template: str, second_segment: str) -> Tuple[str, int]:
    """生成单个标题"""
    # 生成第一段
    first = generate_first_segment(product_type, material, first_template)
    
    # 生成第三段（去重）
    third = remove_duplicate_type(first, product_name, product_type)
    
    # 构建完整标题
    title = f"{first} {second_segment} {third}"
    
    # 计算字符数
    char_count = calculate_chars(title)
    
    return title, char_count


def generate_titles(product_name: str, material: str, count: int = 5) -> List[dict]:
    """生成多个标题"""
    titles = []
    used_combinations = set()
    
    # 提取产品类型
    product_type = extract_product_type(product_name)
    
    # 如果没有检测到产品类型，默认使用"手链"
    if not product_type:
        product_type = "手链"
    
    attempts = 0
    max_attempts = count * 5
    
    while len(titles) < count and attempts < max_attempts:
        attempts += 1
        
        # 随机选择第一段模板和第二段
        first_template = random.choice(FIRST_SEGMENT_TEMPLATES)
        second = random.choice(SECOND_SEGMENTS)
        
        # 避免重复组合
        combo_key = f"{first_template}|{second}"
        if combo_key in used_combinations:
            continue
        used_combinations.add(combo_key)
        
        # 生成标题
        title, char_count = generate_title(product_type, material, product_name, 
                                           first_template, second)
        
        titles.append({
            "title": title,
            "char_count": char_count,
            "valid": True
        })
    
    return titles


def main():
    # 设置 UTF-8 编码输出
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    parser = argparse.ArgumentParser(
        description="电商商品标题生成器 v2.0 - 生成三段式合规标题"
    )
    parser.add_argument(
        "--product", "-p",
        required=True,
        help="产品名（如：金钱召唤双圈手链）"
    )
    parser.add_argument(
        "--material", "-m",
        required=True,
        help="材质（如：天然黄水晶）"
    )
    parser.add_argument(
        "--count", "-c",
        type=int,
        default=5,
        help="生成标题数量（默认 5 条）"
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("技能 - 电商标题生成 v2.0")
    print("=" * 70)
    print(f"产品名：{args.product}")
    print(f"材质：{args.material}")
    print("=" * 70 + "\n")
    
    titles = generate_titles(args.product, args.material, args.count)
    
    if not titles:
        print("[X] 无法生成符合要求的标题，请检查输入或调整参数")
        return
    
    print(f"[OK] 生成 {len(titles)} 条标题：\n")
    
    for i, item in enumerate(titles, 1):
        print(f"{i}. {item['title']}")
        print(f"   字符数：{item['char_count']}\n")
    
    print("=" * 70)


if __name__ == "__main__":
    main()
