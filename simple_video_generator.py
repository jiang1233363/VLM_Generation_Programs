#!/usr/bin/env python3
"""
使用diffusers库生成日落渐变视频并抽取帧
"""

import os
import sys
import cv2
import numpy as np
from pathlib import Path
from typing import List
# 移除AI模型依赖，使用纯算法生成

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def even_indices(total: int, k: int) -> List[int]:
    if k <= 0:
        return []
    if total <= 0:
        return []
    if k >= total:
        return list(range(total))
    return [round(i * (total - 1) / (k - 1)) for i in range(k)]

def extract_frames_evenly(video_path: Path, frames_dir: Path, num_frames: int = 20) -> List[Path]:
    if not video_path.exists():
        raise FileNotFoundError(f"视频文件不存在: {video_path}")
    
    ensure_dir(frames_dir)
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        raise RuntimeError(f"无法打开视频: {video_path}")
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        cap.release()
        raise RuntimeError("视频为空或无法读取帧数")
    
    indices = even_indices(total_frames, num_frames)
    saved_paths: List[Path] = []
    
    for idx, frame_index in enumerate(indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cap.read()
        if ret and frame is not None:
            frame_path = frames_dir / f"frame_{idx:03d}.png"
            if cv2.imwrite(str(frame_path), frame):
                saved_paths.append(frame_path)
    
    cap.release()
    return saved_paths

def create_gradient_video(output_path: Path, width: int = 768, height: int = 512, duration: int = 60, fps: int = 24):
    """创建一个日落渐变的简单视频"""
    
    total_frames = duration * fps
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    
    print(f"正在生成 {total_frames} 帧的日落渐变视频...")
    
    for frame_idx in range(total_frames):
        # 计算渐变进度 (0.0 到 1.0)
        progress = frame_idx / (total_frames - 1)
        
        # 创建渐变图像
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # 日落前的金色 -> 日落后的深蓝色
        # 上半部分天空
        sky_height = int(height * 0.7)
        for y in range(sky_height):
            # 从上到下的垂直渐变
            y_progress = y / sky_height
            
            # 时间渐变：从金色到深蓝
            # 金色 RGB(255, 215, 0) -> 橙红色 RGB(255, 100, 0) -> 深蓝 RGB(25, 25, 112)
            if progress < 0.3:  # 日落前期：金色主导
                r = int(255 * (1 - y_progress * 0.3))
                g = int(215 * (1 - y_progress * 0.5))
                b = int(0 + y_progress * 100 * progress)
            elif progress < 0.7:  # 日落时期：橙红色
                r = int(255 * (1 - y_progress * 0.2))
                g = int(100 + (progress - 0.3) * 50 - y_progress * 80)
                b = int(100 * progress + y_progress * 50)
            else:  # 日落后：深蓝色
                r = int(255 * (1 - progress) * (1 - y_progress))
                g = int(100 * (1 - progress) * (1 - y_progress))
                b = int(25 + progress * 87 + y_progress * 50)
            
            # 限制颜色范围
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            frame[y, :] = [b, g, r]  # OpenCV使用BGR格式
        
        # 下半部分海面：深蓝色到黑色
        for y in range(sky_height, height):
            sea_progress = (y - sky_height) / (height - sky_height)
            r = int(30 * (1 - sea_progress) * (1 - progress * 0.5))
            g = int(50 * (1 - sea_progress) * (1 - progress * 0.3))
            b = int(80 * (1 - sea_progress))
            
            frame[y, :] = [b, g, r]
        
        # 添加一些微妙的噪声模拟海面波光
        if progress > 0.5:
            sea_start = int(height * 0.7)
            sea_height = height - sea_start
            noise = np.random.randint(-10, 10, (height//4, width//4, 3))
            noise_resized = cv2.resize(noise.astype(np.float32), (width, sea_height))
            frame[sea_start:] = np.clip(
                frame[sea_start:].astype(np.float32) + noise_resized * 0.3, 
                0, 255
            ).astype(np.uint8)
        
        out.write(frame)
        
        if frame_idx % (fps * 5) == 0:  # 每5秒显示进度
            print(f"已生成 {frame_idx}/{total_frames} 帧 ({progress*100:.1f}%)")
    
    out.release()
    print(f"视频生成完成: {output_path}")

def main():
    # 设置输出目录
    output_dir = Path("/home/jgy/wan_outputs")
    ensure_dir(output_dir)
    
    # 生成视频
    video_path = output_dir / "sunset_gradient.mp4"
    print("开始生成日落渐变视频...")
    create_gradient_video(video_path, width=768, height=512, duration=10, fps=24)
    
    # 抽取帧
    frames_dir = output_dir / "frames"
    print(f"开始从视频中抽取20帧...")
    saved_frames = extract_frames_evenly(video_path, frames_dir, num_frames=20)
    
    print(f"\n✅ 任务完成!")
    print(f"📹 生成的视频: {video_path}")
    print(f"🖼️  抽取了 {len(saved_frames)} 帧到目录: {frames_dir}")
    print("\n抽取的帧文件:")
    for frame_path in saved_frames:
        print(f"  - {frame_path}")

if __name__ == "__main__":
    main()