import os
import shutil
from compression import compress_image, load_image

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Assumes an 'input.jpg' exists in the project root for testing
user_image_path = os.path.join(BASE_DIR, "input.jpg") 
project_upload_path = os.path.join(BASE_DIR, "static", "uploads", "user_image.jpg")
output_path = os.path.join(BASE_DIR, "static", "outputs", "user_image_compressed.jpg")

# Ensure dir exists (it should)
os.makedirs(os.path.dirname(project_upload_path), exist_ok=True)
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# 1. Copy image to project
print(f"Copying {user_image_path} to {project_upload_path}...")
shutil.copy(user_image_path, project_upload_path)

# 2. Check Dimensions
img, mode = load_image(project_upload_path)
if img is not None:
    h, w = img.shape[:2]
    print(f"Image Dimensions: {w}x{h}")
    
    # 3. Determine 'k' for 'no quality loss'
    # 'No quality loss' in SVD is subjective, but usually k=10% - 20% of min(w,h) is very good.
    # To be safe for "without quality loss", let's try k=100 or k=20% of rank.
    full_rank = min(w, h)
    target_k = int(min(full_rank * 0.25, 200)) # Cap at 200 to show compression, but take 25% if smaller.
    if target_k < 10: target_k = 10 
    
    print(f"Selected k={target_k} (approx {round(target_k/full_rank*100)}% of full rank)")

    # 4. Compress
    stats = compress_image(project_upload_path, target_k, output_path)
    print("Compression Stats:", stats)

else:
    print("Failed to load image.")
