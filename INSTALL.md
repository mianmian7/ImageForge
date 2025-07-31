# ImagePass 安装指南

## 系统要求
- Python 3.8+
- Linux/Windows/macOS
- ImageMagick (可选，程序会自动使用Pillow作为备用方案)

## 安装步骤

### 1. 安装系统依赖

#### 必需依赖
```bash
# Ubuntu/Debian 系统
sudo apt update
sudo apt install python3 python3-pip python3-venv

# CentOS/RHEL 系统
sudo yum install python3 python3-pip

# macOS 系统
brew install python

# Windows 系统
从Python官网安装Python 3.8+
```

#### 可选依赖 - ImageMagick (推荐)
如果系统安装了ImageMagick，程序会优先使用ImageMagick进行图片处理。如果没有安装ImageMagick，程序会自动使用Pillow作为备用方案。

**Ubuntu/Debian 系统**
```bash
sudo apt install imagemagick
magick --version
```

**CentOS/RHEL 系统**
```bash
sudo yum install ImageMagick
magick --version
```

**macOS 系统**
```bash
brew install imagemagick
magick --version
```

**Windows 系统**
1. 从ImageMagick官网安装ImageMagick
2. 确保将ImageMagick添加到系统PATH

### 2. 创建虚拟环境
```bash
# 进入项目目录
cd /home/mianmian/py-ImagePass

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\\Scripts\\activate
```

### 3. 安装Python依赖
```bash
# 升级pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

### 4. 配置程序

#### 获取TinyPNG API密钥
1. 访问 https://tinypng.com/developers
2. 注册账号并获取API密钥

#### 配置config.ini
编辑 `config.ini` 文件：
```ini
[DEFAULT]
# 设置你的TinyPNG API密钥
tinypng_api_key = your_actual_api_key_here

# ImageMagick路径 (可选)
# 如果未安装ImageMagick，程序会自动使用Pillow作为备用方案
# Linux通常在: /usr/bin/magick
# macOS通常在: /usr/local/bin/magick
# Windows通常在: C:\\Program Files\\ImageMagick\\magick.exe
imagemagick_path = /usr/bin/magick
```

**注意**: 
- 如果ImageMagick不可用，程序会自动使用Pillow进行图片处理
- Pillow已经包含在requirements.txt中，无需额外安装
- 所有功能（图片调整、格式转换、优化）在两种处理器下都正常工作

### 5. 运行程序
```bash
# 确保虚拟环境已激活
python main.py
```

## 常见问题解决

### 问题1: tkinter未找到
**现象**: `ModuleNotFoundError: No module named 'tkinter'`

**解决方案**:
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# CentOS/RHEL
sudo yum install tkinter

# macOS (如果使用Homebrew的Python)
brew install python-tk
```

### 问题2: ImageMagick未找到
**现象**: `wand.exceptions.WandException` 或 `MagickWand not found`

**解决方案**:
程序现在支持自动备用方案，即使ImageMagick不可用也能正常工作：

```bash
# 检查程序是否能正常运行
python main.py

# 程序会自动检测并使用Pillow作为备用处理器
# 如果仍然希望使用ImageMagick：
sudo apt install --reinstall imagemagick  # Ubuntu/Debian
sudo yum install ImageMagick              # CentOS/RHEL
brew install imagemagick                   # macOS
```

### 问题3: Wand安装失败
**现象**: 安装Wand时出现编译错误

**解决方案**:
```bash
# 安装ImageMagick开发库
# Ubuntu/Debian
sudo apt install libmagickwand-dev

# CentOS/RHEL
sudo yum install ImageMagick-devel

# 然后重新安装Wand
pip install wand
```

### 问题4: 权限错误
**现象**: `Permission denied` 错误

**解决方案**:
```bash
# 确保使用虚拟环境
source venv/bin/activate

# 或者使用用户安装
pip install --user -r requirements.txt
```

### 问题5: TinyPNG API调用失败
**现象**: 网络相关错误或认证失败

**解决方案**:
1. 检查网络连接
2. 验证API密钥是否正确
3. 检查API调用次数是否超出限制

## 验证安装

### 检查Python依赖
```bash
python -c "
import tkinter
from PIL import Image
import requests
import configparser
print('基础依赖安装成功!')
"
```

### 检查图片处理器
```bash
python -c "
from utils.imagemagick_wrapper import ImageMagickWrapper
wrapper = ImageMagickWrapper()
info = wrapper.get_processor_info()
print(f'当前处理器: {info[\"processor\"]}')
print(f'ImageMagick可用: {info[\"imagemagick_available\"]}')
print(f'Pillow可用: {info[\"pillow_available\"]}')
print(f'备用方案可用: {info[\"has_fallback\"]}')
"
```

这个命令会显示当前使用的图片处理器以及各库的可用性。程序会自动选择最佳处理器：
- 如果ImageMagick可用，会优先使用ImageMagick
- 如果ImageMagick不可用，会自动使用Pillow作为备用方案
- 两种方案都支持完整的图片处理功能

### 检查TinyPNG API
```python
# 在Python交互环境中
from utils.tinypng_client import TinyPNGClient
client = TinyPNGClient('your_api_key')
print('API验证结果:', client.validate_api_key())
```

## 项目结构

安装完成后，项目结构应该是：
```
py-ImagePass/
├── venv/                   # 虚拟环境
├── main.py                 # 主程序
├── requirements.txt        # Python依赖
├── config.ini             # 配置文件
├── test_fallback.py       # 备用方案测试脚本
├── todo.md                # 开发计划
├── gui/                   # GUI模块
├── core/                  # 核心模块
│   ├── image_processor.py # 图片处理核心
│   ├── file_manager.py    # 文件管理
│   └── config.py          # 配置管理
└── utils/                 # 工具模块
    ├── imagemagick_wrapper.py  # ImageMagick封装（含Pillow备用）
    ├── pillow_wrapper.py       # Pillow图片处理封装
    └── tinypng_client.py       # TinyPNG客户端
```

**新增功能**:
- `utils/pillow_wrapper.py`: 新增的Pillow图片处理封装，作为ImageMagick的备用方案
- `utils/imagemagick_wrapper.py`: 更新后的ImageMagick封装，支持自动检测和备用方案切换
- `test_fallback.py`: 用于测试备用方案的脚本

## 开始使用

1. 运行程序: `python main.py`
2. 选择图片文件或文件夹
3. 选择处理方式（调整分辨率或压缩）
4. 设置输出选项
5. 点击处理按钮开始处理

详细使用说明请参考 `todo.md` 文件。