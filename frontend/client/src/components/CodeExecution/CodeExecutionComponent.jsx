import React, { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FiCode, FiCopy, FiDownload, FiPlay, FiSave, FiTrash2, FiUpload } from 'react-icons/fi';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

import { copyToClipboard } from '../../utils/clipboard';
import ArtifactDisplay from '../Artifacts/ArtifactDisplay';

const CodeExecutionComponent = ({
  onExecute,
  onSave,
  initialCode = '',
  language = 'python',
  readOnly = false,
  showControls = true,
  artifacts = [],
  onArtifactDownload,
  onArtifactDelete,
}) => {
  const { t } = useTranslation();
  const [code, setCode] = useState(initialCode);
  const [executing, setExecuting] = useState(false);
  const [output, setOutput] = useState('');
  const [error, setError] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState(language);
  const [selectedArtifact, setSelectedArtifact] = useState(null);
  const editorRef = useRef(null);

  useEffect(() => {
    setCode(initialCode);
  }, [initialCode]);

  useEffect(() => {
    setSelectedLanguage(language);
  }, [language]);

  const handleCodeChange = (e) => {
    setCode(e.target.value);
  };

  const handleExecute = async () => {
    if (!code.trim()) return;

    setExecuting(true);
    setOutput('');
    setError('');

    try {
      const result = await onExecute(code, selectedLanguage);

      if (result.success) {
        setOutput(result.stdout || 'Execution completed successfully.');
      } else {
        setError(result.stderr || result.error || 'Execution failed.');
      }
    } catch (err) {
      setError(`Error: ${err.message || 'Unknown error occurred'}`);
    } finally {
      setExecuting(false);
    }
  };

  const handleSave = () => {
    if (onSave && code.trim()) {
      onSave(code, selectedLanguage);
    }
  };

  const handleCopy = () => {
    copyToClipboard(code);
  };

  const handleLanguageChange = (e) => {
    setSelectedLanguage(e.target.value);
  };

  const handleArtifactClick = (artifact) => {
    setSelectedArtifact(artifact);
  };

  const handleArtifactClose = () => {
    setSelectedArtifact(null);
  };

  const handleArtifactDownload = (artifact) => {
    if (onArtifactDownload) {
      onArtifactDownload(artifact);
    }
  };

  const handleArtifactDelete = (artifactId) => {
    if (onArtifactDelete) {
      onArtifactDelete(artifactId);
    }
  };

  const getLanguageOptions = () => {
    return [
      { value: 'python', label: 'Python' },
      { value: 'javascript', label: 'JavaScript' },
      { value: 'typescript', label: 'TypeScript' },
      { value: 'java', label: 'Java' },
      { value: 'cpp', label: 'C++' },
      { value: 'csharp', label: 'C#' },
      { value: 'go', label: 'Go' },
      { value: 'rust', label: 'Rust' },
      { value: 'ruby', label: 'Ruby' },
      { value: 'php', label: 'PHP' },
      { value: 'swift', label: 'Swift' },
      { value: 'kotlin', label: 'Kotlin' },
      { value: 'bash', label: 'Bash' },
      { value: 'sql', label: 'SQL' },
    ];
  };

  return (
    <div className="code-execution-component">
      <div className="code-editor-container">
        <div className="code-editor-header">
          <div className="code-editor-title">
            <FiCode className="icon" />
            <span>{t('Code Editor')}</span>
          </div>
          {showControls && (
            <div className="code-editor-controls">
              <select
                value={selectedLanguage}
                onChange={handleLanguageChange}
                className="language-selector"
                disabled={readOnly || executing}
              >
                {getLanguageOptions().map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <button
                className="icon-button"
                onClick={handleCopy}
                title={t('Copy code')}
                disabled={!code.trim()}
              >
                <FiCopy />
              </button>
              <button
                className="icon-button"
                onClick={handleSave}
                title={t('Save code')}
                disabled={readOnly || !code.trim()}
              >
                <FiSave />
              </button>
              <button
                className="primary-button execute-button"
                onClick={handleExecute}
                disabled={readOnly || executing || !code.trim()}
              >
                <FiPlay className="icon" />
                {executing ? t('Executing...') : t('Execute')}
              </button>
            </div>
          )}
        </div>
        <div className="code-editor-content">
          {readOnly ? (
            <SyntaxHighlighter
              language={selectedLanguage}
              style={vscDarkPlus}
              showLineNumbers
              wrapLines
              className="code-highlighter"
            >
              {code}
            </SyntaxHighlighter>
          ) : (
            <textarea
              ref={editorRef}
              className="code-textarea"
              value={code}
              onChange={handleCodeChange}
              placeholder={t('Enter your code here...')}
              disabled={readOnly || executing}
              spellCheck={false}
            />
          )}
        </div>
      </div>

      {(output || error) && (
        <div className="code-output-container">
          <div className="code-output-header">
            <div className="code-output-title">
              <span>{t('Output')}</span>
            </div>
          </div>
          <div className="code-output-content">
            {output && (
              <div className="output-section">
                <pre className="output-text">{output}</pre>
              </div>
            )}
            {error && (
              <div className="error-section">
                <pre className="error-text">{error}</pre>
              </div>
            )}
          </div>
        </div>
      )}

      {artifacts && artifacts.length > 0 && (
        <div className="artifacts-container">
          <div className="artifacts-header">
            <div className="artifacts-title">
              <span>{t('Artifacts')}</span>
            </div>
          </div>
          <div className="artifacts-list">
            {artifacts.map((artifact) => (
              <div key={artifact.id} className="artifact-item">
                <div className="artifact-name" onClick={() => handleArtifactClick(artifact)}>
                  {artifact.name}
                </div>
                <div className="artifact-actions">
                  <button
                    className="icon-button"
                    onClick={() => handleArtifactDownload(artifact)}
                    title={t('Download')}
                  >
                    <FiDownload />
                  </button>
                  <button
                    className="icon-button"
                    onClick={() => handleArtifactDelete(artifact.id)}
                    title={t('Delete')}
                  >
                    <FiTrash2 />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {selectedArtifact && (
        <div className="artifact-modal">
          <div className="artifact-modal-content">
            <ArtifactDisplay
              artifact={selectedArtifact}
              onClose={handleArtifactClose}
              onDownload={handleArtifactDownload}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default CodeExecutionComponent;
