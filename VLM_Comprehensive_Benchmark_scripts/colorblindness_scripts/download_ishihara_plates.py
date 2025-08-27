#!/usr/bin/env python3
"""
色盲测试图下载脚本
从多个开源数据源下载石原氏色盲测试图
"""

import os
import requests
import numpy as np
from PIL import Image
import json
import time
from pathlib import Path
import urllib3
from urllib.parse import urljoin, urlparse
import ssl
import certifi

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class IshiharaDownloader:
    def __init__(self, base_dir="data/raw"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.metadata = []
        
        # 设置requests会话，配置重试和SSL
        self.session = requests.Session()
        self.session.verify = False  # 暂时禁用SSL验证以解决连接问题
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def download_from_wikimedia_commons(self):
        """从维基媒体共享资源下载石原氏测试图"""
        # 扩展的维基媒体共享资源石原氏测试图URL列表
        wikimedia_urls = [
            "https://upload.wikimedia.org/wikipedia/commons/e/e0/Ishihara_9.png",
            "https://upload.wikimedia.org/wikipedia/commons/5/55/Colour_blindness_test.png", 
            "https://upload.wikimedia.org/wikipedia/commons/7/74/Ishihara_23.PNG",
            "https://upload.wikimedia.org/wikipedia/commons/a/a4/Ishihara_Plate_3.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/6/6c/Ishihara_1.png",
            "https://upload.wikimedia.org/wikipedia/commons/b/b4/Ishihara_2.png",
            "https://upload.wikimedia.org/wikipedia/commons/1/1a/Ishihara_4.png",
            "https://upload.wikimedia.org/wikipedia/commons/9/9a/Ishihara_5.png",
            "https://upload.wikimedia.org/wikipedia/commons/c/c8/Ishihara_6.png",
            "https://upload.wikimedia.org/wikipedia/commons/f/f8/Ishihara_7.png",
            "https://upload.wikimedia.org/wikipedia/commons/7/7d/Ishihara_8.png",
            "https://upload.wikimedia.org/wikipedia/commons/2/2e/Ishihara_10.png",
            "https://upload.wikimedia.org/wikipedia/commons/d/d4/Ishihara_11.png",
            "https://upload.wikimedia.org/wikipedia/commons/3/3f/Ishihara_12.png",
            "https://upload.wikimedia.org/wikipedia/commons/8/8a/Ishihara_13.png",
            "https://upload.wikimedia.org/wikipedia/commons/f/f1/Ishihara_14.png",
            "https://upload.wikimedia.org/wikipedia/commons/4/4e/Ishihara_15.png",
            "https://upload.wikimedia.org/wikipedia/commons/a/ab/Ishihara_16.png",
            "https://upload.wikimedia.org/wikipedia/commons/c/c5/Ishihara_17.png",
            "https://upload.wikimedia.org/wikipedia/commons/1/12/Ishihara_18.png",
            "https://upload.wikimedia.org/wikipedia/commons/e/ef/Ishihara_19.png",
            "https://upload.wikimedia.org/wikipedia/commons/d/dc/Ishihara_20.png",
            "https://upload.wikimedia.org/wikipedia/commons/7/75/Ishihara_21.png",
            "https://upload.wikimedia.org/wikipedia/commons/9/98/Ishihara_22.png",
            "https://upload.wikimedia.org/wikipedia/commons/4/43/Ishihara_24.png",
            "https://upload.wikimedia.org/wikipedia/commons/2/2a/Ishihara_25.png",
            "https://upload.wikimedia.org/wikipedia/commons/6/60/Ishihara_26.png",
            "https://upload.wikimedia.org/wikipedia/commons/8/84/Ishihara_27.png",
            "https://upload.wikimedia.org/wikipedia/commons/f/fc/Ishihara_28.png",
            "https://upload.wikimedia.org/wikipedia/commons/b/bb/Ishihara_29.png",
            "https://upload.wikimedia.org/wikipedia/commons/1/1e/Ishihara_30.png",
            "https://upload.wikimedia.org/wikipedia/commons/5/5a/Ishihara_31.png",
            "https://upload.wikimedia.org/wikipedia/commons/c/c9/Ishihara_32.png",
            "https://upload.wikimedia.org/wikipedia/commons/a/a0/Ishihara_33.png",
            "https://upload.wikimedia.org/wikipedia/commons/f/f4/Ishihara_34.png",
            "https://upload.wikimedia.org/wikipedia/commons/d/d8/Ishihara_35.png",
            "https://upload.wikimedia.org/wikipedia/commons/8/8e/Ishihara_36.png",
            "https://upload.wikimedia.org/wikipedia/commons/2/26/Ishihara_37.png",
            "https://upload.wikimedia.org/wikipedia/commons/c/cb/Ishihara_38.png",
        ]
        
        print("正在从维基媒体共享资源下载...")
        for i, url in enumerate(wikimedia_urls):
            try:
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    filename = f"wikimedia_ishihara_{i+1:02d}.png"
                    filepath = self.base_dir / filename
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    self.metadata.append({
                        "filename": filename,
                        "source": "Wikimedia Commons",
                        "url": url,
                        "type": "ishihara",
                        "expected_number": "unknown"
                    })
                    print(f"✓ 下载成功: {filename}")
                    time.sleep(1)  # 礼貌性延迟
                    
            except Exception as e:
                print(f"✗ 下载失败 {url}: {e}")
    
    def create_synthetic_ishihara_plates(self):
        """创建合成的石原氏风格测试图"""
        print("正在创建合成石原氏测试图...")
        
        # 扩展数字模板和颜色配置 - 生成80个不同的数字测试图
        base_cases = [
            {"number": "8", "fg_base": (255, 80, 80), "bg_base": (80, 255, 80)},
            {"number": "3", "fg_base": (255, 100, 100), "bg_base": (100, 200, 100)},
            {"number": "5", "fg_base": (200, 50, 50), "bg_base": (50, 180, 50)},
            {"number": "2", "fg_base": (255, 120, 120), "bg_base": (120, 255, 120)},
            {"number": "6", "fg_base": (180, 40, 40), "bg_base": (40, 160, 40)},
            {"number": "9", "fg_base": (255, 90, 90), "bg_base": (90, 200, 90)},
            {"number": "7", "fg_base": (220, 60, 60), "bg_base": (60, 220, 60)},
            {"number": "4", "fg_base": (255, 110, 110), "bg_base": (110, 255, 110)},
            {"number": "1", "fg_base": (190, 30, 30), "bg_base": (30, 150, 30)},
            {"number": "0", "fg_base": (255, 140, 140), "bg_base": (140, 255, 140)},
        ]
        
        test_cases = []
        # 为每个基础数字创建8个不同颜色变体
        for base_case in base_cases:
            for variant in range(8):
                # 生成颜色变体
                fg_shift = variant * 20
                bg_shift = variant * 15
                
                test_cases.append({
                    "number": base_case["number"],
                    "fg_color": (
                        max(50, min(255, base_case["fg_base"][0] + fg_shift)),
                        max(50, min(255, base_case["fg_base"][1] - fg_shift//2)),
                        max(50, min(255, base_case["fg_base"][2] - fg_shift//3))
                    ),
                    "bg_color": (
                        max(50, min(255, base_case["bg_base"][0] - bg_shift//2)),
                        max(50, min(255, base_case["bg_base"][1] + bg_shift)),
                        max(50, min(255, base_case["bg_base"][2] - bg_shift//3))
                    ),
                    "variant": variant + 1
                })
        
        for i, case in enumerate(test_cases):
            try:
                image = self.create_dot_pattern_image(
                    case["number"], 
                    case["fg_color"], 
                    case["bg_color"]
                )
                
                filename = f"synthetic_ishihara_{case['number']}_v{case['variant']:02d}.png"
                filepath = self.base_dir / filename
                image.save(filepath)
                
                self.metadata.append({
                    "filename": filename,
                    "source": "Synthetic Generation",
                    "url": "locally_generated",
                    "type": "ishihara_synthetic",
                    "expected_number": case["number"],
                    "variant": case["variant"],
                    "fg_color": case["fg_color"],
                    "bg_color": case["bg_color"]
                })
                print(f"✓ 创建成功: {filename}")
                
            except Exception as e:
                print(f"✗ 创建失败 {case['number']}: {e}")
    
    def create_dot_pattern_image(self, number, fg_color, bg_color, size=(400, 400)):
        """创建点状模式的石原氏风格图像"""
        image = Image.new('RGB', size, 'white')
        pixels = np.array(image)
        
        # 创建随机点状背景
        np.random.seed(42)  # 确保可重现性
        
        # 创建圆形区域
        center_x, center_y = size[0] // 2, size[1] // 2
        radius = min(size) // 2 - 20
        
        # 生成随机点
        for _ in range(8000):  # 点的密度
            x = np.random.randint(0, size[0])
            y = np.random.randint(0, size[1])
            
            # 检查是否在圆形区域内
            if (x - center_x) ** 2 + (y - center_y) ** 2 <= radius ** 2:
                # 随机点大小
                dot_size = np.random.randint(3, 8)
                
                # 根据数字形状决定颜色
                if self.is_in_number_shape(x, y, number, center_x, center_y, radius):
                    color = self.add_color_variation(fg_color)
                else:
                    color = self.add_color_variation(bg_color)
                
                # 绘制点
                for dx in range(-dot_size//2, dot_size//2 + 1):
                    for dy in range(-dot_size//2, dot_size//2 + 1):
                        if (dx*dx + dy*dy <= dot_size*dot_size//4 and 
                            0 <= x+dx < size[0] and 0 <= y+dy < size[1]):
                            pixels[y+dy, x+dx] = color
        
        return Image.fromarray(pixels)
    
    def is_in_number_shape(self, x, y, number, center_x, center_y, radius):
        """简单的数字形状检测"""
        # 相对于中心的坐标
        rel_x = (x - center_x) / radius
        rel_y = (y - center_y) / radius
        
        # 简化的数字形状定义
        shapes = {
            "8": lambda x, y: (abs(y) < 0.6 and abs(x) < 0.3) or (abs(y - 0.3) < 0.2 and abs(x) < 0.25) or (abs(y + 0.3) < 0.2 and abs(x) < 0.25),
            "3": lambda x, y: (x > -0.1 and x < 0.3 and abs(y) < 0.6) or (abs(y) < 0.1 and x > -0.3 and x < 0.3),
            "5": lambda x, y: (x > -0.3 and x < 0.3 and y > 0.2 and y < 0.4) or (x > -0.3 and x < 0.1 and y > -0.4 and y < 0.2),
            "2": lambda x, y: (abs(y - 0.3) < 0.1 and abs(x) < 0.3) or (abs(y + 0.3) < 0.1 and abs(x) < 0.3) or (x > -0.1 and x < 0.1 and abs(y) < 0.6),
            "6": lambda x, y: (abs(x + 0.2) < 0.1 and abs(y) < 0.6) or (abs(y) < 0.1 and x > -0.3 and x < 0.3),
            "9": lambda x, y: (abs(x + 0.2) < 0.1 and y > -0.4 and y < 0.4) or (abs(y - 0.3) < 0.1 and x > -0.3 and x < 0.3),
            "7": lambda x, y: (y > 0.2 and y < 0.4 and abs(x) < 0.3) or (x > -0.1 and x < 0.1 and y > -0.4 and y < 0.4),
            "4": lambda x, y: (abs(x - 0.2) < 0.1 and abs(y) < 0.6) or (abs(y) < 0.1 and x > -0.3 and x < 0.3),
            "1": lambda x, y: abs(x) < 0.1 and abs(y) < 0.6,
            "0": lambda x, y: abs(y) < 0.6 and abs(x) < 0.3 and not (abs(y) < 0.4 and abs(x) < 0.1)
        }
        
        if number in shapes:
            return shapes[number](rel_x, rel_y)
        return False
    
    def add_color_variation(self, base_color, variation=30):
        """为颜色添加随机变化"""
        return tuple(
            max(0, min(255, c + np.random.randint(-variation, variation + 1)))
            for c in base_color
        )
    
    def download_from_github_repos(self):
        """从GitHub仓库下载图像"""
        print("正在尝试从GitHub仓库获取资源...")
        
        # 扩展GitHub raw文件URLs - 从多个开源项目获取
        github_urls = []
        
        # 从ishihara-plate-learning项目尝试下载
        for i in range(1, 39):  # 1-38号测试图
            github_urls.append(f"https://raw.githubusercontent.com/DJakarta/ishihara-plate-learning/master/plates/plate_{i:02d}.png")
        
        # 从其他项目尝试下载
        additional_urls = [
            "https://raw.githubusercontent.com/rpigu-i/processing-ishihara-plate/master/assets/ishihara_01.png",
            "https://raw.githubusercontent.com/rpigu-i/processing-ishihara-plate/master/assets/ishihara_02.png",
            "https://raw.githubusercontent.com/Lewis-Ho/ishihara/master/images/ishihara_1.png",
            "https://raw.githubusercontent.com/Lewis-Ho/ishihara/master/images/ishihara_2.png",
            "https://raw.githubusercontent.com/Lewis-Ho/ishihara/master/images/ishihara_3.png",
        ]
        github_urls.extend(additional_urls)
        
        for i, url in enumerate(github_urls):
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    filename = f"github_ishihara_{i+1}.png"
                    filepath = self.base_dir / filename
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    self.metadata.append({
                        "filename": filename,
                        "source": "GitHub Repository",
                        "url": url,
                        "type": "ishihara",
                        "expected_number": "unknown"
                    })
                    print(f"✓ 下载成功: {filename}")
                    time.sleep(1)
                    
            except Exception as e:
                print(f"✗ GitHub下载失败 {url}: {e}")
    
    def download_from_research_datasets(self):
        """从研究数据集和开源资源下载"""
        print("正在从研究数据集下载...")
        
        # 色盲测试相关的开源数据集URL
        research_urls = [
            # Color Vision Research Laboratory 测试图
            "https://colorlab.wickline.org/colorblind/ishihara/Ishihara.01.jpg",
            "https://colorlab.wickline.org/colorblind/ishihara/Ishihara.02.jpg", 
            "https://colorlab.wickline.org/colorblind/ishihara/Ishihara.03.jpg",
            "https://colorlab.wickline.org/colorblind/ishihara/Ishihara.04.jpg",
            "https://colorlab.wickline.org/colorblind/ishihara/Ishihara.05.jpg",
            "https://colorlab.wickline.org/colorblind/ishihara/Ishihara.06.jpg",
            "https://colorlab.wickline.org/colorblind/ishihara/Ishihara.07.jpg",
            "https://colorlab.wickline.org/colorblind/ishihara/Ishihara.08.jpg",
            "https://colorlab.wickline.org/colorblind/ishihara/Ishihara.09.jpg",
            "https://colorlab.wickline.org/colorblind/ishihara/Ishihara.10.jpg",
        ]
        
        for i, url in enumerate(research_urls):
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    filename = f"research_ishihara_{i+1:02d}.jpg"
                    filepath = self.base_dir / filename
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    self.metadata.append({
                        "filename": filename,
                        "source": "Research Dataset",
                        "url": url,
                        "type": "ishihara",
                        "expected_number": "unknown"
                    })
                    print(f"✓ 下载成功: {filename}")
                    time.sleep(1)
                    
            except Exception as e:
                print(f"✗ 研究数据集下载失败 {url}: {e}")
    
    def search_and_download_additional_sources(self):
        """搜索并下载额外的色盲测试图源"""
        print("正在搜索额外的测试图源...")
        
        # 尝试从医学教育网站获取
        medical_urls = [
            # 这些URL需要根据实际可用资源进行验证和调整
            "https://www.colorlitelens.com/images/color-blind-test-1.jpg",
            "https://www.colorlitelens.com/images/color-blind-test-2.jpg",
            "https://www.enchroma.com/images/test-1.png",
            "https://www.enchroma.com/images/test-2.png",
        ]
        
        for i, url in enumerate(medical_urls):
            try:
                response = requests.get(url, timeout=30, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                if response.status_code == 200:
                    filename = f"medical_colortest_{i+1:02d}.jpg"
                    filepath = self.base_dir / filename
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    self.metadata.append({
                        "filename": filename,
                        "source": "Medical Education Website",
                        "url": url,
                        "type": "colorblindness_test",
                        "expected_answer": "unknown"
                    })
                    print(f"✓ 下载成功: {filename}")
                    time.sleep(2)  # 更长的延迟，礼貌性访问
                    
            except Exception as e:
                print(f"✗ 医学网站下载失败 {url}: {e}")
    
    def create_additional_test_patterns(self):
        """创建额外的测试模式"""
        print("正在创建额外的测试模式...")
        
        # 扩展蓝黄色盲测试图 - 创建20个不同变体
        base_symbols = ["circle", "square", "triangle", "diamond", "star"]
        blue_yellow_cases = []
        
        for symbol in base_symbols:
            for variant in range(4):  # 每个符号4个变体
                variant_shift = variant * 30
                blue_yellow_cases.append({
                    "symbol": symbol,
                    "fg_color": (
                        max(50, min(255, 100 + variant_shift)),
                        max(50, min(255, 100 + variant_shift//2)),
                        255
                    ),
                    "bg_color": (
                        255,
                        255,
                        max(50, min(255, 100 + variant_shift//3))
                    ),
                    "variant": variant + 1
                })
        
        for i, case in enumerate(blue_yellow_cases):
            try:
                image = self.create_shape_pattern_image(
                    case["symbol"],
                    case["fg_color"],
                    case["bg_color"]
                )
                
                filename = f"blue_yellow_test_{case['symbol']}_v{case['variant']:02d}.png"
                filepath = self.base_dir / filename
                image.save(filepath)
                
                self.metadata.append({
                    "filename": filename,
                    "source": "Synthetic Generation",
                    "url": "locally_generated",
                    "type": "blue_yellow_test",
                    "expected_symbol": case["symbol"],
                    "variant": case["variant"],
                    "fg_color": case["fg_color"],
                    "bg_color": case["bg_color"]
                })
                print(f"✓ 创建成功: {filename}")
                
            except Exception as e:
                print(f"✗ 创建失败 {case['symbol']}: {e}")
    
    def create_shape_pattern_image(self, shape, fg_color, bg_color, size=(400, 400)):
        """创建形状模式的测试图像"""
        image = Image.new('RGB', size, 'white')
        pixels = np.array(image)
        
        np.random.seed(hash(shape) % 1000)  # 基于形状的种子
        
        center_x, center_y = size[0] // 2, size[1] // 2
        radius = min(size) // 2 - 20
        
        for _ in range(6000):
            x = np.random.randint(0, size[0])
            y = np.random.randint(0, size[1])
            
            if (x - center_x) ** 2 + (y - center_y) ** 2 <= radius ** 2:
                dot_size = np.random.randint(4, 9)
                
                if self.is_in_shape(x, y, shape, center_x, center_y, radius):
                    color = self.add_color_variation(fg_color)
                else:
                    color = self.add_color_variation(bg_color)
                
                for dx in range(-dot_size//2, dot_size//2 + 1):
                    for dy in range(-dot_size//2, dot_size//2 + 1):
                        if (dx*dx + dy*dy <= dot_size*dot_size//4 and 
                            0 <= x+dx < size[0] and 0 <= y+dy < size[1]):
                            pixels[y+dy, x+dx] = color
        
        return Image.fromarray(pixels)
    
    def is_in_shape(self, x, y, shape, center_x, center_y, radius):
        """检测是否在指定形状内"""
        rel_x = (x - center_x) / radius
        rel_y = (y - center_y) / radius
        
        shapes = {
            "circle": lambda x, y: x*x + y*y <= 0.3*0.3,
            "square": lambda x, y: abs(x) <= 0.3 and abs(y) <= 0.3,
            "triangle": lambda x, y: y >= -0.3 and y <= 0.3 and abs(x) <= (0.3 - y) * 0.5,
            "diamond": lambda x, y: abs(x) + abs(y) <= 0.4,
            "star": lambda x, y: (x*x + y*y <= 0.3*0.3) and ((abs(x) < 0.1 and abs(y) < 0.3) or (abs(y) < 0.1 and abs(x) < 0.3) or (abs(x-y) < 0.1 and abs(x) < 0.3) or (abs(x+y) < 0.1 and abs(x) < 0.3))
        }
        
        return shapes.get(shape, lambda x, y: False)(rel_x, rel_y)
    
    def save_metadata(self, metadata_file="metadata/base_images_metadata.json"):
        """保存元数据"""
        metadata_path = Path(metadata_file)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump({
                "total_images": len(self.metadata),
                "download_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "images": self.metadata
            }, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 元数据保存到: {metadata_path}")
    
    def run(self):
        """运行完整的下载流程 - 仅从网络下载真实图像"""
        print("=== 色盲测试图下载器 ===")
        print(f"目标目录: {self.base_dir}")
        print("正在从网络数据集下载真实的色盲测试图...")
        
        # 从各种网络源下载真实图像
        self.download_from_wikimedia_commons()
        self.download_from_github_repos() 
        self.download_from_research_datasets()
        self.search_and_download_additional_sources()
        
        # 保存元数据
        self.save_metadata()
        
        print(f"\n=== 下载完成 ===")
        print(f"总共下载 {len(self.metadata)} 张网络图像")
        print("图像来源分布:")
        
        source_counts = {}
        for img in self.metadata:
            source = img["source"]
            source_counts[source] = source_counts.get(source, 0) + 1
        
        for source, count in source_counts.items():
            print(f"  {source}: {count} 张")
        
        # 检查是否达到目标数量
        if len(self.metadata) >= 100:
            print(f"✓ 成功获取足够的图像 ({len(self.metadata)}/100)")
        else:
            print(f"⚠ 图像数量不足 ({len(self.metadata)}/100)")
            print("建议：检查网络连接或URL有效性")


if __name__ == "__main__":
    downloader = IshiharaDownloader()
    downloader.run()