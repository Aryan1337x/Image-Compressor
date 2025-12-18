import os
from werkzeug.utils import secure_filename
import uuid

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, upload_folder):
    if file and allowed_file(file.filename):
        original_filename = secure_filename(file.filename)
        # Generate unique filename to prevent collisions
        unique_name = f"{uuid.uuid4().hex}_{original_filename}"
        file_path = os.path.join(upload_folder, unique_name)
        file.save(file_path)
        return unique_name, file_path
    return None, None
