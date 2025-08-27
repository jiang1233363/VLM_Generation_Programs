#!/usr/bin/env python3
"""
色盲测试数据集生成脚本
整合下载、模拟和梯度生成的完整流程
"""

import os
import sys
import json
import time
from pathlib import Path
from PIL import Image
import numpy as np

# 添加当前目录到路径，以便导入其他模块
sys.path.append(str(Path(__file__).parent))

from download_ishihara_plates import IshiharaDownloader
from colorblind_simulation import ColorBlindnessSimulator, ColorBlindnessMetrics

class ColorBlindnessDatasetGenerator:
    def __init__(self, base_dir=".."):
        """初始化数据集生成器"""
        self.base_dir = Path(base_dir)
        self.raw_dir = self.base_dir / "data" / "raw"
        self.processed_dir = self.base_dir / "data" / "processed"
        self.gradients_dir = self.base_dir / "data" / "gradients"
        self.metadata_dir = self.base_dir / "metadata"
        
        # 创建目录
        for dir_path in [self.raw_dir, self.processed_dir, self.gradients_dir, self.metadata_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.downloader = IshiharaDownloader(str(self.raw_dir))
        self.simulator = ColorBlindnessSimulator()
        self.metrics = ColorBlindnessMetrics()
        
        # 色盲类型配置
        self.colorblind_types = ['protanopia', 'deuteranopia', 'tritanopia']
        self.gradient_steps = 100
    
    def step1_download_base_images(self):
        """步骤1: 下载基础图像"""
        print("=== 步骤1: 下载基础图像 ===")
        self.downloader.run()
        
        # 检查下载结果
        image_files = list(self.raw_dir.glob("*.png")) + list(self.raw_dir.glob("*.jpg"))
        print(f"获得 {len(image_files)} 张基础图像")
        return len(image_files) >= 100  # 必须要有100张真实网络图像
    
    def step2_generate_gradients(self):
        """步骤2: 为每张基础图像生成色盲模拟梯度"""
        print("=== 步骤2: 生成色盲模拟梯度 ===")
        
        # 获取所有基础图像
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp'}
        base_images = []
        
        for ext in image_extensions:
            base_images.extend(self.raw_dir.glob(f"*{ext}"))
        
        if not base_images:
            print("错误: 没有找到基础图像")
            return False
        
        print(f"找到 {len(base_images)} 张基础图像")
        
        total_generated = 0
        dataset_metadata = {
            "generation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_base_images": len(base_images),
            "colorblind_types": self.colorblind_types,
            "gradient_steps": self.gradient_steps,
            "images": []
        }
        
        for i, image_file in enumerate(base_images):
            print(f"\n处理图像 {i+1}/{len(base_images)}: {image_file.name}")
            
            try:
                # 加载并验证图像
                image = Image.open(image_file).convert('RGB')
                print(f"  图像尺寸: {image.size}")
                
                # 为每种色盲类型生成梯度
                image_metadata = {
                    "base_image": image_file.name,
                    "base_image_path": str(image_file),
                    "image_size": image.size,
                    "colorblind_variants": {}
                }
                
                for colorblind_type in self.colorblind_types:
                    print(f"  生成 {colorblind_type} 梯度...")
                    
                    # 创建输出目录
                    type_output_dir = self.gradients_dir / image_file.stem / colorblind_type
                    type_output_dir.mkdir(parents=True, exist_ok=True)
                    
                    # 生成梯度序列
                    generated_files = []
                    contrast_analyses = []
                    
                    for step in range(self.gradient_steps + 1):
                        severity = step / self.gradient_steps
                        
                        # 应用色盲模拟
                        sim_func = getattr(self.simulator, f'simulate_{colorblind_type}')
                        simulated_image = sim_func(image, severity)
                        
                        # 保存图像
                        filename = f"step_{step:03d}_severity_{severity:.2f}.png"
                        filepath = type_output_dir / filename
                        simulated_image.save(filepath)
                        generated_files.append(str(filepath))
                        
                        # 每10步分析一次对比度
                        if step % 10 == 0:
                            contrast_analysis = self.simulator.analyze_color_contrast(
                                image, colorblind_type, severity
                            )
                            contrast_analysis["step"] = step
                            contrast_analysis["filepath"] = str(filepath)
                            contrast_analyses.append(contrast_analysis)
                    
                    # 计算可见性阈值
                    try:
                        visibility_threshold = self.metrics.calculate_visibility_threshold(
                            image, colorblind_type
                        )
                    except Exception as e:
                        print(f"    警告: 无法计算可见性阈值: {e}")
                        visibility_threshold = None
                    
                    variant_metadata = {
                        "colorblind_type": colorblind_type,
                        "generated_files": generated_files,
                        "num_gradients": len(generated_files),
                        "contrast_analyses": contrast_analyses,
                        "visibility_threshold": visibility_threshold,
                        "output_directory": str(type_output_dir)
                    }
                    
                    image_metadata["colorblind_variants"][colorblind_type] = variant_metadata
                    total_generated += len(generated_files)
                    
                    print(f"    ✓ 生成了 {len(generated_files)} 个梯度文件")
                    if visibility_threshold is not None:
                        print(f"    可见性阈值: {visibility_threshold:.2f}")
                
                dataset_metadata["images"].append(image_metadata)
                
            except Exception as e:
                print(f"  ✗ 处理失败: {e}")
                continue
        
        # 保存数据集元数据
        metadata_file = self.metadata_dir / "complete_dataset.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(dataset_metadata, f, indent=2, ensure_ascii=False)
        
        # 生成数据集统计
        stats = self.generate_dataset_statistics(dataset_metadata)
        stats_file = self.metadata_dir / "dataset_statistics.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"\n=== 梯度生成完成 ===")
        print(f"总共生成: {total_generated} 张图像")
        print(f"元数据保存到: {metadata_file}")
        print(f"统计信息保存到: {stats_file}")
        
        return total_generated > 0
    
    def generate_dataset_statistics(self, metadata):
        """生成数据集统计信息"""
        stats = {
            "dataset_overview": {
                "total_base_images": metadata["total_base_images"],
                "total_gradient_images": 0,
                "colorblind_types": metadata["colorblind_types"],
                "gradient_steps": metadata["gradient_steps"]
            },
            "images_per_type": {},
            "visibility_thresholds": {},
            "contrast_analysis_summary": {}
        }
        
        # 统计每种色盲类型的图像数量
        for cb_type in self.colorblind_types:
            stats["images_per_type"][cb_type] = 0
            stats["visibility_thresholds"][cb_type] = []
            stats["contrast_analysis_summary"][cb_type] = {
                "avg_color_difference": [],
                "avg_contrast_change": []
            }
        
        # 遍历所有图像计算统计
        for image_meta in metadata["images"]:
            for cb_type, variant_meta in image_meta["colorblind_variants"].items():
                # 图像数量
                stats["images_per_type"][cb_type] += variant_meta["num_gradients"]
                stats["dataset_overview"]["total_gradient_images"] += variant_meta["num_gradients"]
                
                # 可见性阈值
                if variant_meta["visibility_threshold"] is not None:
                    stats["visibility_thresholds"][cb_type].append(
                        variant_meta["visibility_threshold"]
                    )
                
                # 对比度分析
                for analysis in variant_meta["contrast_analyses"]:
                    stats["contrast_analysis_summary"][cb_type]["avg_color_difference"].append(
                        analysis["color_difference"]
                    )
                    stats["contrast_analysis_summary"][cb_type]["avg_contrast_change"].append(
                        analysis["contrast_change"]
                    )
        
        # 计算平均值
        for cb_type in self.colorblind_types:
            if stats["visibility_thresholds"][cb_type]:
                stats["visibility_thresholds"][cb_type] = {
                    "mean": np.mean(stats["visibility_thresholds"][cb_type]),
                    "std": np.std(stats["visibility_thresholds"][cb_type]),
                    "min": np.min(stats["visibility_thresholds"][cb_type]),
                    "max": np.max(stats["visibility_thresholds"][cb_type])
                }
            
            summary = stats["contrast_analysis_summary"][cb_type]
            if summary["avg_color_difference"]:
                summary["avg_color_difference"] = {
                    "mean": np.mean(summary["avg_color_difference"]),
                    "std": np.std(summary["avg_color_difference"])
                }
            if summary["avg_contrast_change"]:
                summary["avg_contrast_change"] = {
                    "mean": np.mean(summary["avg_contrast_change"]),
                    "std": np.std(summary["avg_contrast_change"])
                }
        
        return stats
    
    def step3_create_test_cases(self):
        """步骤3: 创建测试用例描述"""
        print("=== 步骤3: 创建测试用例描述 ===")
        
        test_cases = []
        
        # 读取数据集元数据
        metadata_file = self.metadata_dir / "complete_dataset.json"
        if not metadata_file.exists():
            print("错误: 找不到数据集元数据文件")
            return False
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            dataset_metadata = json.load(f)
        
        # 为每个基础图像创建测试用例
        for image_meta in dataset_metadata["images"]:
            base_image = image_meta["base_image"]
            
            # 确定期望的答案（基于文件名或元数据）
            expected_answer = self.extract_expected_answer(base_image)
            
            for cb_type, variant_meta in image_meta["colorblind_variants"].items():
                # 创建测试序列
                test_sequence = {
                    "test_id": f"{Path(base_image).stem}_{cb_type}",
                    "base_image": base_image,
                    "colorblind_type": cb_type,
                    "expected_answer": expected_answer,
                    "test_description": f"测试模型在{cb_type}模拟下识别{expected_answer}的能力",
                    "gradient_files": variant_meta["generated_files"],
                    "num_gradients": variant_meta["num_gradients"],
                    "visibility_threshold": variant_meta["visibility_threshold"],
                    "test_questions": []
                }
                
                # 为关键梯度点创建测试问题
                key_steps = [0, 25, 50, 75, 100]  # 关键测试点
                for step in key_steps:
                    if step < len(variant_meta["generated_files"]):
                        severity = step / 100.0
                        test_question = {
                            "step": step,
                            "severity": severity,
                            "image_path": variant_meta["generated_files"][step],
                            "question": f"这张图中显示的是什么数字或符号？",
                            "expected_answer": expected_answer,
                            "difficulty_level": self.assess_difficulty_level(severity, variant_meta["visibility_threshold"])
                        }
                        test_sequence["test_questions"].append(test_question)
                
                test_cases.append(test_sequence)
        
        # 保存测试用例
        test_cases_file = self.metadata_dir / "test_cases.json"
        with open(test_cases_file, 'w', encoding='utf-8') as f:
            json.dump({
                "total_test_sequences": len(test_cases),
                "creation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "test_sequences": test_cases
            }, f, indent=2, ensure_ascii=False)
        
        print(f"创建了 {len(test_cases)} 个测试序列")
        print(f"测试用例保存到: {test_cases_file}")
        return True
    
    def extract_expected_answer(self, filename):
        """从文件名提取期望答案"""
        filename_lower = filename.lower()
        
        # 检查文件名中的数字
        import re
        numbers = re.findall(r'\d+', filename)
        if numbers:
            return numbers[0]
        
        # 检查文件名中的关键词
        if 'circle' in filename_lower:
            return 'circle'
        elif 'square' in filename_lower:
            return 'square'
        elif 'triangle' in filename_lower:
            return 'triangle'
        
        return 'unknown'
    
    def assess_difficulty_level(self, severity, visibility_threshold):
        """评估测试难度级别"""
        if visibility_threshold is None:
            return "unknown"
        
        if severity < visibility_threshold * 0.5:
            return "easy"
        elif severity < visibility_threshold:
            return "medium"
        elif severity < visibility_threshold * 1.5:
            return "hard"
        else:
            return "very_hard"
    
    def generate_readme(self):
        """生成数据集说明文档"""
        readme_content = f"""# 色盲测试数据集

## 概述
这是一个用于评估AI模型色彩视觉能力的综合色盲测试数据集。数据集包含石原氏色盲测试图的多个变体，模拟不同类型和严重程度的色盲状况。

## 数据集结构
```
colorblindness/
├── data/
│   ├── raw/                    # 原始基础图像
│   ├── processed/             # 处理后的图像
│   └── gradients/             # 色盲模拟梯度图像
│       └── [image_name]/
│           ├── protanopia/    # 红色盲模拟 (101张图像, 0%-100%严重程度)
│           ├── deuteranopia/  # 绿色盲模拟 (101张图像, 0%-100%严重程度)  
│           └── tritanopia/    # 蓝色盲模拟 (101张图像, 0%-100%严重程度)
├── metadata/
│   ├── complete_dataset.json     # 完整数据集元数据
│   ├── dataset_statistics.json   # 数据集统计信息
│   └── test_cases.json          # 测试用例定义
├── scripts/
│   ├── download_ishihara_plates.py    # 图像下载脚本
│   ├── colorblind_simulation.py       # 色盲模拟算法
│   └── generate_dataset.py            # 数据集生成主脚本
└── docs/
    └── README.md                       # 本文档
```

## 色盲类型
- **Protanopia (红色盲)**: 无法感知红光
- **Deuteranopia (绿色盲)**: 无法感知绿光  
- **Tritanopia (蓝色盲)**: 无法感知蓝光

## 梯度生成
每个基础图像都会生成101个不同严重程度的色盲模拟版本：
- 步骤 0: 正常视力 (0% 色盲模拟)
- 步骤 1-99: 渐进色盲模拟 (1%-99% 严重程度)
- 步骤 100: 完全色盲模拟 (100% 严重程度)

## 使用方法
1. 运行 `python generate_dataset.py` 生成完整数据集
2. 查看 `metadata/test_cases.json` 了解测试用例
3. 使用 `metadata/dataset_statistics.json` 了解数据集统计信息

## 评测指标
- **可见性阈值**: 目标变得不可见的色盲严重程度
- **颜色对比度变化**: 模拟前后的颜色对比度差异
- **识别准确率**: 模型在不同严重程度下的识别准确率

## 数据集特点
- 高质量的石原氏色盲测试图
- 精确的色盲模拟算法
- 渐进式测试难度
- 详细的元数据和统计信息
- 多种色盲类型支持

生成时间: {time.strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        docs_dir = self.base_dir / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        readme_file = docs_dir / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"README文档保存到: {readme_file}")
    
    def run_complete_generation(self):
        """运行完整的数据集生成流程"""
        print("=== 色盲测试数据集生成器 ===")
        print(f"工作目录: {self.base_dir.absolute()}")
        
        start_time = time.time()
        
        try:
            # 步骤1: 下载基础图像
            if not self.step1_download_base_images():
                print("错误: 基础图像下载失败")
                return False
            
            # 步骤2: 生成梯度
            if not self.step2_generate_gradients():
                print("错误: 梯度生成失败")
                return False
            
            # 步骤3: 创建测试用例
            if not self.step3_create_test_cases():
                print("错误: 测试用例创建失败")
                return False
            
            # 生成文档
            self.generate_readme()
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"\n=== 数据集生成完成 ===")
            print(f"总耗时: {duration:.2f} 秒")
            print(f"数据集位置: {self.base_dir.absolute()}")
            
            # 最终统计
            self.print_final_statistics()
            
            return True
            
        except Exception as e:
            print(f"数据集生成过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def print_final_statistics(self):
        """打印最终统计信息"""
        try:
            stats_file = self.metadata_dir / "dataset_statistics.json"
            if stats_file.exists():
                with open(stats_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
                
                overview = stats["dataset_overview"]
                print(f"\n数据集统计:")
                print(f"- 基础图像: {overview['total_base_images']} 张")
                print(f"- 梯度图像: {overview['total_gradient_images']} 张")
                print(f"- 色盲类型: {', '.join(overview['colorblind_types'])}")
                print(f"- 梯度步数: {overview['gradient_steps']}")
                
                print(f"\n各类型图像数量:")
                for cb_type, count in stats["images_per_type"].items():
                    print(f"- {cb_type}: {count} 张")
                    
        except Exception as e:
            print(f"无法打印统计信息: {e}")


if __name__ == "__main__":
    # 创建生成器并运行
    generator = ColorBlindnessDatasetGenerator()
    success = generator.run_complete_generation()
    
    if success:
        print("\n🎉 数据集生成成功!")
    else:
        print("\n❌ 数据集生成失败!")
        sys.exit(1)