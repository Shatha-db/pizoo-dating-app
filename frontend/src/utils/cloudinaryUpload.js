import axios from 'axios';

// Cloudinary configuration
const CLOUD_NAME = 'demo'; // Replace with your cloud name
const UPLOAD_PRESET = 'unsigned_preset'; // Replace with your upload preset

/**
 * Upload image to Cloudinary
 * @param {File} imageFile - The image file to upload
 * @param {Function} onProgress - Optional callback for upload progress
 * @returns {Promise<string>} - The secure URL of the uploaded image
 */
export const uploadImageToCloudinary = async (imageFile, onProgress = null) => {
  if (!imageFile) {
    throw new Error('No image file provided');
  }

  // Validate file type
  const validTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp', 'image/heic'];
  if (!validTypes.includes(imageFile.type)) {
    throw new Error('نوع الملف غير مدعوم. الرجاء اختيار صورة JPEG أو PNG');
  }

  // Validate file size (max 10MB)
  const maxSize = 10 * 1024 * 1024; // 10MB
  if (imageFile.size > maxSize) {
    throw new Error('حجم الملف كبير جداً. الحد الأقصى 10 ميجابايت');
  }

  const uploadUrl = `https://api.cloudinary.com/v1_1/${CLOUD_NAME}/image/upload`;
  const formData = new FormData();
  formData.append('file', imageFile);
  formData.append('upload_preset', UPLOAD_PRESET);
  formData.append('folder', 'pizoo_profiles'); // Organize in folders

  try {
    const response = await axios.post(uploadUrl, formData, {
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    return response.data.secure_url;
  } catch (error) {
    console.error('Cloudinary upload error:', error);
    throw new Error('فشل رفع الصورة. الرجاء المحاولة مرة أخرى');
  }
};

/**
 * Upload multiple images to Cloudinary
 * @param {File[]} imageFiles - Array of image files
 * @param {Function} onProgress - Optional callback for total progress
 * @returns {Promise<string[]>} - Array of secure URLs
 */
export const uploadMultipleImages = async (imageFiles, onProgress = null) => {
  const uploadPromises = imageFiles.map((file, index) => {
    return uploadImageToCloudinary(file, (progress) => {
      if (onProgress) {
        // Calculate total progress across all files
        const totalProgress = ((index + progress / 100) / imageFiles.length) * 100;
        onProgress(Math.round(totalProgress));
      }
    });
  });

  try {
    const urls = await Promise.all(uploadPromises);
    return urls;
  } catch (error) {
    throw new Error('فشل رفع بعض الصور. الرجاء المحاولة مرة أخرى');
  }
};

/**
 * Compress image before upload (client-side)
 * @param {File} imageFile - The image file to compress
 * @param {number} maxWidth - Maximum width
 * @param {number} maxHeight - Maximum height
 * @param {number} quality - Image quality (0-1)
 * @returns {Promise<File>} - Compressed image file
 */
export const compressImage = (imageFile, maxWidth = 1920, maxHeight = 1920, quality = 0.8) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(imageFile);
    
    reader.onload = (event) => {
      const img = new Image();
      img.src = event.target.result;
      
      img.onload = () => {
        const canvas = document.createElement('canvas');
        let width = img.width;
        let height = img.height;

        // Calculate new dimensions
        if (width > height) {
          if (width > maxWidth) {
            height = height * (maxWidth / width);
            width = maxWidth;
          }
        } else {
          if (height > maxHeight) {
            width = width * (maxHeight / height);
            height = maxHeight;
          }
        }

        canvas.width = width;
        canvas.height = height;

        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);

        canvas.toBlob(
          (blob) => {
            const compressedFile = new File([blob], imageFile.name, {
              type: 'image/jpeg',
              lastModified: Date.now()
            });
            resolve(compressedFile);
          },
          'image/jpeg',
          quality
        );
      };

      img.onerror = (error) => {
        reject(new Error('فشل ضغط الصورة'));
      };
    };

    reader.onerror = (error) => {
      reject(new Error('فشل قراءة الصورة'));
    };
  });
};
