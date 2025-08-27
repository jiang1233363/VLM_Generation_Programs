#!/usr/bin/env python3
"""
处理现有图像 - 直接使用已下载的图像生成色盲测试数据集
"""

import sys
from pathlib import Path

# 添加scripts目录到Python路径
scripts_dir = Path(__file__).parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from scripts.colorblind_simulation import ColorBlindnessSimulator
import json
import time
from PIL import Image

def main():
    print("🎨 色盲测试数据集处理器")
    print("=" * 50)
    print("使用现有的真实网络图像生成完整数据集")
    
    # 检查现有图像
    raw_dir = Path("data/raw")
    if not raw_dir.exists():
        print("❌ 未找到data/raw目录")
        return False
    
    # 获取所有图像文件
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp'}
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(raw_dir.glob(f"*{ext}"))
    
    if not image_files:
        print("❌ 未找到任何图像文件")
        return False
    
    print(f"✓ 找到 {len(image_files)} 张真实网络图像")
    
    # 创建输出目录
    gradients_dir = Path("data/gradients")
    gradients_dir.mkdir(parents=True, exist_ok=True)
    
    metadata_dir = Path("metadata")
    metadata_dir.mkdir(parents=True, exist_ok=True)
    
    # 初始化色盲模拟器
    simulator = ColorBlindnessSimulator()
    colorblind_types = ['protanopia', 'deuteranopia', 'tritanopia']
    gradient_steps = 100
    
    print(f"\n开始处理图像...")
    print(f"- 色盲类型: {len(colorblind_types)} 种")
    print(f"- 梯度步数: {gradient_steps} 步")
    print(f"- 预计生成: {len(image_files) * len(colorblind_types) * (gradient_steps + 1)} 张图像")
    
    dataset_metadata = {
        "generation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_base_images": len(image_files),
        "colorblind_types": colorblind_types,
        "gradient_steps": gradient_steps,
        "images": []
    }
    
    total_generated = 0
    
    for i, image_file in enumerate(image_files):
        print(f"\n处理图像 {i+1}/{len(image_files)}: {image_file.name}")
        
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
            
            for colorblind_type in colorblind_types:
                print(f"  生成 {colorblind_type} 梯度...")
                
                # 创建输出目录
                type_output_dir = gradients_dir / image_file.stem / colorblind_type
                type_output_dir.mkdir(parents=True, exist_ok=True)
                
                # 生成梯度序列
                generated_files = []
                
                for step in range(gradient_steps + 1):
                    severity = step / gradient_steps
                    
                    # 应用色盲模拟
                    sim_func = getattr(simulator, f'simulate_{colorblind_type}')
                    simulated_image = sim_func(image, severity)
                    
                    # 保存图像
                    filename = f"step_{step:03d}_severity_{severity:.2f}.png"
                    filepath = type_output_dir / filename
                    simulated_image.save(filepath)
                    generated_files.append(str(filepath))
                    
                    if step % 20 == 0:  # 每20步显示一次进度
                        print(f"    进度: {step}/{gradient_steps}")
                
                # 分析对比度变化
                try:
                    contrast_analysis = simulator.analyze_color_contrast(
                        image, colorblind_type, 1.0
                    )
                except Exception as e:
                    print(f"    警告: 对比度分析失败: {e}")
                    contrast_analysis = {"error": str(e)}
                
                variant_metadata = {
                    "colorblind_type": colorblind_type,
                    "generated_files": generated_files,
                    "num_gradients": len(generated_files),
                    "contrast_analysis": contrast_analysis,
                    "output_directory": str(type_output_dir)
                }
                
                image_metadata["colorblind_variants"][colorblind_type] = variant_metadata
                total_generated += len(generated_files)
                
                print(f"    ✓ 生成了 {len(generated_files)} 个梯度文件")
            
            dataset_metadata["images"].append(image_metadata)
            
        except Exception as e:
            print(f"  ✗ 处理失败: {e}")
            continue
    
    # 保存数据集元数据
    metadata_file = metadata_dir / "final_dataset.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(dataset_metadata, f, indent=2, ensure_ascii=False)
    
    # 生成统计信息
    stats = {
        "dataset_overview": {
            "total_base_images": len(image_files),
            "total_gradient_images": total_generated,
            "colorblind_types": colorblind_types,
            "gradient_steps": gradient_steps,
            "processing_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "images_per_type": {},
        "file_distribution": {}
    }
    
    # 统计每种色盲类型的图像数量
    for cb_type in colorblind_types:
        count = 0
        for img_meta in dataset_metadata["images"]:
            if cb_type in img_meta["colorblind_variants"]:
                count += img_meta["colorblind_variants"][cb_type]["num_gradients"]
        stats["images_per_type"][cb_type] = count
    
    stats_file = metadata_dir / "final_statistics.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    # 创建测试用例
    test_cases = []
    for img_meta in dataset_metadata["images"]:
        base_image = img_meta["base_image"]
        expected_answer = extract_expected_answer(base_image)
        
        for cb_type, variant_meta in img_meta["colorblind_variants"].items():
            test_sequence = {
                "test_id": f"{Path(base_image).stem}_{cb_type}",
                "base_image": base_image,
                "colorblind_type": cb_type,
                "expected_answer": expected_answer,
                "test_description": f"测试模型在{cb_type}模拟下识别{expected_answer}的能力",
                "gradient_files": variant_meta["generated_files"],
                "num_gradients": variant_meta["num_gradients"]
            }
            test_cases.append(test_sequence)
    
    test_cases_file = metadata_dir / "test_cases.json"
    with open(test_cases_file, 'w', encoding='utf-8') as f:
        json.dump({
            "total_test_sequences": len(test_cases),
            "creation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_sequences": test_cases
        }, f, indent=2, ensure_ascii=False)
    
    # 生成README
    generate_readme(len(image_files), total_generated, colorblind_types, gradient_steps)
    
    print(f"\n" + "=" * 50)
    print("🎉 数据集处理完成!")
    print(f"\n📊 数据集统计:")
    print(f"- 基础图像: {len(image_files)} 张真实网络图像")
    print(f"- 生成图像: {total_generated} 张")
    print(f"- 色盲类型: {', '.join(colorblind_types)}")
    print(f"- 测试序列: {len(test_cases)} 个")
    
    print(f"\n📁 文件位置:")
    print(f"- 梯度图像: data/gradients/")
    print(f"- 元数据: {metadata_file}")
    print(f"- 统计信息: {stats_file}")
    print(f"- 测试用例: {test_cases_file}")
    
    return True

def extract_expected_answer(filename):
    """从文件名提取期望答案"""
    filename_lower = filename.lower()
    
    # 检查数字
    import re
    numbers = re.findall(r'\d+', filename)
    if numbers:
        return numbers[0]
    
    # 检查关键词
    if 'circle' in filename_lower:
        return 'circle'
    elif 'square' in filename_lower:
        return 'square'
    elif 'triangle' in filename_lower:
        return 'triangle'
    
    return 'unknown'

def generate_readme(base_count, total_count, colorblind_types, gradient_steps):
    """生成README文档"""
    readme_content = f"""# 色盲测试数据集

## 概述
基于真实网络石原氏色盲测试图的AI视觉边界评估数据集。

## 数据集统计
- **基础图像**: {base_count} 张真实网络图像
- **生成图像**: {total_count} 张梯度变化图像
- **色盲类型**: {len(colorblind_types)} 种 ({', '.join(colorblind_types)})
- **梯度步数**: {gradient_steps} 步 (0%-100%严重程度)

## 数据来源
所有基础图像均来自合法的网络开源资源：
- GitHub开源仓库 (主要来源)
- 维基媒体共享资源
- 医学教育网站

## 数据集结构
```
data/
├── raw/                    # 原始真实图像 ({base_count}张)
└── gradients/             # 色盲模拟梯度图像
    └── [image_name]/
        ├── protanopia/    # 红色盲模拟
        ├── deuteranopia/  # 绿色盲模拟
        └── tritanopia/    # 蓝色盲模拟
```

## 测试目标
评估AI模型在不同色盲模拟程度下识别隐藏数字/符号的能力边界。

生成时间: {time.strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    readme_file = docs_dir / "README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✓ README文档保存到: {readme_file}")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)