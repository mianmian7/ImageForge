# AssetCleanerForCocosCreator (Python Version)

**简介：一个基于 Python 的 CocosCreator 项目资源清理工具，自动化统计有哪些资源未使用，以及各类型资源的占比情况，从而帮助减小包体。**

代码��址：[https://github.com/foupwang/AssetCleanerForCocosCreator](https://github.com/foupwang/AssetCleanerForCocosCreator)

## 为什么需要AssetCleaner
- 随着产品功能增加、版本迭代、需求变更，项目资源越来越臃肿，其中有不少不再使用或未及时删除的资源（不仅仅是图片，还包括序列帧动画、Spine动画、Prefab等等），如何知道哪些资源是可以删除的？一个个手动查找是不能忍受的。
- 产品上线前，优化包体大小是不可避免的问题，包体里究竟有什么资源？哪些资源最占空间？它们的分布比例怎样？
- 非动态加载的资源，错误地放到了resources目录，增加网络下载和包体的负担。如何找出它们？

当项目资源数超过1000个时，以上问题变得更加突出，**`AssetCleaner`为解决以上资源优化问题而生。**

## AssetCleaner 功能
- **查找未使用资源**。自动查找assets目录下所有未引用的资源，并把结果输出到指定文件，方便开发者核对无误后删除。
- **分析包体**。自动统计指定目录下所有文件信息，并按类型区分从大到小输出到指定文件，方便后续分析做重点优化。
- **资源优化**。自动统计resources目录下非动态加载的资源，方便开发者核对后移动到非resources目录。

## AssetCleaner 使用 (Python Version)

`AssetCleaner` 已被重构为 `Python` 版本，所以需要先安装 `Python` (建议 3.6+)。

### 1. 安装依赖
本项目暂无外部依赖。如果未来有，可以通过 `pip` 安装：
```bash
pip install -r requirements.txt
```

### 2. 执行命令
目前支持以下几种命令：

```bash
# 查找未使用资源
python -m py_src.main clean [项目资源目录] [结果输出文件]

# 查找未使用资源，并且删除项目中未引用的图片、预制件、动画
python -m py_src.main clean [项目资源目录] [结果输出文件] --delete

# 按类型统计目录下所有文件从大到小排序
python -m py_src.main size [项目资源目录] [结果输出文件]
```

**例如:**

CocosCreator项目路径是 `d:/myproject`，则进入 AssetCleaner 的代码目录。

1.  **查找未使用资源**
    ```bash
    python -m py_src.main clean d:/myproject/assets d:/out.txt
    ```
    查找结果将会输出到 `d:/out.txt` 文件。

2.  **查找且自动删除未使用资源** (谨慎！请确保资源已备份)
    ```bash
    python -m py_src.main clean d:/myproject/assets d:/out.txt --delete
    ```

3.  **按类型统计assets目录下所有原始资源**
    ```bash
    python -m py_src.main size d:/myproject/assets d:/out.txt
    ```

4.  **按类型统计构建后的build/web-mobile目录下所有文件**
    ```bash
    python -m py_src.main size d:/myproject/build/web-mobile d:/out.txt
    ```

## QA
#### 1. `AssetCleaner`会自动删除未使用资源吗？
默认不会，`AssetCleaner`只是分析并把统计结果输出到文件，实际删除需自己手动操作。也可使用可选命令`--delete`删除。

#### 2. `AssetCleaner`的局限
查找未使用资源的功能，目前主要适用于非resources目录。对于resources目录，因为原则上resources目录只存放动态加载资源，而动态加载的资源名在代码里多数情况下是变量，暂时没找到有效匹配方案，所以目前只是试验性地支持resources目录的.prefab类型（完全匹配）。

## 交流
欢迎关注微信公众号“楚游香”，做进一步的技术交流。
