#!/usr/bin/env python3
"""
视觉边界数据集 - 视觉退化算法实现
实现6种视觉退化类型，每种类型100个渐变级别
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import os
from pathlib import Path
import json
from typing import Dict, List, Tuple
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class VisualDegradationGenerator:
    """视觉退化生成器"""
    
    def __init__(self, base_dir: str = "/home/jgy/visual_boundary_dataset"):
        self.base_dir = Path(base_dir)
        self.images_dir = self.base_dir / "selected_images"
        self.degraded_dir = self.base_dir / "degraded_images"
        self.metadata_dir = self.base_dir / "metadata"
        
        # 创建输出目录
        self.degraded_dir.mkdir(exist_ok=True)
        for degradation_type in ['sharpness', 'brightness', 'contrast', 'color_distortion', 'color_shift', 'resolution']:
            (self.degraded_dir / degradation_type).mkdir(exist_ok=True)
    
    def load_image_list(self) -> List[Dict]:
        """加载图片列表"""
        metadata_file = self.metadata_dir / "final_image_collection.json"
        with open(metadata_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['selected_images']
    
    def degrade_sharpness(self, image: np.ndarray, level: int) -> np.ndarray:
        """
        清晰度退化 (0-100)
        0: 最清晰 (原图)
        100: 最模糊
        """
        if level == 0:
            return image
        
        # 计算模糊半径 (0.1 到 20)
        blur_radius = 0.1 + (level / 100.0) * 19.9
        
        # 转换为PIL图像进行高斯模糊
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        blurred = pil_image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        
        # 转换回OpenCV格式
        return cv2.cvtColor(np.array(blurred), cv2.COLOR_RGB2BGR)
    
    def degrade_brightness(self, image: np.ndarray, level: int) -> np.ndarray:
        """
        亮度退化 (0-100)
        0: 正常亮度
        50: 亮度适中
        100: 极亮或极暗
        """
        if level == 0:
            return image
        
        # 亮度调整范围：-100到+100
        if level <= 50:
            # 0-50: 变暗
            brightness_factor = 1.0 - (level / 50.0) * 0.8  # 0.2 到 1.0
        else:
            # 50-100: 变亮
            brightness_factor = 1.0 + ((level - 50) / 50.0) * 1.5  # 1.0 到 2.5
        
        # 应用亮度调整
        adjusted = image.astype(np.float32) * brightness_factor
        return np.clip(adjusted, 0, 255).astype(np.uint8)
    
    def degrade_contrast(self, image: np.ndarray, level: int) -> np.ndarray:
        """
        对比度退化 (0-100)
        0: 正常对比度
        100: 极低对比度（接近灰色）
        """
        if level == 0:
            return image
        
        # 对比度调整因子 (1.0 到 0.01)
        contrast_factor = 1.0 - (level / 100.0) * 0.99
        
        # 计算图像均值
        mean = np.mean(image)
        
        # 应用对比度调整
        adjusted = (image - mean) * contrast_factor + mean
        return np.clip(adjusted, 0, 255).astype(np.uint8)
    
    def degrade_color_distortion(self, image: np.ndarray, level: int) -> np.ndarray:
        """
        颜色失真 (0-100)
        0: 正常颜色
        100: 严重颜色失真（色相偏移、饱和度异常）
        """
        if level == 0:
            return image
        
        # 转换为HSV色彩空间
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # 色相偏移 (-180 到 +180)
        hue_shift = (level / 100.0) * 360 - 180
        hsv[:, :, 0] = (hsv[:, :, 0] + hue_shift) % 180
        
        # 饱和度调整 (0.1 到 3.0)
        saturation_factor = 0.1 + (level / 100.0) * 2.9
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * saturation_factor, 0, 255)
        
        # 转换回BGR
        distorted = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        return distorted
    
    def degrade_color_shift(self, image: np.ndarray, level: int) -> np.ndarray:
        """
        色偏识别 (0-100)
        0: 正常色彩平衡
        100: 严重色偏（偏红、偏绿、偏蓝等）
        """
        if level == 0:
            return image
        
        # 随机选择色偏类型（基于level确定性选择）
        shift_type = (level % 6)  # 6种色偏类型
        shift_intensity = level / 100.0
        
        image_float = image.astype(np.float32)
        
        if shift_type == 0:  # 偏红
            image_float[:, :, 2] *= (1.0 + shift_intensity)  # 增强红色
            image_float[:, :, 1] *= (1.0 - shift_intensity * 0.3)  # 减少绿色
        elif shift_type == 1:  # 偏绿
            image_float[:, :, 1] *= (1.0 + shift_intensity)  # 增强绿色
            image_float[:, :, 2] *= (1.0 - shift_intensity * 0.3)  # 减少红色
        elif shift_type == 2:  # 偏蓝
            image_float[:, :, 0] *= (1.0 + shift_intensity)  # 增强蓝色
            image_float[:, :, 1] *= (1.0 - shift_intensity * 0.3)  # 减少绿色
        elif shift_type == 3:  # 偏黄（减蓝）
            image_float[:, :, 0] *= (1.0 - shift_intensity * 0.5)  # 减少蓝色
        elif shift_type == 4:  # 偏青（减红）
            image_float[:, :, 2] *= (1.0 - shift_intensity * 0.5)  # 减少红色
        else:  # 偏洋红（减绿）
            image_float[:, :, 1] *= (1.0 - shift_intensity * 0.5)  # 减少绿色
        
        return np.clip(image_float, 0, 255).astype(np.uint8)
    
    def degrade_resolution(self, image: np.ndarray, level: int) -> np.ndarray:
        """
        分辨率退化 (0-100)
        0: 原始分辨率
        100: 极低分辨率
        """
        if level == 0:
            return image
        
        h, w = image.shape[:2]
        
        # 计算缩放因子 (1.0 到 0.05)
        scale_factor = 1.0 - (level / 100.0) * 0.95
        
        # 计算新尺寸
        new_w = max(int(w * scale_factor), 8)  # 最小8像素
        new_h = max(int(h * scale_factor), 8)
        
        # 下采样
        downsampled = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        # 上采样回原尺寸
        upsampled = cv2.resize(downsampled, (w, h), interpolation=cv2.INTER_LINEAR)
        
        return upsampled
    
    def generate_degraded_dataset(self):
        """生成完整的退化数据集"""
        print("🎨 生成视觉边界退化数据集")
        print("=" * 50)
        
        # 加载图片列表
        image_list = self.load_image_list()
        print(f"📁 加载了 {len(image_list)} 张基础图片")
        
        # 退化类型和对应的函数
        degradation_methods = {
            'sharpness': self.degrade_sharpness,
            'brightness': self.degrade_brightness, 
            'contrast': self.degrade_contrast,
            'color_distortion': self.degrade_color_distortion,
            'color_shift': self.degrade_color_shift,
            'resolution': self.degrade_resolution
        }
        
        total_images = len(image_list) * 6 * 100  # 图片数 × 退化类型 × 级别
        processed = 0
        
        metadata = {
            'dataset_info': {
                'total_base_images': len(image_list),
                'degradation_types': list(degradation_methods.keys()),
                'levels_per_type': 100,
                'total_generated_images': total_images
            },
            'degraded_images': []
        }
        
        for img_info in image_list:
            # 使用正确的路径 - 从selected_images目录读取
            if 'selected_path' in img_info:
                image_path = Path(img_info['selected_path'])
            else:
                image_path = self.base_dir / "selected_images" / img_info['filename']
            
            # 加载图片
            image = cv2.imread(str(image_path))
            if image is None:
                print(f"❌ 无法加载图片: {image_path}")
                continue
                
            print(f"🖼️  处理图片: {img_info['filename']}")
            
            for degradation_type, method in degradation_methods.items():
                print(f"  📊 {degradation_type}退化...")
                
                for level in range(0, 101):  # 0-100级别
                    # 生成退化图片
                    degraded_image = method(image, level)
                    
                    # 生成输出文件名
                    base_name = Path(img_info['filename']).stem
                    output_filename = f"{base_name}_{degradation_type}_level_{level:03d}.jpg"
                    output_path = self.degraded_dir / degradation_type / output_filename
                    
                    # 保存退化图片
                    cv2.imwrite(str(output_path), degraded_image)
                    
                    # 记录元数据
                    metadata['degraded_images'].append({
                        'original_image': img_info['filename'],
                        'degradation_type': degradation_type,
                        'level': level,
                        'filename': output_filename,
                        'file_path': str(output_path),
                        'original_quality_score': img_info['quality_score']
                    })
                    
                    processed += 1
                    if level % 20 == 0:  # 每20级别显示一次进度
                        progress = (processed / total_images) * 100
                        print(f"    Level {level}: {progress:.1f}% 完成")
        
        # 保存元数据
        metadata_file = self.metadata_dir / "degraded_dataset.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 数据集生成完成!")
        print(f"📊 统计信息:")
        print(f"  基础图片: {len(image_list)} 张")
        print(f"  退化类型: {len(degradation_methods)} 种")
        print(f"  每类型级别: 101 个 (0-100)")
        print(f"  总生成图片: {processed} 张")
        print(f"  元数据保存: {metadata_file}")

def main():
    """主函数"""
    generator = VisualDegradationGenerator()
    generator.generate_degraded_dataset()

if __name__ == "__main__":
    main()