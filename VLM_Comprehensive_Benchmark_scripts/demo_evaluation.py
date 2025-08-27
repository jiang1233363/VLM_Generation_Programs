#!/usr/bin/env python3
"""
色盲测试数据集评测演示
展示如何使用数据集评测视觉模型的边界能力
"""

import json
import numpy as np
from pathlib import Path
import random
from typing import Tuple
import matplotlib.pyplot as plt

def simulate_model_prediction(image_path: str, model_type: str = "robust") -> Tuple[str, float]:
    """
    模拟不同类型模型的预测行为
    
    Args:
        image_path: 图像路径
        model_type: 模型类型 ("robust", "fragile", "inconsistent")
    
    Returns:
        (预测结果, 置信度)
    """
    # 从文件名提取真实答案
    filename = Path(image_path).name
    if "severity_0.00" in filename:
        # 正常图像，所有模型都应该能识别
        true_answer = extract_true_answer(filename)
        return true_answer, 0.95
    
    # 从文件名提取严重程度
    import re
    severity_match = re.search(r'severity_(\d+\.\d+)', filename)
    if severity_match:
        severity = float(severity_match.group(1))
    else:
        severity = 0.0
    
    true_answer = extract_true_answer(filename)
    
    # 根据模型类型和严重程度模拟预测
    if model_type == "robust":
        # 鲁棒模型：在高严重程度下仍能保持较好性能
        success_prob = max(0.1, 1.0 - severity * 0.8)
        confidence = max(0.3, 0.9 - severity * 0.6)
        
    elif model_type == "fragile":
        # 脆弱模型：在低严重程度下就开始失效
        success_prob = max(0.05, 1.0 - severity * 1.5)
        confidence = max(0.2, 0.8 - severity * 1.2)
        
    elif model_type == "inconsistent":
        # 不一致模型：表现不稳定
        base_success = max(0.1, 1.0 - severity)
        noise = random.uniform(-0.3, 0.3)
        success_prob = max(0.05, min(0.95, base_success + noise))
        confidence = max(0.2, min(0.9, success_prob + random.uniform(-0.2, 0.2)))
    
    else:
        success_prob = 0.5
        confidence = 0.5
    
    # 决定是否预测正确
    if random.random() < success_prob:
        prediction = true_answer
    else:
        # 错误预测
        wrong_answers = ["1", "2", "3", "5", "6", "8", "9", "circle", "square"]
        prediction = random.choice([ans for ans in wrong_answers if ans != true_answer])
    
    return prediction, confidence

def extract_true_answer(filename: str) -> str:
    """从文件名提取真实答案"""
    # 简化的答案提取逻辑
    if "learning" in filename:
        # 从GitHub学习数据集的文件名提取
        import re
        numbers = re.findall(r'_(\d+)_', filename)
        if numbers:
            return numbers[0]
    
    # 其他规则...
    return random.choice(["8", "3", "5", "2", "6"])

def run_quick_demo():
    """运行快速演示"""
    print("🎯 色盲测试数据集评测演示")
    print("=" * 50)
    
    # 检查数据集是否存在
    gradients_dir = Path("data/gradients")
    if not gradients_dir.exists():
        print("❌ 找不到梯度数据集，请先运行数据生成")
        return
    
    # 找一些测试图像进行演示
    demo_images = []
    for image_dir in gradients_dir.iterdir():
        if image_dir.is_dir():
            protanopia_dir = image_dir / "protanopia"
            if protanopia_dir.exists():
                # 选择几个关键严重程度的图像
                key_steps = [0, 25, 50, 75, 100]
                for step in key_steps:
                    image_file = protanopia_dir / f"step_{step:03d}_severity_{step/100:.2f}.png"
                    if image_file.exists():
                        demo_images.append({
                            "path": str(image_file),
                            "severity": step / 100,
                            "colorblind_type": "protanopia",
                            "base_image": image_dir.name
                        })
                break  # 只用一张基础图像做演示
    
    if not demo_images:
        print("❌ 找不到可用的测试图像")
        return
    
    print(f"找到 {len(demo_images)} 张演示图像")
    
    # 测试三种不同类型的模型
    model_types = ["robust", "fragile", "inconsistent"]
    results = {}
    
    for model_type in model_types:
        print(f"\n📊 测试 {model_type} 模型...")
        
        model_results = {
            "predictions": [],
            "accuracies": [],
            "confidences": [],
            "severities": []
        }
        
        for img_info in demo_images:
            prediction, confidence = simulate_model_prediction(img_info["path"], model_type)
            true_answer = extract_true_answer(Path(img_info["path"]).name)
            
            is_correct = prediction == true_answer
            
            model_results["predictions"].append({
                "severity": img_info["severity"],
                "prediction": prediction,
                "true_answer": true_answer,
                "confidence": confidence,
                "correct": is_correct
            })
            model_results["accuracies"].append(1.0 if is_correct else 0.0)
            model_results["confidences"].append(confidence)
            model_results["severities"].append(img_info["severity"])
            
            print(f"  严重程度 {img_info['severity']:.2f}: {prediction} (真实: {true_answer}) "
                  f"置信度: {confidence:.3f} {'✓' if is_correct else '✗'}")
        
        # 计算失效阈值
        failure_threshold = None
        for pred in model_results["predictions"]:
            if not pred["correct"]:
                failure_threshold = pred["severity"]
                break
        
        model_results["failure_threshold"] = failure_threshold
        model_results["robustness_score"] = 1.0 - (failure_threshold if failure_threshold else 1.0)
        
        results[model_type] = model_results
        
        print(f"  失效阈值: {failure_threshold}")
        print(f"  鲁棒性评分: {model_results['robustness_score']:.3f}")
    
    # 可视化结果
    plot_demo_results(results)
    
    # 生成简单报告
    generate_demo_report(results)
    
    print("\n✅ 演示完成！")
    print("📁 输出文件:")
    print("  - demo_comparison.png: 模型对比图")
    print("  - demo_report.txt: 简单评测报告")

def plot_demo_results(results):
    """绘制演示结果"""
    
    plt.figure(figsize=(12, 8))
    
    # 子图1: 准确率对比
    plt.subplot(2, 2, 1)
    for model_type, data in results.items():
        plt.plot(data["severities"], data["accuracies"], 'o-', label=model_type)
    plt.xlabel('色盲严重程度')
    plt.ylabel('准确率')
    plt.title('不同模型的准确率 vs 色盲严重程度')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 子图2: 置信度对比
    plt.subplot(2, 2, 2)
    for model_type, data in results.items():
        plt.plot(data["severities"], data["confidences"], 's-', label=model_type)
    plt.xlabel('色盲严重程度')
    plt.ylabel('置信度')
    plt.title('不同模型的置信度 vs 色盲严重程度')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 子图3: 鲁棒性对比
    plt.subplot(2, 2, 3)
    model_names = list(results.keys())
    robustness_scores = [results[name]["robustness_score"] for name in model_names]
    bars = plt.bar(model_names, robustness_scores, color=['green', 'red', 'orange'])
    plt.ylabel('鲁棒性评分')
    plt.title('模型鲁棒性对比')
    plt.ylim(0, 1)
    
    # 在柱状图上添加数值
    for bar, score in zip(bars, robustness_scores):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{score:.3f}', ha='center', va='bottom')
    
    # 子图4: 失效阈值对比
    plt.subplot(2, 2, 4)
    failure_thresholds = [results[name]["failure_threshold"] or 1.0 for name in model_names]
    bars = plt.bar(model_names, failure_thresholds, color=['lightgreen', 'lightcoral', 'lightsalmon'])
    plt.ylabel('失效阈值')
    plt.title('模型失效阈值对比')
    plt.ylim(0, 1)
    
    # 在柱状图上添加数值
    for bar, threshold in zip(bars, failure_thresholds):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{threshold:.2f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('demo_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def generate_demo_report(results):
    """生成演示报告"""
    
    report = """色盲测试数据集评测演示报告
=====================================

本报告展示了如何使用色盲测试数据集评测不同类型视觉模型的边界能力。

模型对比结果：
"""
    
    for model_type, data in results.items():
        report += f"""
{model_type.upper()} 模型:
  - 失效阈值: {data['failure_threshold'] or '> 1.0'}
  - 鲁棒性评分: {data['robustness_score']:.3f}
  - 平均置信度: {np.mean(data['confidences']):.3f}
  - 总体准确率: {np.mean(data['accuracies']):.3f}
"""
    
    report += """
评测指标说明：
- 失效阈值: 模型开始无法正确识别的色盲严重程度（越高越好）
- 鲁棒性评分: 1 - 失效阈值，反映模型在色盲条件下的稳定性（越高越好）
- 置信度: 模型对自己预测的信心程度
- 准确率: 正确预测的比例

应用建议：
1. Robust模型适合需要高可靠性的医疗应用
2. Fragile模型需要进一步改进，特别是颜色处理能力
3. Inconsistent模型表现不稳定，需要提升一致性

这个数据集可以帮助：
- 客观评估模型的视觉边界
- 识别模型的薄弱环节
- 指导模型改进方向
- 进行模型选择和对比
"""
    
    with open('demo_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)

if __name__ == "__main__":
    run_quick_demo()