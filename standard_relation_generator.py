#!/usr/bin/env python3
"""
标准版本关系生成器 - 每类25个关系，每个50梯度
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

class StandardRelationGenerator:
    def __init__(self):
        self.base_path = Path("/home/jgy")
        self.output_path = self.base_path / "Standard_Quality_Relation_Dataset"
        
        # 标准设置
        self.image_size = (512, 512)
        self.gradients_per_relation = 50  # 减少到50个梯度
        
        # 关系类型定义 - 每类25个
        self.relation_types = {
            "spatial_relations": {"description": "空间位置关系", "target_count": 25},
            "proximity_relations": {"description": "距离关系", "target_count": 25}, 
            "alignment_relations": {"description": "对齐关系", "target_count": 25},
            "comparative_relations": {"description": "比较关系", "target_count": 25}
        }
        
        self.setup_directories()
        print("🎨 标准版关系数据生成器")
        print("每类25个关系，每个50梯度变化")
        print("=" * 50)

    def setup_directories(self):
        if self.output_path.exists():
            import shutil
            shutil.rmtree(self.output_path)
        
        self.output_path.mkdir()
        
        for rel_type in self.relation_types.keys():
            rel_path = self.output_path / rel_type
            rel_path.mkdir()
            (rel_path / "svg_sources").mkdir()
            (rel_path / "gradients").mkdir()
            (rel_path / "metadata").mkdir()

    def hsl_to_rgb(self, h, s, l):
        r, g, b = colorsys.hls_to_rgb(h/360, l/100, s/100)
        return f'rgb({int(r*255)}, {int(g*255)}, {int(b*255)})'

    def generate_spatial_relations(self):
        print("\n🏠 生成空间关系数据...")
        spatial_path = self.output_path / "spatial_relations"
        relation_id = 1
        
        # 空间关系类型 - 总共25个
        configs = [
            ("above_below", 8),
            ("left_right", 8), 
            ("inside_outside", 5),
            ("overlapping", 4)
        ]
        
        for config_type, count in configs:
            for i in range(count):
                svg_data, metadata = self.create_spatial_svg(relation_id, config_type, i)
                self.save_svg_and_gradients(svg_data, metadata, spatial_path, 
                                           f"{config_type}_{relation_id:03d}")
                relation_id += 1
        
        print(f"✅ 空间关系: {relation_id-1} 个关系，每个50梯度")

    def create_spatial_svg(self, rel_id, spatial_type, variant):
        svg = svgwrite.Drawing(size=self.image_size, profile='tiny')
        canvas_w, canvas_h = self.image_size
        
        if spatial_type == "above_below":
            distance = 50 + variant * 15
            circle_radius = 25 + variant * 3
            rect_size = 40 + variant * 5
            
            # 上方圆形
            circle_x, circle_y = canvas_w // 2, canvas_h // 3 - distance // 2
            svg.add(svg.circle(
                center=(circle_x, circle_y),
                r=circle_radius,
                fill=self.hsl_to_rgb(200 + variant * 20, 75, 60),
                stroke='black', stroke_width=2
            ))
            
            # 下方矩形
            rect_x = canvas_w // 2 - rect_size // 2
            rect_y = canvas_h // 3 * 2 + distance // 2
            svg.add(svg.rect(
                insert=(rect_x, rect_y),
                size=(rect_size, rect_size // 2),
                fill=self.hsl_to_rgb(120 + variant * 15, 75, 60),
                stroke='black', stroke_width=2
            ))
            
            metadata = {
                "spatial_type": "above_below",
                "vertical_distance": distance,
                "circle_radius": circle_radius,
                "rectangle_size": rect_size
            }
            
        elif spatial_type == "left_right":
            distance = 60 + variant * 10
            size = 30 + variant * 3
            
            # 左边三角形
            left_x, left_y = canvas_w // 2 - distance // 2, canvas_h // 2
            points = []
            for i in range(3):
                angle = i * 2 * math.pi / 3 - math.pi / 2
                x = left_x + size * math.cos(angle)
                y = left_y + size * math.sin(angle)
                points.append((x, y))
            
            svg.add(svg.polygon(
                points=points,
                fill=self.hsl_to_rgb(0 + variant * 30, 80, 65),
                stroke='black', stroke_width=2
            ))
            
            # 右边圆形
            right_x, right_y = canvas_w // 2 + distance // 2, canvas_h // 2
            svg.add(svg.circle(
                center=(right_x, right_y),
                r=size,
                fill=self.hsl_to_rgb(180 + variant * 25, 80, 65),
                stroke='black', stroke_width=2
            ))
            
            metadata = {
                "spatial_type": "left_right",
                "horizontal_distance": distance,
                "object_size": size
            }
        else:
            metadata = {"spatial_type": "unknown"}
        
        base_metadata = {
            "relation_type": "spatial_relations",
            "relation_id": rel_id,
            "variant": variant,
            "description": f"Spatial: {spatial_type} - variant {variant}",
            "parameters": metadata,
            "difficulty": "medium"
        }
        
        return svg, base_metadata

    def generate_proximity_relations(self):
        print("\n📏 生成距离关系数据...")
        proximity_path = self.output_path / "proximity_relations"
        relation_id = 1
        
        distance_configs = [
            ("very_close", 20, 50, 6),
            ("close", 50, 100, 6),
            ("medium", 100, 180, 7),
            ("far", 180, 280, 6)
        ]
        
        for dist_name, min_d, max_d, count in distance_configs:
            for i in range(count):
                actual_distance = min_d + (max_d - min_d) * i / max(1, count - 1)
                svg_data, metadata = self.create_proximity_svg(
                    relation_id, dist_name, actual_distance, i)
                self.save_svg_and_gradients(svg_data, metadata, proximity_path,
                                          f"{dist_name}_{relation_id:03d}")
                relation_id += 1
        
        print(f"✅ 距离关系: {relation_id-1} 个关系，每个50梯度")

    def create_proximity_svg(self, rel_id, dist_type, distance, variant):
        svg = svgwrite.Drawing(size=self.image_size, profile='tiny')
        canvas_w, canvas_h = self.image_size
        
        obj_size = 25
        center_x, center_y = canvas_w // 2, canvas_h // 2
        
        # 对象1 - 左侧六边形
        obj1_x = center_x - distance // 2
        obj1_y = center_y
        
        hexagon_points = []
        for i in range(6):
            angle = i * math.pi / 3
            x = obj1_x + obj_size * math.cos(angle)
            y = obj1_y + obj_size * math.sin(angle)
            hexagon_points.append((x, y))
        
        svg.add(svg.polygon(
            points=hexagon_points,
            fill=self.hsl_to_rgb(30 + variant * 15, 85, 65),
            stroke='black', stroke_width=2
        ))
        
        # 对象2 - 右侧椭圆
        obj2_x = center_x + distance // 2
        obj2_y = center_y
        
        svg.add(svg.ellipse(
            center=(obj2_x, obj2_y),
            r=(obj_size * 1.2, obj_size * 0.8),
            fill=self.hsl_to_rgb(200 + variant * 10, 85, 65),
            stroke='black', stroke_width=2
        ))
        
        metadata = {
            "relation_type": "proximity_relations",
            "relation_id": rel_id,
            "variant": variant,
            "description": f"Proximity: {dist_type} - distance {distance:.0f}",
            "parameters": {
                "distance_type": dist_type,
                "actual_distance": distance,
                "object_size": obj_size,
                "positions": [[obj1_x, obj1_y], [obj2_x, obj2_y]]
            },
            "difficulty": "easy" if distance < 100 else "medium"
        }
        
        return svg, metadata

    def generate_alignment_relations(self):
        print("\n📐 生成对齐关系数据...")
        alignment_path = self.output_path / "alignment_relations"
        relation_id = 1
        
        alignment_configs = [
            ("horizontal_perfect", 6),
            ("horizontal_imperfect", 4),
            ("vertical_perfect", 6),
            ("vertical_imperfect", 4),
            ("circular_arrangement", 5)
        ]
        
        for align_type, count in alignment_configs:
            for i in range(count):
                svg_data, metadata = self.create_alignment_svg(relation_id, align_type, i)
                self.save_svg_and_gradients(svg_data, metadata, alignment_path,
                                          f"{align_type}_{relation_id:03d}")
                relation_id += 1
        
        print(f"✅ 对齐关系: {relation_id-1} 个关系，每个50梯度")

    def create_alignment_svg(self, rel_id, align_type, variant):
        svg = svgwrite.Drawing(size=self.image_size, profile='tiny')
        canvas_w, canvas_h = self.image_size
        obj_size = 18
        
        if "horizontal" in align_type:
            num_objects = 4 + variant % 3
            base_y = canvas_h // 2
            
            if "perfect" in align_type:
                y_deviation = 0
            else:
                y_deviation = variant * 6 - 12
            
            spacing = (canvas_w - 120) // max(1, num_objects - 1)
            
            for i in range(num_objects):
                x_pos = 60 + i * spacing
                y_pos = base_y + (random.randint(-1, 1) * y_deviation // 2 if i > 0 else 0)
                
                color_hue = (i * 70 + variant * 20) % 360
                
                if i % 2 == 0:
                    svg.add(svg.circle(
                        center=(x_pos, y_pos),
                        r=obj_size,
                        fill=self.hsl_to_rgb(color_hue, 75, 65),
                        stroke='black', stroke_width=2
                    ))
                else:
                    svg.add(svg.rect(
                        insert=(x_pos - obj_size, y_pos - obj_size),
                        size=(obj_size * 2, obj_size * 2),
                        fill=self.hsl_to_rgb(color_hue, 75, 65),
                        stroke='black', stroke_width=2
                    ))
            
            metadata = {
                "alignment_type": "horizontal",
                "num_objects": num_objects,
                "reference_y": base_y,
                "y_deviation": abs(y_deviation),
                "perfect_alignment": "perfect" in align_type
            }
            
        elif align_type == "circular_arrangement":
            num_objects = 5 + variant % 3
            center_x, center_y = canvas_w // 2, canvas_h // 2
            radius = 60 + variant * 8
            
            for i in range(num_objects):
                angle = 2 * math.pi * i / num_objects + variant * 0.03
                x_pos = center_x + radius * math.cos(angle)
                y_pos = center_y + radius * math.sin(angle)
                
                color_hue = (i * 360 // num_objects + variant * 15) % 360
                
                svg.add(svg.circle(
                    center=(x_pos, y_pos),
                    r=obj_size,
                    fill=self.hsl_to_rgb(color_hue, 80, 70),
                    stroke='black', stroke_width=2
                ))
            
            metadata = {
                "alignment_type": "circular",
                "num_objects": num_objects,
                "center": [center_x, center_y],
                "radius": radius,
                "angle_offset": variant * 0.03
            }
        elif "vertical" in align_type:
            num_objects = 4 + variant % 3
            base_x = canvas_w // 2
            
            if "perfect" in align_type:
                x_deviation = 0
            else:
                x_deviation = variant * 6 - 12
            
            spacing = (canvas_h - 120) // max(1, num_objects - 1)
            
            for i in range(num_objects):
                y_pos = 60 + i * spacing
                x_pos = base_x + (random.randint(-1, 1) * x_deviation // 2 if i > 0 else 0)
                
                color_hue = (i * 70 + variant * 20) % 360
                
                if i % 2 == 0:
                    svg.add(svg.circle(
                        center=(x_pos, y_pos),
                        r=obj_size,
                        fill=self.hsl_to_rgb(color_hue, 75, 65),
                        stroke='black', stroke_width=2
                    ))
                else:
                    svg.add(svg.rect(
                        insert=(x_pos - obj_size, y_pos - obj_size),
                        size=(obj_size * 2, obj_size * 2),
                        fill=self.hsl_to_rgb(color_hue, 75, 65),
                        stroke='black', stroke_width=2
                    ))
            
            metadata = {
                "alignment_type": "vertical",
                "num_objects": num_objects,
                "reference_x": base_x,
                "x_deviation": abs(x_deviation),
                "perfect_alignment": "perfect" in align_type
            }
        else:
            metadata = {"alignment_type": "unknown"}
        
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
        print("\n⚖️ 生成比较关系数据...")
        comparative_path = self.output_path / "comparative_relations"
        relation_id = 1
        
        comparison_configs = [
            ("size_bigger_smaller", 8),
            ("color_darker_lighter", 8),
            ("quantity_more_fewer", 9)
        ]
        
        for comp_type, count in comparison_configs:
            for i in range(count):
                svg_data, metadata = self.create_comparison_svg(relation_id, comp_type, i)
                self.save_svg_and_gradients(svg_data, metadata, comparative_path,
                                          f"{comp_type}_{relation_id:03d}")
                relation_id += 1
        
        print(f"✅ 比较关系: {relation_id-1} 个关系，每个50梯度")

    def create_comparison_svg(self, rel_id, comp_type, variant):
        svg = svgwrite.Drawing(size=self.image_size, profile='tiny')
        canvas_w, canvas_h = self.image_size
        center_y = canvas_h // 2
        
        if comp_type == "size_bigger_smaller":
            small_size = 20 + variant * 2
            large_size = 40 + variant * 4
            
            if large_size - small_size < 15:
                large_size = small_size + 15 + variant * 2
            
            # 小对象
            small_x = canvas_w // 3
            svg.add(svg.circle(
                center=(small_x, center_y),
                r=small_size,
                fill=self.hsl_to_rgb(220, 80, 65),
                stroke='black', stroke_width=3
            ))
            
            # 大对象
            large_x = canvas_w // 3 * 2
            svg.add(svg.circle(
                center=(large_x, center_y),
                r=large_size,
                fill=self.hsl_to_rgb(220, 80, 65),
                stroke='black', stroke_width=3
            ))
            
            metadata = {
                "comparison_type": "size",
                "small_size": small_size,
                "large_size": large_size,
                "size_ratio": large_size / small_size,
                "size_difference": large_size - small_size
            }
            
        elif comp_type == "quantity_more_fewer":
            few_count = 2 + variant % 3
            many_count = 6 + variant % 4
            obj_size = 12
            
            # 少数组
            few_x = canvas_w // 3
            for i in range(few_count):
                y_offset = (i - few_count // 2) * (obj_size * 3)
                svg.add(svg.circle(
                    center=(few_x, center_y + y_offset),
                    r=obj_size,
                    fill=self.hsl_to_rgb(120, 75, 60),
                    stroke='black', stroke_width=2
                ))
            
            # 多数组
            many_x = canvas_w // 3 * 2
            cols = int(math.ceil(math.sqrt(many_count)))
            rows = int(math.ceil(many_count / cols))
            
            for i in range(many_count):
                row = i // cols
                col = i % cols
                x_offset = (col - cols // 2) * (obj_size * 2.5)
                y_offset = (row - rows // 2) * (obj_size * 2.5)
                
                svg.add(svg.circle(
                    center=(many_x + x_offset, center_y + y_offset),
                    r=obj_size,
                    fill=self.hsl_to_rgb(120, 75, 60),
                    stroke='black', stroke_width=2
                ))
            
            metadata = {
                "comparison_type": "quantity",
                "few_count": few_count,
                "many_count": many_count,
                "quantity_ratio": many_count / few_count,
                "difference": many_count - few_count
            }
        elif comp_type == "color_darker_lighter":
            obj_size = 30
            
            # 深色对象
            dark_x = canvas_w // 3
            dark_hue = 220 + variant * 10
            dark_lightness = 25 + variant * 5  # 较暗
            svg.add(svg.circle(
                center=(dark_x, center_y),
                r=obj_size,
                fill=self.hsl_to_rgb(dark_hue, 80, dark_lightness),
                stroke='black', stroke_width=3
            ))
            
            # 浅色对象
            light_x = canvas_w // 3 * 2
            light_lightness = 70 + variant * 5  # 较亮
            svg.add(svg.circle(
                center=(light_x, center_y),
                r=obj_size,
                fill=self.hsl_to_rgb(dark_hue, 80, light_lightness),
                stroke='black', stroke_width=3
            ))
            
            metadata = {
                "comparison_type": "color",
                "dark_lightness": dark_lightness,
                "light_lightness": light_lightness,
                "lightness_difference": light_lightness - dark_lightness,
                "hue": dark_hue
            }
        else:
            metadata = {"comparison_type": "unknown"}
        
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
        # 保存SVG源文件
        svg_path = category_path / "svg_sources" / f"{base_name}.svg"
        svg_data.saveas(str(svg_path))
        
        # 创建梯度目录
        gradient_dir = category_path / "gradients" / base_name
        gradient_dir.mkdir(exist_ok=True)
        
        print(f"    🎨 {base_name}: 生成50个梯度变化...")
        
        # 生成50个梯度变化（减少数量）
        for i in range(50):
            intensity = i / 49.0
            
            modified_image = self.apply_gradient_effects(svg_path, intensity, i)
            
            img_path = gradient_dir / f"gradient_{i:03d}.png"
            modified_image.save(img_path, "PNG")
            
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
        try:
            png_data = cairosvg.svg2png(url=str(svg_path), output_width=512, output_height=512)
            base_image = Image.open(io.BytesIO(png_data)).convert('RGB')
        except Exception as e:
            print(f"      ⚠️ SVG转换失败: {e}")
            base_image = Image.new('RGB', (512, 512), 'white')
        
        effect_type = self.get_effect_type(level)
        
        if effect_type == "original":
            return base_image
        elif effect_type == "brightness":
            enhancer = ImageEnhance.Brightness(base_image)
            factor = 0.4 + intensity * 1.2
            return enhancer.enhance(factor)
        elif effect_type == "contrast":
            enhancer = ImageEnhance.Contrast(base_image)
            factor = 0.3 + intensity * 1.4
            return enhancer.enhance(factor)
        elif effect_type == "color":
            enhancer = ImageEnhance.Color(base_image)
            factor = 0.2 + intensity * 1.6
            return enhancer.enhance(factor)
        elif effect_type == "blur":
            radius = intensity * 3
            return base_image.filter(ImageFilter.GaussianBlur(radius=radius))
        elif effect_type == "noise":
            img_array = np.array(base_image)
            noise = np.random.normal(0, intensity * 20, img_array.shape)
            noisy = np.clip(img_array + noise, 0, 255).astype(np.uint8)
            return Image.fromarray(noisy)
        
        return base_image

    def get_effect_type(self, level):
        if level < 5:
            return "original"
        elif level < 15:
            return "brightness"
        elif level < 25:
            return "contrast"
        elif level < 35:
            return "color"
        elif level < 45:
            return "blur"
        else:
            return "noise"

    def generate_all_relations(self):
        print("🚀 开始生成标准版Relation数据集")
        print("每类25个关系，每个50梯度变化")
        print("=" * 50)
        
        self.generate_spatial_relations()
        self.generate_proximity_relations()
        self.generate_alignment_relations()
        self.generate_comparative_relations()
        
        self.generate_statistics()
        
        print("\n" + "=" * 50)
        print("🎉 标准版Relation数据集生成完成！")
        print(f"📁 输出: {self.output_path}")

    def generate_statistics(self):
        print("\n📊 统计生成结果...")
        
        total_relations = 0
        total_images = 0
        stats = {}
        
        for category in self.relation_types.keys():
            category_path = self.output_path / category
            if category_path.exists():
                svg_count = len(list((category_path / "svg_sources").glob("*.svg")))
                gradient_count = svg_count * 50
                
                stats[category] = {
                    "relations": svg_count,
                    "gradients": gradient_count,
                    "description": self.relation_types[category]["description"]
                }
                
                total_relations += svg_count
                total_images += gradient_count
                
                print(f"  ✅ {category}: {svg_count} 关系, {gradient_count:,} 图片")
        
        final_stats = {
            "dataset_name": "Standard Quality Relation Dataset",
            "creation_date": datetime.now().isoformat(),
            "total_relations": total_relations,
            "total_images": total_images,
            "gradients_per_relation": 50,
            "categories": stats,
            "technology": ["SVG Precision", "50 Gradients", "6 Effect Types"],
            "achievement": f"✅ 标准版关系数据集，时间优化版本"
        }
        
        with open(self.output_path / "STANDARD_DATASET_STATS.json", 'w', encoding='utf-8') as f:
            json.dump(final_stats, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎯 总计: {total_relations} 个关系, {total_images:,} 张图片")
        return final_stats

def main():
    generator = StandardRelationGenerator()
    stats = generator.generate_all_relations()
    
    print(f"\n🌟 标准版Relation数据集已完成！")
    print(f"📊 包含 {stats['total_relations']} 个关系")
    print(f"🎨 生成 {stats['total_images']:,} 张图片")
    print(f"⏱️ 优化版本，生成时间约1-2小时")

if __name__ == "__main__":
    main()