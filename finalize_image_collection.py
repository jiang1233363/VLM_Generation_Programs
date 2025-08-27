#!/usr/bin/env python3
"""
完成图片收集 - 分析所有图片质量并选择最好的100张
"""

import cv2
import numpy as np
import json
import os
from pathlib import Path
from PIL import Image
import hashlib
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class ImageCollectionFinalizer:
    """图片收集最终处理器"""
    
    def __init__(self, base_dir: str = "/home/jgy/visual_boundary_dataset"):
        self.base_dir = Path(base_dir)
        self.downloaded_dir = self.base_dir / "downloaded_images"
        self.selected_dir = self.base_dir / "selected_images"
        self.metadata_dir = self.base_dir / "metadata"
        
        # 创建最终选择目录
        self.selected_dir.mkdir(exist_ok=True)
        self.metadata_dir.mkdir(exist_ok=True)
    
    def get_image_hash(self, image_path: str) -> str:
        """计算图片哈希值"""
        try:
            with open(image_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""
    
    def analyze_image_quality(self, image_path: Path) -> dict:
        """详细分析单张图片质量"""
        try:
            # 基本检查
            if not image_path.exists() or os.path.getsize(image_path) < 3000:
                return None
            
            # 加载图片
            image = cv2.imread(str(image_path))
            if image is None:
                return None
            
            # 获取PIL图片信息
            with Image.open(image_path) as pil_img:
                pil_img.verify()
                
            with Image.open(image_path) as pil_img:
                width, height = pil_img.size
                format_name = pil_img.format
                mode = pil_img.mode
            
            # 尺寸过小的跳过
            if width < 200 or height < 200:
                return None
            
            # 转换色彩空间
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # 清晰度 - 拉普拉斯方差
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # 亮度 - RGB平均值
            brightness = np.mean(rgb)
            
            # 对比度 - 灰度标准差
            contrast = gray.std()
            
            # 颜色丰富度 - 色相方差
            color_variance = hsv[:,:,0].std()
            
            # 饱和度 - S通道平均值
            saturation = np.mean(hsv[:,:,1])
            
            # 噪声估计 - 高频成分
            noise_level = np.mean(np.abs(cv2.Laplacian(gray, cv2.CV_64F)))
            
            # 边缘密度
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (width * height)
            
            # 动态范围
            dynamic_range = gray.max() - gray.min()
            
            # 综合质量评分
            # 清晰度权重最高
            sharpness_score = min(sharpness / 800, 1.0) * 0.25
            
            # 亮度适中最好 (128左右)
            brightness_score = (1.0 - abs(brightness - 128) / 128) * 0.15
            
            # 对比度适中
            contrast_score = min(contrast / 70, 1.0) * 0.20
            
            # 颜色丰富度
            color_score = min(color_variance / 50, 1.0) * 0.10
            
            # 饱和度适中
            saturation_score = min(saturation / 200, 1.0) * 0.10
            
            # 噪声惩罚
            noise_penalty = max(0, 1 - noise_level / 15) * 0.05
            
            # 边缘丰富度
            edge_score = min(edge_density * 10, 1.0) * 0.10
            
            # 动态范围
            dynamic_score = min(dynamic_range / 200, 1.0) * 0.05
            
            quality_score = (sharpness_score + brightness_score + contrast_score + 
                           color_score + saturation_score + noise_penalty + 
                           edge_score + dynamic_score)
            
            return {
                'filename': image_path.name,
                'file_path': str(image_path),
                'width': width,
                'height': height,
                'resolution': width * height,
                'file_size': os.path.getsize(image_path),
                'format': format_name,
                'mode': mode,
                'sharpness': float(sharpness),
                'brightness': float(brightness),
                'contrast': float(contrast),
                'color_variance': float(color_variance),
                'saturation': float(saturation),
                'noise_level': float(noise_level),
                'edge_density': float(edge_density),
                'dynamic_range': int(dynamic_range),
                'quality_score': float(quality_score),
                'hash': self.get_image_hash(str(image_path))
            }
            
        except Exception as e:
            print(f"❌ 分析失败 {image_path.name}: {e}")
            return None
    
    def finalize_collection(self, target_count: int = 100):
        """完成图片收集和选择"""
        print("🎯 完成图片收集和质量分析")
        print("=" * 50)
        
        # 收集所有图片
        all_images = list(self.downloaded_dir.glob("*.jpg")) + list(self.downloaded_dir.glob("*.jpeg"))
        print(f"📁 发现 {len(all_images)} 张图片")
        
        # 分析每张图片质量
        valid_analyses = []
        unique_hashes = set()
        
        print("🔍 开始质量分析...")
        for i, img_path in enumerate(all_images, 1):
            print(f"  分析 {i}/{len(all_images)}: {img_path.name}")
            
            analysis = self.analyze_image_quality(img_path)
            if analysis and analysis['hash'] not in unique_hashes:
                valid_analyses.append(analysis)
                unique_hashes.add(analysis['hash'])
                print(f"    ✓ 质量分数: {analysis['quality_score']:.3f}")
            else:
                print(f"    ❌ 无效或重复")
        
        print(f"\n📊 有效图片: {len(valid_analyses)} 张")
        
        # 按质量分数排序
        valid_analyses.sort(key=lambda x: x['quality_score'], reverse=True)
        
        # 选择最好的N张
        selected_count = min(target_count, len(valid_analyses))
        selected_images = valid_analyses[:selected_count]
        
        print(f"🏆 选择最佳 {selected_count} 张图片")
        
        # 复制选中的图片到选择目录
        for i, analysis in enumerate(selected_images, 1):
            src_path = Path(analysis['file_path'])
            # 使用统一命名格式
            if 'existing_face_' in src_path.name:
                category = 'face'
                dst_name = f"face_{i:03d}_{src_path.name.replace('existing_', '')}"
            elif 'existing_' in src_path.name and any(fruit in src_path.name for fruit in ['apple', 'banana', 'cherry', 'grape']):
                category = 'fruit'
                dst_name = f"fruit_{i:03d}_{src_path.name.replace('existing_', '')}"
            else:
                category = 'general'
                dst_name = f"general_{i:03d}_{src_path.name}"
            
            dst_path = self.selected_dir / dst_name
            
            try:
                import shutil
                shutil.copy2(src_path, dst_path)
                # 更新路径信息
                analysis['selected_filename'] = dst_name
                analysis['selected_path'] = str(dst_path)
                analysis['category'] = category
                print(f"  ✓ {dst_name} (质量: {analysis['quality_score']:.3f})")
            except Exception as e:
                print(f"  ❌ 复制失败: {e}")
        
        # 生成统计信息
        if selected_images:
            avg_quality = sum(img['quality_score'] for img in selected_images) / len(selected_images)
            total_size = sum(img['file_size'] for img in selected_images)
            
            # 质量分布
            quality_ranges = {
                'excellent': len([img for img in selected_images if img['quality_score'] >= 0.8]),
                'very_good': len([img for img in selected_images if 0.7 <= img['quality_score'] < 0.8]),
                'good': len([img for img in selected_images if 0.6 <= img['quality_score'] < 0.7]),
                'fair': len([img for img in selected_images if 0.5 <= img['quality_score'] < 0.6]),
                'poor': len([img for img in selected_images if img['quality_score'] < 0.5])
            }
            
            # 分辨率分布
            resolutions = [img['resolution'] for img in selected_images]
            avg_resolution = sum(resolutions) / len(resolutions)
            
            # 分类统计
            categories = {}
            for img in selected_images:
                cat = img.get('category', 'unknown')
                categories[cat] = categories.get(cat, 0) + 1
        else:
            avg_quality = 0
            total_size = 0
            quality_ranges = {}
            avg_resolution = 0
            categories = {}
        
        # 生成最终元数据
        final_metadata = {
            'dataset_info': {
                'name': 'Visual Boundary Dataset - Base Images',
                'description': '用于视觉边界测试的高质量真实图片集合',
                'total_candidates': len(all_images),
                'valid_images': len(valid_analyses),
                'selected_images': len(selected_images),
                'target_count': target_count,
                'collection_date': str(Path(__file__).stat().st_mtime),
                'avg_quality_score': float(avg_quality),
                'total_size_mb': total_size / (1024 * 1024),
                'avg_resolution': int(avg_resolution),
            },
            'quality_distribution': quality_ranges,
            'category_distribution': categories,
            'selected_images': selected_images
        }
        
        # 保存元数据
        metadata_file = self.metadata_dir / "final_image_collection.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(final_metadata, f, indent=2, ensure_ascii=False)
        
        # 打印总结
        print(f"\n✅ 图片收集完成!")
        print(f"📄 元数据保存: {metadata_file}")
        print(f"📂 选择图片目录: {self.selected_dir}")
        print(f"\n📊 最终统计:")
        print(f"   总候选图片: {len(all_images)} 张")
        print(f"   有效图片: {len(valid_analyses)} 张")
        print(f"   最终选择: {len(selected_images)} 张")
        print(f"   平均质量分数: {avg_quality:.3f}")
        print(f"   总文件大小: {total_size / (1024 * 1024):.1f} MB")
        print(f"   平均分辨率: {int(avg_resolution):,} 像素")
        
        print(f"\n🎯 质量分布:")
        for range_name, count in quality_ranges.items():
            print(f"   {range_name}: {count} 张")
        
        print(f"\n📂 分类分布:")
        for category, count in categories.items():
            print(f"   {category}: {count} 张")
        
        return selected_images

def main():
    finalizer = ImageCollectionFinalizer()
    finalizer.finalize_collection(100)

if __name__ == "__main__":
    main()