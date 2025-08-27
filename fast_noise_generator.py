#!/usr/bin/env python3
"""
快速噪声梯度生成器 - 为100张真实世界图片生成噪声和像素操作的100个梯度
"""

import os
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import json
from pathlib import Path

def apply_noise_gradient(image, gradient_level):
    """对图片应用噪声，gradient_level从0到99"""
    intensity = gradient_level / 99.0
    
    # 转换为numpy数组
    img_array = np.array(image)
    
    # 应用高斯噪声
    noise = np.random.normal(0, intensity * 25, img_array.shape)
    noisy_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
    
    return Image.fromarray(noisy_array)

def apply_pixel_manipulation(image, gradient_level):
    """对图片应用像素操作，gradient_level从0到99"""
    intensity = gradient_level / 99.0
    
    # 像素化效果
    original_size = image.size
    pixel_size = max(1, int(intensity * 20) + 1)
    small_size = (max(1, original_size[0] // pixel_size), 
                 max(1, original_size[1] // pixel_size))
    
    resized = image.resize(small_size, Image.NEAREST)
    return resized.resize(original_size, Image.NEAREST)

def process_single_image(image_path, output_base_path):
    """处理单张图片，生成200个变化（100个噪声+100个像素操作）"""
    try:
        # 加载图片
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        image_name = Path(image_path).stem
        
        # 创建输出目录
        noise_dir = output_base_path / "noise_gradients" / image_name
        pixel_dir = output_base_path / "pixel_gradients" / image_name
        noise_dir.mkdir(parents=True, exist_ok=True)
        pixel_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成100个噪声梯度
        for i in range(100):
            noisy_image = apply_noise_gradient(image, i)
            noisy_image.save(noise_dir / f"noise_{i:03d}.png")
        
        # 生成100个像素操作梯度
        for i in range(100):
            pixel_image = apply_pixel_manipulation(image, i)
            pixel_image.save(pixel_dir / f"pixel_{i:03d}.png")
        
        return True
        
    except Exception as e:
        print(f"错误处理 {image_path}: {e}")
        return False

def main():
    print("🚀 快速噪声梯度生成器")
    print("=" * 40)
    
    # 读取图片列表
    base_path = Path("/home/jgy/visual_boundary_dataset")
    output_path = Path("/home/jgy/Real_World_Noise_Dataset")
    output_path.mkdir(exist_ok=True)
    
    # 获取前100张多样化图片
    image_list_path = "/home/jgy/selected_100_diverse_images.txt"
    with open(image_list_path, 'r') as f:
        image_paths = [line.strip() for line in f.readlines() if line.strip()]
    
    # 处理前20张图片作为示例
    processed = 0
    total_images = min(20, len(image_paths))  # 先处理20张图片
    
    for i, relative_path in enumerate(image_paths[:total_images]):
        full_path = base_path / relative_path.lstrip('./')
        if full_path.exists():
            print(f"处理 {i+1}/{total_images}: {full_path.name}")
            if process_single_image(full_path, output_path):
                processed += 1
        else:
            print(f"文件不存在: {full_path}")
    
    # 生成统计
    stats = {
        "processed_images": processed,
        "noise_gradients_per_image": 100,
        "pixel_gradients_per_image": 100,
        "total_generated_images": processed * 200
    }
    
    with open(output_path / "generation_stats.json", 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"\n✅ 完成！")
    print(f"处理了 {processed} 张图片")
    print(f"生成了 {processed * 200} 个变化图片")
    print(f"输出目录: {output_path}")

if __name__ == "__main__":
    main()