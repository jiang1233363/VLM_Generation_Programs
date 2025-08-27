#!/usr/bin/env python3
"""
色盲数据集生成启动脚本
"""

import sys
from pathlib import Path

# 添加scripts目录到Python路径
scripts_dir = Path(__file__).parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from scripts.generate_dataset import ColorBlindnessDatasetGenerator

def main():
    print("🎨 色盲测试数据集生成器")
    print("=" * 50)
    
    # 检查依赖
    try:
        import numpy
        import PIL
        import requests
        print("✓ 依赖检查通过")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    # 创建生成器
    generator = ColorBlindnessDatasetGenerator(".")
    
    # 运行生成过程
    success = generator.run_complete_generation()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 数据集生成完成!")
        print("\n📊 数据集概览:")
        print("- 20+ 基础色盲测试图")
        print("- 3种色盲类型模拟 (红绿蓝)")
        print("- 每张图101个梯度级别 (0%-100%)")
        print("- 总计6000+张测试图像")
        print("\n📁 文件结构:")
        print("- data/raw/: 原始图像")
        print("- data/gradients/: 梯度图像")
        print("- metadata/: 元数据和测试用例")
        print("- docs/: 说明文档")
        return True
    else:
        print("\n❌ 数据集生成失败!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)