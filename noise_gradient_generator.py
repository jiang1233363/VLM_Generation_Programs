#!/usr/bin/env python3
"""
真实世界图片噪声和像素操作梯度生成器
为100张多样化的真实世界图片生成100个梯度变化的噪声和像素操作效果
"""

import os
import json
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import random
from pathlib import Path
from datetime import datetime

class NoiseGradientGenerator:
    def __init__(self, base_path="/home/jgy/visual_boundary_dataset"):
        self.base_path = Path(base_path)
        self.output_path = Path("/home/jgy/Real_World_Noise_Dataset")
        self.setup_directories()
        
        # 多种噪声和像素操作类型
        self.transformations = {
            "gaussian_noise": self.apply_gaussian_noise,
            "salt_pepper_noise": self.apply_salt_pepper_noise,
            "poisson_noise": self.apply_poisson_noise,
            "speckle_noise": self.apply_speckle_noise,
            "blur_effect": self.apply_blur_effect,
            "pixelation": self.apply_pixelation,
            "color_shift": self.apply_color_shift,
            "contrast_variation": self.apply_contrast_variation,
            "brightness_variation": self.apply_brightness_variation,
            "saturation_variation": self.apply_saturation_variation
        }
        
        print("🎨 REAL-WORLD IMAGE NOISE GRADIENT GENERATOR")
        print("=" * 60)

    def setup_directories(self):
        """创建输出目录结构"""
        self.output_path.mkdir(exist_ok=True)
        
        # 为每种变换类型创建目录
        transform_types = [
            "gaussian_noise", "salt_pepper_noise", "poisson_noise", 
            "speckle_noise", "blur_effect", "pixelation",
            "color_shift", "contrast_variation", "brightness_variation", "saturation_variation"
        ]
        
        for transform_type in transform_types:
            (self.output_path / transform_type).mkdir(exist_ok=True)
            (self.output_path / transform_type / "gradients").mkdir(exist_ok=True)
            (self.output_path / transform_type / "metadata").mkdir(exist_ok=True)

    def load_image_list(self):
        """加载选定的100张图片列表"""
        image_list_path = "/home/jgy/selected_100_diverse_images.txt"
        with open(image_list_path, 'r') as f:
            image_paths = [line.strip() for line in f.readlines() if line.strip()]
        
        # 转换为完整路径并取前100张
        full_paths = []
        for path in image_paths[:100]:
            full_path = self.base_path / path.lstrip('./')
            if full_path.exists():
                full_paths.append(full_path)
        
        print(f"📂 成功加载 {len(full_paths)} 张多样化图片")
        return full_paths

    def apply_gaussian_noise(self, image, intensity):
        """应用高斯噪声"""
        img_array = np.array(image)
        noise = np.random.normal(0, intensity * 50, img_array.shape)
        noisy_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        return Image.fromarray(noisy_array)

    def apply_salt_pepper_noise(self, image, intensity):
        """应用椒盐噪声"""
        img_array = np.array(image)
        noise_mask = np.random.random(img_array.shape[:2])
        
        # 盐噪声 (白点)
        salt_mask = noise_mask < intensity * 0.05
        img_array[salt_mask] = 255
        
        # 椒噪声 (黑点)
        pepper_mask = noise_mask > 1 - intensity * 0.05
        img_array[pepper_mask] = 0
        
        return Image.fromarray(img_array)

    def apply_poisson_noise(self, image, intensity):
        """应用泊松噪声"""
        img_array = np.array(image, dtype=float)
        # 泊松噪声基于图像本身的强度
        noisy_array = np.random.poisson(img_array * intensity * 0.1) / (intensity * 0.1)
        noisy_array = np.clip(noisy_array, 0, 255).astype(np.uint8)
        return Image.fromarray(noisy_array)

    def apply_speckle_noise(self, image, intensity):
        """应用散斑噪声"""
        img_array = np.array(image, dtype=float)
        noise = np.random.randn(*img_array.shape) * intensity * 20
        noisy_array = img_array + img_array * noise / 100
        noisy_array = np.clip(noisy_array, 0, 255).astype(np.uint8)
        return Image.fromarray(noisy_array)

    def apply_blur_effect(self, image, intensity):
        """应用模糊效果"""
        blur_radius = intensity * 5
        return image.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    def apply_pixelation(self, image, intensity):
        """应用像素化效果"""
        # 降低分辨率然后放大回原尺寸
        original_size = image.size
        # 像素化程度：intensity越高，像素块越大
        pixel_size = max(1, int(intensity * 50))
        small_size = (max(1, original_size[0] // pixel_size), 
                     max(1, original_size[1] // pixel_size))
        
        resized = image.resize(small_size, Image.NEAREST)
        return resized.resize(original_size, Image.NEAREST)

    def apply_color_shift(self, image, intensity):
        """应用色彩偏移"""
        img_array = np.array(image)
        if len(img_array.shape) == 3:  # RGB图像
            # 随机色彩偏移
            shift = intensity * 50
            r_shift = random.uniform(-shift, shift)
            g_shift = random.uniform(-shift, shift)
            b_shift = random.uniform(-shift, shift)
            
            img_array[:, :, 0] = np.clip(img_array[:, :, 0] + r_shift, 0, 255)
            img_array[:, :, 1] = np.clip(img_array[:, :, 1] + g_shift, 0, 255)
            img_array[:, :, 2] = np.clip(img_array[:, :, 2] + b_shift, 0, 255)
        
        return Image.fromarray(img_array.astype(np.uint8))

    def apply_contrast_variation(self, image, intensity):
        """应用对比度变化"""
        enhancer = ImageEnhance.Contrast(image)
        # intensity从0到1，对应对比度从0.5到2.0
        contrast_factor = 0.5 + intensity * 1.5
        return enhancer.enhance(contrast_factor)

    def apply_brightness_variation(self, image, intensity):
        """应用亮度变化"""
        enhancer = ImageEnhance.Brightness(image)
        # intensity从0到1，对应亮度从0.3到1.7
        brightness_factor = 0.3 + intensity * 1.4
        return enhancer.enhance(brightness_factor)

    def apply_saturation_variation(self, image, intensity):
        """应用饱和度变化"""
        enhancer = ImageEnhance.Color(image)
        # intensity从0到1，对应饱和度从0到2.0
        saturation_factor = intensity * 2.0
        return enhancer.enhance(saturation_factor)

    def generate_gradients_for_image(self, image_path, transform_type):
        """为单张图片生成100个梯度变化"""
        try:
            # 加载原始图片
            original_image = Image.open(image_path)
            if original_image.mode != 'RGB':
                original_image = original_image.convert('RGB')
            
            # 获取图片名称（去掉扩展名）
            image_name = image_path.stem
            transform_func = self.transformations[transform_type]
            
            # 输出目录
            output_dir = self.output_path / transform_type / "gradients" / image_name
            metadata_dir = self.output_path / transform_type / "metadata"
            output_dir.mkdir(exist_ok=True)
            
            metadata_list = []
            
            # 生成100个梯度变化
            for i in range(100):
                intensity = i / 99.0  # 0.0 到 1.0 的梯度
                
                # 应用变换
                transformed_image = transform_func(original_image, intensity)
                
                # 保存变换后的图片
                output_filename = f"gradient_{i:03d}.png"
                output_filepath = output_dir / output_filename
                transformed_image.save(output_filepath, "PNG")
                
                # 保存参数元数据
                metadata = {
                    "gradient_index": i,
                    "intensity": intensity,
                    "transform_type": transform_type,
                    "original_image": str(image_path.name),
                    "output_image": output_filename,
                    "image_size": transformed_image.size,
                    "mode": transformed_image.mode
                }
                
                # 保存单独的参数文件
                param_filename = f"gradient_{i:03d}_params.json"
                param_filepath = output_dir / param_filename
                with open(param_filepath, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                metadata_list.append(metadata)
            
            # 保存该图片的完整元数据
            image_metadata_file = metadata_dir / f"{image_name}_metadata.json"
            with open(image_metadata_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "original_image": str(image_path.name),
                    "transform_type": transform_type,
                    "total_gradients": 100,
                    "gradients": metadata_list
                }, f, indent=2, ensure_ascii=False)
            
            return True, len(metadata_list)
            
        except Exception as e:
            print(f"❌ 处理图片 {image_path.name} 时出错: {e}")
            return False, 0

    def generate_all_transformations(self):
        """为所有100张图片生成所有类型的变换"""
        image_paths = self.load_image_list()
        
        total_images = 0
        total_gradients = 0
        
        # 对每种变换类型
        for transform_type in self.transformations.keys():
            print(f"\n🔄 正在处理变换类型: {transform_type}")
            transform_images = 0
            transform_gradients = 0
            
            # 对每张图片
            for i, image_path in enumerate(image_paths, 1):
                success, gradients_count = self.generate_gradients_for_image(image_path, transform_type)
                
                if success:
                    transform_images += 1
                    transform_gradients += gradients_count
                    
                    if i % 10 == 0:
                        print(f"  ✨ 已处理 {i}/{len(image_paths)} 张图片")
            
            print(f"✅ {transform_type}: {transform_images} 张图片，{transform_gradients} 个梯度变化")
            total_images += transform_images
            total_gradients += transform_gradients

        # 生成总体统计
        self.generate_final_statistics(total_images, total_gradients)
        
        return total_images, total_gradients

    def generate_final_statistics(self, total_images, total_gradients):
        """生成最终统计信息"""
        stats = {
            "generation_timestamp": datetime.now().isoformat(),
            "dataset_name": "Real_World_Noise_Dataset",
            "total_original_images": 100,
            "transformation_types": list(self.transformations.keys()),
            "gradients_per_image": 100,
            "total_processed_images": total_images,
            "total_gradient_variations": total_gradients,
            "expected_total": 100 * len(self.transformations) * 100,
            "completion_rate": f"{(total_gradients / (100 * len(self.transformations) * 100)) * 100:.1f}%"
        }
        
        # 保存统计信息
        stats_file = self.output_path / "dataset_statistics.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        # 打印最终报告
        print("\n" + "="*60)
        print("🎯 最终生成统计")
        print("="*60)
        print(f"📊 数据集名称: {stats['dataset_name']}")
        print(f"📂 原始图片数量: {stats['total_original_images']}")
        print(f"🔄 变换类型数量: {len(stats['transformation_types'])}")
        print(f"📈 每张图片梯度数: {stats['gradients_per_image']}")
        print(f"📸 总处理图片数: {stats['total_processed_images']}")
        print(f"🎨 总梯度变化数: {stats['total_gradient_variations']:,}")
        print(f"🎯 完成率: {stats['completion_rate']}")
        print(f"💾 统计文件保存至: {stats_file}")
        print("\n🌟 真实世界图片噪声梯度数据集生成完成！")

def main():
    generator = NoiseGradientGenerator()
    
    print("开始生成真实世界图片的噪声和像素操作梯度变化...")
    print("预期生成: 100张图片 × 10种变换 × 100个梯度 = 100,000 个变化图片")
    
    total_images, total_gradients = generator.generate_all_transformations()
    
    print(f"\n🎉 生成完成！")
    print(f"实际生成: {total_images} 张处理图片，{total_gradients:,} 个梯度变化")

if __name__ == "__main__":
    main()