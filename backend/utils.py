"""
Utility functions for PhotoPro AI backend.
Image processing, validation, and helper functions.
"""

import os
import uuid
import hashlib
from typing import Optional, Tuple
from PIL import Image, ImageOps
import io
import requests
from fastapi import HTTPException


def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename with UUID"""
    file_extension = os.path.splitext(original_filename)[1]
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{file_extension}"


def validate_image_file(file_content: bytes, filename: str) -> Tuple[bool, str]:
    """
    Validate image file format, size, and dimensions
    Returns (is_valid, error_message)
    """
    try:
        # Check file size (max 10MB)
        if len(file_content) > 10 * 1024 * 1024:
            return False, "File size must be less than 10MB"
        
        # Check file extension
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
        file_ext = os.path.splitext(filename.lower())[1]
        if file_ext not in allowed_extensions:
            return False, "File must be JPG, PNG, or WEBP format"
        
        # Validate image with PIL
        try:
            image = Image.open(io.BytesIO(file_content))
            width, height = image.size
            
            # Check dimensions
            if width < 512 or height < 512:
                return False, "Image must be at least 512x512 pixels"
            
            # Check if image is too large
            if width > 4096 or height > 4096:
                return False, "Image dimensions too large (max 4096x4096)"
            
            return True, ""
            
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
            
    except Exception as e:
        return False, f"File validation error: {str(e)}"


def optimize_image_for_upload(image_content: bytes, max_size: int = 2048) -> bytes:
    """
    Optimize image for upload by resizing if necessary
    """
    try:
        image = Image.open(io.BytesIO(image_content))
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')
        
        # Resize if too large
        if image.width > max_size or image.height > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Optimize quality
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=85, optimize=True)
        return output.getvalue()
        
    except Exception as e:
        # Return original if optimization fails
        return image_content


def generate_thumbnail(image_url: str, size: Tuple[int, int] = (300, 300)) -> Optional[str]:
    """
    Generate thumbnail from image URL
    """
    try:
        # Download image
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # Create thumbnail
        image = Image.open(io.BytesIO(response.content))
        image.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Convert to bytes
        thumbnail_buffer = io.BytesIO()
        image.save(thumbnail_buffer, format='JPEG', quality=85)
        thumbnail_buffer.seek(0)
        
        return thumbnail_buffer.getvalue()
        
    except Exception as e:
        print(f"Thumbnail generation failed: {str(e)}")
        return None


def calculate_file_hash(file_content: bytes) -> str:
    """Calculate SHA-256 hash of file content"""
    return hashlib.sha256(file_content).hexdigest()


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def validate_style(style: str) -> bool:
    """Validate photo generation style"""
    valid_styles = ["corporate", "creative", "formal", "casual"]
    return style.lower() in valid_styles


def get_style_description(style: str) -> str:
    """Get human-readable description for style"""
    descriptions = {
        "corporate": "Professional business look with clean, formal appearance",
        "creative": "Artistic and expressive style with creative flair",
        "formal": "Elegant and sophisticated formal appearance",
        "casual": "Relaxed and approachable casual style"
    }
    return descriptions.get(style.lower(), "Professional photo style")


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 100:
        name, ext = os.path.splitext(filename)
        filename = name[:95] + ext
    
    return filename
