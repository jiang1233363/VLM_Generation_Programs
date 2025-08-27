#!/usr/bin/env python3
"""
VLM Benchmark 数据集整理脚本
按照Subject、Relation、Attribute、Illusion四大类别整理现有数据
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

class VLMBenchmarkOrganizer:
    def __init__(self):
        self.base_path = Path("/home/jgy")
        self.output_path = Path("/home/jgy/VLM_Comprehensive_Benchmark")
        
        # 数据集分类映射
        self.dataset_mapping = {
            "Subject": {
                "description": "VLM对图像中单个或多个独立主体的识别、感知和属性理解能力",
                "subcategories": {
                    "clarity_degradation": "清晰度退化感知",
                    "brightness_variation": "亮度变化感知", 
                    "contrast_variation": "对比度变化感知",
                    "color_distortion": "颜色失真感知",
                    "color_shift": "色偏识别",
                    "fine_grained_classification": "细粒度主体分类",
                    "colorblind_recognition": "色盲识别",
                    "resolution_variation": "分辨率变化"
                },
                "source_datasets": [
                    "/home/jgy/Real_World_Noise_Dataset",
                    "/home/jgy/visual_boundary_dataset"
                ]
            },
            "Relation": {
                "description": "VLM对图像中多个主体之间空间、时间、因果和逻辑关系的理解能力",
                "subcategories": {
                    "spatial_relations": "空间位置关系",
                    "proximity_relations": "距离/靠近关系",
                    "alignment_relations": "对齐/方向关系", 
                    "comparative_relations": "比较关系"
                },
                "source_datasets": []
            },
            "Attribute": {
                "description": "VLM对图像属性的感知和理解能力",
                "subcategories": {
                    "global_noise": "图像整体加噪声",
                    "pixel_manipulation": "像素点操作"
                },
                "source_datasets": [
                    "/home/jgy/Real_World_Noise_Dataset"
                ]
            },
            "Illusion": {
                "description": "VLM对视觉错觉的感知和理解能力",
                "subcategories": {
                    "geometric_illusions": "几何错觉",
                    "color_illusions": "色彩错觉",
                    "motion_illusions": "运动错觉",
                    "ambiguous_figures": "模糊图形"
                },
                "source_datasets": [
                    "/home/jgy/Unified_Illusion_Dataset"
                ]
            }
        }
        
        # 初始化目录
        self.setup_directories()

    def setup_directories(self):
        """创建输出目录结构"""
        self.output_path.mkdir(exist_ok=True)
        
        # 为四大类别创建目录
        for category in self.dataset_mapping.keys():
            category_path = self.output_path / category
            category_path.mkdir(exist_ok=True)
            
            # 为子类别创建目录
            subcategories = self.dataset_mapping[category]["subcategories"]
            for subcat_key, subcat_name in subcategories.items():
                subcat_path = category_path / subcat_key
                subcat_path.mkdir(exist_ok=True)

    def analyze_existing_datasets(self):
        """分析现有数据集"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "categories": {}
        }
        
        for category, info in self.dataset_mapping.items():
            category_analysis = {
                "description": info["description"],
                "subcategories": info["subcategories"],
                "datasets": []
            }
            
            for dataset_path in info["source_datasets"]:
                if Path(dataset_path).exists():
                    dataset_info = self.analyze_dataset(dataset_path)
                    category_analysis["datasets"].append(dataset_info)
            
            analysis["categories"][category] = category_analysis
        
        return analysis

    def analyze_dataset(self, dataset_path):
        """分析单个数据集"""
        path = Path(dataset_path)
        
        # 统计文件数量
        total_images = 0
        total_dirs = 0
        
        for ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
            total_images += len(list(path.glob(f"**/*{ext}")))
        
        total_dirs = len([d for d in path.glob("**/*") if d.is_dir()])
        
        return {
            "path": str(path),
            "name": path.name,
            "total_images": total_images,
            "total_directories": total_dirs,
            "size_mb": self.get_directory_size(path)
        }

    def get_directory_size(self, path):
        """获取目录大小（MB）"""
        try:
            total = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total += os.path.getsize(filepath)
            return round(total / (1024 * 1024), 2)
        except:
            return 0

    def organize_subject_data(self):
        """整理Subject类别数据"""
        print("🎯 整理Subject类别数据...")
        
        subject_path = self.output_path / "Subject"
        
        # 1. 处理Real_World_Noise_Dataset - 对应多个Subject子类别
        noise_dataset = self.base_path / "Real_World_Noise_Dataset"
        if noise_dataset.exists():
            # 噪声梯度 -> 清晰度退化
            if (noise_dataset / "noise_gradients").exists():
                clarity_path = subject_path / "clarity_degradation"
                self.copy_with_symlink(noise_dataset / "noise_gradients", 
                                     clarity_path / "noise_gradients")
            
            # 模糊梯度 -> 清晰度退化  
            if (noise_dataset / "blur_gradients").exists():
                clarity_path = subject_path / "clarity_degradation"
                self.copy_with_symlink(noise_dataset / "blur_gradients",
                                     clarity_path / "blur_gradients")
            
            # 亮度变化
            if (noise_dataset / "brightness_variation").exists():
                brightness_path = subject_path / "brightness_variation"
                self.copy_with_symlink(noise_dataset / "brightness_variation",
                                     brightness_path / "brightness_data")
            
            # 对比度变化
            if (noise_dataset / "contrast_variation").exists():
                contrast_path = subject_path / "contrast_variation" 
                self.copy_with_symlink(noise_dataset / "contrast_variation",
                                     contrast_path / "contrast_data")
            
            # 色彩变化
            if (noise_dataset / "color_shift").exists():
                color_path = subject_path / "color_shift"
                self.copy_with_symlink(noise_dataset / "color_shift",
                                     color_path / "color_shift_data")

        # 2. 处理visual_boundary_dataset
        boundary_dataset = self.base_path / "visual_boundary_dataset"
        if boundary_dataset.exists():
            # 原始多样化图片 -> 细粒度分类
            if (boundary_dataset / "downloaded_images").exists():
                fine_grained_path = subject_path / "fine_grained_classification"
                self.copy_with_symlink(boundary_dataset / "downloaded_images",
                                     fine_grained_path / "diverse_images")
            
            # 退化图片 -> 各种感知任务
            if (boundary_dataset / "degraded_images").exists():
                brightness_path = subject_path / "brightness_variation"
                self.copy_with_symlink(boundary_dataset / "degraded_images",
                                     brightness_path / "degraded_images")

        print("✅ Subject类别数据整理完成")

    def organize_relation_data(self):
        """整理Relation类别数据"""
        print("🔗 整理Relation类别数据...")
        
        relation_path = self.output_path / "Relation"
        
        # 创建占位符文件说明需要的数据
        for subcat_key, subcat_name in self.dataset_mapping["Relation"]["subcategories"].items():
            subcat_path = relation_path / subcat_key
            placeholder_file = subcat_path / "README.md"
            
            content = f"""# {subcat_name}

## 数据需求说明
- **目标**: {subcat_name}评估数据
- **状态**: 待收集/生成
- **建议数据源**: 
  - Blender生成的3D场景
  - SVG几何图形
  - 手工标注的关系数据

## 数据格式要求
- 图片格式: PNG/JPG
- 标注格式: JSON
- 关系类型: 空间位置、距离、方向、比较等
"""
            
            with open(placeholder_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print("✅ Relation类别框架创建完成（需要后续数据收集）")

    def organize_attribute_data(self):
        """整理Attribute类别数据"""
        print("🎨 整理Attribute类别数据...")
        
        attribute_path = self.output_path / "Attribute"
        
        # Real_World_Noise_Dataset 的噪声和像素操作数据
        noise_dataset = self.base_path / "Real_World_Noise_Dataset"
        if noise_dataset.exists():
            # 全局噪声
            if (noise_dataset / "gaussian_noise").exists():
                global_noise_path = attribute_path / "global_noise"
                self.copy_with_symlink(noise_dataset / "gaussian_noise",
                                     global_noise_path / "gaussian_noise")
            
            if (noise_dataset / "salt_pepper_noise").exists():
                global_noise_path = attribute_path / "global_noise"
                self.copy_with_symlink(noise_dataset / "salt_pepper_noise",
                                     global_noise_path / "salt_pepper_noise")
            
            # 像素操作
            if (noise_dataset / "pixel_gradients").exists():
                pixel_path = attribute_path / "pixel_manipulation"
                self.copy_with_symlink(noise_dataset / "pixel_gradients",
                                     pixel_path / "pixelization")
            
            if (noise_dataset / "pixelation").exists():
                pixel_path = attribute_path / "pixel_manipulation"
                self.copy_with_symlink(noise_dataset / "pixelation",
                                     pixel_path / "pixelation_effects")

        print("✅ Attribute类别数据整理完成")

    def organize_illusion_data(self):
        """整理Illusion类别数据"""
        print("👁️ 整理Illusion类别数据...")
        
        illusion_path = self.output_path / "Illusion"
        
        # Unified_Illusion_Dataset 包含所有错觉数据
        illusion_dataset = self.base_path / "Unified_Illusion_Dataset"
        if illusion_dataset.exists():
            # 合成错觉数据
            if (illusion_dataset / "Synthetic_Illusions").exists():
                synthetic_path = illusion_dataset / "Synthetic_Illusions"
                
                # 几何错觉
                geometric_illusion_path = illusion_path / "geometric_illusions"
                self.copy_with_symlink(synthetic_path / "Geometric_Length_Illusions",
                                     geometric_illusion_path / "geometric_length")
                self.copy_with_symlink(synthetic_path / "Ambiguous_Figures_Illusions", 
                                     geometric_illusion_path / "ambiguous_figures")
                
                # 色彩错觉
                color_illusion_path = illusion_path / "color_illusions"
                self.copy_with_symlink(synthetic_path / "Color_Brightness_Illusions",
                                     color_illusion_path / "color_brightness")
                
                # 运动错觉
                motion_illusion_path = illusion_path / "motion_illusions"
                self.copy_with_symlink(synthetic_path / "Grid_Motion_Illusions",
                                     motion_illusion_path / "grid_motion")
                
                # 其他错觉
                misc_illusion_path = illusion_path / "ambiguous_figures"
                self.copy_with_symlink(synthetic_path / "Miscellaneous_Illusions",
                                     misc_illusion_path / "miscellaneous")
            
            # 研究数据集
            if (illusion_dataset / "IllusionBench_Research_Dataset").exists():
                research_path = illusion_path / "research_benchmark"
                self.copy_with_symlink(illusion_dataset / "IllusionBench_Research_Dataset",
                                     research_path / "illusionbench_data")

        print("✅ Illusion类别数据整理完成")

    def copy_with_symlink(self, source, target):
        """使用符号链接复制数据（节省空间）"""
        try:
            if source.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists():
                    # 创建符号链接而不是复制文件
                    target.symlink_to(source.resolve())
                    print(f"  📎 链接: {source.name} -> {target}")
        except Exception as e:
            print(f"  ❌ 链接失败: {source} -> {target}, 错误: {e}")

    def generate_comprehensive_readme(self):
        """生成综合README文档"""
        analysis = self.analyze_existing_datasets()
        
        readme_content = f"""# VLM Comprehensive Benchmark Dataset

## 🎯 数据集概述

这是一个面向视觉语言模型(VLM)的综合性基准测试数据集，按照四大核心能力维度组织：**Subject（主体感知）**、**Relation（关系理解）**、**Attribute（属性感知）**、**Illusion（错觉感知）**。

### 📊 数据集统计

生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

"""
        
        for category, info in analysis["categories"].items():
            readme_content += f"""
## {category} - {info["description"]}

### 子类别：
"""
            for subcat_key, subcat_name in info["subcategories"].items():
                readme_content += f"- **{subcat_key}**: {subcat_name}\n"
            
            if info["datasets"]:
                readme_content += f"\n### 包含数据集：\n"
                for dataset in info["datasets"]:
                    readme_content += f"""
- **{dataset["name"]}**
  - 图片数量: {dataset["total_images"]:,}
  - 目录数量: {dataset["total_directories"]}
  - 数据大小: {dataset["size_mb"]} MB
"""

        readme_content += f"""

## 📁 目录结构

```
VLM_Comprehensive_Benchmark/
├── Subject/                    # 主体感知能力评估
│   ├── clarity_degradation/    # 清晰度退化感知
│   ├── brightness_variation/   # 亮度变化感知
│   ├── contrast_variation/     # 对比度变化感知
│   ├── color_distortion/       # 颜色失真感知
│   ├── color_shift/           # 色偏识别
│   ├── fine_grained_classification/  # 细粒度主体分类
│   ├── colorblind_recognition/ # 色盲识别
│   └── resolution_variation/   # 分辨率变化
│
├── Relation/                   # 关系理解能力评估
│   ├── spatial_relations/      # 空间位置关系
│   ├── proximity_relations/    # 距离/靠近关系
│   ├── alignment_relations/    # 对齐/方向关系
│   └── comparative_relations/  # 比较关系
│
├── Attribute/                  # 属性感知能力评估
│   ├── global_noise/          # 图像整体加噪声
│   └── pixel_manipulation/    # 像素点操作
│
├── Illusion/                   # 错觉感知能力评估
│   ├── geometric_illusions/    # 几何错觉
│   ├── color_illusions/       # 色彩错觉
│   ├── motion_illusions/      # 运动错觉
│   └── ambiguous_figures/     # 模糊图形
│
├── README.md                   # 本文档
├── dataset_analysis.json      # 数据集分析报告
└── organize_benchmark.py      # 数据整理脚本
```

## 🚀 使用方法

### 数据加载
```python
from pathlib import Path
import json

# 加载数据集
benchmark_path = Path("VLM_Comprehensive_Benchmark")

# 加载Subject类别数据
subject_data = benchmark_path / "Subject"
clarity_data = subject_data / "clarity_degradation"

# 加载Illusion类别数据  
illusion_data = benchmark_path / "Illusion"
geometric_illusions = illusion_data / "geometric_illusions"
```

### 评估指标

#### Subject类别
- 主体识别准确率
- 属性描述准确性
- 退化条件下的鲁棒性

#### Relation类别
- 空间关系判断准确率
- 相对位置描述准确性
- 比较关系理解能力

#### Attribute类别
- 全局属性感知能力
- 局部细节识别能力
- 噪声条件下的性能

#### Illusion类别
- 错觉识别准确率
- 错觉解释合理性
- 视觉机制理解深度

## 📈 数据集特点

1. **多模态覆盖**: 涵盖几何、色彩、运动、空间等多个视觉维度
2. **梯度变化**: 每种效果都有100个强度梯度，支持细粒度评估
3. **真实场景**: 基于真实世界图片生成，具有实际应用价值
4. **标准化格式**: 统一的PNG格式和JSON元数据
5. **可扩展性**: 模块化设计，便于添加新的测试类别

## 🔧 技术细节

- **图片格式**: PNG (无损压缩)
- **分辨率**: 根据原始数据集保持
- **色彩空间**: RGB
- **元数据**: JSON格式，包含生成参数和标注信息

## 📝 引用

如果您在研究中使用了此数据集，请引用：

```bibtex
@dataset{{vlm_comprehensive_benchmark,
  title={{VLM Comprehensive Benchmark Dataset}},
  year={{2025}},
  month={{08}},
  note={{Generated dataset for comprehensive VLM evaluation}}
}}
```

## 🤝 贡献

欢迎提交Issue和Pull Request来改进数据集质量或添加新的测试类别。

## 📄 许可证

本数据集仅供研究使用。

---
*最后更新: {datetime.now().strftime("%Y-%m-%d")}*
"""

        # 保存README
        with open(self.output_path / "README.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # 保存分析数据
        with open(self.output_path / "dataset_analysis.json", 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print("✅ README和分析报告已生成")

    def organize_all(self):
        """执行完整的数据整理流程"""
        print("🚀 开始VLM综合基准数据集整理")
        print("=" * 60)
        
        self.organize_subject_data()
        self.organize_relation_data() 
        self.organize_attribute_data()
        self.organize_illusion_data()
        self.generate_comprehensive_readme()
        
        print("\n" + "=" * 60)
        print("🎉 VLM综合基准数据集整理完成！")
        print(f"📁 输出目录: {self.output_path}")
        print("📖 查看README.md了解详细信息")

def main():
    organizer = VLMBenchmarkOrganizer()
    organizer.organize_all()

if __name__ == "__main__":
    main()