/**
 * Utility for handling chunked file uploads
 * Addresses the medium-priority issue with large file uploads failing
 */

// Default chunk size (1MB)
const DEFAULT_CHUNK_SIZE = 1024 * 1024;

/**
 * Splits a file into chunks for upload
 * @param {File} file - The file to be chunked
 * @param {number} chunkSize - Size of each chunk in bytes
 * @returns {Array} Array of file chunks
 */
export const createFileChunks = (file, chunkSize = DEFAULT_CHUNK_SIZE) => {
  const chunks = [];
  let start = 0;
  
  while (start < file.size) {
    const end = Math.min(start + chunkSize, file.size);
    const chunk = file.slice(start, end);
    chunks.push(chunk);
    start = end;
  }
  
  return chunks;
};

/**
 * Uploads a file in chunks with progress tracking
 * @param {string} url - The API endpoint for file upload
 * @param {File} file - The file to upload
 * @param {Object} headers - Request headers including auth token
 * @param {Object} metadata - Additional metadata to include with the upload
 * @param {Function} onProgress - Callback for upload progress updates
 * @param {Function} onError - Callback for error handling
 * @param {Function} onSuccess - Callback for successful upload
 * @param {number} chunkSize - Size of each chunk in bytes
 */
export const uploadFileInChunks = async (
  url,
  file,
  headers,
  metadata = {},
  onProgress = () => {},
  onError = () => {},
  onSuccess = () => {},
  chunkSize = DEFAULT_CHUNK_SIZE
) => {
  try {
    // Create chunks from file
    const chunks = createFileChunks(file, chunkSize);
    const totalChunks = chunks.length;
    
    // Initialize upload session
    const initResponse = await fetch(`${url}/init`, {
      method: 'POST',
      headers: {
        ...headers,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        filename: file.name,
        fileSize: file.size,
        fileType: file.type,
        totalChunks,
        metadata
      })
    });
    
    if (!initResponse.ok) {
      throw new Error(`Failed to initialize upload: ${initResponse.statusText}`);
    }
    
    const { uploadId } = await initResponse.json();
    
    // Upload each chunk
    let uploadedChunks = 0;
    
    for (let i = 0; i < totalChunks; i++) {
      const chunk = chunks[i];
      const formData = new FormData();
      formData.append('chunk', chunk);
      formData.append('chunkIndex', i);
      formData.append('uploadId', uploadId);
      
      const chunkResponse = await fetch(`${url}/chunk`, {
        method: 'POST',
        headers: {
          ...headers,
          // Content-Type is automatically set by FormData
        },
        body: formData
      });
      
      if (!chunkResponse.ok) {
        throw new Error(`Failed to upload chunk ${i}: ${chunkResponse.statusText}`);
      }
      
      uploadedChunks++;
      onProgress({
        uploadId,
        totalChunks,
        uploadedChunks,
        progress: Math.round((uploadedChunks / totalChunks) * 100)
      });
    }
    
    // Complete the upload
    const completeResponse = await fetch(`${url}/complete`, {
      method: 'POST',
      headers: {
        ...headers,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        uploadId
      })
    });
    
    if (!completeResponse.ok) {
      throw new Error(`Failed to complete upload: ${completeResponse.statusText}`);
    }
    
    const result = await completeResponse.json();
    onSuccess(result);
    
    return result;
  } catch (error) {
    onError(error);
    throw error;
  }
};

/**
 * Aborts an in-progress chunked upload
 * @param {string} url - The API endpoint for file upload
 * @param {string} uploadId - The ID of the upload to abort
 * @param {Object} headers - Request headers including auth token
 */
export const abortChunkedUpload = async (url, uploadId, headers) => {
  try {
    const response = await fetch(`${url}/abort`, {
      method: 'POST',
      headers: {
        ...headers,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        uploadId
      })
    });
    
    if (!response.ok) {
      throw new Error(`Failed to abort upload: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error aborting upload:', error);
    throw error;
  }
};

export default {
  createFileChunks,
  uploadFileInChunks,
  abortChunkedUpload
};
