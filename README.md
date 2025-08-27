# VLM 数据集完整生成程序


### 🏗️ visual_boundary_dataset 生成器
- `batch_download_images.py` - 批量图像下载器
- `collect_and_analyze_images.py` - 图像收集分析器
- `finalize_image_collection.py` - 图像收集最终化工具

### 🛠️ 高级工具
- `fast_noise_generator.py` - 快速噪声生成器
- `noise_gradient_generator.py` - 噪声梯度生成器
- `merge_datasets.py` - 数据集合并工具
- `cleanup_datasets.py` - 数据集清理工具
- `detailed_dataset_analysis.py` - 详细数据集分析器
- `fix_incomplete_illusions.py` - 错觉数据修复工具
- `recreate_illusion_dataset.py` - 错觉数据集重建工具
- `evaluation_framework.py` - 评估框架

## 🔧 VLM_Comprehensive_Benchmark 生成流程

### 主生成器: organize_vlm_benchmark.py 🎯
**作用**: 主整合器，生成 VLM_Comprehensive_Benchmark
**功能**: 整合所有源数据集为四大类别综合基准
**输出**: 44,472+ 图片 + 72 视频的大规模数据集


### Ultra_Quality_Relation_Dataset 生成

#### ultra_relation_generator.py
**作用**: 直接生成超高质量关系数据集
**功能**: 
- SVG精确几何关系生成
- 4种关系类型，每类50个  
- 每个关系100个梯度变化
- 6种视觉效果变化

### VLM_Comprehensive_Benchmark 生成

#### organize_vlm_benchmark.py
**作用**: 生成综合性基准数据集
**功能**:
- 整合所有可用VLM数据集
- 按4大类别重新组织：Subject、Relation、Attribute、Illusion
- 创建符号链接避免数据重复
- 生成详细统计分析报告

**数据源**:
- Real_World_Noise_Dataset (4,327张)
- visual_boundary_dataset (5,808张)
- Unified_Illusion_Dataset (5,010张)
- 各种关系数据集

#### VLM_Comprehensive_Benchmark_scripts/
**包含内部程序**:
- **colorblindness_scripts/**: 色盲识别专用脚本集合
  - `download_ishihara_plates.py` - 下载Ishihara色盲测试图
  - `colorblind_simulation.py` - 色盲视觉模拟
  - `generate_dataset.py` - 色盲测试数据集生成
  - `comprehensive_download.py` - 综合下载器
- **evaluation_framework.py** - 评估框架
- **run_generation.py** - 批量生成脚本
- **process_existing_images.py** - 现有图片处理





## 📦 依赖安装

```bash
pip install svgwrite cairosvg pillow matplotlib numpy opencv-python requests beautifulsoup4 tqdm
```


