import os
import glob
import random
import shutil

def create_unified_structure(base_dir):
    for split in ['train', 'val']:
        for label in ['live', 'spoof']:
            os.makedirs(os.path.join(base_dir, split, label), exist_ok=True)

def safe_symlink(src, dst):
    if not os.path.exists(dst):
        os.symlink(os.path.abspath(src), os.path.abspath(dst))

def process_casia(src_dir, unified_dir):
    print("Processing Casia-FASD...")
    # Train
    train_color_dir = os.path.join(src_dir, "train_img", "train_img", "color")
    if os.path.exists(train_color_dir):
        for img_path in glob.glob(os.path.join(train_color_dir, "*.jpg")):
            filename = os.path.basename(img_path)
            label = "live" if "_real.jpg" in filename else "spoof"
            safe_symlink(img_path, os.path.join(unified_dir, "train", label, f"casia_{filename}"))
    
    # Test (mapped to Val)
    test_color_dir = os.path.join(src_dir, "test_img", "test_img", "color")
    if os.path.exists(test_color_dir):
        for img_path in glob.glob(os.path.join(test_color_dir, "*.jpg")):
            filename = os.path.basename(img_path)
            label = "live" if "_real.jpg" in filename else "spoof"
            safe_symlink(img_path, os.path.join(unified_dir, "val", label, f"casia_{filename}"))

def process_oulu(src_dir, unified_dir):
    print("Processing Oulu-NPU...")
    for original_label, unified_label in [("true", "live"), ("false", "spoof")]:
        label_dir = os.path.join(src_dir, original_label)
        if os.path.exists(label_dir):
            images = glob.glob(os.path.join(label_dir, "*.jpg"))
            random.shuffle(images)
            split_idx = int(0.8 * len(images))
            
            for img in images[:split_idx]:
                safe_symlink(img, os.path.join(unified_dir, "train", unified_label, f"oulu_{os.path.basename(img)}"))
            for img in images[split_idx:]:
                safe_symlink(img, os.path.join(unified_dir, "val", unified_label, f"oulu_{os.path.basename(img)}"))

def process_realvsfake(src_dir, unified_dir):
    print("Processing RealVSFake...")
    splits_mapping = {"train": "train", "test": "val"}
    labels_mapping = {"real_video": "live", "attack": "spoof"}
    
    for orig_split, unif_split in splits_mapping.items():
        for orig_label, unif_label in labels_mapping.items():
            dir_path = os.path.join(src_dir, orig_split, orig_label)
            if os.path.exists(dir_path):
                for img_path in glob.glob(os.path.join(dir_path, "*.jpg")):
                    safe_symlink(img_path, os.path.join(unified_dir, unif_split, unif_label, f"rvf_{os.path.basename(img_path)}"))

def process_siw(src_dir, unified_dir):
    print("Processing SiW...")
    splits_mapping = {"train": "train", "val": "val", "test": "val"}
    labels_mapping = {"real": "live", "spoof": "spoof"}
    
    for orig_split, unif_split in splits_mapping.items():
        for orig_label, unif_label in labels_mapping.items():
            dir_path = os.path.join(src_dir, orig_split, orig_label)
            if os.path.exists(dir_path):
                for img_path in glob.glob(os.path.join(dir_path, "*.jpg")):
                    safe_symlink(img_path, os.path.join(unified_dir, unif_split, unif_label, f"siw_{os.path.basename(img_path)}"))

if __name__ == "__main__":
    base_proj_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    unified_dir = os.path.join(base_proj_dir, "datasets", "unified")
    
    # Create unified structure
    create_unified_structure(unified_dir)
    
    # Process each dataset
    process_casia(os.path.join(base_proj_dir, "ACT_DATASETS", "Casia-FASD"), unified_dir)
    process_oulu(os.path.join(base_proj_dir, "ACT_DATASETS", "Oulu-NPU"), unified_dir)
    process_realvsfake(os.path.join(base_proj_dir, "ACT_DATASETS", "RealVSFake"), unified_dir)
    process_siw(os.path.join(base_proj_dir, "SiW"), unified_dir)
    
    # Print statistics
    for split in ['train', 'val']:
        for label in ['live', 'spoof']:
            path = os.path.join(unified_dir, split, label)
            count = len(os.listdir(path)) if os.path.exists(path) else 0
            print(f"Unified {split}/{label}: {count} images")

    print("Dataset consolidation complete.")
