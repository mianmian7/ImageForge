# ImageForge 安装指南

## 系统要求
- Python 3.8+
- Linux/Windows/macOS

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


### 2. 创建虚拟环境
```bash
# 进入项目目录
cd /home/mianmian/ImageForge

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

```

**注意**: 
- 程序使用Pillow进行图片处理
- Pillow已经包含在requirements.txt中，无需额外安装
- 所有功能（图片调整、格式转换、优化）都正常工作

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


### 问题2: 权限错误
**现象**: `Permission denied` 错误

**解决方案**:
```bash
# 确保使用虚拟环境
source venv/bin/activate

# 或者使用用户安装
pip install --user -r requirements.txt
```

### 问题3: TinyPNG API调用失败
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
from utils.pillow_wrapper import PillowWrapper
wrapper = PillowWrapper()
print('Pillow图片处理器已启用')
"
```

程序使用Pillow进行图片处理，支持完整的图片处理功能。

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
ImageForge/
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
    ├── pillow_wrapper.py       # Pillow图片处理封装
    └── tinypng_client.py       # TinyPNG客户端
```

**功能**:
- `utils/pillow_wrapper.py`: Pillow图片处理封装

## 开始使用

1. 运行程序: `python main.py`
2. 选择图片文件或文件夹
3. 选择处理方式（调整分辨率或压缩）
4. 设置输出选项
5. 点击处理按钮开始处理

详细使用说明请参考 `todo.md` 文件。