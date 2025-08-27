#!/usr/bin/env python3
"""
视觉边界测试评估框架
用于测试AI模型在不同视觉退化级别下的性能边界
"""

import json
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Callable
import matplotlib.pyplot as plt
import pandas as pd
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """测试结果数据类"""
    image_name: str
    degradation_type: str
    level: int
    success: bool
    confidence: float
    processing_time: float
    error_message: Optional[str] = None

class VisualBoundaryEvaluator:
    """视觉边界评估器"""
    
    def __init__(self, base_dir: str = "/home/jgy/visual_boundary_dataset"):
        self.base_dir = Path(base_dir)
        self.degraded_dir = self.base_dir / "degraded_images"
        self.results_dir = self.base_dir / "evaluation_results"
        self.metadata_dir = self.base_dir / "metadata"
        
        # 创建结果目录
        self.results_dir.mkdir(exist_ok=True)
        
        # 支持的退化类型
        self.degradation_types = [
            'sharpness', 'brightness', 'contrast', 
            'color_distortion', 'color_shift', 'resolution'
        ]
        
        # 加载基础图片信息
        self.base_images = self.load_base_images()
        
    def load_base_images(self) -> List[Dict]:
        """加载基础图片信息"""
        try:
            metadata_file = self.metadata_dir / "final_image_collection.json"
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data['selected_images']
        except Exception as e:
            logger.warning(f"无法加载基础图片信息: {e}")
            return []
    
    def get_degraded_image_path(self, base_filename: str, degradation_type: str, level: int) -> Path:
        """获取退化图片路径"""
        # 从selected_filename获取基础名称
        if 'selected_filename' in base_filename:
            base_name = Path(base_filename['selected_filename']).stem
        else:
            base_name = Path(base_filename).stem
            
        filename = f"{base_name}_{degradation_type}_level_{level:03d}.jpg"
        return self.degraded_dir / degradation_type / filename
    
    def dummy_ai_model(self, image_path: Path) -> Dict:
        """
        模拟AI模型测试函数
        实际使用时，替换为真实的AI模型调用
        """
        try:
            # 加载图片
            image = cv2.imread(str(image_path))
            if image is None:
                return {
                    'success': False,
                    'confidence': 0.0,
                    'processing_time': 0.0,
                    'error': 'Cannot load image'
                }
            
            # 模拟图片质量评估
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 计算图片质量指标
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            brightness = np.mean(gray)
            contrast = gray.std()
            
            # 模拟AI模型的性能衰减
            # 基于图片质量计算成功概率和置信度
            quality_score = (
                min(sharpness / 500, 1.0) * 0.4 +
                (1.0 - abs(brightness - 127) / 127) * 0.3 +
                min(contrast / 80, 1.0) * 0.3
            )
            
            # 添加随机噪声模拟真实模型的不确定性
            noise = np.random.normal(0, 0.1)
            final_score = np.clip(quality_score + noise, 0, 1)
            
            # 设定成功阈值
            success_threshold = 0.3
            success = final_score > success_threshold
            confidence = final_score if success else (1 - final_score)
            
            # 模拟处理时间
            processing_time = np.random.uniform(0.1, 0.5)
            
            return {
                'success': bool(success),
                'confidence': float(confidence),
                'processing_time': processing_time,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'confidence': 0.0,
                'processing_time': 0.0,
                'error': str(e)
            }
    
    def test_single_image(self, 
                         base_image: Dict, 
                         degradation_type: str,
                         test_levels: List[int],
                         model_function: Callable) -> List[TestResult]:
        """测试单张图片在指定退化类型下的性能"""
        results = []
        
        base_filename = base_image.get('selected_filename', base_image['filename'])
        image_name = Path(base_filename).stem
        
        print(f"📸 测试图片: {image_name} - {degradation_type}")
        
        for level in test_levels:
            image_path = self.get_degraded_image_path(base_image, degradation_type, level)
            
            if not image_path.exists():
                print(f"  ❌ Level {level}: 图片不存在")
                results.append(TestResult(
                    image_name=image_name,
                    degradation_type=degradation_type,
                    level=level,
                    success=False,
                    confidence=0.0,
                    processing_time=0.0,
                    error_message="Image file not found"
                ))
                continue
            
            # 调用AI模型测试函数
            model_result = model_function(image_path)
            
            result = TestResult(
                image_name=image_name,
                degradation_type=degradation_type,
                level=level,
                success=model_result['success'],
                confidence=model_result['confidence'],
                processing_time=model_result['processing_time'],
                error_message=model_result.get('error')
            )
            
            results.append(result)
            
            # 显示进度
            status = "✓" if result.success else "❌"
            print(f"  {status} Level {level}: 成功={result.success}, 置信度={result.confidence:.3f}")
        
        return results
    
    def find_failure_threshold(self, results: List[TestResult]) -> Dict:
        """找到模型失败的阈值级别"""
        # 按级别排序
        sorted_results = sorted(results, key=lambda x: x.level)
        
        # 找到连续失败的起始点
        failure_threshold = None
        success_count = 0
        failure_count = 0
        
        for result in sorted_results:
            if result.success:
                success_count += 1
                failure_count = 0
            else:
                failure_count += 1
                success_count = 0
                
                # 如果连续失败3次，认为达到失败阈值
                if failure_count >= 3 and failure_threshold is None:
                    failure_threshold = result.level - 2
                    break
        
        # 计算成功率
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.success)
        success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        # 计算平均置信度
        avg_confidence = np.mean([r.confidence for r in results])
        
        return {
            'failure_threshold': failure_threshold,
            'success_rate': success_rate,
            'avg_confidence': avg_confidence,
            'total_tests': total_tests,
            'successful_tests': successful_tests
        }
    
    def run_comprehensive_evaluation(self, 
                                   model_function: Optional[Callable] = None,
                                   test_images: Optional[List[str]] = None,
                                   test_levels: Optional[List[int]] = None) -> Dict:
        """运行综合评估"""
        
        print("🎯 开始视觉边界综合评估")
        print("=" * 60)
        
        # 使用默认参数
        if model_function is None:
            model_function = self.dummy_ai_model
            print("📝 使用模拟AI模型进行测试")
        
        if test_levels is None:
            # 测试关键级别: 0, 10, 20, ..., 100
            test_levels = list(range(0, 101, 10))
            
        # 选择测试图片
        if test_images is None:
            # 选择前10张高质量图片进行测试
            test_images = self.base_images[:10]
        else:
            # 根据文件名筛选
            test_images = [img for img in self.base_images 
                          if any(name in img['filename'] for name in test_images)]
        
        print(f"📊 测试配置:")
        print(f"   测试图片: {len(test_images)} 张")
        print(f"   退化类型: {len(self.degradation_types)} 种")
        print(f"   测试级别: {len(test_levels)} 个 {test_levels}")
        print(f"   预计总测试: {len(test_images) * len(self.degradation_types) * len(test_levels)} 次")
        
        # 存储所有测试结果
        all_results = []
        summary_stats = {}
        
        # 逐类型测试
        for degradation_type in self.degradation_types:
            print(f"\\n🔬 测试退化类型: {degradation_type.upper()}")
            print("-" * 40)
            
            type_results = []
            
            for base_image in test_images:
                image_results = self.test_single_image(
                    base_image, degradation_type, test_levels, model_function
                )
                type_results.extend(image_results)
                all_results.extend(image_results)
            
            # 分析该类型的结果
            threshold_analysis = self.find_failure_threshold(type_results)
            summary_stats[degradation_type] = threshold_analysis
            
            print(f"📈 {degradation_type} 结果总结:")
            print(f"   失败阈值: Level {threshold_analysis['failure_threshold']}")
            print(f"   成功率: {threshold_analysis['success_rate']:.1%}")
            print(f"   平均置信度: {threshold_analysis['avg_confidence']:.3f}")
        
        # 生成综合报告
        evaluation_results = {
            'test_configuration': {
                'test_images_count': len(test_images),
                'degradation_types': self.degradation_types,
                'test_levels': test_levels,
                'total_tests': len(all_results)
            },
            'detailed_results': [
                {
                    'image_name': r.image_name,
                    'degradation_type': r.degradation_type,
                    'level': r.level,
                    'success': r.success,
                    'confidence': r.confidence,
                    'processing_time': r.processing_time,
                    'error_message': r.error_message
                }
                for r in all_results
            ],
            'summary_statistics': summary_stats,
            'overall_metrics': {
                'total_tests': len(all_results),
                'successful_tests': sum(1 for r in all_results if r.success),
                'overall_success_rate': sum(1 for r in all_results if r.success) / len(all_results),
                'avg_processing_time': np.mean([r.processing_time for r in all_results]),
                'avg_confidence': np.mean([r.confidence for r in all_results])
            }
        }
        
        # 保存结果
        results_file = self.results_dir / f"evaluation_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(evaluation_results, f, indent=2, ensure_ascii=False)
        
        print(f"\\n✅ 评估完成!")
        print(f"📄 结果保存: {results_file}")
        print(f"\\n📊 总体性能:")
        print(f"   总测试次数: {evaluation_results['overall_metrics']['total_tests']}")
        print(f"   总体成功率: {evaluation_results['overall_metrics']['overall_success_rate']:.1%}")
        print(f"   平均置信度: {evaluation_results['overall_metrics']['avg_confidence']:.3f}")
        print(f"   平均处理时间: {evaluation_results['overall_metrics']['avg_processing_time']:.3f}秒")
        
        return evaluation_results
    
    def generate_visualization(self, results: Dict):
        """生成可视化图表"""
        print("\\n📈 生成可视化图表...")
        
        # 创建图表目录
        charts_dir = self.results_dir / "charts"
        charts_dir.mkdir(exist_ok=True)
        
        # 1. 各退化类型的失败阈值对比
        degradation_types = list(results['summary_statistics'].keys())
        failure_thresholds = [
            results['summary_statistics'][dt]['failure_threshold'] or 100 
            for dt in degradation_types
        ]
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(degradation_types, failure_thresholds, 
                      color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'])
        plt.title('AI模型在不同退化类型下的失败阈值', fontsize=14, fontweight='bold')
        plt.xlabel('退化类型')
        plt.ylabel('失败阈值级别')
        plt.ylim(0, 100)
        
        # 添加数值标签
        for bar, value in zip(bars, failure_thresholds):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                    f'{int(value)}', ha='center', va='bottom', fontweight='bold')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(charts_dir / 'failure_thresholds.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. 成功率对比
        success_rates = [
            results['summary_statistics'][dt]['success_rate'] * 100
            for dt in degradation_types
        ]
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(degradation_types, success_rates,
                      color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'])
        plt.title('AI模型在不同退化类型下的成功率', fontsize=14, fontweight='bold')
        plt.xlabel('退化类型')
        plt.ylabel('成功率 (%)')
        plt.ylim(0, 100)
        
        # 添加数值标签
        for bar, value in zip(bars, success_rates):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                    f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(charts_dir / 'success_rates.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 图表保存到: {charts_dir}")
        
        return charts_dir

def main():
    """主函数 - 演示评估框架的使用"""
    evaluator = VisualBoundaryEvaluator()
    
    # 运行综合评估
    results = evaluator.run_comprehensive_evaluation()
    
    # 生成可视化图表
    evaluator.generate_visualization(results)
    
    print("\\n🎉 视觉边界评估演示完成!")

if __name__ == "__main__":
    main()