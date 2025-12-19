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
    try:
        clipped = np.clip(matrix, 0, 255).astype(np.uint8)
        img = Image.fromarray(clipped, mode=mode)
        
        fmt = 'JPEG' 
        if isinstance(output, str):
            ext = os.path.splitext(output)[1].lower()
            if ext in ['.png']: fmt = 'PNG'
            elif ext in ['.webp']: fmt = 'WEBP'
            elif ext in ['.bmp']: fmt = 'BMP'
        
        if fmt in ['JPEG', 'WEBP']:
             img.save(output, format=fmt, optimize=True, quality=quality)
        else:
             img.save(output, format=fmt, optimize=True)
            
        return True
    except Exception as e:
        print(f"Error saving image: {e}")
        return False

def calculate_energy_k(S, retention=0.95):
    energy = np.square(S)
    total_energy = np.sum(energy)
    cumulative_energy = np.cumsum(energy)
    
    k = np.searchsorted(cumulative_energy, retention * total_energy) + 1
    return int(k)

def compress_channel_svd(channel_matrix, k):
    U, S, Vt = np.linalg.svd(channel_matrix, full_matrices=False)
    
    rec_k = calculate_energy_k(S, retention=0.95)
    
    if k == 'auto':
        k_used = rec_k
    else:
        k_used = min(int(k), len(S))
    
    U_k = U[:, :k_used]
    S_k = np.diag(S[:k_used])
    Vt_k = Vt[:k, :]
    
    reconstructed_matrix = np.dot(U_k, np.dot(S_k, Vt_k))
    
    return reconstructed_matrix, k_used, rec_k

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
        reconstructed, k_final, rec_k = compress_channel_svd(img_array, k)
        error = calculate_frobenius_error(img_array, reconstructed)
        save_mode = 'L'
        recommended_k = rec_k
        
    elif len(original_shape) == 3:
        channels = []
        rec_ks = []
        k_used_list = []
        
        for i in range(3): 
             rec_channel, k_used_ch, rec_k_ch = compress_channel_svd(img_array[:, :, i], k)
             channels.append(rec_channel)
             rec_ks.append(rec_k_ch)
             k_used_list.append(k_used_ch)
        
        reconstructed = np.stack(channels, axis=2)
        k_final = max(k_used_list) 
        recommended_k = max(rec_ks)
        
        diff = img_array[:,:,:3].astype(float) - reconstructed.astype(float)
        error = np.linalg.norm(diff)
        save_mode = 'RGB'

    else:
        return {"error": "Unsupported image format"}
    
    ext = os.path.splitext(output_path)[1].lower()
    is_lossy_format = ext in ['.jpg', '.jpeg', '.webp']

    current_quality = 85
    min_quality = 50
    final_quality = current_quality
    file_size_compressed = file_size_original

    if is_lossy_format:
        while True:
            buffer = io.BytesIO()
            
            clipped = np.clip(reconstructed, 0, 255).astype(np.uint8)
            img_pil = Image.fromarray(clipped, mode=save_mode)
            
            fmt_map = {'.jpg': 'JPEG', '.jpeg': 'JPEG', '.webp': 'WEBP'}
            pil_fmt = fmt_map.get(ext, 'JPEG')
            
            img_pil.save(buffer, format=pil_fmt, optimize=True, quality=current_quality)
            
            size_in_bytes = buffer.tell()
            
            if size_in_bytes < file_size_original or current_quality <= min_quality:
                file_size_compressed = size_in_bytes
                final_quality = current_quality
                break
            
            current_quality -= 5
            
        save_image(reconstructed, output_path, mode=save_mode, quality=final_quality)
        
    else:
        save_image(reconstructed, output_path, mode=save_mode)
        file_size_compressed = os.path.getsize(output_path)
        final_quality = 100 

    compression_ratio_val = ((file_size_original - file_size_compressed) / file_size_original) * 100
    
    return {
        "k": k_final,
        "recommended_k": recommended_k,
        "original_size": file_size_original,
        "compressed_size": file_size_compressed,
        "compression_percentage": round(compression_ratio_val, 2),
        "frobenius_error": round(error, 2),
        "quality_used": final_quality
    }
