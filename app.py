import os
import time
from flask import Flask, render_template, request, url_for, send_from_directory
from utils import save_uploaded_file, ALLOWED_EXTENSIONS
from compression import compress_image

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
OUTPUT_FOLDER = os.path.join('static', 'outputs')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 

def cleanup_old_files(folder: str, age_limit: int = 1800):
    """
    Deletes files in the specified folder that are older than age_limit (in seconds).
    Default age_limit is 1800 seconds (30 minutes).
    """
    try:
        current_time = time.time()
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > age_limit:
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error deleting old file {filename}: {e}")
    except Exception as e:
        print(f"Error accessing folder {folder}: {e}")

def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"

@app.route('/', methods=['GET', 'POST'])
def index():
    # Trigger cleanup on each access (simple approach)
    cleanup_old_files(app.config['UPLOAD_FOLDER'])
    cleanup_old_files(app.config['OUTPUT_FOLDER'])

    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file part')
        
        file = request.files['file']
        
        if file.filename == '':
            return render_template('index.html', error='No selected file')
            
        try:
            k = int(request.form.get('k', 50))
        except ValueError:
            k = 50
            
        filename, file_path = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
        
        if filename:
            output_filename = f"compressed_k{k}_{filename}"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            
            stats = compress_image(file_path, k, output_path)
            
            if stats:
                stats['original_size_str'] = format_size(stats['original_size'])
                stats['compressed_size_str'] = format_size(stats['compressed_size'])
                
                return render_template('index.html', 
                                       original_image=url_for('static', filename=f'uploads/{filename}'),
                                       compressed_image=url_for('static', filename=f'outputs/{output_filename}'),
                                       stats=stats,
                                       k_value=k)
            else:
                 return render_template('index.html', error='Error processing image')
        else:
            return render_template('index.html', error='File type not allowed')

    return render_template('index.html', k_value=50)

if __name__ == '__main__':
    app.run(debug=True)
