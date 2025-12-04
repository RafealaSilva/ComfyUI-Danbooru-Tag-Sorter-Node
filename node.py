import pandas as pd
from collections import defaultdict
import os
import ast
import comfy
import torch
import hashlib
import json

# 全局缓存字典
_tag_cache = {}


# 处理类
class DanbooruTagSorter:
    def __init__(self, excel_path, category_mapping, new_category_order, default_category="未归类词"):
        self.excel_path = excel_path
        self.category_mapping = category_mapping
        self.new_category_order = new_category_order
        self.default_category = default_category
        self.tag_db = self._load_database_with_cache()

    def get_new_category(self, original_category, original_subcategory):
        key = (original_category, original_subcategory)
        return self.category_mapping.get(key, self.default_category)

    def _generate_cache_key(self):
        # 生成哈希键
        params = {
            "excel_path": self.excel_path,
            "category_mapping": json.dumps(sorted(self.category_mapping.items())),
            "new_category_order": json.dumps(self.new_category_order),
            "default_category": self.default_category
        }

        # 将参数字典转换为字符串、并生成哈希
        params_str = json.dumps(params, sort_keys=True)
        cache_key = hashlib.md5(params_str.encode()).hexdigest()
        return cache_key

    def _load_database_with_cache(self):
        # 生成缓存键
        cache_key = self._generate_cache_key()

        if cache_key in _tag_cache:
            print(f"从缓存加载数据库喵:{self.excel_path}")
            return _tag_cache[cache_key]
        # 缓存没有就重载数据库
        print(f"正在读取数据库喵:{self.excel_path} ...")
        if not os.path.exists(self.excel_path):
            raise FileNotFoundError(f"找不到文件喵:{self.excel_path}\n如果是复制绝对路径请删除两边引号喵")
        if self.excel_path.endswith('.csv'):
            df = pd.read_csv(self.excel_path)
        else:
            df = pd.read_excel(self.excel_path)
        tag_db = {}
        for index, row in df.iterrows():
            eng_tag = str(row['english']).strip().lower()
            cat = str(row['category']).strip()
            sub = str(row['subcategory']).strip()
            new_cat = self.get_new_category(cat, sub)
            clean_key = eng_tag.replace('_', ' ')

            tag_db[clean_key] = {
                'original': eng_tag,
                'original_category': cat,
                'original_subcategory': sub,
                'new_category': new_cat,
                'rank': index
            }

        print(f"数据库加载完成喵，共索引 {len(tag_db)} 个 Tags喵，已缓存喵。")

        _tag_cache[cache_key] = tag_db

        return tag_db

    def process_tags(self, raw_string, add_category_comment=True):
        input_tags = [t.strip() for t in raw_string.split(',') if t.strip()]

        new_category_buckets = defaultdict(list)
        unmatched_tags = []

        # 匹配
        for tag in input_tags:
            tag_lower = tag.lower()
            lookup_key = tag_lower.replace('_', ' ')

            if lookup_key in self.tag_db:
                info = self.tag_db[lookup_key]
                group_key = info['new_category']
                new_category_buckets[group_key].append((info['rank'], tag))
            else:
                unmatched_tags.append(tag)

        categorized_tags = {}
        for category in self.new_category_order:
            categorized_tags[category] = ""

        final_lines = []

        # 按照新分类顺序 输出
        for category in self.new_category_order:
            if category in new_category_buckets:
                items = sorted(new_category_buckets[category], key=lambda x: x[0])
                tags_str = ", ".join([item[1] for item in items])
                categorized_tags[category] = tags_str
                if add_category_comment:
                    final_lines.append(f"{category}:")

                final_lines.append(f"{tags_str},")

                del new_category_buckets[category]

        # 处理未在分类顺序中定义的新分类
        remaining_categories = list(new_category_buckets.keys())
        if remaining_categories:
            for category in sorted(remaining_categories):
                items = sorted(new_category_buckets[category], key=lambda x: x[0])
                tags_str = ", ".join([item[1] for item in items])
                if category not in categorized_tags:
                    categorized_tags[category] = tags_str
                if add_category_comment:
                    final_lines.append(f"{category}:")

                final_lines.append(f"{tags_str},")

        # 处理完全未识别的Tags
        if unmatched_tags:
            unmatched_str = ", ".join(unmatched_tags)
            final_lines.append(unmatched_str)
            # 将未识别的标签添加到未归类词
            if categorized_tags.get("未归类词"):
                categorized_tags["未归类词"] += ", " + unmatched_str if categorized_tags["未归类词"] else unmatched_str
            else:
                categorized_tags["未归类词"] = unmatched_str

        return "\n".join(final_lines), categorized_tags


# ComfyUI
class DanbooruTagSorterNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tags": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "placeholder": "输入Danbooru标签喵，逗号分隔喵"
                }),
            },
            "optional": {
                "excel_file": ("STRING", {
                    "multiline": False,
                }),
                "category_mapping": ("STRING", {
                    "multiline": True,
                    "default": """{
    ("画面", "艺术家风格"): "画师词",
    ("画面", "艺术派系"): "画师词",
    ("画面", "艺术类型"): "画师词",
    ("画面", "艺术风格"): "画师词",
    ("艺术家", "设定"): "画师词",
    ("画面", "光照"): "背景词",
    ("画面", "画笔"): "背景词",
    ("画面", "画面量质"): "背景词",
    ("画面", "背景"): "背景词",
    ("画面", "颜色"): "背景词",
    ("场景", "城市"): "背景词",
    ("场景", "室内"): "背景词",
    ("场景", "室外"): "背景词",
    ("环境", "云"): "背景词",
    ("环境", "大自然"): "背景词",
    ("环境", "天气"): "背景词",
    ("环境", "天空"): "背景词",
    ("环境", "季节"): "背景词",
    ("环境", "氛围"): "背景词",
    ("环境", "水"): "背景词",
    ("人物", "对象"): "人物对象词",
    ("人物", "翅膀"): "角色特征词",
    ("人物", "眼睛"): "角色特征词",
    ("人物", "头发发型"): "角色特征词",
    ("人物", "肩部"): "角色部位词",
    ("人物", "腿部"): "角色部位词",
    ("人物", "腹部"): "角色部位词",
    ("人物", "腰部"): "角色部位词",
    ("人物", "指甲"): "角色部位词",
    ("人物", "身材"): "角色部位词",
    ("人物", "胸部"): "性征部位词",
    ("人物", "性器官"): "性征部位词",
    ("服饰", "正装"): "服饰词",
    ("服饰", "衣服风格"): "服饰词",
    ("服饰", "上半身服装"): "服饰词",
    ("服饰", "裙子"): "服饰词",
    ("服饰", "裤子"): "服饰词",
    ("服饰", "衣服套装"): "服饰词",
    ("服饰", "袜子"): "服饰词",
    ("服饰", "鞋子"): "服饰词",
    ("服饰", "衣服花纹"): "服饰词",
    ("服饰", "衣服装饰"): "服饰词",
    ("服饰", "围巾"): "服饰词",
    ("服饰", "头部装饰物"): "服饰词",
    ("服饰", "手部装饰物"): "服饰词",
    ("服饰", "脸部装饰物"): "服饰词",
    ("服饰", "腿部装饰物"): "服饰词",
    ("服饰", "其他装饰物"): "服饰词",
    ("表情动作", "性爱动作"): "动作词",
    ("表情动作", "基础动作"): "动作词",
    ("表情动作", "手部动作"): "动作词",
    ("表情动作", "手抓着某物"): "动作词",
    ("表情动作", "手放在某地"): "动作词",
    ("表情动作", "手部拿着某物"): "动作词",
    ("表情动作", "腿部动作"): "动作词",
    ("表情动作", "其他动作"): "动作词",
    ("镜头", "人物视觉朝向"): "角色表情词",
    ("表情动作", "哭"): "角色表情词",
    ("表情动作", "笑"): "角色表情词",
    ("表情动作", "生气"): "角色表情词",
    ("表情动作", "不开心"): "角色表情词",
    ("表情动作", "蔑视"): "角色表情词",
    ("表情动作", "其他表情"): "角色表情词",
    ("人物", "面部"): "角色五官词",
    ("人物", "脸型"): "角色五官词",
    ("人物", "眉毛"): "角色五官词",
    ("人物", "瞳孔"): "角色五官词",
    ("人物", "鼻子"): "角色五官词",
    ("人物", "嘴巴"): "角色五官词",
    ("人物", "牙齿"): "角色五官词",
    ("人物", "舌头"): "角色五官词",
    ("镜头", "人物构图"): "镜头词",
    ("镜头", "特写镜头"): "镜头词",
    ("镜头", "其他沟通"): "镜头词",
    ("镜头", "镜头角度"): "镜头词",
    ("镜头", "效果"): "镜头词",
}""",
                    "placeholder": "输入分类映射字典喵"
                }),
                "new_category_order": ("STRING", {
                    "multiline": True,
                    "default": "[\"画师词\", \"背景词\", \"人物对象词\", \"角色特征词\", \"角色五官词\", \"角色部位词\", \"性征部位词\", \"服饰词\", \"动作词\", \"角色表情词\", \"镜头词\", \"未归类词\"]",
                    "placeholder": "输入新分类顺序列表喵"
                }),
                "default_category": ("STRING", {
                    "multiline": False,
                    "default": "未归类词"
                }),
                "force_reload": ("BOOLEAN", {
                    "default": False,
                    "label": "强制重新加载"
                }),
                "is_comment": ("BOOLEAN", {
                    "default": True,
                    "label": "是否注释"
                }),
            }
        }

    RETURN_TYPES = (
    "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING",
    "STRING", "STRING")
    RETURN_NAMES = (
    "画师词", "背景词", "人物对象词", "角色特征词", "角色五官词", "角色部位词", "性征部位词", "服饰词", "动作词",
    "角色表情词", "镜头词", "未归类词", "ALL_TAGS")
    FUNCTION = "process"
    CATEGORY = "Danbooru Tags"

    def process(self, tags, excel_file="", category_mapping="",
                new_category_order="", default_category="未归类词", force_reload=False, is_comment=True):
        try:
            # 解析输入参数
            if category_mapping:
                try:
                    category_mapping_dict = ast.literal_eval(category_mapping)
                    if not isinstance(category_mapping_dict, dict):
                        raise ValueError("category_mapping必须是字典格式喵")
                except Exception as e:
                    print(f"解析category_mapping失败喵，使用默认值喵:{e}")
                    category_mapping_dict = self._get_default_mapping()
            else:
                category_mapping_dict = self._get_default_mapping()

            if new_category_order:
                try:
                    new_category_order_list = ast.literal_eval(new_category_order)
                    if not isinstance(new_category_order_list, list):
                        raise ValueError("new_category_order必须是列表格式喵")
                except Exception as e:
                    print(f"解析new_category_order失败喵，使用默认值喵:{e}")
                    new_category_order_list = self._get_default_order()
            else:
                new_category_order_list = self._get_default_order()

            if not excel_file:
                excel_file = ""

            # 检查文件是否存在
            if not os.path.exists(excel_file):
                raise FileNotFoundError(f"库不存在喵:{excel_file}\n如果是复制绝对路径请删除两边引号喵")

            # 如果强制重新加载，清除相关缓存
            if force_reload:
                self._clear_cache(excel_file, category_mapping_dict, new_category_order_list, default_category)
                print("已清除缓存喵，将重新加载库喵")

            # 创建分类器并处理标签
            sorter = DanbooruTagSorter(
                excel_file,
                category_mapping_dict,
                new_category_order_list,
                default_category
            )

            # 传递is_comment参数给process_tags方法
            all_tags_result, categorized_tags = sorter.process_tags(tags, add_category_comment=is_comment)

            # 按照固定顺序输出
            output_order = self._get_default_order()
            outputs = []
            for category in output_order:
                tag_output = categorized_tags.get(category, "")
                outputs.append(tag_output)
            outputs.append(all_tags_result)

            return tuple(outputs)

        except Exception as e:
            print(f"DanbooruTagSorterNode错误喵，气死了喵:{e}")
            empty_outputs = [""] * 13
            return tuple(empty_outputs)

    def _get_default_mapping(self):
        return {
            ("画面", "艺术家风格"): "画师词",
            ("画面", "艺术派系"): "画师词",
            ("画面", "艺术类型"): "画师词",
            ("画面", "艺术风格"): "画师词",
            ("艺术家", "设定"): "画师词",
            ("画面", "光照"): "背景词",
            ("画面", "画笔"): "背景词",
            ("画面", "画面量质"): "背景词",
            ("画面", "背景"): "背景词",
            ("画面", "颜色"): "背景词",
            ("场景", "城市"): "背景词",
            ("场景", "室内"): "背景词",
            ("场景", "室外"): "背景词",
            ("环境", "云"): "背景词",
            ("环境", "大自然"): "背景词",
            ("环境", "天气"): "背景词",
            ("环境", "天空"): "背景词",
            ("环境", "季节"): "背景词",
            ("环境", "氛围"): "背景词",
            ("环境", "水"): "背景词",
            ("人物", "对象"): "人物对象词",
            ("人物", "翅膀"): "角色特征词",
            ("人物", "眼睛"): "角色特征词",
            ("人物", "头发发型"): "角色特征词",
            ("人物", "肩部"): "角色部位词",
            ("人物", "腿部"): "角色部位词",
            ("人物", "腹部"): "角色部位词",
            ("人物", "腰部"): "角色部位词",
            ("人物", "指甲"): "角色部位词",
            ("人物", "身材"): "角色部位词",
            ("人物", "胸部"): "性征部位词",
            ("人物", "性器官"): "性征部位词",
            ("服饰", "正装"): "服饰词",
            ("服饰", "衣服风格"): "服饰词",
            ("服饰", "上半身服装"): "服饰词",
            ("服饰", "裙子"): "服饰词",
            ("服饰", "裤子"): "服饰词",
            ("服饰", "衣服套装"): "服饰词",
            ("服饰", "袜子"): "服饰词",
            ("服饰", "鞋子"): "服饰词",
            ("服饰", "衣服花纹"): "服饰词",
            ("服饰", "衣服装饰"): "服饰词",
            ("服饰", "围巾"): "服饰词",
            ("服饰", "头部装饰物"): "服饰词",
            ("服饰", "手部装饰物"): "服饰词",
            ("服饰", "脸部装饰物"): "服饰词",
            ("服饰", "腿部装饰物"): "服饰词",
            ("服饰", "其他装饰物"): "服饰词",
            ("表情动作", "性爱动作"): "动作词",
            ("表情动作", "基础动作"): "动作词",
            ("表情动作", "手部动作"): "动作词",
            ("表情动作", "手抓着某物"): "动作词",
            ("表情动作", "手放在某地"): "动作词",
            ("表情动作", "手部拿着某物"): "动作词",
            ("表情动作", "腿部动作"): "动作词",
            ("表情动作", "其他动作"): "动作词",
            ("镜头", "人物视觉朝向"): "角色表情词",
            ("表情动作", "哭"): "角色表情词",
            ("表情动作", "笑"): "角色表情词",
            ("表情动作", "生气"): "角色表情词",
            ("表情动作", "不开心"): "角色表情词",
            ("表情动作", "蔑视"): "角色表情词",
            ("表情动作", "其他表情"): "角色表情词",
            ("人物", "面部"): "角色五官词",
            ("人物", "脸型"): "角色五官词",
            ("人物", "眉毛"): "角色五官词",
            ("人物", "瞳孔"): "角色五官词",
            ("人物", "鼻子"): "角色五官词",
            ("人物", "嘴巴"): "角色五官词",
            ("人物", "牙齿"): "角色五官词",
            ("人物", "舌头"): "角色五官词",
            ("镜头", "人物构图"): "镜头词",
            ("镜头", "特写镜头"): "镜头词",
            ("镜头", "其他沟通"): "镜头词",
            ("镜头", "镜头角度"): "镜头词",
            ("镜头", "效果"): "镜头词",
        }

    def _get_default_order(self):
        return ["画师词", "背景词", "人物对象词", "角色特征词", "角色五官词", "角色部位词", "性征部位词", "服饰词",
                "动作词", "角色表情词", "镜头词", "未归类词"]

    def _clear_cache(self, excel_file, category_mapping, new_category_order, default_category):
        try:
            # 创建个临时的sorter生成缓存键
            temp_sorter = DanbooruTagSorter(
                excel_file,
                category_mapping,
                new_category_order,
                default_category
            )

            cache_key = temp_sorter._generate_cache_key()
            if cache_key in _tag_cache:
                del _tag_cache[cache_key]
                print(f"已清除缓存喵:{cache_key}")
        except Exception as e:
            print(f"清除缓存失败了喵:{e}")


class DanbooruTagClearCacheNode:  # 手动清除缓存
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {}
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "clear_cache"
    CATEGORY = "Danbooru Tags"
    OUTPUT_NODE = True

    def clear_cache(self):
        global _tag_cache
        cache_count = len(_tag_cache)
        _tag_cache.clear()
        print(f"已清除所有DanbooruTags缓存喵({cache_count}个缓存项喵)")
        return ()


# Register nodes
NODE_CLASS_MAPPINGS = {
    "DanbooruTagSorterNode": DanbooruTagSorterNode,
    "DanbooruTagClearCacheNode": DanbooruTagClearCacheNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DanbooruTagSorterNode": "Danbooru Tag Sorter",
    "DanbooruTagClearCacheNode": "Danbooru Tag Clear Cache"
}
