import numpy as np
import os
import io
from PIL import Image

def load_image(image_path):
    try:
        img = Image.open(image_path)
        return np.array(img), img.mode
    except Exception as e:
        print(f"Error loading image: {e}")
        return None, None

def save_image(matrix, output, mode='RGB', quality=85):
    """
    Save image to a path or file-like object.
    output: str (file path) or file-like object (e.g., io.BytesIO)
    """
    try:
        clipped = np.clip(matrix, 0, 255).astype(np.uint8)
        img = Image.fromarray(clipped, mode=mode)
        
        # Determine format
        fmt = 'JPEG' # Default
        if isinstance(output, str):
            ext = os.path.splitext(output)[1].lower()
            if ext in ['.png']: fmt = 'PNG'
            elif ext in ['.webp']: fmt = 'WEBP'
            elif ext in ['.bmp']: fmt = 'BMP'
        
        # JPEG/WEBP support quality
        if fmt in ['JPEG', 'WEBP']:
             img.save(output, format=fmt, optimize=True, quality=quality)
        else:
             img.save(output, format=fmt, optimize=True)
            
        return True
    except Exception as e:
        print(f"Error saving image: {e}")
        return False

def compress_channel_svd(channel_matrix, k):
    U, S, Vt = np.linalg.svd(channel_matrix, full_matrices=False)
    
    k = min(k, len(S)) 
    
    U_k = U[:, :k]
    S_k = np.diag(S[:k])
    Vt_k = Vt[:k, :]
    
    reconstructed_matrix = np.dot(U_k, np.dot(S_k, Vt_k))
    
    return reconstructed_matrix

def calculate_frobenius_error(original, reconstructed):
    diff_matrix = original.astype(float) - reconstructed.astype(float)
    return np.linalg.norm(diff_matrix)

def compress_image(image_path, k, output_path):
    img_array, mode = load_image(image_path)
    if img_array is None:
        return None

    original_shape = img_array.shape
    file_size_original = os.path.getsize(image_path)
    
    if len(original_shape) == 2:
        reconstructed = compress_channel_svd(img_array, k)
        error = calculate_frobenius_error(img_array, reconstructed)
        save_mode = 'L'
        
    elif len(original_shape) == 3:
        channels = []
        for i in range(3): 
             rec_channel = compress_channel_svd(img_array[:, :, i], k)
             channels.append(rec_channel)
        
        reconstructed = np.stack(channels, axis=2)
        
        diff = img_array[:,:,:3].astype(float) - reconstructed.astype(float)
        error = np.linalg.norm(diff)
        save_mode = 'RGB'

    else:
        return {"error": "Unsupported image format"}
    
    current_quality = 85
    min_quality = 50
    final_quality = current_quality
    file_size_compressed = file_size_original # Default fallback

    # Optimization: Use in-memory buffer for finding optimal quality
    # to avoid hitting the disk repeatedly
    
    while True:
        # Create an in-memory buffer
        buffer = io.BytesIO()
        
        # Save to buffer
        save_success = save_image(reconstructed, buffer, mode=save_mode, quality=current_quality)
        
        if not save_success:
            break
            
        # Get size from buffer
        size_in_bytes = buffer.tell()
        
        if size_in_bytes < file_size_original or current_quality <= min_quality:
            file_size_compressed = size_in_bytes
            final_quality = current_quality
            break
            
        current_quality -= 5
    
    # Finally, write the best result to disk
    save_image(reconstructed, output_path, mode=save_mode, quality=final_quality)

    compression_ratio_val = ((file_size_original - file_size_compressed) / file_size_original) * 100
    
    return {
        "k": k,
        "original_size": file_size_original,
        "compressed_size": file_size_compressed,
        "compression_percentage": round(compression_ratio_val, 2),
        "frobenius_error": round(error, 2),
        "quality_used": final_quality
    }
