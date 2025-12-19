import os
import shutil
from compression import compress_image, load_image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
user_image_path = os.path.join(BASE_DIR, "input.jpg") 
project_upload_path = os.path.join(BASE_DIR, "static", "uploads", "user_image.jpg")
output_path = os.path.join(BASE_DIR, "static", "outputs", "user_image_compressed.jpg")

os.makedirs(os.path.dirname(project_upload_path), exist_ok=True)
os.makedirs(os.path.dirname(output_path), exist_ok=True)

print(f"Copying {user_image_path} to {project_upload_path}...")
shutil.copy(user_image_path, project_upload_path)

img, mode = load_image(project_upload_path)
if img is not None:
    h, w = img.shape[:2]
    print(f"Image Dimensions: {w}x{h}")
    
    full_rank = min(w, h)
    target_k = int(min(full_rank * 0.25, 200)) 
    if target_k < 10: target_k = 10 
    
    print(f"Selected k={target_k} (approx {round(target_k/full_rank*100)}% of full rank)")

    stats = compress_image(project_upload_path, target_k, output_path)
    print("Compression Stats:", stats)

else:
    print("Failed to load image.")
