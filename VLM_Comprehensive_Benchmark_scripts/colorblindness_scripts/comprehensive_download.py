#!/usr/bin/env python3
"""
综合下载器 - 从多个网络源尽可能多地下载真实色盲测试图像
"""

import requests
import json
import time
import re
from pathlib import Path
import urllib3
from urllib.parse import urljoin, urlparse, quote
# from bs4 import BeautifulSoup  # 暂时注释掉，不是必需的

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ComprehensiveIshiharaDownloader:
    def __init__(self, base_dir="data/raw"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.metadata = []
        
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def download_from_online_test_sites(self):
        """从在线测试网站下载图像"""
        print("正在从在线色盲测试网站下载...")
        
        # 这些网站通常有测试图像的直接链接
        test_sites = [
            {
                "name": "ColorBlindTest.net",
                "base_url": "https://www.colorblindtest.net",
                "image_patterns": [
                    "/images/ishihara-{}.jpg",
                    "/images/plate-{}.jpg",
                    "/images/test-{}.png"
                ]
            },
            {
                "name": "ColorLiteLens",
                "base_url": "https://www.colorlitelens.com",
                "image_patterns": [
                    "/images/ishihara/plate{}.jpg",
                    "/images/test/plate{}.png"
                ]
            },
            {
                "name": "Color-Blindness.com",
                "base_url": "https://www.color-blindness.com",
                "image_patterns": [
                    "/wp-content/uploads/ishihara-{}.jpg",
                    "/images/plate-{}.png"
                ]
            }
        ]
        
        downloaded = 0
        
        for site in test_sites:
            print(f"  尝试从 {site['name']} 下载...")
            
            for pattern in site['image_patterns']:
                for i in range(1, 40):  # 尝试1-39号图像
                    url = site['base_url'] + pattern.format(i)
                    
                    try:
                        response = self.session.head(url, timeout=10)
                        if response.status_code == 200:
                            # 找到了图像，下载它
                            response = self.session.get(url, timeout=30)
                            if response.status_code == 200:
                                filename = f"online_{site['name'].lower().replace('.', '_')}_{i:02d}.jpg"
                                filepath = self.base_dir / filename
                                
                                with open(filepath, 'wb') as f:
                                    f.write(response.content)
                                
                                self.metadata.append({
                                    "filename": filename,
                                    "source": f"Online Test Site - {site['name']}",
                                    "url": url,
                                    "type": "ishihara_online",
                                    "file_size": len(response.content)
                                })
                                
                                downloaded += 1
                                print(f"    ✓ 下载成功: {filename}")
                                time.sleep(0.5)
                                
                    except Exception as e:
                        # 忽略404等错误，继续尝试下一个
                        pass
        
        return downloaded

    def download_from_educational_sites(self):
        """从教育网站下载"""
        print("正在从教育网站下载...")
        
        # 教育网站通常有用于教学的色盲测试图
        edu_sites = [
            "https://www.nei.nih.gov",  # National Eye Institute
            "https://www.aao.org",     # American Academy of Ophthalmology
            "https://www.college-optometrists.org",  # College of Optometrists
        ]
        
        downloaded = 0
        
        for base_url in edu_sites:
            try:
                print(f"  搜索 {base_url}...")
                
                # 尝试常见的图像路径
                common_paths = [
                    "/images/color-vision/",
                    "/resources/images/",
                    "/media/images/",
                    "/assets/images/",
                    "/files/images/"
                ]
                
                for path in common_paths:
                    for i in range(1, 20):
                        test_urls = [
                            f"{base_url}{path}ishihara-{i}.jpg",
                            f"{base_url}{path}plate-{i}.png",
                            f"{base_url}{path}colortest-{i}.jpg"
                        ]
                        
                        for url in test_urls:
                            try:
                                response = self.session.head(url, timeout=10)
                                if response.status_code == 200:
                                    response = self.session.get(url, timeout=30)
                                    if response.status_code == 200:
                                        domain = urlparse(base_url).netloc
                                        filename = f"edu_{domain.replace('.', '_')}_{downloaded+1:02d}.jpg"
                                        filepath = self.base_dir / filename
                                        
                                        with open(filepath, 'wb') as f:
                                            f.write(response.content)
                                        
                                        self.metadata.append({
                                            "filename": filename,
                                            "source": f"Educational Site - {domain}",
                                            "url": url,
                                            "type": "ishihara_educational",
                                            "file_size": len(response.content)
                                        })
                                        
                                        downloaded += 1
                                        print(f"    ✓ 下载成功: {filename}")
                                        time.sleep(1)
                                        
                            except Exception:
                                pass
                                
            except Exception as e:
                print(f"  ✗ 访问失败 {base_url}: {e}")
        
        return downloaded

    def download_from_medical_archives(self):
        """从医学档案和数据库下载"""
        print("正在从医学档案下载...")
        
        # 医学档案网站
        medical_sources = [
            "https://medlineplus.gov",
            "https://www.healthline.com",
            "https://www.webmd.com",
            "https://www.mayoclinic.org"
        ]
        
        downloaded = 0
        
        for base_url in medical_sources:
            try:
                print(f"  搜索 {base_url}...")
                
                # 常见的医学图像路径
                medical_paths = [
                    "/images/medical/",
                    "/media/medical-images/",
                    "/assets/health-images/",
                    "/images/conditions/",
                    "/media/eye-health/"
                ]
                
                for path in medical_paths:
                    for i in range(1, 15):
                        test_urls = [
                            f"{base_url}{path}color-vision-test-{i}.jpg",
                            f"{base_url}{path}ishihara-test-{i}.png",
                            f"{base_url}{path}eye-test-{i}.jpg"
                        ]
                        
                        for url in test_urls:
                            try:
                                response = self.session.head(url, timeout=10)
                                if response.status_code == 200:
                                    response = self.session.get(url, timeout=30)
                                    if response.status_code == 200:
                                        domain = urlparse(base_url).netloc
                                        filename = f"medical_{domain.replace('.', '_')}_{downloaded+1:02d}.jpg"
                                        filepath = self.base_dir / filename
                                        
                                        with open(filepath, 'wb') as f:
                                            f.write(response.content)
                                        
                                        self.metadata.append({
                                            "filename": filename,
                                            "source": f"Medical Archive - {domain}",
                                            "url": url,
                                            "type": "ishihara_medical",
                                            "file_size": len(response.content)
                                        })
                                        
                                        downloaded += 1
                                        print(f"    ✓ 下载成功: {filename}")
                                        time.sleep(1)
                                        
                            except Exception:
                                pass
                                
            except Exception as e:
                print(f"  ✗ 访问失败 {base_url}: {e}")
        
        return downloaded

    def download_from_google_images_api(self):
        """尝试从搜索结果中获取图像链接"""
        print("正在搜索更多图像链接...")
        
        # 注意：这个方法可能受到限制，仅作为补充手段
        search_terms = [
            "ishihara color blindness test plate",
            "pseudoisochromatic plates color vision",
            "color blindness test chart",
            "ishihara test number plates"
        ]
        
        downloaded = 0
        
        for term in search_terms:
            try:
                # 构建搜索URL（这里使用DuckDuckGo作为示例）
                search_url = f"https://duckduckgo.com/?q={quote(term)}&iax=images&ia=images"
                
                print(f"  搜索: {term}")
                
                # 注意：实际的图像搜索和下载需要更复杂的实现
                # 这里只是一个框架示例
                
            except Exception as e:
                print(f"  ✗ 搜索失败 {term}: {e}")
        
        return downloaded

    def download_from_alternative_sources(self):
        """从其他可能的来源下载"""
        print("正在从其他来源下载...")
        
        # 其他可能的图像来源
        alternative_urls = [
            # 一些可能包含色盲测试图的直接链接
            "https://i.imgur.com/ishihara1.jpg",
            "https://i.imgur.com/ishihara2.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Ishihara_9.png/800px-Ishihara_9.png",
            # 添加更多可能的直接图像链接
        ]
        
        downloaded = 0
        
        for url in alternative_urls:
            try:
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    filename = f"alternative_{downloaded+1:02d}.jpg"
                    filepath = self.base_dir / filename
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    self.metadata.append({
                        "filename": filename,
                        "source": "Alternative Source",
                        "url": url,
                        "type": "ishihara_alternative",
                        "file_size": len(response.content)
                    })
                    
                    downloaded += 1
                    print(f"  ✓ 下载成功: {filename}")
                    time.sleep(1)
                    
            except Exception as e:
                print(f"  ✗ 下载失败 {url}: {e}")
        
        return downloaded

    def save_metadata(self, metadata_file="metadata/comprehensive_download_metadata.json"):
        """保存元数据"""
        metadata_path = Path(metadata_file)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump({
                "total_images": len(self.metadata),
                "download_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "source": "Comprehensive Download",
                "images": self.metadata
            }, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 元数据保存到: {metadata_path}")

    def run(self):
        """运行综合下载流程"""
        print("=== 综合色盲测试图下载器 ===")
        print("从多个网络源尽可能多地下载真实色盲测试图...")
        
        total_downloaded = 0
        
        # 各种下载方法
        methods = [
            ("在线测试网站", self.download_from_online_test_sites),
            ("教育网站", self.download_from_educational_sites),
            ("医学档案", self.download_from_medical_archives),
            ("替代来源", self.download_from_alternative_sources),
        ]
        
        for method_name, method_func in methods:
            print(f"\n--- {method_name} ---")
            try:
                downloaded = method_func()
                total_downloaded += downloaded
                print(f"从 {method_name} 下载了 {downloaded} 张图像")
                
                # 如果已经达到目标，可以提前结束
                if len(self.metadata) >= 100:
                    print("已达到目标数量，停止下载")
                    break
                    
            except Exception as e:
                print(f"从 {method_name} 下载失败: {e}")
        
        # 保存元数据
        self.save_metadata()
        
        print(f"\n=== 综合下载完成 ===")
        print(f"新下载: {len(self.metadata)} 张图像")
        
        # 统计总数（包括之前下载的）
        total_files = len(list(self.base_dir.glob("*.png"))) + len(list(self.base_dir.glob("*.jpg")))
        print(f"总计图像: {total_files} 张")
        print(f"目标进度: {total_files}/100")
        
        if total_files >= 100:
            print("✓ 达到目标数量!")
        else:
            print(f"还需要: {100 - total_files} 张图像")
        
        return len(self.metadata)


if __name__ == "__main__":
    downloader = ComprehensiveIshiharaDownloader()
    downloader.run()