#!/usr/bin/env python3

from datasets import load_dataset, get_dataset_config_names
import json
from collections import Counter

def analyze_dataset():
    """Analyze the IllusionBench dataset in detail"""
    
    try:
        # Check available configurations
        print("Checking dataset configurations...")
        configs = get_dataset_config_names("MingZhangSJTU/IllusionBench")
        print(f"Available configs: {configs}")
        
        # Load dataset
        print("Loading dataset...")
        dataset = load_dataset("MingZhangSJTU/IllusionBench")
        
        print(f"Dataset splits: {list(dataset.keys())}")
        train_data = dataset['train']
        print(f"Train split size: {len(train_data)}")
        
        # Examine first few samples
        print("\n=== EXAMINING SAMPLES ===")
        for i in range(min(3, len(train_data))):
            sample = train_data[i]
            print(f"\nSample {i+1}:")
            print(f"  Keys: {list(sample.keys())}")
            
            for key, value in sample.items():
                if key == 'image':
                    print(f"  {key}: {type(value)} - {value.mode if hasattr(value, 'mode') else 'N/A'} {value.size if hasattr(value, 'size') else 'N/A'}")
                elif isinstance(value, dict):
                    print(f"  {key}: dict with keys {list(value.keys())}")
                elif isinstance(value, list):
                    print(f"  {key}: list with {len(value)} items")
                else:
                    print(f"  {key}: {type(value)} - {str(value)[:100]}")
        
        # Check dataset features/schema
        print(f"\n=== DATASET FEATURES ===")
        print(f"Features: {train_data.features}")
        
        # Save a sample for detailed inspection
        if len(train_data) > 0:
            sample_dict = dict(train_data[0])
            # Convert image to string representation for JSON serialization
            if 'image' in sample_dict:
                sample_dict['image'] = f"PIL Image: mode={sample_dict['image'].mode}, size={sample_dict['image'].size}"
            
            with open('detailed_sample.json', 'w') as f:
                json.dump(sample_dict, f, indent=2, default=str)
            print("Saved detailed sample to 'detailed_sample.json'")
        
        return dataset
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    dataset = analyze_dataset()