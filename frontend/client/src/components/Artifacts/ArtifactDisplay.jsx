import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  FiCode,
  FiCopy,
  FiDownload,
  FiExternalLink,
  FiFileText,
  FiImage,
  FiInfo,
  FiMaximize2,
  FiMinimize2,
  FiShare2,
} from 'react-icons/fi';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { getFileExtension, getMimeType } from '../../utils/artifacts';
import { copyToClipboard } from '../../utils/clipboard';

const ArtifactDisplay = ({ artifact, onClose, onDownload, onShare, showMetadata = false }) => {
  const { t } = useTranslation();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [language, setLanguage] = useState('text');
  const [content, setContent] = useState('');
  const [isImage, setIsImage] = useState(false);
  const [imageUrl, setImageUrl] = useState('');
  const [showDetails, setShowDetails] = useState(false);
  const [isHovering, setIsHovering] = useState(false);

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
      // Show toast notification
      const toast = document.createElement('div');
      toast.className = 'toast-notification';
      toast.textContent = t('Copied to clipboard');
      document.body.appendChild(toast);
      setTimeout(() => {
        document.body.removeChild(toast);
      }, 2000);
    }
  };

  const handleDownload = () => {
    if (onDownload && artifact) {
      onDownload(artifact);
    }
  };

  const handleShare = () => {
    if (onShare && artifact) {
      onShare(artifact);
    }
  };

  const toggleDetails = () => {
    setShowDetails(!showDetails);
  };

  if (!artifact) return null;

  const getArtifactIcon = () => {
    if (isImage) return <FiImage className="artifact-type-icon" />;

    const extension = getFileExtension(artifact.name);
    switch (extension) {
      case 'py':
        return <span className="language-icon python">Py</span>;
      case 'js':
        return <span className="language-icon javascript">JS</span>;
      case 'html':
        return <span className="language-icon html">HTML</span>;
      case 'css':
        return <span className="language-icon css">CSS</span>;
      case 'json':
        return <span className="language-icon json">JSON</span>;
      case 'md':
        return <span className="language-icon markdown">MD</span>;
      default:
        return <FiFileText className="artifact-type-icon" />;
    }
  };

  return (
    <div
      className={`artifact-display ${isFullscreen ? 'fullscreen' : ''} ${isHovering ? 'hover' : ''}`}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
    >
      <div className="artifact-card">
        <div className="artifact-header">
          <div className="artifact-title">
            {getArtifactIcon()}
            <span className="artifact-name">{artifact.name}</span>
          </div>
          <div className="artifact-actions">
            {!isImage && (
              <button className="icon-button tooltip-container" onClick={handleCopyContent}>
                <FiCopy />
                <span className="tooltip">{t('Copy content')}</span>
              </button>
            )}
            <button className="icon-button tooltip-container" onClick={handleDownload}>
              <FiDownload />
              <span className="tooltip">{t('Download')}</span>
            </button>
            {onShare && (
              <button className="icon-button tooltip-container" onClick={handleShare}>
                <FiShare2 />
                <span className="tooltip">{t('Share')}</span>
              </button>
            )}
            <button className="icon-button tooltip-container" onClick={toggleFullscreen}>
              {isFullscreen ? <FiMinimize2 /> : <FiMaximize2 />}
              <span className="tooltip">
                {isFullscreen ? t('Exit fullscreen') : t('Fullscreen')}
              </span>
            </button>
            <button className="icon-button tooltip-container info-button" onClick={toggleDetails}>
              <FiInfo />
              <span className="tooltip">{t('Details')}</span>
            </button>
            {onClose && (
              <button className="icon-button close-button tooltip-container" onClick={onClose}>
                &times;
                <span className="tooltip">{t('Close')}</span>
              </button>
            )}
          </div>
        </div>

        <div className="artifact-content-wrapper">
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

          {showDetails && (
            <div className="artifact-details">
              <h3>{t('Artifact Details')}</h3>
              <div className="details-grid">
                <div className="detail-item">
                  <span className="detail-label">{t('Name')}:</span>
                  <span className="detail-value">{artifact.name}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">{t('Type')}:</span>
                  <span className="detail-value">
                    {isImage ? t('Image') : language !== 'text' ? language : t('Text')}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">{t('Size')}:</span>
                  <span className="detail-value">
                    {artifact.metadata?.size
                      ? `${Math.round(artifact.metadata.size / 1024)} KB`
                      : `${Math.round((artifact.content_base64.length * 3) / 4 / 1024)} KB`}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">{t('Created')}:</span>
                  <span className="detail-value">
                    {new Date(artifact.created_at).toLocaleString()}
                  </span>
                </div>
                {artifact.metadata?.task_id && (
                  <div className="detail-item">
                    <span className="detail-label">{t('Task')}:</span>
                    <span className="detail-value">{artifact.metadata.task_id}</span>
                  </div>
                )}
                {artifact.metadata?.agent_id && (
                  <div className="detail-item">
                    <span className="detail-label">{t('Agent')}:</span>
                    <span className="detail-value">{artifact.metadata.agent_id}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="artifact-footer">
          <div className="artifact-metadata">
            <span className="artifact-type">{isImage ? t('Image') : language}</span>
            <span className="artifact-size">
              {artifact.metadata?.size
                ? `${Math.round(artifact.metadata.size / 1024)} KB`
                : `${Math.round((artifact.content_base64.length * 3) / 4 / 1024)} KB`}
            </span>
          </div>
          <div className="artifact-timestamp">{new Date(artifact.created_at).toLocaleString()}</div>
        </div>
      </div>

      {/* Manus.im style floating action button for quick actions */}
      {isHovering && !isFullscreen && (
        <div className="floating-actions">
          {!isImage && (
            <button
              className="floating-action-button"
              onClick={handleCopyContent}
              title={t('Copy content')}
            >
              <FiCopy />
            </button>
          )}
          <button className="floating-action-button" onClick={handleDownload} title={t('Download')}>
            <FiDownload />
          </button>
          <button
            className="floating-action-button"
            onClick={toggleFullscreen}
            title={isFullscreen ? t('Exit fullscreen') : t('Fullscreen')}
          >
            {isFullscreen ? <FiMinimize2 /> : <FiMaximize2 />}
          </button>
        </div>
      )}
    </div>
  );
};

export default ArtifactDisplay;
