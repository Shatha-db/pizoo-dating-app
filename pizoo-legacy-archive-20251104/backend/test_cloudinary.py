#!/usr/bin/env python3
"""
Test Cloudinary Image Upload
Verifies the image service can connect to Cloudinary and process images
"""

import sys
sys.path.append('/app/backend')

from image_service import ImageUploadService
from PIL import Image
import io

def create_test_image():
    """Create a simple test image"""
    # Create a 800x600 test image
    img = Image.new('RGB', (800, 600), color=(255, 100, 100))
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG', quality=90)
    img_bytes = img_bytes.getvalue()
    
    return img_bytes

def test_cloudinary_connection():
    """Test Cloudinary configuration and upload"""
    print("🧪 Testing Cloudinary Connection...")
    print("=" * 60)
    
    # Create test image
    print("\n1️⃣ Creating test image (800x600)...")
    test_image = create_test_image()
    print(f"   ✅ Test image created: {len(test_image) / 1024:.1f} KB")
    
    # Test validation
    print("\n2️⃣ Testing image validation...")
    is_valid, error = ImageUploadService.validate_image(test_image, "test.jpg", "image/jpeg")
    if is_valid:
        print("   ✅ Image validation passed")
    else:
        print(f"   ❌ Image validation failed: {error}")
        return False
    
    # Test compression
    print("\n3️⃣ Testing image compression (auto-orient, EXIF strip, resize)...")
    compressed = ImageUploadService.compress_image(test_image)
    print(f"   ✅ Image compressed: {len(test_image) / 1024:.1f} KB → {len(compressed) / 1024:.1f} KB")
    
    # Test upload to Cloudinary
    print("\n4️⃣ Testing upload to Cloudinary...")
    print("   📤 Uploading test image...")
    result = ImageUploadService.upload_image(
        file_bytes=test_image,
        user_id="test_user_123",
        upload_type="profile",
        filename="test_image.jpg",
        is_primary=False,
        mime_type="image/jpeg"
    )
    
    if result.get("success"):
        print("   ✅ Upload successful!")
        print(f"\n📊 Upload Result:")
        print(f"   • URL: {result.get('url')}")
        print(f"   • WebP URL: {result.get('webp_url', 'Not generated')}")
        print(f"   • Public ID: {result.get('public_id')}")
        print(f"   • Dimensions: {result.get('width')}x{result.get('height')}")
        print(f"   • Format: {result.get('format')}")
        print(f"   • Size: {result.get('size', 0) / 1024:.1f} KB")
        print("\n✅ Cloudinary connection verified successfully!")
        return True
    else:
        print(f"   ❌ Upload failed: {result.get('error')}")
        print(f"   Error code: {result.get('error_code')}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  CLOUDINARY CONNECTION TEST")
    print("=" * 60)
    
    success = test_cloudinary_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED - Cloudinary is ready!")
    else:
        print("❌ TEST FAILED - Please check configuration")
    print("=" * 60 + "\n")
    
    sys.exit(0 if success else 1)
