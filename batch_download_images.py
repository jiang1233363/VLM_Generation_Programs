#!/usr/bin/env python3
"""
批量图片下载器 - 确保获得至少100张高质量真实图片
"""

import requests
import os
import time
import json
import cv2
import numpy as np
from pathlib import Path
from PIL import Image
import urllib.parse
import random
import logging
import hashlib

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class BatchImageDownloader:
    """批量图片下载器"""
    
    def __init__(self, base_dir: str = "/home/jgy/visual_boundary_dataset"):
        self.base_dir = Path(base_dir)
        self.images_dir = self.base_dir / "downloaded_images"
        self.metadata_dir = self.base_dir / "metadata"
        
        self.images_dir.mkdir(exist_ok=True)
        self.metadata_dir.mkdir(exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # 大量高质量图片URL列表
        self.image_urls = [
            # 自然风景
            "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800",
            "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800", 
            "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=800",
            "https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?w=800",
            "https://images.unsplash.com/photo-1501594907352-04cda38ebc29?w=800",
            "https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=800",
            "https://images.unsplash.com/photo-1562813733-b31f71025d54?w=800",
            "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=800",
            "https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=800",
            
            # 动物
            "https://images.unsplash.com/photo-1574158622682-e40e69881006?w=800",
            "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=800",
            "https://images.unsplash.com/photo-1592194996308-7b43878e84a6?w=800",
            "https://images.unsplash.com/photo-1548247416-ec66f4900b2e?w=800",
            "https://images.unsplash.com/photo-1601758228041-f3b2795255f1?w=800",
            "https://images.unsplash.com/photo-1583512603805-3cc6b41f3edb?w=800",
            "https://images.unsplash.com/photo-1560807707-8cc77767d783?w=800",
            
            # 建筑
            "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=800",
            "https://images.unsplash.com/photo-1480714378408-67cf0d13bc1f?w=800",
            "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=800",
            "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=800",
            "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800",
            
            # 食物
            "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800",
            "https://images.unsplash.com/photo-1551782450-a2132b4ba21d?w=800", 
            "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=800",
            "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800",
            "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=800",
            
            # Pexels URLs
            "https://images.pexels.com/photos/1440727/pexels-photo-1440727.jpeg?w=800",
            "https://images.pexels.com/photos/417074/pexels-photo-417074.jpeg?w=800",
            "https://images.pexels.com/photos/302743/pexels-photo-302743.jpeg?w=800",
            "https://images.pexels.com/photos/572897/pexels-photo-572897.jpeg?w=800",
            "https://images.pexels.com/photos/956999/pexels-photo-956999.jpeg?w=800",
            "https://images.pexels.com/photos/1758144/pexels-photo-1758144.jpeg?w=800",
            "https://images.pexels.com/photos/1619317/pexels-photo-1619317.jpeg?w=800",
            "https://images.pexels.com/photos/1382734/pexels-photo-1382734.jpeg?w=800",
            "https://images.pexels.com/photos/1624496/pexels-photo-1624496.jpeg?w=800",
            "https://images.pexels.com/photos/1379636/pexels-photo-1379636.jpeg?w=800",
            "https://images.pexels.com/photos/1264210/pexels-photo-1264210.jpeg?w=800",
            "https://images.pexels.com/photos/1181263/pexels-photo-1181263.jpeg?w=800",
            "https://images.pexels.com/photos/1181216/pexels-photo-1181216.jpeg?w=800",
            "https://images.pexels.com/photos/1181244/pexels-photo-1181244.jpeg?w=800",
            "https://images.pexels.com/photos/1181248/pexels-photo-1181248.jpeg?w=800",
            "https://images.pexels.com/photos/1181467/pexels-photo-1181467.jpeg?w=800",
            "https://images.pexels.com/photos/1546901/pexels-photo-1546901.jpeg?w=800",
            "https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg?w=800",
            "https://images.pexels.com/photos/1769524/pexels-photo-1769524.jpeg?w=800",
            "https://images.pexels.com/photos/1851415/pexels-photo-1851415.jpeg?w=800",
            "https://images.pexels.com/photos/2662116/pexels-photo-2662116.jpeg?w=800",
            "https://images.pexels.com/photos/1000445/pexels-photo-1000445.jpeg?w=800",
            "https://images.pexels.com/photos/1761279/pexels-photo-1761279.jpeg?w=800",
            
            # Wikimedia Commons URLs
            "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Felis_catus-cat_on_snow.jpg/800px-Felis_catus-cat_on_snow.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Red_Apple.jpg/800px-Red_Apple.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Bananas.jpg/800px-Bananas.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/YellowLabradorLooking_new.jpg/800px-YellowLabradorLooking_new.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/800px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Pink_flower.jpg/800px-Pink_flower.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Oranges_and_orange_juice.jpg/800px-Oranges_and_orange_juice.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Vd-Orig.jpg/800px-Vd-Orig.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Colosseo_2020.jpg/800px-Colosseo_2020.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/New_York_City_at_night_HDR_edit1.jpg/800px-New_York_City_at_night_HDR_edit1.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/20100726_Kalamitsi_Beach_Ionian_Sea_Lefkada_island_Greece.jpg/800px-20100726_Kalamitsi_Beach_Ionian_Sea_Lefkada_island_Greece.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/Flight_landscape.jpg/800px-Flight_landscape.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/London_Big_Ben_Phone_box.jpg/600px-London_Big_Ben_Phone_box.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Tour_eiffel_at_sunrise_from_the_trocadero.jpg/800px-Tour_eiffel_at_sunrise_from_the_trocadero.jpg",
            
            # 更多高质量图片URLs
            "https://picsum.photos/800/600?random=1",
            "https://picsum.photos/800/600?random=2", 
            "https://picsum.photos/800/600?random=3",
            "https://picsum.photos/800/600?random=4",
            "https://picsum.photos/800/600?random=5",
            "https://picsum.photos/800/600?random=6",
            "https://picsum.photos/800/600?random=7",
            "https://picsum.photos/800/600?random=8",
            "https://picsum.photos/800/600?random=9",
            "https://picsum.photos/800/600?random=10",
            "https://picsum.photos/800/600?random=11",
            "https://picsum.photos/800/600?random=12",
            "https://picsum.photos/800/600?random=13", 
            "https://picsum.photos/800/600?random=14",
            "https://picsum.photos/800/600?random=15",
            "https://picsum.photos/800/600?random=16",
            "https://picsum.photos/800/600?random=17",
            "https://picsum.photos/800/600?random=18",
            "https://picsum.photos/800/600?random=19",
            "https://picsum.photos/800/600?random=20",
            "https://picsum.photos/800/600?random=21",
            "https://picsum.photos/800/600?random=22",
            "https://picsum.photos/800/600?random=23",
            "https://picsum.photos/800/600?random=24",
            "https://picsum.photos/800/600?random=25",
            "https://picsum.photos/800/600?random=26",
            "https://picsum.photos/800/600?random=27",
            "https://picsum.photos/800/600?random=28",
            "https://picsum.photos/800/600?random=29",
            "https://picsum.photos/800/600?random=30",
            "https://picsum.photos/800/600?random=31",
            "https://picsum.photos/800/600?random=32",
            "https://picsum.photos/800/600?random=33", 
            "https://picsum.photos/800/600?random=34",
            "https://picsum.photos/800/600?random=35",
            "https://picsum.photos/800/600?random=36",
            "https://picsum.photos/800/600?random=37",
            "https://picsum.photos/800/600?random=38",
            "https://picsum.photos/800/600?random=39",
            "https://picsum.photos/800/600?random=40",
            "https://picsum.photos/800/600?random=41",
            "https://picsum.photos/800/600?random=42",
            "https://picsum.photos/800/600?random=43",
            "https://picsum.photos/800/600?random=44",
            "https://picsum.photos/800/600?random=45",
            "https://picsum.photos/800/600?random=46",
            "https://picsum.photos/800/600?random=47",
            "https://picsum.photos/800/600?random=48",
            "https://picsum.photos/800/600?random=49",
            "https://picsum.photos/800/600?random=50"
        ]
    
    def get_image_hash(self, image_path: str) -> str:
        """计算图片哈希值用于去重"""
        try:
            with open(image_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""
    
    def validate_and_analyze_image(self, image_path: Path) -> dict:
        """验证并分析图片质量"""
        try:
            # 检查文件大小
            if os.path.getsize(image_path) < 5000:  # 小于5KB
                return None
            
            # 使用PIL验证
            with Image.open(image_path) as img:
                img.verify()
                
            # 重新打开进行详细分析
            image = cv2.imread(str(image_path))
            if image is None:
                return None
                
            pil_image = Image.open(image_path)
            height, width = image.shape[:2]
            
            # 尺寸检查
            if width < 200 or height < 200:
                return None
            
            # 质量分析
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 清晰度
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # 亮度
            brightness = np.mean(rgb_image)
            
            # 对比度  
            contrast = gray.std()
            
            # 质量评分
            sharpness_score = min(sharpness / 500, 1.0)
            brightness_score = 1.0 - abs(brightness - 127.5) / 127.5
            contrast_score = min(contrast / 80, 1.0)
            resolution_score = min((width * height) / (800 * 600), 1.0)
            
            quality_score = (
                sharpness_score * 0.35 + 
                brightness_score * 0.25 +
                contrast_score * 0.25 + 
                resolution_score * 0.15
            )
            
            return {
                'filename': image_path.name,
                'file_path': str(image_path),
                'width': width,
                'height': height,
                'resolution': width * height,
                'file_size': os.path.getsize(image_path),
                'sharpness': float(sharpness),
                'brightness': float(brightness),
                'contrast': float(contrast),
                'quality_score': float(quality_score),
                'hash': self.get_image_hash(str(image_path))
            }
            
        except Exception as e:
            return None
    
    def download_single_image(self, url: str, filename: str) -> bool:
        """下载单个图片"""
        try:
            response = self.session.get(url, timeout=20, allow_redirects=True)
            if response.status_code == 200 and len(response.content) > 5000:
                file_path = self.images_dir / filename
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                return True
        except Exception:
            pass
        return False
    
    def batch_download(self, target_count: int = 100) -> list:
        """批量下载图片达到目标数量"""
        print("🚀 批量下载高质量真实图片")
        print("=" * 50)
        
        all_valid_images = []
        downloaded_hashes = set()
        
        # 首先处理现有图片
        existing_count = 0
        for existing_file in self.images_dir.glob("existing_*"):
            if existing_file.is_file():
                analysis = self.validate_and_analyze_image(existing_file)
                if analysis and analysis['hash'] not in downloaded_hashes:
                    all_valid_images.append(analysis)
                    downloaded_hashes.add(analysis['hash'])
                    existing_count += 1
        
        print(f"📁 现有有效图片: {existing_count} 张")
        
        if len(all_valid_images) >= target_count:
            print("✅ 现有图片已满足需求")
            return all_valid_images[:target_count]
        
        # 需要下载的数量
        need_download = target_count - len(all_valid_images)
        print(f"📡 需要额外下载: {need_download} 张")
        
        # 随机打乱URL列表
        random.shuffle(self.image_urls)
        
        download_count = 0
        for i, url in enumerate(self.image_urls):
            if len(all_valid_images) >= target_count:
                break
                
            filename = f"download_{i+1:03d}.jpg"
            file_path = self.images_dir / filename
            
            print(f"⬇️  下载 {i+1}/{len(self.image_urls)}: {filename}")
            
            if self.download_single_image(url, filename):
                analysis = self.validate_and_analyze_image(file_path)
                
                if analysis and analysis['hash'] not in downloaded_hashes:
                    all_valid_images.append(analysis)
                    downloaded_hashes.add(analysis['hash'])
                    download_count += 1
                    print(f"   ✓ 质量分数: {analysis['quality_score']:.3f}")
                else:
                    # 删除无效或重复图片
                    if file_path.exists():
                        os.remove(file_path)
                    print(f"   ❌ 无效或重复")
            else:
                print(f"   ❌ 下载失败")
            
            # 避免请求过快
            time.sleep(0.2)
            
            # 每10张显示进度
            if (i + 1) % 10 == 0:
                print(f"📊 进度: 已下载有效图片 {len(all_valid_images)} / {target_count}")
        
        print(f"\n🎉 下载完成!")
        print(f"📊 统计:")
        print(f"   现有图片: {existing_count} 张")
        print(f"   新下载: {download_count} 张") 
        print(f"   总有效图片: {len(all_valid_images)} 张")
        
        return all_valid_images

def main():
    """主函数"""
    downloader = BatchImageDownloader()
    
    # 批量下载100张图片
    images = downloader.batch_download(100)
    
    # 按质量分数排序
    images.sort(key=lambda x: x['quality_score'], reverse=True)
    selected_images = images[:100] if len(images) >= 100 else images
    
    # 生成统计信息
    if selected_images:
        avg_quality = sum(img['quality_score'] for img in selected_images) / len(selected_images)
        total_size = sum(img['file_size'] for img in selected_images)
        avg_resolution = sum(img['resolution'] for img in selected_images) / len(selected_images)
    else:
        avg_quality = 0
        total_size = 0
        avg_resolution = 0
    
    # 保存最终元数据
    final_metadata = {
        'dataset_info': {
            'total_images': len(selected_images),
            'target_count': 100,
            'avg_quality_score': float(avg_quality),
            'total_size_mb': total_size / (1024 * 1024),
            'avg_resolution': int(avg_resolution)
        },
        'quality_distribution': {
            'excellent': len([img for img in selected_images if img['quality_score'] >= 0.8]),
            'good': len([img for img in selected_images if 0.6 <= img['quality_score'] < 0.8]),
            'fair': len([img for img in selected_images if 0.4 <= img['quality_score'] < 0.6]),
            'poor': len([img for img in selected_images if img['quality_score'] < 0.4])
        },
        'selected_images': selected_images
    }
    
    # 保存元数据
    metadata_file = downloader.metadata_dir / "final_image_collection.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(final_metadata, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 最终元数据保存到: {metadata_file}")
    print(f"🏆 最终选择: {len(selected_images)} 张高质量图片")
    print(f"📈 平均质量分数: {avg_quality:.3f}")
    print(f"💾 总文件大小: {total_size / (1024 * 1024):.1f} MB")
    print(f"📐 平均分辨率: {int(avg_resolution)} 像素")
    
    quality_dist = final_metadata['quality_distribution']
    print(f"🎯 质量分布:")
    print(f"   优秀(≥0.8): {quality_dist['excellent']} 张")
    print(f"   良好(0.6-0.8): {quality_dist['good']} 张") 
    print(f"   一般(0.4-0.6): {quality_dist['fair']} 张")
    print(f"   较差(<0.4): {quality_dist['poor']} 张")

if __name__ == "__main__":
    main()