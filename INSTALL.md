# ImagePass 安装指南

## 系统要求
- Python 3.8+
- Linux/Windows/macOS
- ImageMagick

## 安装步骤

### 1. 安装系统依赖

#### Ubuntu/Debian 系统
```bash
# 更新包管理器
sudo apt update

# 安装Python和venv
sudo apt install python3 python3-pip python3-venv

# 安装ImageMagick
sudo apt install imagemagick

# 验证ImageMagick安装
magick --version
```

#### CentOS/RHEL 系统
```bash
# 安装Python和pip
sudo yum install python3 python3-pip

# 安装ImageMagick
sudo yum install ImageMagick

# 验证ImageMagick安装
magick --version
```

#### macOS 系统
```bash
# 使用Homebrew安装Python
brew install python

# 安装ImageMagick
brew install imagemagick

# 验证ImageMagick安装
magick --version
```

#### Windows 系统
1. 从Python官网安装Python 3.8+
2. 从ImageMagick官网安装ImageMagick
3. 确保将Python和ImageMagick添加到系统PATH

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

# 根据系统设置ImageMagick路径
# Linux通常在: /usr/bin/magick
# macOS通常在: /usr/local/bin/magick
# Windows通常在: C:\\Program Files\\ImageMagick\\magick.exe
imagemagick_path = /usr/bin/magick
```

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
```bash
# 确认ImageMagick安装路径
which magick

# 如果找不到，重新安装ImageMagick
# Ubuntu/Debian
sudo apt install --reinstall imagemagick

# 或者从源码编译安装
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
from wand.image import Image as WandImage
import requests
import configparser
print('所有依赖安装成功!')
"
```

### 检查ImageMagick
```bash
python -c "
from wand.image import Image as WandImage
print('ImageMagick集成成功!')
"
```

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
├── todo.md                # 开发计划
├── gui/                   # GUI模块
├── core/                  # 核心模块
└── utils/                 # 工具模块
```

## 开始使用

1. 运行程序: `python main.py`
2. 选择图片文件或文件夹
3. 选择处理方式（调整分辨率或压缩）
4. 设置输出选项
5. 点击处理按钮开始处理

详细使用说明请参考 `todo.md` 文件。