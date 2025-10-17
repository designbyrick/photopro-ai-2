"""
Cloudinary storage module for PhotoPro AI.
Handles image upload, deletion, and optimization using Cloudinary.
"""

import cloudinary
import cloudinary.uploader
import cloudinary.api
from fastapi import UploadFile, HTTPException
from typing import Dict, Optional, Tuple
import os
import io
from PIL import Image
import uuid

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

class CloudinaryStorage:
    """Cloudinary storage service for PhotoPro AI"""
    
    @staticmethod
    async def upload_photo(
        file: UploadFile, 
        user_id: int, 
        folder: str = "originals",
        optimize: bool = True
    ) -> Dict[str, str]:
        """
        Upload photo to Cloudinary with optimization
        
        Args:
            file: FastAPI UploadFile object
            user_id: User ID for folder organization
            folder: Subfolder within user directory
            optimize: Whether to apply automatic optimization
            
        Returns:
            Dict with 'url' and 'public_id'
            
        Raises:
            HTTPException: If upload fails
        """
        try:
            # Read file content
            file_content = await file.read()
            
            # Reset file pointer
            await file.seek(0)
            
            # Prepare upload parameters
            upload_params = {
                "folder": f"photopro/user_{user_id}/{folder}",
                "resource_type": "image",
                "public_id": f"{uuid.uuid4()}_{file.filename}",
                "overwrite": True,
                "invalidate": True
            }
            
            # Add optimization if requested
            if optimize:
                upload_params["transformation"] = [
                    {"quality": "auto"},
                    {"fetch_format": "auto"},
                    {"width": 2048, "height": 2048, "crop": "limit"}
                ]
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                file_content,
                **upload_params
            )
            
            return {
                "url": result['secure_url'],
                "public_id": result['public_id'],
                "format": result['format'],
                "width": result['width'],
                "height": result['height'],
                "bytes": result['bytes']
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Photo upload failed: {str(e)}"
            )
    
    @staticmethod
    async def upload_from_url(
        url: str, 
        user_id: int, 
        folder: str = "generated",
        public_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Upload image from URL to Cloudinary
        
        Args:
            url: Image URL to upload
            user_id: User ID for folder organization
            folder: Subfolder within user directory
            public_id: Custom public ID (optional)
            
        Returns:
            Dict with 'url' and 'public_id'
        """
        try:
            upload_params = {
                "folder": f"photopro/user_{user_id}/{folder}",
                "resource_type": "image",
                "public_id": public_id or f"{uuid.uuid4()}_generated",
                "overwrite": True,
                "invalidate": True,
                "transformation": [
                    {"quality": "auto"},
                    {"fetch_format": "auto"}
                ]
            }
            
            result = cloudinary.uploader.upload(
                url,
                **upload_params
            )
            
            return {
                "url": result['secure_url'],
                "public_id": result['public_id'],
                "format": result['format'],
                "width": result['width'],
                "height": result['height'],
                "bytes": result['bytes']
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"URL upload failed: {str(e)}"
            )
    
    @staticmethod
    async def delete_photo(public_id: str) -> bool:
        """
        Delete photo from Cloudinary
        
        Args:
            public_id: Cloudinary public ID
            
        Returns:
            bool: True if successful
            
        Raises:
            HTTPException: If deletion fails
        """
        try:
            result = cloudinary.uploader.destroy(public_id)
            
            if result.get('result') == 'ok':
                return True
            else:
                raise Exception(f"Delete failed: {result.get('result', 'unknown error')}")
                
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Photo deletion failed: {str(e)}"
            )
    
    @staticmethod
    async def get_photo_url(public_id: str, transformations: Optional[Dict] = None) -> str:
        """
        Get optimized photo URL from Cloudinary
        
        Args:
            public_id: Cloudinary public ID
            transformations: Optional transformation parameters
            
        Returns:
            str: Optimized photo URL
        """
        try:
            if transformations:
                return cloudinary.utils.cloudinary_url(
                    public_id,
                    **transformations
                )[0]
            else:
                return cloudinary.utils.cloudinary_url(public_id)[0]
                
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"URL generation failed: {str(e)}"
            )
    
    @staticmethod
    async def generate_thumbnail(
        public_id: str, 
        width: int = 300, 
        height: int = 300
    ) -> str:
        """
        Generate thumbnail URL from existing photo
        
        Args:
            public_id: Cloudinary public ID
            width: Thumbnail width
            height: Thumbnail height
            
        Returns:
            str: Thumbnail URL
        """
        try:
            transformations = {
                "width": width,
                "height": height,
                "crop": "fill",
                "gravity": "face",
                "quality": "auto",
                "fetch_format": "auto"
            }
            
            return cloudinary.utils.cloudinary_url(
                public_id,
                **transformations
            )[0]
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Thumbnail generation failed: {str(e)}"
            )
    
    @staticmethod
    async def list_user_photos(user_id: int, folder: str = "originals") -> list:
        """
        List all photos for a user
        
        Args:
            user_id: User ID
            folder: Folder to list (originals, generated, etc.)
            
        Returns:
            list: List of photo information
        """
        try:
            result = cloudinary.api.resources(
                type="upload",
                prefix=f"photopro/user_{user_id}/{folder}",
                max_results=100
            )
            
            return result.get('resources', [])
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Photo listing failed: {str(e)}"
            )
    
    @staticmethod
    async def test_connection() -> bool:
        """
        Test Cloudinary connection
        
        Returns:
            bool: True if connection successful
        """
        try:
            # Test with a simple API call
            cloudinary.api.ping()
            return True
        except Exception as e:
            print(f"Cloudinary connection test failed: {e}")
            return False

# Global storage instance
storage = CloudinaryStorage()
