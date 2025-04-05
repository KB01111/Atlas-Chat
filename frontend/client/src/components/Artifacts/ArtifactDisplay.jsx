import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { FiCode, FiFileText, FiImage, FiDownload, FiCopy, FiMaximize2, FiMinimize2 } from 'react-icons/fi';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { copyToClipboard } from '../../utils/clipboard';
import { getFileExtension, getMimeType } from '../../utils/artifacts';

const ArtifactDisplay = ({ artifact, onClose, onDownload }) => {
  const { t } = useTranslation();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [language, setLanguage] = useState('text');
  const [content, setContent] = useState('');
  const [isImage, setIsImage] = useState(false);
  const [imageUrl, setImageUrl] = useState('');

  useEffect(() => {
    if (!artifact) return;

    // Determine content type and set appropriate display mode
    const contentType = artifact.content_type || getMimeType(artifact.name);
    
    if (contentType.startsWith('image/')) {
      setIsImage(true);
      // For images, create a data URL
      setImageUrl(`data:${contentType};base64,${artifact.content_base64}`);
    } else {
      setIsImage(false);
      
      // For text content, decode the base64 content
      try {
        const decoded = atob(artifact.content_base64);
        setContent(decoded);
        
        // Determine language for syntax highlighting
        const extension = getFileExtension(artifact.name);
        switch (extension) {
          case 'js':
            setLanguage('javascript');
            break;
          case 'py':
            setLanguage('python');
            break;
          case 'java':
            setLanguage('java');
            break;
          case 'html':
            setLanguage('html');
            break;
          case 'css':
            setLanguage('css');
            break;
          case 'json':
            setLanguage('json');
            break;
          case 'md':
            setLanguage('markdown');
            break;
          case 'ts':
            setLanguage('typescript');
            break;
          case 'jsx':
            setLanguage('jsx');
            break;
          case 'tsx':
            setLanguage('tsx');
            break;
          case 'c':
          case 'cpp':
          case 'h':
          case 'hpp':
            setLanguage('cpp');
            break;
          case 'go':
            setLanguage('go');
            break;
          case 'rs':
            setLanguage('rust');
            break;
          case 'rb':
            setLanguage('ruby');
            break;
          case 'sh':
          case 'bash':
            setLanguage('bash');
            break;
          case 'sql':
            setLanguage('sql');
            break;
          case 'xml':
            setLanguage('xml');
            break;
          case 'yaml':
          case 'yml':
            setLanguage('yaml');
            break;
          default:
            setLanguage('text');
        }
      } catch (error) {
        console.error('Error decoding artifact content:', error);
        setContent('Error: Could not decode artifact content');
      }
    }
  }, [artifact]);

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const handleCopyContent = () => {
    if (content) {
      copyToClipboard(content);
    }
  };

  const handleDownload = () => {
    if (onDownload && artifact) {
      onDownload(artifact);
    }
  };

  if (!artifact) return null;

  return (
    <div className={`artifact-display ${isFullscreen ? 'fullscreen' : ''}`}>
      <div className="artifact-header">
        <div className="artifact-title">
          {isImage ? <FiImage className="icon" /> : <FiFileText className="icon" />}
          <span>{artifact.name}</span>
        </div>
        <div className="artifact-actions">
          <button 
            className="icon-button" 
            onClick={handleCopyContent} 
            title={t('Copy content')}
            disabled={isImage}
          >
            <FiCopy />
          </button>
          <button 
            className="icon-button" 
            onClick={handleDownload} 
            title={t('Download')}
          >
            <FiDownload />
          </button>
          <button 
            className="icon-button" 
            onClick={toggleFullscreen} 
            title={isFullscreen ? t('Exit fullscreen') : t('Fullscreen')}
          >
            {isFullscreen ? <FiMinimize2 /> : <FiMaximize2 />}
          </button>
          {onClose && (
            <button 
              className="icon-button close-button" 
              onClick={onClose} 
              title={t('Close')}
            >
              &times;
            </button>
          )}
        </div>
      </div>
      <div className="artifact-content">
        {isImage ? (
          <div className="image-container">
            <img src={imageUrl} alt={artifact.name} />
          </div>
        ) : (
          <SyntaxHighlighter
            language={language}
            style={vscDarkPlus}
            showLineNumbers={true}
            wrapLines={true}
            className="code-highlighter"
          >
            {content}
          </SyntaxHighlighter>
        )}
      </div>
      <div className="artifact-footer">
        <div className="artifact-metadata">
          <span className="artifact-type">
            {isImage ? t('Image') : t('Code')}
          </span>
          <span className="artifact-size">
            {artifact.metadata?.size 
              ? `${Math.round(artifact.metadata.size / 1024)} KB` 
              : `${Math.round((artifact.content_base64.length * 3) / 4 / 1024)} KB`}
          </span>
        </div>
        <div className="artifact-timestamp">
          {new Date(artifact.created_at).toLocaleString()}
        </div>
      </div>
    </div>
  );
};

export default ArtifactDisplay;
