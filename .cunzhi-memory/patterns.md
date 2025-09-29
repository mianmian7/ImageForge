# 常用模式和最佳实践

- ImageForge 项目优化最佳实践：
1. 使用单例模式的日志管理器（LoggerManager）统一日志配置
2. 将超长GUI类（1564行）拆分为独立管理器模块（StatusBarManager, PreviewManager等）
3. 提取公共工具函数（format_file_size, get_image_info_text等）到 utils/common_utils.py
4. 用 logging 替换所有 print 语句，提升代码质量和可调试性
5. 遵循管理器模式：每个管理器职责单一，通过主窗口协调
