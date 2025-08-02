# Windows 构建说明

## 前提条件
- Windows操作系统
- Python 3.8+ 已安装
- 项目代码完整

## 构建步骤

### 1. 安装依赖
```cmd
pip install -r requirements.txt
pip install pyinstaller
```

### 2. 构建 exe 文件
```cmd
pyinstaller ImageForge.spec
```

### 3. 查找生成的文件
构建完成后，exe文件将位于 `dist/ImageForge.exe`

## 重要说明

### 当前环境限制
- 当前在WSL Linux环境下，无法直接生成Windows exe文件
- 需要在Windows环境下执行构建命令

### 解决方案
1. **在Windows机器上执行**：
   - 将整个项目文件夹复制到Windows机器
   - 在Windows上安装Python和依赖
   - 运行 `pyinstaller ImageForge.spec`

2. **使用交叉编译工具**（高级）：
   - 使用 `wine` 在Linux上模拟Windows环境
   - 或使用Docker容器进行交叉编译

### 推荐方法
最简单可靠的方法是在Windows机器上直接构建，确保所有依赖和GUI组件正确兼容。