# ComfyUI Danbooru 标签分类器 V2.0 (Danbooru Tag Sorter - Packer/Extractor)

[](https://github.com/comfyanonymous/ComfyUI)
[](https://www.python.org/)
[](https://www.google.com/search?q=LICENSE)

你是否还在为别人给的串很难看懂而烦恼？是否还在为反推出一堆史山tag而焦虑？  
一个高效的 Danbooru 标签分类器 ComfyUI 节点，能够自动将输入的杂乱 Danbooru 标签按照您自定义的类别进行智能分类和排序！  
开发用于配合 WD1.4 反推图片使用。

觉得有用请点个 Star \~！

## V2.0 Update

1.  **解决了臃肿的输出口**：从单节点12输出变为“单节点打包+单节点解包提取”的模块化模式。
2.  **新功能**：增加了正则黑名单、Tag黑名单、自动去重、JSON配置文件加载等功能。
3.  **修复**：修复了V1.0分类后输出的tag串中，最末尾的tag没有逗号的问题。

## ✨ 功能特点
![节点预览](example/sample.png)

  - **智能标签分类**：基于本地 Excel 数据库自动分类 Danbooru 标签，相比调用 LLM 更快、更省钱（完全免费！）
  - **模块化设计（V2.0）**：采用 **Sorter节点 (打包)** + **Getter节点 (提取)** 的模式，更注重用户自主搭配各种Tag组成新的大类输出；界面更简洁，想取哪个分类就取哪个，告别杂乱的连线。
  - **高级过滤功能（V2.0）**：支持 **正则匹配黑名单** 和 **精确匹配黑名单**，新增 **自动去重**。
  - **配置外置化（V2.0）**：支持通过修改本地同级目录中的 `defaults_config.json` 文件加载默认映射和顺序，无需修改代码。
  - **内存缓存优化**：仅在首次运行时加载数据库，后续调用使用内存缓存。
  - **灵活 I/O**：支持多行标签输入，可选择是否包含分类注释。
  - **性能优先**：哈希表索引快速匹配，处理大量标签无压力。

## 📦 安装方法

### 方法一：直接安装

1.  将 Source ZIP 文件复制到 ComfyUI  `./custom_nodes` 文件夹中并解压
2.  重启 ComfyUI
3.  在节点列表中搜索 "Danbooru Tag Sorter (Packer)" 节点和"Danbooru Tag Getter (Extractor)"节点

### 方法二：Git 安装

```bash
git clone https://github.com/RafealaSilva/ComfyUI-Danbooru-Tag-Sorter-Node.git
```

### 依赖要求

  - Python 3.8+
  - openpyxl 库
  - pandas 库

<!-- end list -->

```bash
pip install openpyxl pandas
```

或者

```bash
pip install -r requirements.txt
```

**请将这两个库安装在 ComfyUI 的 Python 环境中！不要 cmd 直接安装在系统环境里！**

## 🎮 使用方法

### 基本流程

1.  **加载分类器**：添加 **Danbooru Tag Sorter (Packer)** 节点。
2.  **输入标签**：连接反推节点的输出或直接在 `tags` 文本框输入。
3.  **获取全量文本**：直接使用 `ALL_TAGS` 输出口，获得整理好格式的完整 Prompt。
4.  **获取特定分类（如只想要“服饰词”）**：
      - 添加 **Danbooru Tag Getter (Extractor)** 节点。
      - 用户自定义配置相关的映射规则，并且设定新分类的输出顺序。（或直接使用我提供的懒人预设）
      - 将 Sorter 的 `分类数据包` 输出口连接到 Getter 的 `tag_bundle` 输入。
      - 在 Getter 的 `category_name` 中输入你想提取的分类名（例如：`服饰词`）。
6.  **本项目附带无脑懒人分类工作流示例，直接下载使用即可。**

### Tag黑名单

**黑名单过滤**  

1. 精确匹配过滤：  
   基本语法为：tag1, tag2, tag3, 如同正常走一遍输入提示词的流程  
   例如，在 `tag_blacklist` 中输入 `bad hands, mutation`，这些词将不会出现在结果中。 
        
2. 正则匹配过滤：  
   使用正则表达式匹配相关词，不懂可以上网搜或者问LLM。  
   例如，在 `regex_blacklist` 中输入 `[^,]*(censor)[^,]*\s*`，所有包含 "censor" 这六个字母的标签都会被移除。

### 数据库配置

Danbooru 标签表格在本项目文件夹 `tags_database` 中，在 `excel_file` 参数中填入绝对路径即可（记得删除路径两边的引号）。

### 性能说明

第一次运行需要加载数据库并缓存，大概耗时 10s 以内；第二次开始仅需不到 0.01 秒即可分类完成。（测试环境：AMD-9000系 CPU）

### 输入示例

```text
1girl, solo, blonde hair, solo, blue eyes, smile, school uniform, classroom, looking at viewer, masterpiece, best quality, bad hands, 
```

### 输出示例 (此时由ALL\_TAGS端口输出)

**当 is\_comment 为 True 时：**

```text
背景词:
classroom, 
人物对象词:
1girl, 
角色特征词:
blue eyes, blonde hair, 
角色部位词:
bad hands, 
服饰词:
school uniform, 
角色表情词:
looking at viewer, smile, 
镜头词:
solo, solo, 
未归类词:
masterpiece, best quality,
--------------输出结果带注释
```

**当 is\_comment 为 False 时：**

```text
classroom, 
1girl, 
blue eyes, blonde hair, 
bad hands, 
school uniform, 
looking at viewer, smile, 
solo, solo, 
masterpiece, best quality,
--------------输出结果无注释
```

**当 黑名单列表 为 smile, classroom  时：**

```text
1girl, 
blue eyes, blonde hair, 
bad hands, 
school uniform, 
looking at viewer, 
solo, solo, 
masterpiece, best quality,
--------------输出结果没有“smile, classroom, ”这两个tag
```

**当 deduplicate\_tags(自动去重) 为 True 时：**

```text
1girl, 
blue eyes, blonde hair, 
bad hands, 
school uniform, 
looking at viewer, 
solo, 
masterpiece, best quality, 
```

### 输出示例 (由Packer的分类数据包端口输出，交由Extractor解包)

**当 Extractor 的 category\_name == 角色表情词 且 黑名单为空 时**

```text
looking at viewer, smile, 
```




## 🔧 节点接口说明

### 1\. Danbooru Tag Sorter (Packer) - 核心分类器

**输入参数**

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `tags` | STRING | - | Danbooru标签，支持多行输入 |
| `excel_file` | STRING | - | Excel或CSV数据库文件路径| 
| `category_mapping` | STRING | default | 分类映射规则字典 |
| `new_category_order` | STRING | default | 新分类输出顺序列表 |
| `default_category` | STRING | "未归类词" | 无法识别的Tag归入此类，可自定义名称 |
| `regex_blacklist` | STRING | "" | **(V2.0)** 正则表达式黑名单，匹配到的Tag会被剔除 |
| `tag_blacklist` | STRING | "" | **(V2.0)** 精确Tag黑名单，匹配到的Tag会被剔除 |
| `deduplicate_tags` | BOOLEAN | False | **(V2.0)** 是否自动去除重复的Tag |
| `validation` | BOOLEAN | True | **(V2.0)** 是否校验Mapping和Order的一致性 |
| `force_reload` | BOOLEAN | False | 强制重新加载数据库 |
| `is_comment` | BOOLEAN | True | 是否在ALL\_TAGS输出中添加分类注释 |

**输出参数**

| 输出名 | 类型 | 说明 |
|--------|------|------|
| `分类数据包` | TAG\_BUNDLE | **(V2.0)** 包含所有分类数据的打包对象，需连接 Getter 节点解包 |
| `ALL_TAGS` | STRING | 格式化后的完整字符串 |

-----

### 2\. Danbooru Tag Getter (Extractor) - 分类提取器

用于从数据包中提取特定的单一分类。

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `tag_bundle` | TAG\_BUNDLE | 连接 Sorter 节点的分类数据包节点输出 |
| `category_name` | STRING | 输入你想提取的分类名称（如：`角色特征词`、`背景词`） |

**输出**：对应分类下的 Tag 字符串。

-----

### 3\. Danbooru Tag Clear Cache - 缓存清理

用于强制刷新数据库。

-----

## ⚙️ 配置文件说明

### defaults\_config.json

你可以在插件根目录下修改 `defaults_config.json` 中的映射规则来修改默认规则，而无需修改 Python 代码。

**JSON 格式示例：**

```json
{
  "order": [
    "新大类", "画师词", "背景词", "人物对象词", "角色特征词", "未归类词"
  ],
  "mapping": [
    ["原大类", "小类", "新大类"],
    ["画面", "艺术家风格", "画师词"],
    ["环境", "天空", "背景词"],
    ["人物", "翅膀", "角色特征词"]
  ]
}
```

### Excel/CSV 数据库格式

数据库文件需要包含以下列：

  - `english`: 标签英文名
  - `category`: 原始父类
  - `subcategory`: 原始子类

