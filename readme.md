# Image Compressor using SVD

A Flask-based web application that compresses images using Singular Value Decomposition (SVD) and quality optimization. This tool allows users to upload images, adjust compression parameters, and visualize the results in real-time.

## How SVD Works (Brief)
An image is treated as a matrix of pixel values. Singular Value Decomposition breaks this matrix into simpler components. By keeping only the top 'k' singular values, the image is approximated using less data, resulting in compression.

## Features

- **SVD Compression**: Uses Singular Value Decomposition to compress image channels.
- **Format Support**: Supports common image formats including PNG, JPG, JPEG, WEBP, BMP, and TIFF.
- **Detailed Statistics**: Displays:
    - Original vs Compressed file size
    - Compression Percentage
    - Frobenius Error (mathematical difference between original and compressed)
    - Quality level used
- **Side-by-Side Comparison**: Visually compare the original and compressed images.

## Installation

1.  **Clone the repository** (if applicable) or download the source code.
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the application**:
    ```bash
    python app.py
    ```
2.  **Open your browser** and navigate to `http://127.0.0.1:5000`.
3.  **Upload an image** and optionally set the 'k' value (Singular Values to keep).
    - Lower 'k' = Higher compression, lower quality.
    - Higher 'k' = Lower compression, higher quality.
4.  **Click "Upload"** to see the results.

## Various files
- `app.py`: Main Flask application.
- `compression.py`: Core logic for SVD compression and image handling.
- `utils.py`: Utility functions for file handling and validation.
- `process_req.py`: script for testing compression logic without the web UI.

## Requirements
- Python 3.x
- Flask
- NumPy
- Pillow

## Credits

Made by Aryan  
Instagram: [@aryan.skid](https://www.instagram.com/aryan.skid/)
