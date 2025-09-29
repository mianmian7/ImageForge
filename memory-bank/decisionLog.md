# Decision Log

This file records architectural and implementation decisions using a list format.

## Decision 1: 采用单例模式的日志管理器

**Date**: 2025-09-30
**Context**: 项目中使用大量 print 语句，缺乏统一的日志管理

**Decision**: 
创建 LoggerManager 单例类，提供统一的日志配置和获取接口

**Rationale**:
1. 单例模式确保全局只有一个日志配置实例
2. 提供便捷函数 setup_logging() 和 get_logger() 简化使用
3. 支持滚动日志文件（最大10MB，保留5个备份）
4. 分离文件和控制台日志级别（文件DEBUG，控制台INFO）

**Implementation Details**:
- 创建 utils/logger.py 模块
- LoggerManager 使用 __new__ 实现单例
- 使用 RotatingFileHandler 管理日志文件
- 在 main.py 入口初始化日志系统

## Decision 2: GUI 模块化重构采用管理器模式

**Date**: 2025-09-30 (Updated: 2025-09-30 01:39:58)
**Context**: gui/main_window.py 有1567行代码，严重违反单一职责原则

**Decision**:
将 main_window.py 拆分为多个独立管理器，每个管理器负责一个功能区域

**Rationale**:
1. 符合项目规范中的管理器模式要求
2. 提升代码可维护性（每个管理器约300-400行）
3. 降低耦合度，方便单独测试和修改
4. 更好的职责划分和代码复用
5. 通过回调函数实现管理器间通信，保持解耦

**Implementation Details**:
- 创建 gui/managers/ 目录
- 实现管理器：
  * StatusBarManager (76行) - 状态栏和进度显示
  * PreviewManager (197行) - 图像预览和缩略图
  * FileManagerView (392行) - 文件选择、导航、过滤、排序
  * ProcessControlManager (约450行) - 处理控制、参数设置、批量处理
- main_window.py 重构为协调器（450行），仅负责管理器协调和核心状态管理
- 代码量从1567行精简到约1565行（分布在多个文件中），但结构更清晰

**Refactoring Results** (2025-09-30 01:39:58):
- ✅ 完成 FileManagerView 管理器创建
- ✅ 完成 ProcessControlManager 管理器创建
- ✅ 完成 main_window.py 重构为协调器
- ✅ 所有管理器通过回调函数通信
- ✅ 主窗口代码从1567行减少到450行
- ✅ 功能模块化，易于维护和扩展

## Decision 3: 提取公共工具函数

**Date**: 2025-09-30
**Context**: 多处重复代码（文件大小格式化、图像信息获取等）

**Decision**:
创建 utils/common_utils.py 模块，集中管理公共工具函数

**Rationale**:
1. 消除代码重复，提升复用率
2. 统一实现，便于维护和测试
3. 符合 DRY 原则（Don't Repeat Yourself）

**Implementation Details**:
- 创建 utils/common_utils.py
- 实现函数：
  * format_file_size() - 格式化文件大小显示
  * get_image_info_text() - 获取图像信息文本
  * calculate_thumbnail_size() - 计算缩略图尺寸