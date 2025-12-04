# ComfyUI Danbooru 标签分类器

[![ComfyUI](https://img.shields.io/badge/ComfyUI-Node-blue)](https://github.com/comfyanonymous/ComfyUI)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

你是否还在为别人给的串很难看懂而烦恼？是否还在为反推出的一堆史山tag而焦虑？  
一个高效的 Danbooru 标签分类器 ComfyUI 节点，能够自动将输入的杂乱 Danbooru 标签按照预设的分类系统进行智能分类和排序！  
开发用于配合WD1.4反推图片使用。

觉得有用请点个Star ~！

## ✨ 功能特点

![节点预览](example/1.png)

- **智能标签分类**：基于本地 Excel 数据库自动分类 Danbooru 标签，相比调用LLM更快、更省钱
- **12个分类输出**：提供画师词、背景词、人物对象词等 12 个独立输出口
- **内存缓存优化**：仅在首次运行时加载数据库，后续调用使用内存缓存
- **可自定义的映射规则**：支持自定义分类映射规则和排序顺序
- **灵活I/O**：支持多行标签输入，可选择是否包含分类注释
- **性能优先**：哈希表索引快速匹配，处理大量标签无压力

## 📦 安装方法

### 方法一：直接安装
1. 将Source ZIP文件复制到 ComfyUI  `./custom_nodes` 文件夹中并解压
2. 重启 ComfyUI
3. 在节点列表中搜索 "Danbooru Tag Sorter" 节点

### 方法二：Git 安装
```bash
git clone https://github.com/RafealaSilva/ComfyUI-Danbooru-Tag-Sorter-Node.git
```

### 依赖要求
- Python 3.8+
- pandas 库

## 🎮 使用方法

### 基本使用
1. 在 ComfyUI 中右键或双击鼠标左键打开节点搜索框
2. 搜索 "Danbooru Tag Sorter"
3. 将节点拖到工作区
4. 连接标签输入或直接输入标签文本，搭配反推工作流表现优异
5. 配置节点参数，Danbooru 标签表格在本项目文件夹tags_database中，直接复制绝对路径即可，记得删除两边的引号
6. 运行工作流，第一次需要缓存数据比较慢，大概耗时3秒；第二次开始仅需不到0.01秒即可分类完成。（AMD-9700X）

### 输入示例
```text
1girl, solo, blonde hair, blue eyes, smile, school uniform, classroom, looking at viewer, masterpiece, best quality
```

### 输出示例
**当is_comment 为 True 时：**
```text
画师词:
masterpiece, best quality,
角色特征词:
blonde hair, blue eyes,
角色表情词:
smile,
服饰词:
school uniform,
背景词:
classroom,
镜头词:
looking at viewer,
```

**当is_comment 为 False 时：**
```text
masterpiece, best quality,
blonde hair, blue eyes,
smile,
school uniform,
classroom,
looking at viewer,
```

## 🔧 节点接口说明

### 输入参数

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `tags` | STRING | - | Danbooru标签，逗号分隔，支持多行输入 |
| `excel_file` | STRING | 默认路径 | Excel数据库文件路径 |
| `category_mapping` | STRING | 默认映射 | 分类映射规则字典 |
| `new_category_order` | STRING | 默认顺序 | 新分类输出顺序列表 |
| `default_category` | STRING | "未归类词" | 默认分类名称 |
| `force_reload` | BOOLEAN | False | 强制重新加载数据库 |
| `is_comment` | BOOLEAN | True | 是否在ALL_TAGS输出中添加分类注释 |

### 输出参数

| 输出名 | 类型 | 说明 |
|--------|------|------|
| `画师词` | STRING | 画师相关标签 |
| `背景词` | STRING | 背景相关标签 |
| `人物对象词` | STRING | 人物对象标签 |
| `角色特征词` | STRING | 角色特征标签 |
| `角色五官词` | STRING | 角色五官标签 |
| `角色部位词` | STRING | 角色身体部位标签 |
| `性征部位词` | STRING | 性征部位标签 |
| `服饰词` | STRING | 服饰相关标签 |
| `动作词` | STRING | 动作相关标签 |
| `角色表情词` | STRING | 表情相关标签 |
| `镜头词` | STRING | 镜头相关标签 |
| `未归类词` | STRING | 未识别标签 |
| `ALL_TAGS` | STRING | 完整格式化输出 |

## ⚙️ 配置文件说明

### Excel 数据库格式
数据库文件需要包含以下列：
- `english`: 标签英文名
- `category`: 原始父类
- `subcategory`: 原始子类

### 默认分类映射
节点内置了默认分类映射，举例如下：

```python
{
    ("画面", "艺术家风格"): "画师词",
    ("画面", "艺术派系"): "画师词",
    ("画面", "艺术类型"): "画师词",
    ("画面", "艺术风格"): "画师词",
    # ... 更多映射规则或需要自定义请前往node.py第176行开始查看
}
```

### 默认分类及其输出顺序
```python
[
    "画师词", "背景词", "人物对象词", "角色特征词", 
    "角色五官词", "角色部位词", "性征部位词", "服饰词", 
    "动作词", "角色表情词", "镜头词", "未归类词"
]
```

## 🚀 另类用法

### 自定义数据库
1. 准备 Excel 文件，确保包含 `english`、`category`、`subcategory` 三列
2. 修改节点中的 `excel_file` 参数指向你的文件路径
3. 根据需要调整分类映射规则

### 缓存管理
节点内置了缓存机制：
- **自动缓存**：首次加载后自动缓存到内存
- **强制重载**：设置 `force_reload=True` 强制重新加载
- **清除缓存**：使用 "Danbooru Tag Clear Cache" 节点清除所有缓存
