#!/usr/bin/env python3
"""
清理数据集中的空文件夹和不清晰的结构
"""

import os
import shutil
from pathlib import Path

def cleanup_empty_directories(base_path):
    """递归删除空目录"""
    removed_dirs = []
    
    def remove_empty_dirs(path):
        if not path.is_dir():
            return False
        
        # 先处理子目录
        subdirs = [p for p in path.iterdir() if p.is_dir()]
        for subdir in subdirs:
            if remove_empty_dirs(subdir):
                removed_dirs.append(str(subdir))
        
        # 检查当前目录是否为空
        try:
            contents = list(path.iterdir())
            if not contents:
                path.rmdir()
                return True
        except:
            pass
        
        return False
    
    remove_empty_dirs(Path(base_path))
    return removed_dirs

def analyze_dataset_structure(dataset_path):
    """分析数据集结构"""
    path = Path(dataset_path)
    if not path.exists():
        return None
    
    analysis = {
        "name": path.name,
        "total_files": 0,
        "image_files": 0,
        "empty_dirs": [],
        "large_dirs": [],
        "structure": {}
    }
    
    for root, dirs, files in os.walk(path):
        root_path = Path(root)
        level = len(root_path.relative_to(path).parts)
        
        # 统计文件
        analysis["total_files"] += len(files)
        image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        analysis["image_files"] += len(image_files)
        
        # 记录空目录
        if not files and not dirs:
            analysis["empty_dirs"].append(str(root_path.relative_to(path)))
        
        # 记录大目录（>100个文件）
        if len(files) > 100:
            analysis["large_dirs"].append({
                "path": str(root_path.relative_to(path)),
                "file_count": len(files),
                "image_count": len(image_files)
            })
    
    return analysis

def cleanup_vlm_benchmark():
    """清理VLM基准数据集"""
    print("🧹 清理VLM数据集结构")
    print("=" * 50)
    
    base_path = Path("/home/jgy")
    datasets_to_cleanup = [
        "VLM_Comprehensive_Benchmark",
        "Real_World_Noise_Dataset", 
        "Unified_Illusion_Dataset",
        "visual_boundary_dataset"
    ]
    
    cleanup_report = {
        "cleanup_summary": {},
        "recommendations": []
    }
    
    for dataset in datasets_to_cleanup:
        dataset_path = base_path / dataset
        if dataset_path.exists():
            print(f"\n📁 分析 {dataset}...")
            
            # 分析结构
            analysis = analyze_dataset_structure(dataset_path)
            if analysis:
                print(f"  📊 总文件: {analysis['total_files']}")
                print(f"  🖼️  图片: {analysis['image_files']}")
                print(f"  📂 空目录: {len(analysis['empty_dirs'])}")
                
                # 清理空目录
                removed = cleanup_empty_directories(dataset_path)
                if removed:
                    print(f"  🗑️  删除空目录: {len(removed)} 个")
                    for d in removed[:5]:  # 只显示前5个
                        print(f"     - {d}")
                    if len(removed) > 5:
                        print(f"     - ... 还有 {len(removed)-5} 个")
                
                cleanup_report["cleanup_summary"][dataset] = {
                    "total_files": analysis["total_files"],
                    "image_files": analysis["image_files"],
                    "empty_dirs_removed": len(removed),
                    "large_dirs": analysis["large_dirs"]
                }
                
                # 生成建议
                if analysis["empty_dirs"]:
                    cleanup_report["recommendations"].append(
                        f"{dataset}: 清理了 {len(analysis['empty_dirs'])} 个空目录"
                    )
    
    return cleanup_report

def organize_clear_structure():
    """重新组织为清晰的结构"""
    print("\n🏗️  重新组织数据集结构...")
    
    benchmark_path = Path("/home/jgy/VLM_Comprehensive_Benchmark")
    
    # 检查符号链接的有效性
    broken_links = []
    valid_links = []
    
    for link_path in benchmark_path.rglob("*"):
        if link_path.is_symlink():
            if not link_path.exists():
                broken_links.append(str(link_path))
            else:
                valid_links.append(str(link_path))
    
    print(f"  🔗 有效链接: {len(valid_links)}")
    print(f"  ❌ 损坏链接: {len(broken_links)}")
    
    # 删除损坏的链接
    for broken_link in broken_links:
        try:
            Path(broken_link).unlink()
            print(f"     删除损坏链接: {Path(broken_link).name}")
        except:
            pass
    
    return {
        "valid_links": len(valid_links),
        "broken_links_removed": len(broken_links)
    }

def generate_clean_summary():
    """生成清理后的总结"""
    print("\n📋 生成清理总结...")
    
    # 重新统计清理后的数据
    datasets = {
        "VLM_Comprehensive_Benchmark": "/home/jgy/VLM_Comprehensive_Benchmark",
        "Real_World_Noise_Dataset": "/home/jgy/Real_World_Noise_Dataset",
        "Unified_Illusion_Dataset": "/home/jgy/Unified_Illusion_Dataset",
        "visual_boundary_dataset": "/home/jgy/visual_boundary_dataset"
    }
    
    summary = {}
    
    for name, path in datasets.items():
        if Path(path).exists():
            analysis = analyze_dataset_structure(path)
            if analysis:
                summary[name] = {
                    "total_files": analysis["total_files"],
                    "image_files": analysis["image_files"],
                    "empty_dirs": len(analysis["empty_dirs"]),
                    "structure_clean": len(analysis["empty_dirs"]) == 0
                }
    
    # 保存清理报告
    import json
    with open("/home/jgy/dataset_cleanup_report.json", 'w') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    return summary

def main():
    print("🚀 开始VLM数据集清理")
    
    # 1. 清理空目录和无效结构
    cleanup_report = cleanup_vlm_benchmark()
    
    # 2. 整理符号链接
    link_report = organize_clear_structure()
    
    # 3. 生成清理后的总结
    final_summary = generate_clean_summary()
    
    print("\n" + "=" * 50)
    print("🎉 数据集清理完成！")
    print("=" * 50)
    
    total_images = sum(info.get("image_files", 0) for info in final_summary.values())
    clean_datasets = sum(1 for info in final_summary.values() if info.get("structure_clean", False))
    
    print(f"📊 总图片数: {total_images:,}")
    print(f"🧹 清理数据集: {clean_datasets}/{len(final_summary)}")
    print(f"🔗 有效链接: {link_report['valid_links']}")
    print(f"❌ 删除损坏链接: {link_report['broken_links_removed']}")
    
    print(f"\n📄 详细报告: /home/jgy/dataset_cleanup_report.json")

if __name__ == "__main__":
    main()