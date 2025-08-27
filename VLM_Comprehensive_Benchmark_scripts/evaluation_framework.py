#!/usr/bin/env python3
"""
视觉模型边界评测框架
使用色盲测试数据集评估视觉模型的色彩感知边界
"""

import json
import numpy as np
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Callable
import cv2

class ColorBlindnessEvaluator:
    """色盲测试数据集评测器"""
    
    def __init__(self, dataset_path="data/gradients", metadata_path="metadata/final_dataset.json"):
        self.dataset_path = Path(dataset_path)
        self.metadata_path = Path(metadata_path)
        
        # 加载数据集元数据
        with open(self.metadata_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
        
        # 色盲类型
        self.colorblind_types = ['protanopia', 'deuteranopia', 'tritanopia']
        
        # 评测结果存储
        self.evaluation_results = {}
        
    def evaluate_model_boundary(self, model_predict_func: Callable, 
                               confidence_threshold: float = 0.5) -> Dict:
        """
        评测模型的视觉边界
        
        Args:
            model_predict_func: 模型预测函数，输入图像路径，返回(预测结果, 置信度)
            confidence_threshold: 置信度阈值
            
        Returns:
            评测结果字典
        """
        print("🔍 开始评测视觉模型边界...")
        
        results = {
            "overall_metrics": {},
            "per_colorblind_type": {},
            "per_image_analysis": {},
            "boundary_analysis": {}
        }
        
        total_sequences = len(self.metadata["images"])
        
        for i, image_meta in enumerate(self.metadata["images"]):
            print(f"评测图像 {i+1}/{total_sequences}: {image_meta['base_image']}")
            
            base_image = image_meta['base_image']
            expected_answer = self.extract_expected_answer(base_image)
            
            image_results = {
                "base_image": base_image,
                "expected_answer": expected_answer,
                "colorblind_results": {}
            }
            
            for cb_type in self.colorblind_types:
                if cb_type in image_meta["colorblind_variants"]:
                    cb_result = self.evaluate_colorblind_sequence(
                        image_meta["colorblind_variants"][cb_type],
                        model_predict_func,
                        expected_answer,
                        confidence_threshold
                    )
                    image_results["colorblind_results"][cb_type] = cb_result
            
            results["per_image_analysis"][base_image] = image_results
        
        # 计算总体指标
        results["overall_metrics"] = self.calculate_overall_metrics(results["per_image_analysis"])
        results["per_colorblind_type"] = self.calculate_per_type_metrics(results["per_image_analysis"])
        results["boundary_analysis"] = self.analyze_boundaries(results["per_image_analysis"])
        
        return results
    
    def evaluate_colorblind_sequence(self, variant_meta: Dict, 
                                   model_predict_func: Callable,
                                   expected_answer: str,
                                   confidence_threshold: float) -> Dict:
        """评测单个色盲类型的梯度序列"""
        
        gradient_files = variant_meta["generated_files"]
        colorblind_type = variant_meta["colorblind_type"]
        
        sequence_results = {
            "colorblind_type": colorblind_type,
            "total_steps": len(gradient_files),
            "predictions": [],
            "accuracy_curve": [],
            "confidence_curve": [],
            "failure_threshold": None,
            "recovery_threshold": None
        }
        
        print(f"  评测 {colorblind_type} 序列...")
        
        for step, image_path in enumerate(gradient_files):
            severity = step / (len(gradient_files) - 1)  # 0.0 到 1.0
            
            try:
                # 调用模型预测
                prediction, confidence = model_predict_func(image_path)
                
                # 判断预测是否正确
                is_correct = self.is_prediction_correct(prediction, expected_answer)
                is_confident = confidence >= confidence_threshold
                
                step_result = {
                    "step": step,
                    "severity": severity,
                    "image_path": image_path,
                    "prediction": prediction,
                    "confidence": confidence,
                    "is_correct": is_correct,
                    "is_confident": is_confident,
                    "success": is_correct and is_confident
                }
                
                sequence_results["predictions"].append(step_result)
                sequence_results["accuracy_curve"].append(1.0 if is_correct else 0.0)
                sequence_results["confidence_curve"].append(confidence)
                
            except Exception as e:
                print(f"    ✗ 步骤 {step} 预测失败: {e}")
                sequence_results["predictions"].append({
                    "step": step,
                    "severity": severity,
                    "error": str(e)
                })
        
        # 分析失败和恢复阈值
        sequence_results["failure_threshold"] = self.find_failure_threshold(sequence_results["predictions"])
        sequence_results["recovery_threshold"] = self.find_recovery_threshold(sequence_results["predictions"])
        
        return sequence_results
    
    def find_failure_threshold(self, predictions: List[Dict]) -> float:
        """找到模型开始失败的色盲严重程度阈值"""
        for pred in predictions:
            if "success" in pred and not pred["success"]:
                return pred["severity"]
        return 1.0  # 如果始终成功
    
    def find_recovery_threshold(self, predictions: List[Dict]) -> float:
        """找到模型从失败中恢复的阈值（如果有的话）"""
        failed = False
        for pred in predictions:
            if "success" in pred:
                if not pred["success"]:
                    failed = True
                elif failed and pred["success"]:
                    return pred["severity"]
        return None  # 没有恢复
    
    def calculate_overall_metrics(self, per_image_analysis: Dict) -> Dict:
        """计算总体评测指标"""
        
        all_predictions = []
        for image_results in per_image_analysis.values():
            for cb_type, cb_results in image_results["colorblind_results"].items():
                all_predictions.extend(cb_results["predictions"])
        
        # 过滤出有效预测
        valid_predictions = [p for p in all_predictions if "success" in p]
        
        if not valid_predictions:
            return {"error": "没有有效预测"}
        
        total_predictions = len(valid_predictions)
        successful_predictions = sum(1 for p in valid_predictions if p["success"])
        
        # 按严重程度分组计算准确率
        severity_bins = np.linspace(0, 1, 11)  # 10个区间
        severity_accuracy = []
        
        for i in range(len(severity_bins) - 1):
            bin_start, bin_end = severity_bins[i], severity_bins[i + 1]
            bin_predictions = [p for p in valid_predictions 
                             if bin_start <= p["severity"] < bin_end]
            
            if bin_predictions:
                bin_accuracy = sum(1 for p in bin_predictions if p["success"]) / len(bin_predictions)
                severity_accuracy.append({
                    "severity_range": f"{bin_start:.1f}-{bin_end:.1f}",
                    "accuracy": bin_accuracy,
                    "sample_count": len(bin_predictions)
                })
        
        return {
            "total_predictions": total_predictions,
            "overall_accuracy": successful_predictions / total_predictions,
            "mean_confidence": np.mean([p["confidence"] for p in valid_predictions]),
            "severity_accuracy_breakdown": severity_accuracy
        }
    
    def calculate_per_type_metrics(self, per_image_analysis: Dict) -> Dict:
        """计算每种色盲类型的指标"""
        
        type_metrics = {}
        
        for cb_type in self.colorblind_types:
            type_predictions = []
            failure_thresholds = []
            
            for image_results in per_image_analysis.values():
                if cb_type in image_results["colorblind_results"]:
                    cb_results = image_results["colorblind_results"][cb_type]
                    type_predictions.extend([p for p in cb_results["predictions"] if "success" in p])
                    
                    if cb_results["failure_threshold"] is not None:
                        failure_thresholds.append(cb_results["failure_threshold"])
            
            if type_predictions:
                successful = sum(1 for p in type_predictions if p["success"])
                
                type_metrics[cb_type] = {
                    "total_predictions": len(type_predictions),
                    "accuracy": successful / len(type_predictions),
                    "mean_confidence": np.mean([p["confidence"] for p in type_predictions]),
                    "mean_failure_threshold": np.mean(failure_thresholds) if failure_thresholds else None,
                    "failure_threshold_std": np.std(failure_thresholds) if failure_thresholds else None
                }
        
        return type_metrics
    
    def analyze_boundaries(self, per_image_analysis: Dict) -> Dict:
        """分析视觉边界特征"""
        
        boundary_analysis = {
            "global_failure_distribution": {},
            "type_comparison": {},
            "difficulty_ranking": []
        }
        
        # 收集所有失败阈值
        all_failure_thresholds = []
        type_failure_thresholds = {cb_type: [] for cb_type in self.colorblind_types}
        
        for image_results in per_image_analysis.values():
            for cb_type, cb_results in image_results["colorblind_results"].items():
                if cb_results["failure_threshold"] is not None:
                    all_failure_thresholds.append(cb_results["failure_threshold"])
                    type_failure_thresholds[cb_type].append(cb_results["failure_threshold"])
        
        # 全局失败分布
        if all_failure_thresholds:
            boundary_analysis["global_failure_distribution"] = {
                "mean": np.mean(all_failure_thresholds),
                "std": np.std(all_failure_thresholds),
                "median": np.median(all_failure_thresholds),
                "min": np.min(all_failure_thresholds),
                "max": np.max(all_failure_thresholds)
            }
        
        # 类型间比较
        for cb_type, thresholds in type_failure_thresholds.items():
            if thresholds:
                boundary_analysis["type_comparison"][cb_type] = {
                    "mean_failure_threshold": np.mean(thresholds),
                    "robustness_score": 1.0 - np.mean(thresholds),  # 失败阈值越低，鲁棒性越差
                    "consistency": 1.0 / (1.0 + np.std(thresholds))  # 标准差越小，一致性越好
                }
        
        return boundary_analysis
    
    def generate_evaluation_report(self, results: Dict, output_path: str = "evaluation_report.html"):
        """生成评测报告"""
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>色盲测试数据集模型评测报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .metric {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
        .chart {{ margin: 20px 0; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>色盲测试数据集模型评测报告</h1>
    
    <h2>总体指标</h2>
    <div class="metric">
        <p><strong>总预测数:</strong> {results['overall_metrics'].get('total_predictions', 'N/A')}</p>
        <p><strong>总体准确率:</strong> {results['overall_metrics'].get('overall_accuracy', 0):.3f}</p>
        <p><strong>平均置信度:</strong> {results['overall_metrics'].get('mean_confidence', 0):.3f}</p>
    </div>
    
    <h2>各色盲类型表现</h2>
    <table>
        <tr>
            <th>色盲类型</th>
            <th>准确率</th>
            <th>平均置信度</th>
            <th>平均失败阈值</th>
            <th>鲁棒性评分</th>
        </tr>
"""
        
        for cb_type, metrics in results["per_colorblind_type"].items():
            robustness = results["boundary_analysis"]["type_comparison"].get(cb_type, {}).get("robustness_score", 0)
            html_content += f"""
        <tr>
            <td>{cb_type}</td>
            <td>{metrics.get('accuracy', 0):.3f}</td>
            <td>{metrics.get('mean_confidence', 0):.3f}</td>
            <td>{metrics.get('mean_failure_threshold', 'N/A')}</td>
            <td>{robustness:.3f}</td>
        </tr>
"""
        
        html_content += """
    </table>
    
    <h2>边界分析</h2>
    <div class="metric">
"""
        
        if "global_failure_distribution" in results["boundary_analysis"]:
            dist = results["boundary_analysis"]["global_failure_distribution"]
            html_content += f"""
        <p><strong>平均失败阈值:</strong> {dist.get('mean', 0):.3f}</p>
        <p><strong>失败阈值标准差:</strong> {dist.get('std', 0):.3f}</p>
        <p><strong>失败阈值中位数:</strong> {dist.get('median', 0):.3f}</p>
"""
        
        html_content += """
    </div>
    
    <h2>评测说明</h2>
    <div class="metric">
        <p><strong>失败阈值:</strong> 模型开始无法正确识别的色盲严重程度</p>
        <p><strong>鲁棒性评分:</strong> 1 - 平均失败阈值，越高表示模型越鲁棒</p>
        <p><strong>色盲严重程度:</strong> 0.0 = 正常视力，1.0 = 完全色盲</p>
    </div>
    
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ 评测报告已保存到: {output_path}")
    
    def plot_accuracy_curves(self, results: Dict, output_dir: str = "evaluation_plots"):
        """绘制准确率曲线"""
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 为每种色盲类型绘制准确率曲线
        for cb_type in self.colorblind_types:
            plt.figure(figsize=(10, 6))
            
            all_severities = []
            all_accuracies = []
            
            for image_results in results["per_image_analysis"].values():
                if cb_type in image_results["colorblind_results"]:
                    cb_results = image_results["colorblind_results"][cb_type]
                    severities = [p["severity"] for p in cb_results["predictions"] if "severity" in p]
                    accuracies = cb_results["accuracy_curve"]
                    
                    if len(severities) == len(accuracies):
                        all_severities.extend(severities)
                        all_accuracies.extend(accuracies)
            
            if all_severities and all_accuracies:
                # 按严重程度排序
                sorted_data = sorted(zip(all_severities, all_accuracies))
                severities, accuracies = zip(*sorted_data)
                
                plt.plot(severities, accuracies, 'o-', alpha=0.6, label=f'{cb_type}')
                plt.xlabel('色盲严重程度')
                plt.ylabel('准确率')
                plt.title(f'{cb_type.title()} 准确率 vs 色盲严重程度')
                plt.grid(True, alpha=0.3)
                plt.legend()
                
                plt.tight_layout()
                plt.savefig(output_path / f'{cb_type}_accuracy_curve.png', dpi=300, bbox_inches='tight')
                plt.close()
        
        print(f"✓ 准确率曲线已保存到: {output_path}")
    
    @staticmethod
    def is_prediction_correct(prediction: str, expected: str) -> bool:
        """判断预测是否正确"""
        # 这里可以根据具体任务调整比较逻辑
        if expected.lower() == "unknown":
            return True  # 如果期望答案未知，认为预测正确
        
        # 提取数字或关键词进行比较
        import re
        pred_numbers = re.findall(r'\d+', str(prediction))
        expected_numbers = re.findall(r'\d+', str(expected))
        
        if pred_numbers and expected_numbers:
            return pred_numbers[0] == expected_numbers[0]
        
        # 关键词比较
        return str(prediction).lower() == str(expected).lower()
    
    def extract_expected_answer(self, filename: str) -> str:
        """从文件名提取期望答案"""
        import re
        filename_lower = filename.lower()
        
        # 检查数字
        numbers = re.findall(r'\d+', filename)
        if numbers:
            return numbers[0]
        
        # 检查关键词
        keywords = ['circle', 'square', 'triangle', 'diamond', 'star']
        for keyword in keywords:
            if keyword in filename_lower:
                return keyword
        
        return "unknown"


# 示例使用
def example_model_predict(image_path: str) -> Tuple[str, float]:
    """
    示例模型预测函数
    实际使用时替换为你的模型
    
    Args:
        image_path: 图像文件路径
        
    Returns:
        (预测结果, 置信度)
    """
    # 这里是示例实现，实际使用时替换为真实模型
    import random
    
    # 模拟预测逻辑：随机返回数字和置信度
    predicted_number = str(random.randint(1, 9))
    confidence = random.uniform(0.3, 0.95)
    
    return predicted_number, confidence


def main():
    """主函数：演示如何使用评测框架"""
    
    print("🎯 色盲测试数据集模型评测框架")
    print("=" * 50)
    
    # 初始化评测器
    evaluator = ColorBlindnessEvaluator()
    
    # 运行评测（使用示例模型）
    print("使用示例模型进行评测...")
    results = evaluator.evaluate_model_boundary(
        model_predict_func=example_model_predict,
        confidence_threshold=0.7
    )
    
    # 生成报告
    evaluator.generate_evaluation_report(results)
    evaluator.plot_accuracy_curves(results)
    
    # 保存结果
    with open("evaluation_results.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n✅ 评测完成！")
    print("📁 输出文件:")
    print("  - evaluation_report.html: 详细评测报告")
    print("  - evaluation_plots/: 准确率曲线图")
    print("  - evaluation_results.json: 完整评测数据")


if __name__ == "__main__":
    main()