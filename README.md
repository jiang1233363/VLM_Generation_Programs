# VLM 数据集完整生成程序


## 📁 目标数据集

### 1. VLM_Final_Benchmark_Dataset
- **位置**: `/home/jgy/VLM_Final_Benchmark_Dataset/`
- **内容**: 912个样本，4大类别

### 2. Ultra_Quality_Relation_Dataset
- **位置**: `/home/jgy/Ultra_Quality_Relation_Dataset/`
- **内容**: 200个关系，20,000张梯度图片

## 🔧 完整生成程序

#### create_final_dataset.py
**作用**: 最终整合器，生成 VLM_Final_Benchmark_Dataset
**功能**: 整合以下源数据集为4大类别 (Subject/Relation/Attribute/Illusion)

#### 源数据集生成器：

**1. complete_50_illusions_final.py**
- **生成**: Unified_Illusion_Dataset → VLM_Final_Benchmark_Dataset/Illusion
- **功能**: 50种光学错觉，每种100个变化
- **类型**: Müller-Lyer, Hermann Grid, Penrose Triangle等

**2. complete_noise_dataset.py**  
- **生成**: Real_World_Noise_Dataset → VLM_Final_Benchmark_Dataset/Subject
- **功能**: 基于visual_boundary_dataset的噪声处理
- **效果**: 10种噪声/退化类型

**3. standard_relation_generator.py**
- **生成**: Standard_Quality_Relation_Dataset → VLM_Final_Benchmark_Dataset/Relation  
- **功能**: 4种关系类型，每类25个关系
- **输出**: 100个关系，5,000张图片

**4. enhanced_image_downloader.py**
- **生成**: visual_boundary_dataset → VLM_Final_Benchmark_Dataset/Subject+Attribute
- **功能**: 下载和处理真实世界图片
- **来源**: 多个图片数据库

**5. visual_degradation.py**
- **生成**: 图片退化效果 → VLM_Final_Benchmark_Dataset/Attribute
- **功能**: 亮度、对比度、清晰度等属性变化
- **效果**: 多种视觉属性退化

### Ultra_Quality_Relation_Dataset 生成

#### ultra_relation_generator.py
**作用**: 直接生成超高质量关系数据集
**功能**: 
- SVG精确几何关系生成
- 4种关系类型，每类50个  
- 每个关系100个梯度变化
- 6种视觉效果变化

## 📊 数据生成依赖关系


## 🔄 完整重新生成指南

### 重新生成 VLM_Final_Benchmark_Dataset：

```bash
# 1. 生成基础图片数据
python enhanced_image_downloader.py    # 下载visual_boundary_dataset
python visual_degradation.py           # 生成退化效果

# 2. 生成各类别源数据
python complete_noise_dataset.py       # Subject类别数据
python complete_50_illusions_final.py  # Illusion类别数据  
python standard_relation_generator.py  # Relation类别数据

# 3. 最终整合
python create_final_dataset.py        # 整合为VLM_Final_Benchmark_Dataset
```

### 重新生成 Ultra_Quality_Relation_Dataset：

```bash
python ultra_relation_generator.py
```

## 📋 各类别对应关系

| VLM最终数据集类别 | 源数据集 | 生成程序 |
|-------------------|----------|----------|
| Subject (主体感知) | Real_World_Noise_Dataset + visual_boundary_dataset | complete_noise_dataset.py + enhanced_image_downloader.py |
| Relation (关系理解) | Standard_Quality_Relation_Dataset | standard_relation_generator.py |
| Attribute (属性感知) | visual_boundary_dataset + 退化效果 | visual_degradation.py + enhanced_image_downloader.py |
| Illusion (错觉感知) | Unified_Illusion_Dataset | complete_50_illusions_final.py |

## 📦 依赖安装

```bash
pip install svgwrite cairosvg pillow matplotlib numpy opencv-python requests beautifulsoup4 tqdm
```

