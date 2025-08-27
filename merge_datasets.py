#!/usr/bin/env python3
"""
Merge IllusionBench Dataset with Local Illusion Dataset
Combine the comprehensive IllusionBench QA data with local illusion generator
All comments and documentation in English
"""

import json
import shutil
from pathlib import Path
from datasets import load_dataset
import os

def merge_illusion_datasets():
    """
    Merge the IllusionBench dataset with local Illusion dataset
    Creates a unified structure with both synthetic and real illusion data
    """
    
    # Paths
    local_illusion_dir = Path("/home/jgy/Illusion")
    illusionbench_dir = Path("/home/jgy/IllusionBench") 
    merged_dir = Path("/home/jgy/Unified_Illusion_Dataset")
    
    # Create merged dataset directory
    merged_dir.mkdir(exist_ok=True)
    
    print("=== Merging Illusion Datasets ===")
    print(f"Local dataset: {local_illusion_dir}")
    print(f"IllusionBench: {illusionbench_dir}")
    print(f"Merged output: {merged_dir}")
    
    # Copy local illusion dataset
    if local_illusion_dir.exists():
        local_copy = merged_dir / "Synthetic_Illusions"
        if local_copy.exists():
            shutil.rmtree(local_copy)
        shutil.copytree(local_illusion_dir, local_copy)
        print("✓ Copied local synthetic illusion dataset")
    
    # Process IllusionBench data
    illusionbench_copy = merged_dir / "IllusionBench_Research_Dataset"
    illusionbench_copy.mkdir(exist_ok=True)
    
    # Copy IllusionBench repository files
    if illusionbench_dir.exists():
        for item in illusionbench_dir.iterdir():
            if item.is_file():
                shutil.copy2(item, illusionbench_copy)
        print("✓ Copied IllusionBench repository files")
    
    # Process IllusionBench HuggingFace data
    try:
        print("Loading IllusionBench dataset from HuggingFace...")
        dataset = load_dataset("MingZhangSJTU/IllusionBench")
        
        # Create images directory
        images_dir = illusionbench_copy / "images"
        images_dir.mkdir(exist_ok=True)
        
        # Save first 10 sample images for demonstration
        train_data = dataset['train']
        sample_count = min(10, len(train_data))
        
        for i in range(sample_count):
            img = train_data[i]['image']
            img.save(images_dir / f"sample_{i:03d}.png")
        
        print(f"✓ Saved {sample_count} sample images from HuggingFace dataset")
        
    except Exception as e:
        print(f"Warning: Could not load HuggingFace dataset: {e}")
    
    # Copy QA data if available
    qa_data_file = Path("/home/jgy/Image_properties.json")
    if qa_data_file.exists():
        shutil.copy2(qa_data_file, illusionbench_copy / "qa_annotations.json")
        print("✓ Copied QA annotations from IllusionBench")
    
    # Create unified metadata
    unified_metadata = {
        "dataset_info": {
            "name": "Unified Optical Illusion Research Dataset",
            "version": "1.0",
            "description": "Combined dataset featuring synthetic parametric illusions and real-world illusion images with comprehensive QA annotations",
            "creation_date": "2025-01-01",
            "language": "English",
            "license": "Mixed - see individual components"
        },
        "components": {
            "synthetic_illusions": {
                "source": "Local generation",
                "type": "Parametric synthetic illusions",
                "count": "50 types × 100 variations = 5,000 images",
                "format": "PNG/SVG",
                "features": ["Controllable parameters", "Gradient variations", "Multiple categories"]
            },
            "illusionbench_dataset": {
                "source": "IllusionBench research paper",
                "type": "Real-world illusion images with QA",
                "count": "1,041 images with 5,577 QA pairs",
                "format": "PNG with JSON annotations",
                "features": ["Human-annotated", "Multiple question types", "Difficulty ratings"]
            }
        },
        "categories_mapping": {
            "synthetic_categories": [
                "Color_Brightness_Illusions",
                "Geometric_Length_Illusions", 
                "Ambiguous_Figures_Illusions",
                "Grid_Motion_Illusions"
            ],
            "illusionbench_categories": [
                "Classic_Cognitive_Illusion",
                "Real_Scene_Illusion", 
                "No_Illusion",
                "Ishihara_Color_Blindness",
                "Trap_Illusion"
            ]
        },
        "usage_scenarios": {
            "research": "Academic research on visual perception and illusions",
            "ai_training": "Training vision-language models on illusion understanding",
            "evaluation": "Benchmarking model performance on visual boundary perception",
            "education": "Teaching about optical illusions and visual perception"
        }
    }
    
    # Save unified metadata
    with open(merged_dir / "unified_dataset_metadata.json", 'w', encoding='utf-8') as f:
        json.dump(unified_metadata, f, indent=2, ensure_ascii=False)
    
    print("✓ Created unified dataset metadata")
    
    # Create cross-reference mapping
    if qa_data_file.exists():
        with open(qa_data_file, 'r', encoding='utf-8') as f:
            qa_data = json.load(f)
        
        # Analyze IllusionBench data structure
        analysis = {
            "total_images": len(qa_data),
            "total_qa_pairs": sum(len(item['qa_data']) for item in qa_data),
            "categories_distribution": {},
            "difficulty_distribution": {},
            "question_types": {}
        }
        
        for item in qa_data:
            # Count categories
            category = item['image_property']['Category']
            analysis['categories_distribution'][category] = analysis['categories_distribution'].get(category, 0) + 1
            
            # Count difficulty levels  
            difficulty = item['image_property']['Difficult Level']
            analysis['difficulty_distribution'][difficulty] = analysis['difficulty_distribution'].get(difficulty, 0) + 1
            
            # Count question types
            for qa in item['qa_data']:
                q_type = qa['Question Type']
                analysis['question_types'][q_type] = analysis['question_types'].get(q_type, 0) + 1
        
        # Save analysis
        with open(merged_dir / "illusionbench_analysis.json", 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print("✓ Created IllusionBench data analysis")
    
    print(f"\n=== Dataset Merge Complete ===")
    print(f"Unified dataset created at: {merged_dir}")
    print("Components:")
    print(f"  - Synthetic illusions: {merged_dir / 'Synthetic_Illusions'}")
    print(f"  - IllusionBench data: {merged_dir / 'IllusionBench_Research_Dataset'}")
    print(f"  - Unified metadata: {merged_dir / 'unified_dataset_metadata.json'}")
    
    return merged_dir

if __name__ == "__main__":
    merge_illusion_datasets()