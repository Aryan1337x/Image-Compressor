import numpy as np
import os
from PIL import Image

def load_image(image_path):
    """
    Loads an image from path and returns it as a NumPy array.
    """
    try:
        img = Image.open(image_path)
        return np.array(img), img.mode
    except Exception as e:
        print(f"Error loading image: {e}")
        return None, None

def save_image(matrix, output_path, mode='RGB', quality=85):
    """
    Saves a NumPy array as an image.
    Handles clipping to [0, 255] and type conversion.
    """
    try:
        # Clip values to valid pixel range and convert to uint8
        clipped = np.clip(matrix, 0, 255).astype(np.uint8)
        img = Image.fromarray(clipped, mode=mode)
        
        # Save with optimization to reduce file size
        # If JPEG, we can use optimize=True and quality
        ext = os.path.splitext(output_path)[1].lower()
        if ext in ['.jpg', '.jpeg']:
            img.save(output_path, optimize=True, quality=quality)
        else:
            img.save(output_path, optimize=True)
            
        return True
    except Exception as e:
        print(f"Error saving image: {e}")
        return False

def compress_channel_svd(channel_matrix, k):
    """
    Performs SVD on a single 2D matrix (channel) and reconstructs it using top k singular values.
    """
    # 1. Compute SVD
    # full_matrices=False makes U be (M, K_min) and Vt be (K_min, N)
    U, S, Vt = np.linalg.svd(channel_matrix, full_matrices=False)
    
    # 2. Rank-k Approximation
    k = min(k, len(S)) 
    
    U_k = U[:, :k]
    S_k = np.diag(S[:k])
    Vt_k = Vt[:k, :]
    
    # Reconstruct
    reconstructed_matrix = np.dot(U_k, np.dot(S_k, Vt_k))
    
    return reconstructed_matrix

def calculate_frobenius_error(original, reconstructed):
    """
    Calculates the Frobenius norm of the difference matrix (Error).
    """
    diff_matrix = original.astype(float) - reconstructed.astype(float)
    return np.linalg.norm(diff_matrix)

def compress_image(image_path, k, output_path):
    """
    Main function to handle image compression pipeline.
    Supports Grayscale (L) and RGB images.
    Returns Dictionary with ACTUAL file sizes.
    """
    img_array, mode = load_image(image_path)
    if img_array is None:
        return None

    original_shape = img_array.shape
    file_size_original = os.path.getsize(image_path)
    
    # Process Image Data (SVD)
    if len(original_shape) == 2:
        # Grayscale
        reconstructed = compress_channel_svd(img_array, k)
        error = calculate_frobenius_error(img_array, reconstructed)
        save_mode = 'L'
        
    elif len(original_shape) == 3:
        # RGB
        channels = []
        for i in range(3): 
             rec_channel = compress_channel_svd(img_array[:, :, i], k)
             channels.append(rec_channel)
        
        reconstructed = np.stack(channels, axis=2)
        
        # Quick error calc
        diff = img_array[:,:,:3].astype(float) - reconstructed.astype(float)
        error = np.linalg.norm(diff)
        save_mode = 'RGB'

    else:
        return {"error": "Unsupported image format"}
    
    # Dynamic Quality Adjustment Loop
    # Goal: Ensure compressed size < original size, if possible, without ruining quality.
    current_quality = 85
    min_quality = 50
    
    while True:
        save_image(reconstructed, output_path, mode=save_mode, quality=current_quality)
        file_size_compressed = os.path.getsize(output_path)
        
        # If compressed size is smaller than original OR we hit min quality, stop.
        if file_size_compressed < file_size_original or current_quality <= min_quality:
            break
            
        # Reduce quality and try again
        print(f"Compressed size ({file_size_compressed}) >= Original ({file_size_original}). Reducing quality from {current_quality} to {current_quality - 5}...")
        current_quality -= 5

    compression_ratio_val = ((file_size_original - file_size_compressed) / file_size_original) * 100
    
    return {
        "k": k,
        "original_size": file_size_original,
        "compressed_size": file_size_compressed,
        "compression_percentage": round(compression_ratio_val, 2),
        "frobenius_error": round(error, 2),
        "quality_used": current_quality
    }
