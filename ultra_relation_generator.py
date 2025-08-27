#!/usr/bin/env python3
"""
超高质量Relation数据生成器
使用SVG + 100梯度变化，确保兼容性和高质量
"""

import os
import json
import numpy as np
from pathlib import Path
from datetime import datetime
import random
import math
import colorsys
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import svgwrite
import cairosvg
import io

class UltraRelationGenerator:
    def __init__(self):
        self.base_path = Path("/home/jgy")
        self.output_path = self.base_path / "Ultra_Quality_Relation_Dataset"
        
        # 图片设置
        self.image_size = (512, 512)
        
        # 关系类型定义
        self.relation_types = {
            "spatial_relations": {"description": "空间位置关系", "target_count": 55},
            "proximity_relations": {"description": "距离关系", "target_count": 55},
            "alignment_relations": {"description": "对齐关系", "target_count": 55},
            "comparative_relations": {"description": "比较关系", "target_count": 55}
        }
        
        self.setup_directories()
        print("🎨 超高质量Relation数据生成器")
        print("SVG精确几何 + 100梯度变化")
        print("=" * 60)

    def setup_directories(self):
        """设置输出目录"""
        # 不删除现有目录，只创建缺失的目录
        self.output_path.mkdir(exist_ok=True)
        
        for rel_type in self.relation_types.keys():
            rel_path = self.output_path / rel_type
            rel_path.mkdir(exist_ok=True)
            (rel_path / "svg_sources").mkdir(exist_ok=True)
            (rel_path / "gradients").mkdir(exist_ok=True)
            (rel_path / "metadata").mkdir(exist_ok=True)

    def hsl_to_rgb(self, h, s, l):
        """将HSL转换为RGB字符串"""
        r, g, b = colorsys.hls_to_rgb(h/360, l/100, s/100)
        return f'rgb({int(r*255)}, {int(g*255)}, {int(b*255)})'

    def generate_spatial_relations(self):
        """生成空间关系"""
        print("\n🏠 生成空间关系数据...")
        
        spatial_path = self.output_path / "spatial_relations"
        relation_id = 1
        
        # 空间关系类型
        configs = [
            ("above_below", 13, "上下关系"),
            ("left_right", 13, "左右关系"), 
            ("inside_outside", 12, "内外关系"),
            ("overlapping", 12, "重叠关系"),
            ("touching", 0, "接触关系")
        ]
        
        for config_type, count, desc in configs:
            for i in range(count):
                svg_data, metadata = self.create_spatial_svg(relation_id, config_type, i)
                self.save_svg_and_gradients(svg_data, metadata, spatial_path, 
                                           f"{config_type}_{relation_id:03d}")
                relation_id += 1
        
        print(f"✅ 空间关系: {relation_id-1} 个关系，每个100梯度")

    def create_spatial_svg(self, rel_id, spatial_type, variant):
        """创建空间关系SVG"""
        svg = svgwrite.Drawing(size=self.image_size, profile='tiny')
        canvas_w, canvas_h = self.image_size
        
        if spatial_type == "above_below":
            # 精确的上下关系
            distance = 60 + variant * 12
            obj1_size = 30 + variant * 2
            obj2_size = 35 + variant * 1.5
            
            # 上方对象
            obj1_x = canvas_w // 2
            obj1_y = canvas_h // 3 - distance // 2
            svg.add(svg.circle(
                center=(obj1_x, obj1_y),
                r=obj1_size,
                fill=self.hsl_to_rgb(240 + variant * 8, 75, 60),
                stroke='black',
                stroke_width=2
            ))
            
            # 下方对象
            obj2_x = canvas_w // 2
            obj2_y = canvas_h // 3 * 2 + distance // 2
            svg.add(svg.rect(
                insert=(obj2_x - obj2_size, obj2_y - obj2_size//2),
                size=(obj2_size * 2, obj2_size),
                fill=self.hsl_to_rgb(120 + variant * 12, 75, 60),
                stroke='black',
                stroke_width=2
            ))
            
            # 添加空间关系标注
            if distance > 80:
                svg.add(svg.line(
                    start=(obj1_x + 40, obj1_y + obj1_size),
                    end=(obj2_x + 40, obj2_y - obj2_size//2),
                    stroke='gray',
                    stroke_width=1,
                    stroke_dasharray='3,3'
                ))
                
                mid_y = (obj1_y + obj1_size + obj2_y - obj2_size//2) // 2
                svg.add(svg.text(
                    f'{distance}px',
                    insert=(obj1_x + 50, mid_y),
                    font_size='12',
                    fill='gray'
                ))
            
            metadata = {
                "spatial_type": "above_below",
                "vertical_distance": distance,
                "upper_object": {"position": [obj1_x, obj1_y], "size": obj1_size},
                "lower_object": {"position": [obj2_x, obj2_y], "size": obj2_size}
            }
            
        elif spatial_type == "left_right":
            # 左右关系
            distance = 80 + variant * 15
            obj_size = 25 + variant * 2
            
            # 左侧对象
            left_x = canvas_w // 2 - distance // 2
            left_y = canvas_h // 2
            # 创建五角星
            points = []
            for i in range(10):
                angle = i * math.pi / 5
                radius = obj_size if i % 2 == 0 else obj_size // 2
                x = left_x + radius * math.cos(angle - math.pi/2)
                y = left_y + radius * math.sin(angle - math.pi/2)
                points.append((x, y))
            
            svg.add(svg.polygon(
                points=points,
                fill=self.hsl_to_rgb(0 + variant * 15, 80, 65),
                stroke='black',
                stroke_width=2
            ))
            
            # 右侧对象
            right_x = canvas_w // 2 + distance // 2
            right_y = canvas_h // 2
            svg.add(svg.rect(
                insert=(right_x - obj_size, right_y - obj_size),
                size=(obj_size * 2, obj_size * 2),
                fill=self.hsl_to_rgb(180 + variant * 10, 80, 65),
                stroke='black',
                stroke_width=2,
                rx=obj_size // 3  # 圆角
            ))
            
            metadata = {
                "spatial_type": "left_right",
                "horizontal_distance": distance,
                "left_object": {"position": [left_x, left_y], "type": "star"},
                "right_object": {"position": [right_x, right_y], "type": "rounded_rect"}
            }
            
        elif spatial_type == "inside_outside":
            # 内外关系
            outer_radius = 80 + variant * 6
            inner_size = 20 + variant * 3
            center_x, center_y = canvas_w // 2, canvas_h // 2
            
            # 外部圆环
            svg.add(svg.circle(
                center=(center_x, center_y),
                r=outer_radius,
                fill='none',
                stroke=self.hsl_to_rgb(300 + variant * 8, 70, 55),
                stroke_width=6
            ))
            
            # 内部对象（稍微偏移以测试边界情况）
            offset_x = (variant - 5) * 4
            offset_y = (variant - 5) * 3
            inner_x = center_x + offset_x
            inner_y = center_y + offset_y
            
            svg.add(svg.polygon(
                points=[
                    (inner_x, inner_y - inner_size),
                    (inner_x + inner_size, inner_y + inner_size//2),
                    (inner_x - inner_size, inner_y + inner_size//2)
                ],
                fill=self.hsl_to_rgb(60 + variant * 20, 85, 70),
                stroke='black',
                stroke_width=2
            ))
            
            # 检查是否真的在内部
            distance_from_center = math.sqrt(offset_x**2 + offset_y**2)
            is_inside = (distance_from_center + inner_size) < outer_radius
            
            metadata = {
                "spatial_type": "inside_outside",
                "outer_radius": outer_radius,
                "inner_size": inner_size,
                "offset": [offset_x, offset_y],
                "distance_from_center": distance_from_center,
                "is_actually_inside": is_inside
            }
            
        else:
            # 默认情况 - 重叠关系
            obj_size = 40 + variant * 3
            overlap_distance = 20 + variant * 5
            
            # 左侧对象
            obj1_x = canvas_w // 2 - overlap_distance
            obj1_y = canvas_h // 2
            svg.add(svg.circle(
                center=(obj1_x, obj1_y),
                r=obj_size,
                fill=self.hsl_to_rgb(45 + variant * 10, 75, 65),
                stroke='black',
                stroke_width=2,
                opacity=0.8
            ))
            
            # 右侧对象（重叠）
            obj2_x = canvas_w // 2 + overlap_distance
            obj2_y = canvas_h // 2
            svg.add(svg.circle(
                center=(obj2_x, obj2_y),
                r=obj_size,
                fill=self.hsl_to_rgb(225 + variant * 10, 75, 65),
                stroke='black',
                stroke_width=2,
                opacity=0.8
            ))
            
            metadata = {
                "spatial_type": "overlapping",
                "object_size": obj_size,
                "overlap_distance": overlap_distance,
                "object1_position": [obj1_x, obj1_y],
                "object2_position": [obj2_x, obj2_y]
            }
        
        # 通用元数据
        base_metadata = {
            "relation_type": "spatial_relations",
            "relation_id": rel_id,
            "variant": variant,
            "description": f"Spatial: {spatial_type} - variant {variant}",
            "canvas_size": self.image_size,
            "parameters": metadata,
            "difficulty": "medium"
        }
        
        return svg, base_metadata

    def generate_proximity_relations(self):
        """生成距离关系"""
        print("\n📏 生成距离关系数据...")
        
        proximity_path = self.output_path / "proximity_relations"
        relation_id = 1
        
        # 距离配置
        distance_configs = [
            ("very_close", 20, 50, 10),
            ("close", 50, 100, 10),
            ("medium", 100, 180, 10),
            ("far", 180, 280, 10),
            ("very_far", 280, 400, 10)
        ]
        
        for dist_name, min_d, max_d, count in distance_configs:
            for i in range(count):
                actual_distance = min_d + (max_d - min_d) * i / max(1, count - 1)
                svg_data, metadata = self.create_proximity_svg(
                    relation_id, dist_name, actual_distance, i)
                self.save_svg_and_gradients(svg_data, metadata, proximity_path,
                                          f"{dist_name}_{relation_id:03d}")
                relation_id += 1
        
        print(f"✅ 距离关系: {relation_id-1} 个关系，每个100梯度")

    def create_proximity_svg(self, rel_id, dist_type, distance, variant):
        """创建距离关系SVG"""
        svg = svgwrite.Drawing(size=self.image_size, profile='tiny')
        canvas_w, canvas_h = self.image_size
        
        obj_size = 22 + variant % 8
        center_x, center_y = canvas_w // 2, canvas_h // 2
        
        # 对象1 - 左侧
        obj1_x = center_x - distance // 2
        obj1_y = center_y
        
        # 创建六边形
        hexagon_points = []
        for i in range(6):
            angle = i * math.pi / 3
            x = obj1_x + obj_size * math.cos(angle)
            y = obj1_y + obj_size * math.sin(angle)
            hexagon_points.append((x, y))
        
        svg.add(svg.polygon(
            points=hexagon_points,
            fill=self.hsl_to_rgb(30 + variant * 12, 85, 65),
            stroke='black',
            stroke_width=2
        ))
        
        # 对象2 - 右侧
        obj2_x = center_x + distance // 2
        obj2_y = center_y
        
        svg.add(svg.ellipse(
            center=(obj2_x, obj2_y),
            r=(obj_size * 1.2, obj_size * 0.8),
            fill=self.hsl_to_rgb(200 + variant * 8, 85, 65),
            stroke='black',
            stroke_width=2
        ))
        
        # 距离测量线
        if distance > 70:
            y_line = center_y + obj_size + 15
            svg.add(svg.line(
                start=(obj1_x, y_line),
                end=(obj2_x, y_line),
                stroke='darkgray',
                stroke_width=2
            ))
            
            # 距离标记
            svg.add(svg.text(
                f'{distance:.0f}px',
                insert=(center_x, y_line - 5),
                text_anchor='middle',
                font_size='14',
                font_weight='bold',
                fill='darkgray'
            ))
            
            # 端点标记
            svg.add(svg.line(
                start=(obj1_x, y_line - 5),
                end=(obj1_x, y_line + 5),
                stroke='darkgray',
                stroke_width=2
            ))
            svg.add(svg.line(
                start=(obj2_x, y_line - 5),
                end=(obj2_x, y_line + 5),
                stroke='darkgray',
                stroke_width=2
            ))
        
        metadata = {
            "relation_type": "proximity_relations",
            "relation_id": rel_id,
            "variant": variant,
            "description": f"Proximity: {dist_type} - distance {distance:.0f}px",
            "parameters": {
                "distance_type": dist_type,
                "actual_distance": distance,
                "object1_position": [obj1_x, obj1_y],
                "object2_position": [obj2_x, obj2_y],
                "object_size": obj_size
            },
            "difficulty": "easy" if distance < 120 else "medium"
        }
        
        return svg, metadata

    def generate_alignment_relations(self):
        """生成对齐关系"""
        print("\n📐 生成对齐关系数据...")
        
        alignment_path = self.output_path / "alignment_relations"
        relation_id = 1
        
        # 对齐配置
        alignment_configs = [
            ("horizontal_perfect", 10),
            ("horizontal_imperfect", 10),
            ("vertical_perfect", 10),
            ("vertical_imperfect", 10),
            ("circular_arrangement", 10),
            ("diagonal_line", 0)
        ]
        
        for align_type, count in alignment_configs:
            for i in range(count):
                svg_data, metadata = self.create_alignment_svg(relation_id, align_type, i)
                self.save_svg_and_gradients(svg_data, metadata, alignment_path,
                                          f"{align_type}_{relation_id:03d}")
                relation_id += 1
        
        print(f"✅ 对齐关系: {relation_id-1} 个关系，每个100梯度")

    def create_alignment_svg(self, rel_id, align_type, variant):
        """创建对齐关系SVG"""
        svg = svgwrite.Drawing(size=self.image_size, profile='tiny')
        canvas_w, canvas_h = self.image_size
        obj_size = 18
        
        if "horizontal" in align_type:
            # 水平对齐
            num_objects = 4 + variant % 3
            base_y = canvas_h // 2
            
            # 完美对齐 vs 不完美对齐
            if "perfect" in align_type:
                y_deviation = 0
            else:
                y_deviation = variant * 4 - 16  # -16 to +16 像素偏差
            
            spacing = (canvas_w - 120) // max(1, num_objects - 1)
            
            for i in range(num_objects):
                x_pos = 60 + i * spacing
                y_pos = base_y + (random.randint(-1, 1) * y_deviation // 2 if i > 0 else 0)
                
                # 不同形状的对象
                shape_type = i % 4
                color_hue = (i * 70 + variant * 15) % 360
                
                if shape_type == 0:  # 圆形
                    svg.add(svg.circle(
                        center=(x_pos, y_pos),
                        r=obj_size,
                        fill=self.hsl_to_rgb(color_hue, 75, 65),
                        stroke='black',
                        stroke_width=2
                    ))
                elif shape_type == 1:  # 正方形
                    svg.add(svg.rect(
                        insert=(x_pos - obj_size, y_pos - obj_size),
                        size=(obj_size * 2, obj_size * 2),
                        fill=self.hsl_to_rgb(color_hue, 75, 65),
                        stroke='black',
                        stroke_width=2
                    ))
                elif shape_type == 2:  # 三角形
                    points = [
                        (x_pos, y_pos - obj_size),
                        (x_pos - obj_size, y_pos + obj_size),
                        (x_pos + obj_size, y_pos + obj_size)
                    ]
                    svg.add(svg.polygon(
                        points=points,
                        fill=self.hsl_to_rgb(color_hue, 75, 65),
                        stroke='black',
                        stroke_width=2
                    ))
                else:  # 菱形
                    points = [
                        (x_pos, y_pos - obj_size),
                        (x_pos + obj_size, y_pos),
                        (x_pos, y_pos + obj_size),
                        (x_pos - obj_size, y_pos)
                    ]
                    svg.add(svg.polygon(
                        points=points,
                        fill=self.hsl_to_rgb(color_hue, 75, 65),
                        stroke='black',
                        stroke_width=2
                    ))
            
            # 参考线
            svg.add(svg.line(
                start=(40, base_y),
                end=(canvas_w - 40, base_y),
                stroke='lightgray',
                stroke_width=1,
                stroke_dasharray='5,5',
                opacity=0.7
            ))
            
            metadata = {
                "alignment_type": "horizontal",
                "num_objects": num_objects,
                "reference_y": base_y,
                "y_deviation": abs(y_deviation),
                "perfect_alignment": "perfect" in align_type
            }
            
        elif align_type == "circular_arrangement":
            # 圆形排列
            num_objects = 5 + variant % 4
            center_x, center_y = canvas_w // 2, canvas_h // 2
            radius = 70 + variant * 6
            
            for i in range(num_objects):
                angle = 2 * math.pi * i / num_objects + variant * 0.02  # 轻微角度偏移
                x_pos = center_x + radius * math.cos(angle)
                y_pos = center_y + radius * math.sin(angle)
                
                # 根据角度选择颜色
                color_hue = (i * 360 // num_objects + variant * 10) % 360
                
                svg.add(svg.circle(
                    center=(x_pos, y_pos),
                    r=obj_size,
                    fill=self.hsl_to_rgb(color_hue, 80, 70),
                    stroke='black',
                    stroke_width=2
                ))
            
            # 中心标记
            svg.add(svg.circle(
                center=(center_x, center_y),
                r=3,
                fill='red',
                opacity=0.8
            ))
            
            # 参考圆
            svg.add(svg.circle(
                center=(center_x, center_y),
                r=radius,
                fill='none',
                stroke='lightgray',
                stroke_width=1,
                stroke_dasharray='4,4',
                opacity=0.6
            ))
            
            metadata = {
                "alignment_type": "circular",
                "num_objects": num_objects,
                "center": [center_x, center_y],
                "radius": radius,
                "angle_deviation": variant * 0.02
            }
            
        else:
            # 默认情况 - 对角线排列
            num_objects = 4
            
            for i in range(num_objects):
                x_pos = 80 + i * 100
                y_pos = 80 + i * 100 + variant * 10
                
                svg.add(svg.circle(
                    center=(x_pos, y_pos),
                    r=obj_size,
                    fill=self.hsl_to_rgb(i * 60 + variant * 15, 75, 65),
                    stroke='black',
                    stroke_width=2
                ))
            
            metadata = {
                "alignment_type": "diagonal",
                "num_objects": num_objects,
                "diagonal_offset": variant * 10
            }
        
        base_metadata = {
            "relation_type": "alignment_relations",
            "relation_id": rel_id,
            "variant": variant,
            "description": f"Alignment: {align_type} - variant {variant}",
            "parameters": metadata,
            "difficulty": "medium" if "imperfect" in align_type else "easy"
        }
        
        return svg, base_metadata

    def generate_comparative_relations(self):
        """生成比较关系"""
        print("\n⚖️ 生成比较关系数据...")
        
        comparative_path = self.output_path / "comparative_relations"
        relation_id = 1
        
        # 比较配置
        comparison_configs = [
            ("size_bigger_smaller", 13),
            ("color_darker_lighter", 13),
            ("quantity_more_fewer", 12),
            ("brightness_comparison", 12)
        ]
        
        for comp_type, count in comparison_configs:
            for i in range(count):
                svg_data, metadata = self.create_comparison_svg(relation_id, comp_type, i)
                self.save_svg_and_gradients(svg_data, metadata, comparative_path,
                                          f"{comp_type}_{relation_id:03d}")
                relation_id += 1
        
        print(f"✅ 比较关系: {relation_id-1} 个关系，每个100梯度")

    def create_comparison_svg(self, rel_id, comp_type, variant):
        """创建比较关系SVG"""
        svg = svgwrite.Drawing(size=self.image_size, profile='tiny')
        canvas_w, canvas_h = self.image_size
        center_y = canvas_h // 2
        
        if comp_type == "size_bigger_smaller":
            # 大小比较
            small_size = 20 + variant * 2
            large_size = 40 + variant * 4
            
            # 确保有明显差异
            if large_size - small_size < 15:
                large_size = small_size + 15 + variant * 2
            
            # 小对象
            small_x = canvas_w // 3
            svg.add(svg.circle(
                center=(small_x, center_y),
                r=small_size,
                fill=self.hsl_to_rgb(220, 80, 65),
                stroke='black',
                stroke_width=3
            ))
            
            # 大对象
            large_x = canvas_w // 3 * 2
            svg.add(svg.circle(
                center=(large_x, center_y),
                r=large_size,
                fill=self.hsl_to_rgb(220, 80, 65),
                stroke='black',
                stroke_width=3
            ))
            
            # 比较标记
            mid_x = (small_x + large_x) // 2
            svg.add(svg.text(
                '<',
                insert=(mid_x, center_y + 8),
                text_anchor='middle',
                font_size='32',
                font_weight='bold',
                fill='darkred'
            ))
            
            # 尺寸标注
            svg.add(svg.text(
                f'r={small_size}',
                insert=(small_x, center_y + small_size + 25),
                text_anchor='middle',
                font_size='12',
                fill='gray'
            ))
            svg.add(svg.text(
                f'r={large_size}',
                insert=(large_x, center_y + large_size + 25),
                text_anchor='middle',
                font_size='12',
                fill='gray'
            ))
            
            metadata = {
                "comparison_type": "size",
                "small_radius": small_size,
                "large_radius": large_size,
                "size_ratio": large_size / small_size,
                "size_difference": large_size - small_size
            }
            
        elif comp_type == "quantity_more_fewer":
            # 数量比较
            few_count = 2 + variant % 3
            many_count = 8 + variant % 6
            obj_size = 12
            
            # 少数组
            few_x = canvas_w // 3
            for i in range(few_count):
                y_offset = (i - few_count // 2) * (obj_size * 3)
                svg.add(svg.circle(
                    center=(few_x, center_y + y_offset),
                    r=obj_size,
                    fill=self.hsl_to_rgb(120, 75, 60),
                    stroke='black',
                    stroke_width=2
                ))
            
            # 多数组 - 网格排列
            many_x = canvas_w // 3 * 2
            cols = int(math.ceil(math.sqrt(many_count)))
            rows = int(math.ceil(many_count / cols))
            
            grid_width = cols * (obj_size * 2.5)
            grid_height = rows * (obj_size * 2.5)
            
            for i in range(many_count):
                row = i // cols
                col = i % cols
                x_offset = (col - cols // 2) * (obj_size * 2.5)
                y_offset = (row - rows // 2) * (obj_size * 2.5)
                
                svg.add(svg.circle(
                    center=(many_x + x_offset, center_y + y_offset),
                    r=obj_size,
                    fill=self.hsl_to_rgb(120, 75, 60),
                    stroke='black',
                    stroke_width=2
                ))
            
            # 数量标注
            svg.add(svg.text(
                str(few_count),
                insert=(few_x, center_y + 60),
                text_anchor='middle',
                font_size='24',
                font_weight='bold',
                fill='darkgreen'
            ))
            svg.add(svg.text(
                str(many_count),
                insert=(many_x, center_y + 60),
                text_anchor='middle',
                font_size='24',
                font_weight='bold',
                fill='darkgreen'
            ))
            
            metadata = {
                "comparison_type": "quantity",
                "few_count": few_count,
                "many_count": many_count,
                "quantity_ratio": many_count / few_count,
                "difference": many_count - few_count
            }
            
        else:
            # 默认情况 - 颜色比较
            obj_size = 30
            left_x = canvas_w // 3
            right_x = canvas_w // 3 * 2
            
            # 浅色对象
            light_lightness = 80 + variant % 15
            svg.add(svg.circle(
                center=(left_x, center_y),
                r=obj_size,
                fill=self.hsl_to_rgb(200, 70, light_lightness),
                stroke='black',
                stroke_width=2
            ))
            
            # 深色对象
            dark_lightness = 20 + variant % 15
            svg.add(svg.circle(
                center=(right_x, center_y),
                r=obj_size,
                fill=self.hsl_to_rgb(200, 70, dark_lightness),
                stroke='black',
                stroke_width=2
            ))
            
            metadata = {
                "comparison_type": "brightness",
                "light_lightness": light_lightness,
                "dark_lightness": dark_lightness,
                "lightness_difference": light_lightness - dark_lightness
            }
        
        base_metadata = {
            "relation_type": "comparative_relations",
            "relation_id": rel_id,
            "variant": variant,
            "description": f"Comparison: {comp_type} - variant {variant}",
            "parameters": metadata,
            "difficulty": "medium"
        }
        
        return svg, base_metadata

    def save_svg_and_gradients(self, svg_data, metadata, category_path, base_name):
        """保存SVG并生成100个梯度变化"""
        # 保存SVG源文件
        svg_path = category_path / "svg_sources" / f"{base_name}.svg"
        svg_data.saveas(str(svg_path))
        
        # 创建梯度目录
        gradient_dir = category_path / "gradients" / base_name
        gradient_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"    🎨 {base_name}: 生成100个梯度变化...")
        
        # 生成100个梯度变化
        for i in range(100):
            intensity = i / 99.0
            
            # 应用梯度效果
            modified_image = self.apply_gradient_effects(svg_path, intensity, i)
            
            # 保存图片
            img_path = gradient_dir / f"gradient_{i:03d}.png"
            modified_image.save(img_path, "PNG")
            
            # 保存梯度元数据
            gradient_metadata = metadata.copy()
            gradient_metadata.update({
                "gradient_level": i,
                "gradient_intensity": intensity,
                "effect_type": self.get_effect_type(i),
                "image_path": str(img_path),
                "svg_source": str(svg_path)
            })
            
            meta_path = gradient_dir / f"gradient_{i:03d}_params.json"
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(gradient_metadata, f, indent=2, ensure_ascii=False)

    def apply_gradient_effects(self, svg_path, intensity, level):
        """应用梯度效果"""
        # 转换SVG为PNG
        try:
            png_data = cairosvg.svg2png(url=str(svg_path), output_width=512, output_height=512)
            base_image = Image.open(io.BytesIO(png_data)).convert('RGB')
        except Exception as e:
            print(f"      ⚠️ SVG转换失败: {e}")
            # 创建白色背景图片作为备选
            base_image = Image.new('RGB', (512, 512), 'white')
        
        # 根据级别应用不同效果
        effect_type = self.get_effect_type(level)
        
        if effect_type == "original":
            return base_image
        elif effect_type == "brightness":
            enhancer = ImageEnhance.Brightness(base_image)
            factor = 0.3 + intensity * 1.4
            return enhancer.enhance(factor)
        elif effect_type == "contrast":
            enhancer = ImageEnhance.Contrast(base_image)
            factor = 0.2 + intensity * 1.6
            return enhancer.enhance(factor)
        elif effect_type == "color":
            enhancer = ImageEnhance.Color(base_image)
            factor = 0.1 + intensity * 1.8
            return enhancer.enhance(factor)
        elif effect_type == "blur":
            radius = intensity * 5
            return base_image.filter(ImageFilter.GaussianBlur(radius=radius))
        elif effect_type == "noise":
            img_array = np.array(base_image)
            noise = np.random.normal(0, intensity * 25, img_array.shape)
            noisy = np.clip(img_array + noise, 0, 255).astype(np.uint8)
            return Image.fromarray(noisy)
        
        return base_image

    def get_effect_type(self, level):
        """根据级别确定效果类型"""
        if level < 5:
            return "original"
        elif level < 25:
            return "brightness"
        elif level < 45:
            return "contrast"
        elif level < 65:
            return "color"
        elif level < 85:
            return "blur"
        else:
            return "noise"

    def generate_all_relations(self):
        """生成所有关系数据"""
        print("🚀 开始生成超高质量Relation数据集")
        print("SVG精确几何 + 每个关系100个梯度变化")
        print("=" * 60)
        
        self.generate_spatial_relations()
        self.generate_proximity_relations()
        self.generate_alignment_relations()
        self.generate_comparative_relations()
        
        self.generate_statistics()
        
        print("\n" + "=" * 60)
        print("🎉 超高质量Relation数据集生成完成！")
        print(f"📁 输出: {self.output_path}")

    def generate_statistics(self):
        """生成统计信息"""
        print("\n📊 统计生成结果...")
        
        total_relations = 0
        total_images = 0
        stats = {}
        
        for category in self.relation_types.keys():
            category_path = self.output_path / category
            if category_path.exists():
                svg_count = len(list((category_path / "svg_sources").glob("*.svg")))
                gradient_count = svg_count * 100
                
                stats[category] = {
                    "relations": svg_count,
                    "gradients": gradient_count,
                    "description": self.relation_types[category]["description"]
                }
                
                total_relations += svg_count
                total_images += gradient_count
                
                print(f"  ✅ {category}: {svg_count} 关系, {gradient_count:,} 图片")
        
        # 保存统计
        final_stats = {
            "dataset_name": "Ultra Quality Relation Dataset",
            "creation_date": datetime.now().isoformat(),
            "total_relations": total_relations,
            "total_images": total_images,
            "gradients_per_relation": 100,
            "categories": stats,
            "technology": ["SVG Precision", "100 Gradients", "6 Effect Types"],
            "achievement": f"✅ 每个关系都有100个高质量梯度变化"
        }
        
        with open(self.output_path / "ULTRA_DATASET_STATS.json", 'w', encoding='utf-8') as f:
            json.dump(final_stats, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎯 总计: {total_relations} 个关系, {total_images:,} 张超高质量图片")
        return final_stats

def main():
    generator = UltraRelationGenerator()
    stats = generator.generate_all_relations()
    
    print(f"\n🌟 恭喜！超高质量Relation数据集已完成！")
    print(f"📊 包含 {stats['total_relations']} 个精确关系")
    print(f"🎨 生成 {stats['total_images']:,} 张高质量图片") 
    print(f"💯 每个关系都有100个梯度变化，质量保证！")

if __name__ == "__main__":
    main()