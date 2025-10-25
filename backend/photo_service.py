"""
Advanced Photo Upload Service for Pizoo Dating App
Following Tinder/Bumble best practices 2025
"""
import os
import uuid
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException
from typing import Optional
from PIL import Image
import io

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME', 'demo'),
    api_key=os.getenv('CLOUDINARY_API_KEY', ''),
    api_secret=os.getenv('CLOUDINARY_API_SECRET', '')
)

class PhotoUploadService:
    # Recommended dimensions for dating app photos (Tinder/Bumble standard)
    PREFERRED_ASPECT_RATIOS = ['1:1', '4:5']  # Square and portrait
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB
    SUPPORTED_IMAGE_FORMATS = ['jpg', 'jpeg', 'png', 'webp', 'heic']
    SUPPORTED_VIDEO_FORMATS = ['mp4', 'mov', 'avi']
    
    @staticmethod
    async def upload_photo(file: UploadFile, user_id: str, is_primary: bool = False) -> dict:
        """
        Upload photo with automatic optimization
        - Compress to optimal quality
        - Convert to best format (WebP)
        - Resize to standard dimensions
        - Generate multiple sizes for performance
        """
        try:
            # Read file
            contents = await file.read()
            
            # Check file size
            if len(contents) > PhotoUploadService.MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail="Photo size exceeds 10MB limit")
            
            # Validate image format
            try:
                image = Image.open(io.BytesIO(contents))
                format = image.format.lower()
                
                if format not in PhotoUploadService.SUPPORTED_IMAGE_FORMATS:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Unsupported format. Use: {', '.join(PhotoUploadService.SUPPORTED_IMAGE_FORMATS)}"
                    )
            except Exception as e:
                raise HTTPException(status_code=400, detail="Invalid image file")
            
            # Generate unique filename
            photo_id = str(uuid.uuid4())
            folder = f"pizoo/users/{user_id}"
            
            # Upload to Cloudinary with optimizations
            upload_result = cloudinary.uploader.upload(
                contents,
                folder=folder,
                public_id=photo_id,
                transformation=[
                    # Automatic quality optimization
                    {'quality': 'auto:good'},
                    # Best format selection (WebP, AVIF)
                    {'fetch_format': 'auto'},
                    # Face detection for better cropping
                    {'gravity': 'face', 'crop': 'fill'},
                    # Recommended size for dating apps
                    {'width': 800, 'height': 1000, 'crop': 'limit'}
                ],
                # Generate multiple sizes
                eager=[
                    {'width': 400, 'height': 500, 'crop': 'fill', 'quality': 'auto:good'},  # Thumbnail
                    {'width': 150, 'height': 150, 'crop': 'fill', 'quality': 'auto:good'}   # Small icon
                ],
                tags=['profile_photo', f'user_{user_id}', 'primary' if is_primary else 'additional']
            )
            
            return {
                'photo_id': photo_id,
                'url': upload_result['secure_url'],
                'thumbnail_url': upload_result['eager'][0]['secure_url'] if upload_result.get('eager') else None,
                'small_url': upload_result['eager'][1]['secure_url'] if len(upload_result.get('eager', [])) > 1 else None,
                'format': upload_result['format'],
                'width': upload_result['width'],
                'height': upload_result['height'],
                'bytes': upload_result['bytes'],
                'is_primary': is_primary
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error uploading photo: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to upload photo: {str(e)}")
    
    @staticmethod
    async def upload_video(file: UploadFile, user_id: str) -> dict:
        """
        Upload video with optimization for dating app
        - Max 30 seconds duration
        - Compress automatically
        - Generate thumbnail
        """
        try:
            # Read file
            contents = await file.read()
            
            # Check file size
            if len(contents) > PhotoUploadService.MAX_VIDEO_SIZE:
                raise HTTPException(status_code=400, detail="Video size exceeds 100MB limit")
            
            # Generate unique filename
            video_id = str(uuid.uuid4())
            folder = f"pizoo/users/{user_id}/videos"
            
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                contents,
                folder=folder,
                public_id=video_id,
                resource_type="video",
                # Video optimizations
                transformation=[
                    {'quality': 'auto:good'},
                    # Limit to 30 seconds (Tinder/Bumble standard)
                    {'duration': '0-30'},
                    # Standard mobile video size
                    {'width': 640, 'height': 800, 'crop': 'limit'}
                ],
                # Generate video thumbnail
                eager=[
                    {'format': 'jpg', 'transformation': [
                        {'width': 400, 'height': 500, 'crop': 'fill'}
                    ]}
                ],
                tags=['profile_video', f'user_{user_id}']
            )
            
            return {
                'video_id': video_id,
                'url': upload_result['secure_url'],
                'thumbnail_url': upload_result['eager'][0]['secure_url'] if upload_result.get('eager') else None,
                'format': upload_result['format'],
                'duration': upload_result.get('duration', 0),
                'bytes': upload_result['bytes']
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error uploading video: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to upload video: {str(e)}")
    
    @staticmethod
    async def delete_photo(photo_url: str) -> bool:
        """Delete photo from Cloudinary"""
        try:
            # Extract public_id from URL
            public_id = photo_url.split('/')[-1].split('.')[0]
            result = cloudinary.uploader.destroy(public_id)
            return result.get('result') == 'ok'
        except Exception as e:
            print(f"Error deleting photo: {str(e)}")
            return False

photo_service = PhotoUploadService()
