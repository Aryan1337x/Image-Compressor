import os
from flask import Flask, render_template, request, url_for, send_from_directory
from utils import save_uploaded_file, ALLOWED_EXTENSIONS
from compression import compress_image

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = os.path.join('static', 'uploads')
OUTPUT_FOLDER = os.path.join('static', 'outputs')

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
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
                # Format sizes for display
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
