import React, { useState } from 'react';

/**
 * ImageWithPlaceholder component for smooth image loading
 * Addresses the minor issue where image rendering occasionally flickers when first loaded
 * 
 * @param {Object} props Component props
 * @param {string} props.src Image source URL
 * @param {string} props.alt Alternative text for the image
 * @param {Object} props.style Additional styles for the image
 * @param {string} props.className CSS class name for the image
 * @param {Function} props.onLoad Callback function when image loads
 * @param {Function} props.onError Callback function when image fails to load
 */
const ImageWithPlaceholder = ({
  src,
  alt,
  style = {},
  className = '',
  onLoad,
  onError,
  ...rest
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);

  // Handle image load event
  const handleImageLoad = (e) => {
    setIsLoaded(true);
    if (onLoad) onLoad(e);
  };

  // Handle image error event
  const handleImageError = (e) => {
    setHasError(true);
    if (onError) onError(e);
  };

  // Determine placeholder color based on image source
  const getPlaceholderColor = () => {
    if (!src) return '#f0f0f0';
    
    // Generate a consistent color based on the image URL
    let hash = 0;
    for (let i = 0; i < src.length; i++) {
      hash = src.charCodeAt(i) + ((hash << 5) - hash);
    }
    
    // Use a light pastel color
    const hue = hash % 360;
    return `hsl(${hue}, 25%, 90%)`;
  };

  return (
    <div 
      className={`image-container ${className}`}
      style={{
        position: 'relative',
        overflow: 'hidden',
        backgroundColor: getPlaceholderColor(),
        ...style
      }}
    >
      {/* Placeholder */}
      {!isLoaded && !hasError && (
        <div 
          className="image-placeholder"
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <div 
            className="loading-pulse"
            style={{
              width: '30%',
              height: '30%',
              borderRadius: '50%',
              background: 'rgba(255, 255, 255, 0.7)',
              animation: 'pulse 1.5s infinite ease-in-out'
            }}
          />
        </div>
      )}

      {/* Error state */}
      {hasError && (
        <div 
          className="image-error"
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#666',
            fontSize: '0.8rem',
            padding: '1rem',
            textAlign: 'center',
          }}
        >
          <span>Failed to load image</span>
        </div>
      )}

      {/* Actual image */}
      <img
        src={src}
        alt={alt}
        onLoad={handleImageLoad}
        onError={handleImageError}
        style={{
          display: isLoaded ? 'block' : 'none',
          width: '100%',
          height: '100%',
          objectFit: 'contain',
          transition: 'opacity 0.3s ease-in-out',
          opacity: isLoaded ? 1 : 0,
        }}
        {...rest}
      />

      {/* CSS for animations */}
      <style jsx>{`
        @keyframes pulse {
          0% {
            transform: scale(0.8);
            opacity: 0.5;
          }
          50% {
            transform: scale(1);
            opacity: 0.8;
          }
          100% {
            transform: scale(0.8);
            opacity: 0.5;
          }
        }
      `}</style>
    </div>
  );
};

export default ImageWithPlaceholder;
