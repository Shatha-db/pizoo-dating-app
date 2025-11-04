import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

/**
 * Enhanced Image Upload Service
 * Uploads images through backend with compression, progress tracking, and retry logic
 */

/**
 * Compress image client-side before upload
 * Reduces upload time and bandwidth
 */
export const compressImage = (imageFile, maxWidth = 1920, quality = 0.85) => {
  return new Promise((resolve, reject) => {
    // Validate file
    if (!imageFile || !imageFile.type.startsWith('image/')) {
      reject(new Error('الملف ليس صورة صالحة'));
      return;
    }

    const reader = new FileReader();
    reader.readAsDataURL(imageFile);
    
    reader.onload = (event) => {
      const img = new Image();
      img.src = event.target.result;
      
      img.onload = () => {
        const canvas = document.createElement('canvas');
        let width = img.width;
        let height = img.height;

        // Calculate new dimensions maintaining aspect ratio
        if (width > maxWidth) {
          height = height * (maxWidth / width);
          width = maxWidth;
        }

        canvas.width = width;
        canvas.height = height;

        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);

        canvas.toBlob(
          (blob) => {
            if (!blob) {
              reject(new Error('فشل ضغط الصورة'));
              return;
            }

            const compressedFile = new File([blob], imageFile.name, {
              type: 'image/jpeg',
              lastModified: Date.now()
            });

            // Log compression result
            const originalSize = (imageFile.size / 1024).toFixed(1);
            const compressedSize = (compressedFile.size / 1024).toFixed(1);
            const reduction = ((1 - compressedFile.size / imageFile.size) * 100).toFixed(1);
            console.log(`🗜️ Image compressed: ${originalSize}KB → ${compressedSize}KB (${reduction}% reduction)`);

            resolve(compressedFile);
          },
          'image/jpeg',
          quality
        );
      };

      img.onerror = () => {
        reject(new Error('فشل تحميل الصورة'));
      };
    };

    reader.onerror = () => {
      reject(new Error('فشل قراءة الملف'));
    };
  });
};

/**
 * Upload image to backend with progress tracking and retry logic
 * @param {File} imageFile - Image file to upload
 * @param {string} token - Authentication token
 * @param {boolean} isPrimary - Whether this is the primary photo
 * @param {Function} onProgress - Progress callback (percentage)
 * @param {Function} onRetry - Retry callback
 * @returns {Promise<Object>} Upload result
 */
export const uploadImage = async (
  imageFile, 
  token, 
  isPrimary = false, 
  onProgress = null,
  onRetry = null
) => {
  // Validate inputs
  if (!imageFile) {
    throw new Error('لم يتم تحديد صورة');
  }

  if (!token) {
    throw new Error('يرجى تسجيل الدخول أولاً');
  }

  // Validate file type
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/heic', 'image/heif'];
  if (!validTypes.some(type => imageFile.type.toLowerCase().includes(type.split('/')[1]))) {
    throw new Error('صيغة الصورة غير مدعومة. الصيغ المدعومة: JPEG, PNG, WebP, HEIC');
  }

  // Validate file size (10MB max)
  const maxSize = 10 * 1024 * 1024;
  if (imageFile.size > maxSize) {
    const sizeMB = (imageFile.size / (1024 * 1024)).toFixed(1);
    throw new Error(`حجم الملف (${sizeMB}MB) يتجاوز الحد الأقصى 10MB`);
  }

  // Compress image before upload
  let fileToUpload = imageFile;
  try {
    if (onProgress) onProgress(5); // Show initial progress
    fileToUpload = await compressImage(imageFile);
    if (onProgress) onProgress(15); // Compression complete
  } catch (error) {
    console.warn('⚠️ Compression failed, uploading original:', error);
    // Continue with original file if compression fails
  }

  // Prepare form data
  const formData = new FormData();
  formData.append('file', fileToUpload);
  formData.append('is_primary', isPrimary);

  // Upload with retry logic (max 3 attempts)
  const maxRetries = 3;
  let lastError = null;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      if (attempt > 1 && onRetry) {
        onRetry(attempt, maxRetries);
      }

      const response = await axios.post(`${API}/profile/photo/upload`, formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            // Calculate progress from 15% (after compression) to 95%
            const percentCompleted = Math.round(
              15 + ((progressEvent.loaded * 80) / progressEvent.total)
            );
            onProgress(percentCompleted);
          }
        },
        timeout: 60000 // 60 second timeout
      });

      if (onProgress) onProgress(100); // Complete

      return {
        success: true,
        data: response.data,
        url: response.data.photo?.url || response.data.url,
        message: response.data.message || 'تم رفع الصورة بنجاح'
      };

    } catch (error) {
      lastError = error;
      console.error(`Upload attempt ${attempt} failed:`, error);

      // Don't retry on validation errors (4xx)
      if (error.response && error.response.status >= 400 && error.response.status < 500) {
        break;
      }

      // Wait before retry (exponential backoff)
      if (attempt < maxRetries) {
        await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
      }
    }
  }

  // All retries failed
  const errorMessage = lastError?.response?.data?.detail || 
                      lastError?.response?.data?.error ||
                      lastError?.message || 
                      'فشل رفع الصورة';

  throw new Error(errorMessage);
};

/**
 * Upload multiple images with progress tracking
 * @param {File[]} imageFiles - Array of image files
 * @param {string} token - Authentication token
 * @param {Function} onProgress - Progress callback for all uploads
 * @param {Function} onFileProgress - Progress callback per file
 * @returns {Promise<Array>} Array of upload results
 */
export const uploadMultipleImages = async (
  imageFiles,
  token,
  onProgress = null,
  onFileProgress = null
) => {
  const results = [];
  const total = imageFiles.length;

  for (let i = 0; i < total; i++) {
    const file = imageFiles[i];
    const isPrimary = i === 0; // First image is primary

    try {
      const result = await uploadImage(
        file,
        token,
        isPrimary,
        (fileProgress) => {
          // Report individual file progress
          if (onFileProgress) {
            onFileProgress(i, fileProgress);
          }

          // Report total progress
          if (onProgress) {
            const totalProgress = Math.round(
              ((i + fileProgress / 100) / total) * 100
            );
            onProgress(totalProgress);
          }
        }
      );

      results.push({
        success: true,
        file: file.name,
        ...result
      });

    } catch (error) {
      results.push({
        success: false,
        file: file.name,
        error: error.message
      });
    }
  }

  return results;
};

/**
 * Delete photo from profile
 * @param {number} photoIndex - Index of photo to delete
 * @param {string} token - Authentication token
 * @returns {Promise<Object>} Delete result
 */
export const deleteImage = async (photoIndex, token) => {
  if (!token) {
    throw new Error('يرجى تسجيل الدخول أولاً');
  }

  try {
    const response = await axios.delete(`${API}/profile/photo/${photoIndex}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    return {
      success: true,
      message: response.data.message || 'تم حذف الصورة بنجاح'
    };

  } catch (error) {
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error ||
                        'فشل حذف الصورة';
    throw new Error(errorMessage);
  }
};

/**
 * Set photo as primary
 * @param {string} photoUrl - URL of photo to set as primary
 * @param {string} token - Authentication token
 * @returns {Promise<Object>} Update result
 */
export const setPrimaryPhoto = async (photoUrl, token) => {
  if (!token) {
    throw new Error('يرجى تسجيل الدخول أولاً');
  }

  try {
    const response = await axios.put(
      `${API}/profile/photo/primary`,
      { photo_url: photoUrl },
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );

    return {
      success: true,
      message: 'تم تعيين الصورة الرئيسية بنجاح'
    };

  } catch (error) {
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error ||
                        'فشل تحديث الصورة الرئيسية';
    throw new Error(errorMessage);
  }
};

export default {
  compressImage,
  uploadImage,
  uploadMultipleImages,
  deleteImage,
  setPrimaryPhoto
};
