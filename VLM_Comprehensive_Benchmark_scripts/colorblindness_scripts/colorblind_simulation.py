#!/usr/bin/env python3
"""
色盲模拟算法
实现不同类型色盲的模拟，包括红绿色盲(protanopia, deuteranopia)和蓝黄色盲(tritanopia)
"""

import numpy as np
from PIL import Image
import colorsys
import json
from pathlib import Path

class ColorBlindnessSimulator:
    def __init__(self):
        """初始化色盲模拟器，包含不同色盲类型的变换矩阵"""
        
        # Protanopia (红色盲) 变换矩阵
        self.protanopia_matrix = np.array([
            [0.56667, 0.43333, 0.00000],
            [0.55833, 0.44167, 0.00000],
            [0.00000, 0.24167, 0.75833]
        ])
        
        # Deuteranopia (绿色盲) 变换矩阵
        self.deuteranopia_matrix = np.array([
            [0.62500, 0.37500, 0.00000],
            [0.70000, 0.30000, 0.00000],
            [0.00000, 0.30000, 0.70000]
        ])
        
        # Tritanopia (蓝色盲) 变换矩阵
        self.tritanopia_matrix = np.array([
            [0.95000, 0.05000, 0.00000],
            [0.00000, 0.43333, 0.56667],
            [0.00000, 0.47500, 0.52500]
        ])
        
        # 改进的变换矩阵（基于Machado等人的研究）
        self.improved_protanopia = np.array([
            [0.152286, 1.052583, -0.204868],
            [0.114503, 0.786281, 0.099216],
            [-0.003882, -0.048116, 1.051998]
        ])
        
        self.improved_deuteranopia = np.array([
            [0.367322, 0.860646, -0.227968],
            [0.280085, 0.672501, 0.047413],
            [-0.011820, 0.042940, 0.968881]
        ])
        
        self.improved_tritanopia = np.array([
            [1.255528, -0.076749, -0.178779],
            [-0.078411, 0.930809, 0.147602],
            [0.004733, 0.691367, 0.303900]
        ])
    
    def apply_colorblindness_matrix(self, image, matrix, severity=1.0):
        """应用色盲变换矩阵到图像
        
        Args:
            image: PIL Image对象
            matrix: 3x3变换矩阵
            severity: 色盲严重程度 (0.0-1.0)
        
        Returns:
            处理后的PIL Image对象
        """
        # 转换为numpy数组
        img_array = np.array(image, dtype=np.float32) / 255.0
        original_shape = img_array.shape
        
        # 确保是RGB格式
        if len(original_shape) == 3 and original_shape[2] == 3:
            # 重塑为(pixel_count, 3)
            pixels = img_array.reshape(-1, 3)
        else:
            raise ValueError("图像必须是RGB格式")
        
        # 应用变换矩阵
        transformed_pixels = np.dot(pixels, matrix.T)
        
        # 按严重程度混合原始和变换后的颜色
        if severity < 1.0:
            transformed_pixels = (1 - severity) * pixels + severity * transformed_pixels
        
        # 限制到有效范围并转换回uint8
        transformed_pixels = np.clip(transformed_pixels, 0, 1)
        transformed_image = (transformed_pixels * 255).astype(np.uint8)
        
        # 重塑回原始形状
        transformed_image = transformed_image.reshape(original_shape)
        
        return Image.fromarray(transformed_image)
    
    def simulate_protanopia(self, image, severity=1.0, improved=True):
        """模拟红色盲"""
        matrix = self.improved_protanopia if improved else self.protanopia_matrix
        return self.apply_colorblindness_matrix(image, matrix, severity)
    
    def simulate_deuteranopia(self, image, severity=1.0, improved=True):
        """模拟绿色盲"""
        matrix = self.improved_deuteranopia if improved else self.deuteranopia_matrix
        return self.apply_colorblindness_matrix(image, matrix, severity)
    
    def simulate_tritanopia(self, image, severity=1.0, improved=True):
        """模拟蓝色盲"""
        matrix = self.improved_tritanopia if improved else self.tritanopia_matrix
        return self.apply_colorblindness_matrix(image, matrix, severity)
    
    def simulate_protanomaly(self, image, severity=0.5):
        """模拟红色弱视"""
        return self.simulate_protanopia(image, severity)
    
    def simulate_deuteranomaly(self, image, severity=0.5):
        """模拟绿色弱视"""
        return self.simulate_deuteranopia(image, severity)
    
    def simulate_tritanomaly(self, image, severity=0.5):
        """模拟蓝色弱视"""
        return self.simulate_tritanopia(image, severity)
    
    def generate_gradients(self, image, colorblind_type, num_steps=100, output_dir="gradients"):
        """生成色盲模拟的渐变序列
        
        Args:
            image: 输入的PIL Image
            colorblind_type: 色盲类型 ('protanopia', 'deuteranopia', 'tritanopia')
            num_steps: 渐变步数
            output_dir: 输出目录
        
        Returns:
            生成的图像文件路径列表
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 获取模拟函数
        simulation_functions = {
            'protanopia': self.simulate_protanopia,
            'deuteranopia': self.simulate_deuteranopia,
            'tritanopia': self.simulate_tritanopia
        }
        
        if colorblind_type not in simulation_functions:
            raise ValueError(f"不支持的色盲类型: {colorblind_type}")
        
        sim_func = simulation_functions[colorblind_type]
        generated_files = []
        
        # 生成渐变序列
        for step in range(num_steps + 1):
            severity = step / num_steps  # 0.0 到 1.0
            
            # 应用色盲模拟
            simulated_image = sim_func(image, severity)
            
            # 保存图像
            filename = f"{colorblind_type}_severity_{step:03d}.png"
            filepath = output_path / filename
            simulated_image.save(filepath)
            generated_files.append(str(filepath))
        
        return generated_files
    
    def analyze_color_contrast(self, image, colorblind_type, severity=1.0):
        """分析色盲模拟后的颜色对比度"""
        # 模拟色盲
        sim_functions = {
            'protanopia': self.simulate_protanopia,
            'deuteranopia': self.simulate_deuteranopia,
            'tritanopia': self.simulate_tritanopia
        }
        
        simulated_image = sim_functions[colorblind_type](image, severity)
        
        # 转换为numpy数组
        original = np.array(image, dtype=np.float32) / 255.0
        simulated = np.array(simulated_image, dtype=np.float32) / 255.0
        
        # 计算颜色变化
        color_diff = np.mean(np.abs(original - simulated))
        
        # 计算对比度变化
        original_contrast = self.calculate_local_contrast(original)
        simulated_contrast = self.calculate_local_contrast(simulated)
        contrast_change = abs(original_contrast - simulated_contrast)
        
        return {
            "color_difference": float(color_diff),
            "original_contrast": float(original_contrast),
            "simulated_contrast": float(simulated_contrast),
            "contrast_change": float(contrast_change),
            "colorblind_type": colorblind_type,
            "severity": severity
        }
    
    def calculate_local_contrast(self, image_array):
        """计算图像的局部对比度"""
        # 转换为灰度
        if len(image_array.shape) == 3:
            gray = np.mean(image_array, axis=2)
        else:
            gray = image_array
        
        # 计算梯度
        grad_x = np.gradient(gray, axis=1)
        grad_y = np.gradient(gray, axis=0)
        
        # 计算梯度幅值
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # 返回平均对比度
        return np.mean(gradient_magnitude)
    
    def batch_process_images(self, input_dir, output_dir, colorblind_types=None, num_gradients=100):
        """批量处理图像"""
        if colorblind_types is None:
            colorblind_types = ['protanopia', 'deuteranopia', 'tritanopia']
        
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        results = []
        
        # 支持的图像格式
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
        
        for image_file in input_path.iterdir():
            if image_file.suffix.lower() in image_extensions:
                print(f"正在处理: {image_file.name}")
                
                try:
                    # 加载图像
                    image = Image.open(image_file).convert('RGB')
                    
                    # 为每种色盲类型生成渐变
                    for colorblind_type in colorblind_types:
                        type_output_dir = output_path / image_file.stem / colorblind_type
                        type_output_dir.mkdir(parents=True, exist_ok=True)
                        
                        # 生成渐变
                        generated_files = self.generate_gradients(
                            image, 
                            colorblind_type, 
                            num_gradients, 
                            str(type_output_dir)
                        )
                        
                        # 分析对比度变化
                        contrast_analysis = self.analyze_color_contrast(
                            image, colorblind_type, 1.0
                        )
                        
                        results.append({
                            "original_file": str(image_file),
                            "colorblind_type": colorblind_type,
                            "generated_files": generated_files,
                            "num_gradients": len(generated_files),
                            "contrast_analysis": contrast_analysis
                        })
                        
                        print(f"  ✓ {colorblind_type}: {len(generated_files)} 个渐变文件")
                
                except Exception as e:
                    print(f"  ✗ 处理失败: {e}")
        
        # 保存处理结果
        results_file = output_path / "processing_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n处理完成，结果保存到: {results_file}")
        return results


class ColorBlindnessMetrics:
    """色盲测试指标计算类"""
    
    def __init__(self):
        self.simulator = ColorBlindnessSimulator()
    
    def calculate_visibility_threshold(self, image, colorblind_type, target_region=None):
        """计算可见性阈值 - 在什么严重程度下目标变得不可见"""
        thresholds = []
        
        for severity in np.linspace(0, 1, 101):
            sim_image = getattr(self.simulator, f'simulate_{colorblind_type}')(image, severity)
            
            # 计算目标区域的可见性
            visibility_score = self.calculate_target_visibility(image, sim_image, target_region)
            
            if visibility_score < 0.1:  # 阈值可调
                return severity
        
        return 1.0  # 如果始终可见，返回最大值
    
    def calculate_target_visibility(self, original, simulated, target_region=None):
        """计算目标的可见性得分"""
        orig_array = np.array(original, dtype=np.float32)
        sim_array = np.array(simulated, dtype=np.float32)
        
        if target_region is None:
            # 如果没有指定目标区域，计算整体差异
            diff = np.mean(np.abs(orig_array - sim_array))
        else:
            # 计算指定区域的差异
            x1, y1, x2, y2 = target_region
            orig_region = orig_array[y1:y2, x1:x2]
            sim_region = sim_array[y1:y2, x1:x2]
            diff = np.mean(np.abs(orig_region - sim_region))
        
        return diff / 255.0  # 标准化到0-1范围


if __name__ == "__main__":
    # 测试代码
    simulator = ColorBlindnessSimulator()
    
    # 创建一个测试图像
    test_image = Image.new('RGB', (200, 200), (255, 0, 0))  # 红色图像
    
    # 模拟不同类型的色盲
    protanopia_result = simulator.simulate_protanopia(test_image)
    deuteranopia_result = simulator.simulate_deuteranopia(test_image)
    tritanopia_result = simulator.simulate_tritanopia(test_image)
    
    print("色盲模拟器测试完成")
    print("可用的模拟类型:")
    print("- protanopia (红色盲)")
    print("- deuteranopia (绿色盲)")
    print("- tritanopia (蓝色盲)")