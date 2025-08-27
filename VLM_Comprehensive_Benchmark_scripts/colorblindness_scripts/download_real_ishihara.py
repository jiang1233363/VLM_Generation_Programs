#!/usr/bin/env python3
"""
色盲测试图下载脚本 - 仅从网络下载真实图像
从多个开源数据源下载100张真实的石原氏色盲测试图
"""

import os
import requests
import json
import time
from pathlib import Path
import urllib3
from urllib.parse import urljoin, urlparse

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class RealIshiharaDownloader:
    def __init__(self, base_dir="data/raw"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.metadata = []
        
        # 设置requests会话
        self.session = requests.Session()
        self.session.verify = False  # 禁用SSL验证
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def download_from_multiple_sources(self):
        """从多个网络源下载真实的色盲测试图"""
        
        # 数据源1: Wikimedia Commons (完整的石原氏测试图集)
        wikimedia_urls = [
            "https://upload.wikimedia.org/wikipedia/commons/e/e0/Ishihara_9.png",
            "https://upload.wikimedia.org/wikipedia/commons/5/55/Colour_blindness_test.png", 
            "https://upload.wikimedia.org/wikipedia/commons/7/74/Ishihara_23.PNG",
            "https://upload.wikimedia.org/wikipedia/commons/a/a4/Ishihara_Plate_3.jpg",
        ]
        
        # 数据源2: 研究数据集URLs
        research_urls = [
            "http://web.archive.org/web/20201025062935/http://www.colour-blindness.com/wp-content/images/ishihara-1.jpg",
            "http://web.archive.org/web/20201025062935/http://www.colour-blindness.com/wp-content/images/ishihara-2.jpg",
            "http://web.archive.org/web/20201025062935/http://www.colour-blindness.com/wp-content/images/ishihara-3.jpg",
        ]
        
        # 数据源3: 医学教育网站
        medical_edu_urls = [
            "https://www.color-blindness.com/wp-content/images/plate1.jpg",
            "https://www.color-blindness.com/wp-content/images/plate2.jpg", 
            "https://www.color-blindness.com/wp-content/images/plate3.jpg",
        ]
        
        # 数据源4: 开源项目和数据集
        opensource_urls = [
            "https://raw.githubusercontent.com/topics/ishihara-test",
            "https://github.com/search?q=ishihara+plates&type=code",
        ]
        
        all_sources = [
            ("Wikimedia Commons", wikimedia_urls),
            ("Research Archive", research_urls), 
            ("Medical Education", medical_edu_urls),
        ]
        
        total_downloaded = 0
        
        for source_name, urls in all_sources:
            print(f"\n正在从 {source_name} 下载...")
            
            for i, url in enumerate(urls):
                if total_downloaded >= 100:
                    break
                    
                try:
                    print(f"  尝试下载: {url}")
                    response = self.session.get(url, timeout=30)
                    
                    if response.status_code == 200:
                        # 确定文件扩展名
                        content_type = response.headers.get('content-type', '')
                        if 'image' in content_type:
                            if 'png' in content_type:
                                ext = '.png'
                            elif 'jpeg' in content_type or 'jpg' in content_type:
                                ext = '.jpg'
                            else:
                                ext = '.jpg'  # 默认
                        else:
                            # 从URL推断
                            ext = '.png' if url.lower().endswith('.png') else '.jpg'
                        
                        filename = f"{source_name.lower().replace(' ', '_')}_{total_downloaded+1:03d}{ext}"
                        filepath = self.base_dir / filename
                        
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        
                        # 验证图像是否有效
                        try:
                            from PIL import Image
                            img = Image.open(filepath)
                            img.verify()  # 验证图像完整性
                            
                            self.metadata.append({
                                "filename": filename,
                                "source": source_name,
                                "url": url,
                                "type": "ishihara_real",
                                "file_size": len(response.content),
                                "content_type": content_type
                            })
                            
                            total_downloaded += 1
                            print(f"  ✓ 下载成功: {filename} ({len(response.content)} bytes)")
                            
                        except Exception as verify_error:
                            print(f"  ✗ 图像验证失败: {verify_error}")
                            filepath.unlink()  # 删除无效文件
                            
                    else:
                        print(f"  ✗ HTTP错误 {response.status_code}: {url}")
                        
                    time.sleep(1)  # 礼貌性延迟
                    
                except Exception as e:
                    print(f"  ✗ 下载失败: {e}")
                    
        return total_downloaded

    def search_additional_sources(self):
        """搜索并下载额外的色盲测试图源"""
        print("\n正在搜索额外的测试图源...")
        
        # 添加更多可能的数据源
        additional_sources = [
            # 眼科医学网站
            "https://www.aao.org/image/ishihara-color-test-plate-1",
            "https://www.aao.org/image/ishihara-color-test-plate-2", 
            
            # 色盲测试网站
            "https://enchroma.com/pages/test",
            "https://www.colour-blindness.com/colour-blindness-tests/ishihara-colour-blindness-test/",
            
            # 教育资源
            "https://www.nei.nih.gov/learn-about-eye-health/eye-conditions-and-diseases/color-blindness/color-blindness-tests",
        ]
        
        # 注意：这些URL可能需要特殊的网页抓取技术
        # 这里我们使用占位符，实际实现需要根据网站结构调整
        
        return 0

    def download_from_datasets(self):
        """从公开数据集下载"""
        print("\n正在从公开数据集下载...")
        
        # 公开数据集URL（需要实际验证）
        dataset_urls = [
            # 医学图像数据集
            "https://figshare.com/articles/dataset/Ishihara_Color_Blindness_Test_Images/12345",
            "https://www.kaggle.com/datasets/ishihara-color-blindness-test",
            
            # 学术研究数据
            "https://osf.io/ishihara-plates/",
            "https://zenodo.org/record/ishihara-test-images",
        ]
        
        # 注意：这些是示例URL，实际的数据集可能需要不同的下载方法
        downloaded = 0
        
        for url in dataset_urls:
            try:
                print(f"  尝试访问数据集: {url}")
                # 这里需要根据实际数据集的API或下载方式进行调整
                # 由于每个数据集的访问方式不同，这里暂时跳过
                pass
            except Exception as e:
                print(f"  ✗ 数据集访问失败: {e}")
        
        return downloaded

    def download_wiki_commons_systematically(self):
        """系统性地从Wikimedia Commons下载"""
        print("\n正在系统性地从Wikimedia Commons下载...")
        
        # 构建更全面的Wikimedia Commons URL列表
        base_url = "https://upload.wikimedia.org/wikipedia/commons"
        
        # 已知的石原氏测试图文件名模式
        known_patterns = [
            # 直接的石原氏测试图
            ("e/e0", "Ishihara_9.png"),
            ("5/55", "Colour_blindness_test.png"),
            ("7/74", "Ishihara_23.PNG"),
            ("a/a4", "Ishihara_Plate_3.jpg"),
            
            # 可能存在的其他石原氏测试图
            ("b/b1", "Ishihara_1.png"),
            ("c/c2", "Ishihara_2.png"),
            ("d/d3", "Ishihara_4.png"),
            ("e/e4", "Ishihara_5.png"),
            
            # 色盲相关的其他测试图
            ("f/f5", "Color_blindness_test_1.jpg"),
            ("a/a6", "Color_blindness_test_2.jpg"),
        ]
        
        downloaded = 0
        for path, filename in known_patterns:
            if len(self.metadata) >= 100:
                break
                
            url = f"{base_url}/{path}/{filename}"
            try:
                print(f"  尝试下载: {filename}")
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    filepath = self.base_dir / f"wikimedia_{downloaded+1:03d}_{filename}"
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    self.metadata.append({
                        "filename": filepath.name,
                        "source": "Wikimedia Commons Systematic",
                        "url": url,
                        "type": "ishihara_real",
                        "file_size": len(response.content)
                    })
                    
                    downloaded += 1
                    print(f"  ✓ 下载成功: {filepath.name}")
                    
                else:
                    print(f"  ✗ 文件不存在: {filename}")
                    
                time.sleep(1)
                
            except Exception as e:
                print(f"  ✗ 下载失败 {filename}: {e}")
                
        return downloaded

    def save_metadata(self, metadata_file="metadata/real_images_metadata.json"):
        """保存元数据"""
        metadata_path = Path(metadata_file)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump({
                "total_images": len(self.metadata),
                "download_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "target_count": 100,
                "success_rate": f"{len(self.metadata)}/100",
                "images": self.metadata
            }, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 元数据保存到: {metadata_path}")

    def run(self):
        """运行完整的下载流程"""
        print("=== 真实色盲测试图下载器 ===")
        print(f"目标: 下载100张真实的网络色盲测试图")
        print(f"目标目录: {self.base_dir}")
        
        total_downloaded = 0
        
        # 方法1: 从多个来源下载
        downloaded = self.download_from_multiple_sources()
        total_downloaded += downloaded
        print(f"第一阶段下载: {downloaded} 张")
        
        # 方法2: 系统性地从Wikimedia Commons下载
        if total_downloaded < 100:
            downloaded = self.download_wiki_commons_systematically()
            total_downloaded += downloaded
            print(f"第二阶段下载: {downloaded} 张")
        
        # 方法3: 搜索额外数据源
        if total_downloaded < 100:
            downloaded = self.search_additional_sources()
            total_downloaded += downloaded
            print(f"第三阶段下载: {downloaded} 张")
        
        # 方法4: 尝试公开数据集
        if total_downloaded < 100:
            downloaded = self.download_from_datasets()
            total_downloaded += downloaded
            print(f"第四阶段下载: {downloaded} 张")
        
        # 保存元数据
        self.save_metadata()
        
        print(f"\n=== 下载完成 ===")
        print(f"成功下载: {len(self.metadata)} 张真实网络图像")
        
        if len(self.metadata) >= 100:
            print("✓ 达到目标数量 (100张)")
        else:
            print(f"⚠ 未达到目标数量 ({len(self.metadata)}/100)")
            print("建议：")
            print("1. 检查网络连接")
            print("2. 尝试使用VPN")
            print("3. 手动搜索更多数据源")
            print("4. 联系色盲研究机构获取数据集")
        
        return len(self.metadata) >= 100


if __name__ == "__main__":
    downloader = RealIshiharaDownloader()
    downloader.run()