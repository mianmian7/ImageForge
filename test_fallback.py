#!/usr/bin/env python3
"""
测试ImageMagick与Pillow的备用功能
"""

import os
import sys
import tempfile
from PIL import Image

# 添加项目路径到Python路径
sys.path.insert(0, '/mnt/g/dev/ai/py-ImagePass')

from utils.pillow_wrapper import PillowWrapper

def create_test_image(path: str, width: int = 800, height: int = 600) -> None:
    """创建测试图片"""
    # 创建一个简单的渐变测试图片
    img = Image.new('RGB', (width, height), color='red')
    
    # 添加一些渐变效果
    for y in range(height):
        color_value = int(255 * (1 - y / height))
        color = (255, color_value, color_value)
        for x in range(width):
            img.putpixel((x, y), color)
    
    img.save(path, 'JPEG', quality=95)

def test_fallback_functionality():
    """测试备用功能"""
    print("=== 测试ImageMagick与Pillow备用功能 ===\n")
    
    # 创建临时目录和测试图片
    with tempfile.TemporaryDirectory() as temp_dir:
        test_image_path = os.path.join(temp_dir, 'test_input.jpg')
        output_path = os.path.join(temp_dir, 'test_output.jpg')
        
        # 创建测试图片
        print("1. 创建测试图片...")
        create_test_image(test_image_path)
        print(f"   测试图片已创建: {test_image_path}")
        
        # 初始化PillowWrapper
        print("\n2. 初始化PillowWrapper...")
        wrapper = PillowWrapper()
        processor_info = wrapper.get_processor_info()
        print(f"   当前处理器: {processor_info['processor']}")
        print(f"   ImageMagick可用: {processor_info['imagemagick_available']}")
        print(f"   Pillow可用: {processor_info['pillow_available']}")
        print(f"   是否有备用方案: {processor_info['has_fallback']}")
        
        # 测试获取图片信息
        print("\n3. 测试获取图片信息...")
        info = wrapper.get_image_info(test_image_path)
        if info:
            print(f"   成功获取图片信息: {info}")
        else:
            print(f"   获取图片信息失败: {wrapper.get_last_error()}")
        
        # 测试按百分比调整大小
        print("\n4. 测试按百分比调整大小...")
        success = wrapper.resize_by_percentage(test_image_path, output_path, 50, 85)
        if success:
            print("   按百分比调整大小成功")
            
            # 验证调整后的图片
            if os.path.exists(output_path):
                new_info = wrapper.get_image_info(output_path)
                if new_info:
                    print(f"   调整后尺寸: {new_info['width']}x{new_info['height']}")
                    print(f"   调整后大小: {new_info['filesize']} 字节")
        else:
            print(f"   按百分比调整大小失败: {wrapper.get_last_error()}")
        
        # 测试按尺寸调整大小
        print("\n5. 测试按尺寸调整大小...")
        output_path_2 = os.path.join(temp_dir, 'test_output_2.jpg')
        success = wrapper.resize_by_dimensions(test_image_path, output_path_2, 400, 300, True, 85)
        if success:
            print("   按尺寸调整大小成功")
            
            # 验证调整后的图片
            if os.path.exists(output_path_2):
                new_info = wrapper.get_image_info(output_path_2)
                if new_info:
                    print(f"   调整后尺寸: {new_info['width']}x{new_info['height']}")
        else:
            print(f"   按尺寸调整大小失败: {wrapper.get_last_error()}")
        
        # 测试格式转换
        print("\n6. 测试格式转换...")
        png_path = os.path.join(temp_dir, 'test_output.png')
        success = wrapper.convert_format(test_image_path, png_path, 'PNG', 85)
        if success:
            print("   格式转换成功")
            
            # 验证转换后的图片
            if os.path.exists(png_path):
                new_info = wrapper.get_image_info(png_path)
                if new_info:
                    print(f"   转换后格式: {new_info['format']}")
        else:
            print(f"   格式转换失败: {wrapper.get_last_error()}")
        
        # 测试图片优化
        print("\n7. 测试图片优化...")
        optimized_path = os.path.join(temp_dir, 'test_optimized.jpg')
        success = wrapper.optimize_image(test_image_path, optimized_path, 70)
        if success:
            print("   图片优化成功")
            
            # 验证优化后的图片
            if os.path.exists(optimized_path):
                original_size = os.path.getsize(test_image_path)
                optimized_size = os.path.getsize(optimized_path)
                print(f"   原始大小: {original_size} 字节")
                print(f"   优化后大小: {optimized_size} 字节")
                print(f"   压缩率: {(1 - optimized_size / original_size) * 100:.2f}%")
        else:
            print(f"   图片优化失败: {wrapper.get_last_error()}")
        
        print("\n=== 测试完成 ===")
        
        # 显示当前使用的处理器
        print(f"\n当前使用的图片处理器: {processor_info['processor']}")
        if processor_info['processor'] == 'pillow':
            print("✓ ImageMagick不可用，已自动切换到Pillow处理器")
        elif processor_info['processor'] == 'imagemagick':
            print("✓ ImageMagick可用，使用ImageMagick处理器")
        else:
            print("✗ 没有可用的图片处理器")

if __name__ == '__main__':
    test_fallback_functionality()