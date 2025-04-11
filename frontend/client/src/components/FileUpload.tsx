import React, { useState, useRef } from 'react';

import { useSupabase } from '../Providers/SupabaseProvider';

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const ALLOWED_TYPES = ['image/', 'application/pdf', 'text/plain'];

const FileUpload: React.FC = () => {
  const { supabase } = useSupabase();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [url, setUrl] = useState<string | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const dropRef = useRef<HTMLDivElement>(null);

  const validateFile = (file: File) => {
    if (file.size > MAX_FILE_SIZE) {
      setError('File size exceeds 10MB limit.');
      return false;
    }
    if (!ALLOWED_TYPES.some((type) => file.type.startsWith(type))) {
      setError('Unsupported file type.');
      return false;
    }
    setError(null);
    return true;
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      if (validateFile(selectedFile)) {
        setFile(selectedFile);
      } else {
        setFile(null);
      }
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && validateFile(droppedFile)) {
      setFile(droppedFile);
    } else {
      setFile(null);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    setProgress(0);
    const filePath = `${Date.now()}_${file.name}`;

    try {
      const { data, error } = await supabase.storage.from('uploads').upload(filePath, file, {
        upsert: false,
        onUploadProgress: (event: ProgressEvent) => {
          if (event.lengthComputable) {
            setProgress(Math.round((event.loaded / event.total) * 100));
          }
        },
      } as any); // Supabase JS may not support onUploadProgress natively; this is a placeholder

      if (error) {
        setError(error.message);
      } else {
        const { publicURL } = supabase.storage.from('uploads').getPublicUrl(filePath).data;
        setUrl(publicURL);
      }
    } catch {
      setError('Network error during upload.');
    }
    setUploading(false);
  };

  return (
    <div>
      <h2>Upload File</h2>
      <div
        ref={dropRef}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        style={{
          border: '2px dashed #ccc',
          padding: '20px',
          marginBottom: '10px',
          backgroundColor: '#f9f9f9',
        }}
      >
        Drag and drop a file here, or select below
      </div>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={uploading || !file}>
        {uploading ? 'Uploading...' : 'Upload'}
      </button>
      {uploading && (
        <div style={{ width: '100%', background: '#eee', marginTop: '5px' }}>
          <div
            style={{
              width: `${progress}%`,
              background: '#4caf50',
              height: '10px',
            }}
          />
        </div>
      )}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {url && (
        <p>
          File URL:{' '}
          <a href={url} target="_blank" rel="noopener noreferrer">
            {url}
          </a>
        </p>
      )}
    </div>
  );
};

export default FileUpload;
