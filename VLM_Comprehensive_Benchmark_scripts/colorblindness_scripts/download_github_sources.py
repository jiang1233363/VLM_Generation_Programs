#!/usr/bin/env python3
"""
从GitHub仓库下载色盲测试图像
"""

import requests
import json
import time
from pathlib import Path
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class GitHubIshiharaDownloader:
    def __init__(self, base_dir="data/raw"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.metadata = []
        
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_github_repo_files(self, repo_url, target_extensions=None):
        """获取GitHub仓库中的文件列表"""
        if target_extensions is None:
            target_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
        
        # 将GitHub页面URL转换为API URL
        if 'github.com' in repo_url:
            parts = repo_url.replace('https://github.com/', '').split('/')
            if len(parts) >= 2:
                owner, repo = parts[0], parts[1]
                api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
                
                try:
                    response = self.session.get(api_url, timeout=30)
                    if response.status_code == 200:
                        files = response.json()
                        image_files = []
                        
                        for file_info in files:
                            if file_info['type'] == 'file':
                                file_name = file_info['name']
                                file_ext = Path(file_name).suffix.lower()
                                if file_ext in target_extensions:
                                    image_files.append({
                                        'name': file_name,
                                        'download_url': file_info['download_url'],
                                        'size': file_info['size']
                                    })
                        
                        return image_files
                        
                except Exception as e:
                    print(f"获取仓库文件列表失败: {e}")
                    
        return []

    def get_github_subdirectory_files(self, repo_url, subdirectory, target_extensions=None):
        """获取GitHub仓库子目录中的文件"""
        if target_extensions is None:
            target_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
        
        if 'github.com' in repo_url:
            parts = repo_url.replace('https://github.com/', '').split('/')
            if len(parts) >= 2:
                owner, repo = parts[0], parts[1]
                api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{subdirectory}"
                
                try:
                    response = self.session.get(api_url, timeout=30)
                    if response.status_code == 200:
                        files = response.json()
                        image_files = []
                        
                        for file_info in files:
                            if file_info['type'] == 'file':
                                file_name = file_info['name']
                                file_ext = Path(file_name).suffix.lower()
                                if file_ext in target_extensions:
                                    image_files.append({
                                        'name': file_name,
                                        'download_url': file_info['download_url'],
                                        'size': file_info['size'],
                                        'path': file_info['path']
                                    })
                        
                        return image_files
                        
                except Exception as e:
                    print(f"获取子目录文件列表失败: {e}")
                    
        return []

    def download_from_ishihara_plate_learning(self):
        """从ishihara-plate-learning仓库下载图像"""
        print("正在从ishihara-plate-learning仓库下载...")
        
        repo_url = "https://github.com/DJakarta/ishihara-plate-learning"
        downloaded = 0
        
        # 尝试从可能的图像目录下载
        possible_dirs = ['imgs', 'images', 'plates', 'assets', 'src']
        
        for dir_name in possible_dirs:
            files = self.get_github_subdirectory_files(repo_url, dir_name)
            if files:
                print(f"  在 {dir_name} 目录发现 {len(files)} 个图像文件")
                
                for file_info in files:
                    if downloaded >= 38:  # 石原氏标准测试图有38张
                        break
                        
                    try:
                        response = self.session.get(file_info['download_url'], timeout=30)
                        if response.status_code == 200:
                            filename = f"github_learning_{downloaded+1:02d}_{file_info['name']}"
                            filepath = self.base_dir / filename
                            
                            with open(filepath, 'wb') as f:
                                f.write(response.content)
                            
                            self.metadata.append({
                                "filename": filename,
                                "source": "GitHub ishihara-plate-learning",
                                "url": file_info['download_url'],
                                "original_name": file_info['name'],
                                "type": "ishihara_real",
                                "file_size": len(response.content)
                            })
                            
                            downloaded += 1
                            print(f"  ✓ 下载成功: {filename}")
                            time.sleep(0.5)
                            
                    except Exception as e:
                        print(f"  ✗ 下载失败 {file_info['name']}: {e}")
        
        return downloaded

    def download_from_icfaust_ishihara(self):
        """从IshiharaMC仓库下载Monte Carlo生成的图像"""
        print("正在从IshiharaMC仓库下载...")
        
        repo_url = "https://github.com/icfaust/IshiharaMC"
        downloaded = 0
        
        # 检查根目录和可能的子目录
        possible_dirs = ['', 'images', 'examples', 'output']
        
        for dir_name in possible_dirs:
            if dir_name:
                files = self.get_github_subdirectory_files(repo_url, dir_name)
            else:
                files = self.get_github_repo_files(repo_url)
                
            if files:
                print(f"  在 {dir_name or '根目录'} 发现 {len(files)} 个图像文件")
                
                for file_info in files:
                    try:
                        response = self.session.get(file_info['download_url'], timeout=30)
                        if response.status_code == 200:
                            filename = f"github_mc_{downloaded+1:02d}_{file_info['name']}"
                            filepath = self.base_dir / filename
                            
                            with open(filepath, 'wb') as f:
                                f.write(response.content)
                            
                            self.metadata.append({
                                "filename": filename,
                                "source": "GitHub IshiharaMC",
                                "url": file_info['download_url'],
                                "original_name": file_info['name'],
                                "type": "ishihara_monte_carlo",
                                "file_size": len(response.content)
                            })
                            
                            downloaded += 1
                            print(f"  ✓ 下载成功: {filename}")
                            time.sleep(0.5)
                            
                    except Exception as e:
                        print(f"  ✗ 下载失败 {file_info['name']}: {e}")
        
        return downloaded

    def download_from_color_blindness_toolkit(self):
        """从Color_Blindness_Toolkit仓库下载"""
        print("正在从Color_Blindness_Toolkit仓库下载...")
        
        repo_url = "https://github.com/bhav09/Color_Blindness_Toolkit"
        downloaded = 0
        
        possible_dirs = ['', 'images', 'data', 'assets', 'samples']
        
        for dir_name in possible_dirs:
            if dir_name:
                files = self.get_github_subdirectory_files(repo_url, dir_name)
            else:
                files = self.get_github_repo_files(repo_url)
                
            if files:
                print(f"  在 {dir_name or '根目录'} 发现 {len(files)} 个图像文件")
                
                for file_info in files:
                    try:
                        response = self.session.get(file_info['download_url'], timeout=30)
                        if response.status_code == 200:
                            filename = f"github_toolkit_{downloaded+1:02d}_{file_info['name']}"
                            filepath = self.base_dir / filename
                            
                            with open(filepath, 'wb') as f:
                                f.write(response.content)
                            
                            self.metadata.append({
                                "filename": filename,
                                "source": "GitHub Color_Blindness_Toolkit",
                                "url": file_info['download_url'],
                                "original_name": file_info['name'],
                                "type": "ishihara_toolkit",
                                "file_size": len(response.content)
                            })
                            
                            downloaded += 1
                            print(f"  ✓ 下载成功: {filename}")
                            time.sleep(0.5)
                            
                    except Exception as e:
                        print(f"  ✗ 下载失败 {file_info['name']}: {e}")
        
        return downloaded

    def download_from_njtierney_ishihara(self):
        """从njtierney/ishihara R包仓库下载示例图像"""
        print("正在从njtierney/ishihara仓库下载...")
        
        repo_url = "https://github.com/njtierney/ishihara"
        downloaded = 0
        
        possible_dirs = ['', 'inst', 'examples', 'man/figures', 'vignettes']
        
        for dir_name in possible_dirs:
            if dir_name:
                files = self.get_github_subdirectory_files(repo_url, dir_name)
            else:
                files = self.get_github_repo_files(repo_url)
                
            if files:
                print(f"  在 {dir_name or '根目录'} 发现 {len(files)} 个图像文件")
                
                for file_info in files:
                    try:
                        response = self.session.get(file_info['download_url'], timeout=30)
                        if response.status_code == 200:
                            filename = f"github_r_{downloaded+1:02d}_{file_info['name']}"
                            filepath = self.base_dir / filename
                            
                            with open(filepath, 'wb') as f:
                                f.write(response.content)
                            
                            self.metadata.append({
                                "filename": filename,
                                "source": "GitHub njtierney/ishihara",
                                "url": file_info['download_url'],
                                "original_name": file_info['name'],
                                "type": "ishihara_r_generated",
                                "file_size": len(response.content)
                            })
                            
                            downloaded += 1
                            print(f"  ✓ 下载成功: {filename}")
                            time.sleep(0.5)
                            
                    except Exception as e:
                        print(f"  ✗ 下载失败 {file_info['name']}: {e}")
        
        return downloaded

    def save_metadata(self, metadata_file="metadata/github_images_metadata.json"):
        """保存元数据"""
        metadata_path = Path(metadata_file)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump({
                "total_images": len(self.metadata),
                "download_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "source": "GitHub Repositories",
                "images": self.metadata
            }, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 元数据保存到: {metadata_path}")

    def run(self):
        """运行完整的GitHub下载流程"""
        print("=== GitHub色盲测试图下载器 ===")
        print("从GitHub开源仓库下载真实的色盲测试图...")
        
        total_downloaded = 0
        
        # 从各个GitHub仓库下载
        repositories = [
            ("ishihara-plate-learning", self.download_from_ishihara_plate_learning),
            ("IshiharaMC", self.download_from_icfaust_ishihara),
            ("Color_Blindness_Toolkit", self.download_from_color_blindness_toolkit),
            ("njtierney/ishihara", self.download_from_njtierney_ishihara),
        ]
        
        for repo_name, download_func in repositories:
            print(f"\n--- {repo_name} ---")
            try:
                downloaded = download_func()
                total_downloaded += downloaded
                print(f"从 {repo_name} 下载了 {downloaded} 张图像")
            except Exception as e:
                print(f"从 {repo_name} 下载失败: {e}")
        
        # 保存元数据
        self.save_metadata()
        
        print(f"\n=== GitHub下载完成 ===")
        print(f"总共下载: {len(self.metadata)} 张图像")
        print(f"目标进度: {len(self.metadata)}/100")
        
        if len(self.metadata) >= 100:
            print("✓ 达到目标数量!")
        else:
            print(f"还需要: {100 - len(self.metadata)} 张图像")
        
        return len(self.metadata)


if __name__ == "__main__":
    downloader = GitHubIshiharaDownloader()
    total_images = downloader.run()