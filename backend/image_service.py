"""
Enhanced Image Upload Service with Cloudinary Integration
Handles image uploads, compression, folder organization, and error recovery
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api
from PIL import Image
import io
import base64
from typing import Optional, Tuple, Dict
import logging

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Cloudinary from environment variable
CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')
if CLOUDINARY_URL:
    cloudinary.config(cloudinary_url=CLOUDINARY_URL)
    logger.info("✅ Cloudinary configured successfully")
else:
    logger.warning("⚠️ CLOUDINARY_URL not found in environment variables")


class ImageUploadService:
    """Service for handling image uploads to Cloudinary"""
    
    # Constants
    MAX_FILE_SIZE_MB = 10
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    MAX_IMAGE_WIDTH = 1920
    QUALITY = "auto"
    FORMAT = "auto"
    
    # Folder structure
    FOLDERS = {
        "avatar": "pizoo/users/avatars",
        "story": "pizoo/stories",
        "verification": "pizoo/verification",
        "profile": "pizoo/users/profiles"
    }
    
    @classmethod
    def compress_image(cls, image_bytes: bytes, max_width: int = MAX_IMAGE_WIDTH) -> bytes:
        """
        Compress image before upload
        - Resize if too large
        - Optimize quality
        - Convert to efficient format
        """
        try:
            # Open image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert RGBA to RGB if necessary
            if image.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else image.split()[1])
                image = background
            
            # Resize if too large
            if image.width > max_width:
                ratio = max_width / image.width
                new_height = int(image.height * ratio)
                image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
                logger.info(f"📐 Image resized to {max_width}x{new_height}")
            
            # Save to bytes with optimization
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            compressed_bytes = output.getvalue()
            
            # Log compression result
            original_size = len(image_bytes) / 1024  # KB
            compressed_size = len(compressed_bytes) / 1024  # KB
            compression_ratio = (1 - compressed_size / original_size) * 100
            logger.info(f"🗜️ Image compressed: {original_size:.1f}KB → {compressed_size:.1f}KB ({compression_ratio:.1f}% reduction)")
            
            return compressed_bytes
            
        except Exception as e:
            logger.error(f"❌ Image compression failed: {str(e)}")
            # Return original if compression fails
            return image_bytes
    
    @classmethod
    def validate_image(cls, file_bytes: bytes, filename: str) -> Tuple[bool, Optional[str]]:
        """
        Validate image before upload
        Returns: (is_valid, error_message)
        """
        # Check file size
        file_size = len(file_bytes)
        if file_size > cls.MAX_FILE_SIZE_BYTES:
            size_mb = file_size / (1024 * 1024)
            return False, f"حجم الملف ({size_mb:.1f}MB) يتجاوز الحد الأقصى {cls.MAX_FILE_SIZE_MB}MB"
        
        # Check file type
        try:
            image = Image.open(io.BytesIO(file_bytes))
            # Verify it's actually an image
            image.verify()
            
            # Check format
            allowed_formats = ['JPEG', 'JPG', 'PNG', 'WEBP', 'HEIC', 'HEIF']
            if image.format not in allowed_formats:
                return False, f"صيغة الصورة غير مدعومة. الصيغ المدعومة: {', '.join(allowed_formats)}"
            
            return True, None
            
        except Exception as e:
            logger.error(f"❌ Image validation failed: {str(e)}")
            return False, "الملف ليس صورة صالحة"
    
    @classmethod
    def upload_image(
        cls,
        file_bytes: bytes,
        user_id: str,
        upload_type: str = "profile",  # avatar, story, verification, profile
        filename: Optional[str] = None,
        is_primary: bool = False
    ) -> Dict:
        """
        Upload image to Cloudinary with proper organization
        
        Args:
            file_bytes: Image file bytes
            user_id: User ID for folder organization
            upload_type: Type of upload (avatar, story, verification, profile)
            filename: Original filename (optional)
            is_primary: Whether this is the primary/avatar photo
            
        Returns:
            Dict with upload result:
            {
                "success": bool,
                "url": str (secure_url),
                "public_id": str,
                "width": int,
                "height": int,
                "format": str,
                "size": int (bytes),
                "error": str (if failed)
            }
        """
        try:
            # Validate Cloudinary is configured
            if not CLOUDINARY_URL:
                logger.error("❌ Cloudinary not configured")
                return {
                    "success": False,
                    "error": "خدمة رفع الصور غير متاحة حالياً"
                }
            
            # Validate image
            is_valid, error_msg = cls.validate_image(file_bytes, filename or "image")
            if not is_valid:
                return {
                    "success": False,
                    "error": error_msg
                }
            
            # Compress image
            logger.info(f"🗜️ Compressing image before upload...")
            compressed_bytes = cls.compress_image(file_bytes)
            
            # Determine folder
            folder = cls.FOLDERS.get(upload_type, cls.FOLDERS["profile"])
            folder_path = f"{folder}/{user_id}"
            
            # Prepare upload options
            upload_options = {
                "folder": folder_path,
                "resource_type": "image",
                "quality": cls.QUALITY,
                "fetch_format": cls.FORMAT,
                "overwrite": False,
                "unique_filename": True,
                "use_filename": bool(filename),
                "tags": [upload_type, user_id]
            }
            
            # Add transformation for optimization
            upload_options["transformation"] = [
                {
                    "width": cls.MAX_IMAGE_WIDTH,
                    "crop": "limit",
                    "quality": "auto:good",
                    "fetch_format": "auto"
                }
            ]
            
            # If this is primary avatar, set specific public_id
            if is_primary and upload_type == "avatar":
                upload_options["public_id"] = f"{folder_path}/primary"
                upload_options["overwrite"] = True
            
            # Upload to Cloudinary
            logger.info(f"☁️ Uploading to Cloudinary: {folder_path}")
            result = cloudinary.uploader.upload(
                compressed_bytes,
                **upload_options
            )
            
            logger.info(f"✅ Upload successful: {result['public_id']}")
            
            return {
                "success": True,
                "url": result['secure_url'],
                "public_id": result['public_id'],
                "width": result.get('width'),
                "height": result.get('height'),
                "format": result.get('format'),
                "size": result.get('bytes'),
                "created_at": result.get('created_at')
            }
            
        except cloudinary.exceptions.Error as e:
            logger.error(f"❌ Cloudinary error: {str(e)}")
            return {
                "success": False,
                "error": f"فشل رفع الصورة: {str(e)}"
            }
        except Exception as e:
            logger.error(f"❌ Upload error: {str(e)}")
            return {
                "success": False,
                "error": "حدث خطأ أثناء رفع الصورة"
            }
    
    @classmethod
    def delete_image(cls, public_id: str) -> bool:
        """
        Delete image from Cloudinary
        
        Args:
            public_id: Cloudinary public ID
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            if not CLOUDINARY_URL:
                logger.error("❌ Cloudinary not configured")
                return False
            
            result = cloudinary.uploader.destroy(public_id)
            
            if result.get('result') == 'ok':
                logger.info(f"✅ Image deleted: {public_id}")
                return True
            else:
                logger.warning(f"⚠️ Image deletion failed: {public_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Delete error: {str(e)}")
            return False
    
    @classmethod
    def get_user_images(cls, user_id: str, upload_type: str = "profile") -> list:
        """
        Get all images for a user from Cloudinary
        
        Args:
            user_id: User ID
            upload_type: Type of upload (avatar, story, verification, profile)
            
        Returns:
            List of image URLs
        """
        try:
            if not CLOUDINARY_URL:
                return []
            
            folder = cls.FOLDERS.get(upload_type, cls.FOLDERS["profile"])
            folder_path = f"{folder}/{user_id}"
            
            result = cloudinary.api.resources(
                type="upload",
                prefix=folder_path,
                max_results=50
            )
            
            images = [resource['secure_url'] for resource in result.get('resources', [])]
            return images
            
        except Exception as e:
            logger.error(f"❌ Get images error: {str(e)}")
            return []
