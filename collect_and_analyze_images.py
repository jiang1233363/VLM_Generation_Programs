#!/usr/bin/env python3
"""
图片收集和质量分析脚本
收集现有图片并分析质量指标
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageStat
import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import requests
import time

class ImageQualityAnalyzer:
    """图像质量分析器"""
    
    def __init__(self):
        self.quality_metrics = [
            'sharpness',
            'brightness', 
            'contrast',
            'color_variance',
            'resolution',
            'file_size'
        ]
    
    def analyze_image_quality(self, image_path: str) -> Dict:
        """分析单张图像的质量指标"""
        try:
            # 使用PIL加载图像
            pil_image = Image.open(image_path).convert('RGB')
            
            # 使用OpenCV加载图像
            cv_image = cv2.imread(image_path)
            if cv_image is None:
                return {"error": "无法加载图像"}
            
            cv_image_rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            
            # 计算各种质量指标
            metrics = {
                'filename': Path(image_path).name,
                'file_path': image_path,
                'width': pil_image.width,
                'height': pil_image.height,
                'resolution': pil_image.width * pil_image.height,
                'file_size': os.path.getsize(image_path),
                'sharpness': float(self.calculate_sharpness(cv_image)),
                'brightness': float(self.calculate_brightness(cv_image_rgb)),
                'contrast': float(self.calculate_contrast(cv_image)),
                'color_variance': float(self.calculate_color_variance(cv_image_rgb)),
                'saturation': float(self.calculate_saturation(cv_image_rgb)),
                'noise_level': float(self.estimate_noise_level(cv_image)),
                'quality_score': 0  # 将在后面计算
            }
            
            # 计算综合质量分数
            metrics['quality_score'] = float(self.calculate_overall_quality(metrics))
            
            return metrics
            
        except Exception as e:
            return {"error": str(e), "filename": Path(image_path).name}
    
    def calculate_sharpness(self, image: np.ndarray) -> float:
        """计算图像清晰度（拉普拉斯算子方差）"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        return laplacian.var()
    
    def calculate_brightness(self, image: np.ndarray) -> float:
        """计算图像亮度"""
        return np.mean(image)
    
    def calculate_contrast(self, image: np.ndarray) -> float:
        """计算图像对比度（标准差）"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return np.std(gray)
    
    def calculate_color_variance(self, image: np.ndarray) -> float:
        """计算颜色方差"""
        return np.var(image.reshape(-1, 3), axis=0).mean()
    
    def calculate_saturation(self, image: np.ndarray) -> float:
        """计算饱和度"""
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        return np.mean(hsv[:, :, 1])
    
    def estimate_noise_level(self, image: np.ndarray) -> float:
        """估计噪声水平"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 使用高斯滤波器估计噪声
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        noise = gray.astype(np.float32) - blur.astype(np.float32)
        return np.std(noise)
    
    def calculate_overall_quality(self, metrics: Dict) -> float:
        """计算综合质量分数"""
        try:
            # 标准化各个指标（0-1范围）
            sharpness_norm = min(metrics['sharpness'] / 1000, 1.0)  # 清晰度
            brightness_norm = 1.0 - abs(metrics['brightness'] - 127.5) / 127.5  # 亮度适中性
            contrast_norm = min(metrics['contrast'] / 100, 1.0)  # 对比度
            resolution_norm = min(metrics['resolution'] / (1920*1080), 1.0)  # 分辨率
            
            # 噪声惩罚
            noise_penalty = max(0, 1.0 - metrics['noise_level'] / 10)
            
            # 加权平均
            quality_score = (
                sharpness_norm * 0.3 +
                brightness_norm * 0.2 +
                contrast_norm * 0.2 +
                resolution_norm * 0.15 +
                noise_penalty * 0.15
            )
            
            return quality_score
            
        except Exception:
            return 0.0


class ImageCollector:
    """图片收集器"""
    
    def __init__(self, output_dir: str = "data/original"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.analyzer = ImageQualityAnalyzer()
        self.collected_images = []
        
    def collect_from_input_folder(self, input_base_path: str = "/home/jgy/Input") -> List[Dict]:
        """从Input文件夹收集图片"""
        print("📁 从Input文件夹收集图片...")
        
        input_path = Path(input_base_path)
        collected = []
        
        # 收集水果图片
        fruits_dir = input_path / "Fruits"
        if fruits_dir.exists():
            print(f"  收集水果图片从: {fruits_dir}")
            for img_file in fruits_dir.glob("*"):
                if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
                    # 复制到输出目录
                    dest_path = self.output_dir / f"fruit_{img_file.name}"
                    shutil.copy2(img_file, dest_path)
                    
                    # 分析质量
                    quality_metrics = self.analyzer.analyze_image_quality(str(dest_path))
                    if "error" not in quality_metrics:
                        quality_metrics['category'] = 'fruit'
                        quality_metrics['source'] = 'local_input'
                        collected.append(quality_metrics)
                        print(f"    ✓ {img_file.name} (质量分数: {quality_metrics['quality_score']:.3f})")
        
        # 收集人脸图片
        faces_dir = input_path / "Output_faces_clean"
        if faces_dir.exists():
            print(f"  收集人脸图片从: {faces_dir}")
            face_count = 0
            for img_file in faces_dir.glob("*"):
                if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
                    # 只收集部分人脸图片（避免太多重复）
                    if face_count >= 20:  # 限制人脸图片数量
                        break
                        
                    dest_path = self.output_dir / f"face_{face_count:03d}_{img_file.name}"
                    shutil.copy2(img_file, dest_path)
                    
                    quality_metrics = self.analyzer.analyze_image_quality(str(dest_path))
                    if "error" not in quality_metrics:
                        quality_metrics['category'] = 'face'
                        quality_metrics['source'] = 'local_input'
                        collected.append(quality_metrics)
                        face_count += 1
                        print(f"    ✓ {img_file.name} (质量分数: {quality_metrics['quality_score']:.3f})")
        
        self.collected_images.extend(collected)
        print(f"  📊 从Input文件夹收集了 {len(collected)} 张图片")
        return collected
    
    def download_additional_images(self, target_total: int = 100) -> List[Dict]:
        """从网络下载额外的高质量图片"""
        current_count = len(self.collected_images)
        needed = target_total - current_count
        
        if needed <= 0:
            print(f"已有 {current_count} 张图片，无需下载更多")
            return []
        
        print(f"📡 需要下载 {needed} 张额外图片...")
        
        # 定义要下载的图片类别和对应的搜索关键词
        categories = {
            'animals': ['cat', 'dog', 'elephant', 'tiger', 'lion', 'bird', 'fish'],
            'objects': ['car', 'chair', 'table', 'book', 'phone', 'computer', 'camera'],
            'nature': ['flower', 'tree', 'mountain', 'ocean', 'sunset', 'landscape'],
            'food': ['pizza', 'burger', 'salad', 'cake', 'coffee', 'wine'],
            'architecture': ['building', 'bridge', 'castle', 'church', 'tower']
        }
        
        downloaded = []
        
        # 从免费图片API下载
        downloaded.extend(self.download_from_unsplash(needed // 2))
        downloaded.extend(self.download_from_pixabay(needed - len(downloaded)))
        
        self.collected_images.extend(downloaded)
        return downloaded
    
    def download_from_unsplash(self, count: int) -> List[Dict]:
        """从Unsplash下载高质量图片"""
        print(f"  从Unsplash下载 {count} 张图片...")
        downloaded = []
        
        # Unsplash的随机图片API
        keywords = ['nature', 'animal', 'object', 'food', 'architecture', 'landscape', 'portrait']
        
        for i in range(count):
            try:
                keyword = keywords[i % len(keywords)]
                # 使用Unsplash的Source API获取随机高质量图片
                url = f"https://source.unsplash.com/800x600/?{keyword}"
                
                response = requests.get(url, timeout=30, stream=True)
                if response.status_code == 200:
                    filename = f"unsplash_{keyword}_{i+1:03d}.jpg"
                    filepath = self.output_dir / filename
                    
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    # 分析质量
                    quality_metrics = self.analyzer.analyze_image_quality(str(filepath))
                    if "error" not in quality_metrics:
                        quality_metrics['category'] = keyword
                        quality_metrics['source'] = 'unsplash'
                        downloaded.append(quality_metrics)
                        print(f"    ✓ {filename} (质量分数: {quality_metrics['quality_score']:.3f})")
                    else:
                        filepath.unlink()  # 删除无效文件
                
                time.sleep(1)  # 避免请求过于频繁
                
            except Exception as e:
                print(f"    ✗ 下载失败: {e}")
                continue
        
        return downloaded
    
    def download_from_pixabay(self, count: int) -> List[Dict]:
        """从Pixabay下载图片（需要API key，这里使用示例URLs）"""
        print(f"  尝试从其他源下载 {count} 张图片...")
        downloaded = []
        
        # 使用一些示例高质量图片URL
        example_urls = [
            "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=800&h=600&fit=crop"
        ]
        
        for i in range(min(count, len(example_urls))):
            try:
                url = example_urls[i]
                response = requests.get(url, timeout=30, stream=True)
                
                if response.status_code == 200:
                    filename = f"web_download_{i+1:03d}.jpg"
                    filepath = self.output_dir / filename
                    
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    quality_metrics = self.analyzer.analyze_image_quality(str(filepath))
                    if "error" not in quality_metrics:
                        quality_metrics['category'] = 'mixed'
                        quality_metrics['source'] = 'web'
                        downloaded.append(quality_metrics)
                        print(f"    ✓ {filename} (质量分数: {quality_metrics['quality_score']:.3f})")
                    else:
                        filepath.unlink()
                
                time.sleep(1)
                
            except Exception as e:
                print(f"    ✗ 下载失败: {e}")
                continue
        
        return downloaded
    
    def select_best_images(self, target_count: int = 100) -> List[Dict]:
        """选择质量最好的图片"""
        print(f"🔍 从 {len(self.collected_images)} 张图片中选择最好的 {target_count} 张...")
        
        # 按质量分数排序
        valid_images = [img for img in self.collected_images if "error" not in img]
        sorted_images = sorted(valid_images, key=lambda x: x['quality_score'], reverse=True)
        
        # 选择前N张，同时保证类别多样性
        selected = []
        category_counts = {}
        
        # 首先按类别分组
        by_category = {}
        for img in sorted_images:
            category = img.get('category', 'unknown')
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(img)
        
        # 均匀选择各类别的图片
        categories = list(by_category.keys())
        per_category = target_count // len(categories)
        remaining = target_count % len(categories)
        
        for i, category in enumerate(categories):
            count_for_this_category = per_category + (1 if i < remaining else 0)
            selected.extend(by_category[category][:count_for_this_category])
        
        # 如果还不够，从剩余图片中选择质量最高的
        if len(selected) < target_count:
            remaining_images = [img for img in sorted_images if img not in selected]
            selected.extend(remaining_images[:target_count - len(selected)])
        
        # 重新排序并截取
        selected = sorted(selected, key=lambda x: x['quality_score'], reverse=True)[:target_count]
        
        print(f"✓ 选择了 {len(selected)} 张最高质量图片")
        print("类别分布:")
        category_counts = {}
        for img in selected:
            category = img.get('category', 'unknown')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        for category, count in category_counts.items():
            print(f"  {category}: {count} 张")
        
        return selected
    
    def save_metadata(self, selected_images: List[Dict], output_file: str = "metadata/image_collection.json"):
        """保存图片收集的元数据"""
        metadata_path = Path(output_file)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        
        metadata = {
            "collection_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_collected": len(self.collected_images),
            "selected_count": len(selected_images),
            "quality_metrics_used": self.analyzer.quality_metrics,
            "selected_images": selected_images,
            "statistics": self.calculate_statistics(selected_images)
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 元数据保存到: {metadata_path}")
        return metadata
    
    def calculate_statistics(self, images: List[Dict]) -> Dict:
        """计算图片集合的统计信息"""
        if not images:
            return {}
        
        quality_scores = [img['quality_score'] for img in images]
        resolutions = [img['resolution'] for img in images]
        file_sizes = [img['file_size'] for img in images]
        
        return {
            "quality_score": {
                "mean": float(np.mean(quality_scores)),
                "std": float(np.std(quality_scores)),
                "min": float(np.min(quality_scores)),
                "max": float(np.max(quality_scores))
            },
            "resolution": {
                "mean": float(np.mean(resolutions)),
                "std": float(np.std(resolutions)),
                "min": float(np.min(resolutions)),
                "max": float(np.max(resolutions))
            },
            "file_size": {
                "mean": float(np.mean(file_sizes)),
                "std": float(np.std(file_sizes)),
                "min": float(np.min(file_sizes)),
                "max": float(np.max(file_sizes))
            }
        }


def main():
    """主函数"""
    print("🎨 视觉边界数据集图片收集器")
    print("=" * 50)
    
    # 初始化收集器
    collector = ImageCollector("data/original")
    
    # 步骤1: 收集现有图片
    print("\n步骤1: 收集现有图片")
    collector.collect_from_input_folder()
    
    # 步骤2: 下载额外图片
    print("\n步骤2: 下载额外图片")
    collector.download_additional_images(target_total=100)
    
    # 步骤3: 选择最好的100张
    print("\n步骤3: 选择最高质量图片")
    selected_images = collector.select_best_images(100)
    
    # 步骤4: 保存元数据
    print("\n步骤4: 保存元数据")
    metadata = collector.save_metadata(selected_images)
    
    print(f"\n✅ 图片收集完成!")
    print(f"📊 统计信息:")
    print(f"  总收集: {len(collector.collected_images)} 张")
    print(f"  最终选择: {len(selected_images)} 张")
    print(f"  平均质量分数: {metadata['statistics']['quality_score']['mean']:.3f}")


if __name__ == "__main__":
    main()