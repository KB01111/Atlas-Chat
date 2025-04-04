import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useApi } from '../../api-context';
import MonacoEditor from 'react-monaco-editor';
import './CodeExecutionComponent.css';

const CodeExecutionComponent = ({ agentId, threadId }) => {
  const { executeCode, writeFile, readFile, installPackages } = useApi();
  const [code, setCode] = useState('# Enter your Python code here\nprint("Hello, World!")');
  const [language, setLanguage] = useState('python');
  const [output, setOutput] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);
  const [packages, setPackages] = useState('');
  const [isInstalling, setIsInstalling] = useState(false);
  const [fileName, setFileName] = useState('');
  const [theme, setTheme] = useState('vs-dark');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const outputRef = useRef(null);
  const editorRef = useRef(null);
  const monacoRef = useRef(null);

  // Supported languages
  const languages = [
    { id: 'python', name: 'Python', installCmd: 'pip install' },
    { id: 'javascript', name: 'JavaScript', installCmd: 'npm install' },
    { id: 'typescript', name: 'TypeScript', installCmd: 'npm install' },
    { id: 'bash', name: 'Bash', installCmd: 'apt-get install' }
  ];

  // Auto-scroll output to bottom
  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [output]);

  // Store editor reference when it's mounted
  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;
    
    // Focus editor after mounting
    if (editor) {
      setTimeout(() => {
        editor.focus();
      }, 100);
    }
  };

  // Handle code execution
  const handleExecuteCode = async () => {
    if (!code.trim()) return;
    
    setIsExecuting(true);
    setOutput(prev => prev + '\n--- Executing code ---\n');
    
    try {
      const result = await executeCode(code, language, threadId, agentId);
      
      if (result.success) {
        setOutput(prev => prev + (result.stdout || '') + (result.stderr ? `\nErrors:\n${result.stderr}` : ''));
        if (result.exit_code !== 0) {
          setOutput(prev => prev + `\nExited with code ${result.exit_code}`);
        }
      } else {
        setOutput(prev => prev + `\nExecution failed: ${result.error || 'Unknown error'}`);
      }
    } catch (error) {
      setOutput(prev => prev + `\nError: ${error.message || 'Failed to execute code'}`);
    } finally {
      setIsExecuting(false);
      setOutput(prev => prev + '\n--- Execution complete ---\n');
      
      // Restore focus to editor after execution completes
      if (editorRef.current) {
        setTimeout(() => {
          editorRef.current.focus();
        }, 100);
      }
    }
  };

  // Handle package installation
  const handleInstallPackages = async () => {
    if (!packages.trim()) return;
    
    setIsInstalling(true);
    setOutput(prev => prev + `\n--- Installing packages: ${packages} ---\n`);
    
    try {
      const packageList = packages.split(/[ ,]+/).filter(pkg => pkg.trim());
      const result = await installPackages(packageList, language, threadId, agentId);
      
      if (result.success) {
        if (result.status === 'in_progress') {
          // Handle background installation
          setOutput(prev => prev + `\n${result.message}\n`);
          // Poll for status updates would be implemented here in a real app
        } else {
          setOutput(prev => prev + (result.stdout || '') + (result.stderr ? `\nErrors:\n${result.stderr}` : ''));
          if (result.exit_code !== 0) {
            setOutput(prev => prev + `\nExited with code ${result.exit_code}`);
          } else {
            setOutput(prev => prev + `\nPackages installed successfully`);
          }
        }
      } else {
        setOutput(prev => prev + `\nInstallation failed: ${result.error || 'Unknown error'}`);
      }
    } catch (error) {
      setOutput(prev => prev + `\nError: ${error.message || 'Failed to install packages'}`);
    } finally {
      setIsInstalling(false);
      setPackages('');
      setOutput(prev => prev + '\n--- Installation complete ---\n');
    }
  };

  // Handle file save
  const handleSaveFile = async () => {
    const filename = prompt('Enter filename to save:', fileName || `code.${language === 'python' ? 'py' : language === 'javascript' ? 'js' : language === 'typescript' ? 'ts' : 'sh'}`);
    if (!filename) return;
    
    setOutput(prev => prev + `\n--- Saving file: ${filename} ---\n`);
    
    try {
      const result = await writeFile(filename, code, threadId, agentId);
      
      if (result.success) {
        setOutput(prev => prev + `File ${filename} saved successfully`);
        setFileName(filename);
      } else {
        setOutput(prev => prev + `\nFailed to save file: ${result.error || 'Unknown error'}`);
      }
    } catch (error) {
      setOutput(prev => prev + `\nError: ${error.message || 'Failed to save file'}`);
    }
  };

  // Progressive file loading for large files
  const loadFileProgressively = useCallback(async (filename) => {
    setIsLoading(true);
    setLoadingProgress(0);
    setOutput(prev => prev + `\n--- Loading file: ${filename} ---\n`);
    
    try {
      // First, check file size or get metadata
      const metadataResult = await readFile(`${filename}.metadata`, threadId, agentId).catch(() => ({ success: false }));
      
      let fileSize = 0;
      let isLargeFile = false;
      
      if (metadataResult.success) {
        try {
          const metadata = JSON.parse(metadataResult.content);
          fileSize = metadata.size || 0;
          isLargeFile = fileSize > 100000; // Consider files > 100KB as large
        } catch (e) {
          // If metadata parsing fails, proceed with normal loading
          isLargeFile = false;
        }
      }
      
      if (isLargeFile) {
        // For large files, load in chunks
        setOutput(prev => prev + `\nLarge file detected (${Math.round(fileSize/1024)}KB). Loading progressively...\n`);
        
        // Create a model if it doesn't exist
        if (monacoRef.current) {
          const modelUri = monacoRef.current.Uri.parse(`file:///${filename}`);
          let model = monacoRef.current.editor.getModel(modelUri);
          
          if (!model) {
            model = monacoRef.current.editor.createModel('', language, modelUri);
          }
          
          // Set empty model to editor first
          if (editorRef.current) {
            editorRef.current.setModel(model);
          }
          
          // Determine chunk size and count
          const chunkSize = 50000; // 50KB chunks
          const totalChunks = Math.ceil(fileSize / chunkSize);
          let loadedContent = '';
          
          // Load chunks sequentially
          for (let i = 0; i < totalChunks; i++) {
            const start = i * chunkSize;
            const end = Math.min((i + 1) * chunkSize, fileSize);
            
            // In a real implementation, we would have a backend endpoint for range requests
            // Here we simulate by loading the whole file for demo purposes
            const chunkResult = await readFile(filename, threadId, agentId);
            
            if (chunkResult.success) {
              // In a real implementation, this would be just the chunk
              // For demo, we'll slice the content
              const fullContent = chunkResult.content;
              const chunkContent = fullContent.substring(start, end);
              
              loadedContent += chunkContent;
              
              // Update model content progressively
              model.setValue(loadedContent);
              
              // Update progress
              const progress = Math.min(((i + 1) / totalChunks) * 100, 100);
              setLoadingProgress(progress);
              
              // Small delay to show progress (would be removed in production)
              await new Promise(resolve => setTimeout(resolve, 100));
            } else {
              throw new Error(chunkResult.error || 'Failed to load file chunk');
            }
          }
          
          // Set code state after all chunks are loaded
          setCode(loadedContent);
          setFileName(filename);
          setOutput(prev => prev + `File ${filename} loaded successfully`);
          
          // Auto-detect language based on file extension
          updateLanguageFromFilename(filename);
          
        } else {
          throw new Error('Monaco editor not initialized');
        }
      } else {
        // For smaller files, load normally
        const result = await readFile(filename, threadId, agentId);
        
        if (result.success && result.content) {
          setCode(result.content);
          setFileName(filename);
          setOutput(prev => prev + `File ${filename} loaded successfully`);
          
          // Auto-detect language based on file extension
          updateLanguageFromFilename(filename);
        } else {
          throw new Error(result.error || 'Unknown error');
        }
      }
    } catch (error) {
      setOutput(prev => prev + `\nError: ${error.message || 'Failed to load file'}`);
    } finally {
      setIsLoading(false);
      setLoadingProgress(0);
      
      // Restore focus to editor after loading completes
      if (editorRef.current) {
        setTimeout(() => {
          editorRef.current.focus();
        }, 100);
      }
    }
  }, [readFile, threadId, agentId, language]);

  // Handle file load with progressive loading
  const handleLoadFile = async () => {
    const filename = prompt('Enter filename to load:');
    if (!filename) return;
    
    await loadFileProgressively(filename);
  };

  // Update language based on file extension
  const updateLanguageFromFilename = (filename) => {
    const ext = filename.split('.').pop().toLowerCase();
    if (ext === 'py') {
      setLanguage('python');
    } else if (ext === 'js') {
      setLanguage('javascript');
    } else if (ext === 'ts') {
      setLanguage('typescript');
    } else if (ext === 'sh' || ext === 'bash') {
      setLanguage('bash');
    }
  };

  // Clear output
  const handleClearOutput = () => {
    setOutput('');
  };

  // Toggle theme
  const handleToggleTheme = () => {
    setTheme(theme === 'vs-dark' ? 'vs-light' : 'vs-dark');
  };

  // Editor options
  const editorOptions = {
    selectOnLineNumbers: true,
    roundedSelection: false,
    readOnly: false,
    cursorStyle: 'line',
    automaticLayout: true,
    minimap: { enabled: true },
    scrollBeyondLastLine: false,
    lineNumbers: 'on',
    renderLineHighlight: 'all',
    fontFamily: 'JetBrains Mono, Menlo, Monaco, Consolas, "Courier New", monospace',
    fontSize: 14,
    tabSize: 2,
  };

  return (
    <div className="code-execution-container">
      <div className="code-execution-header">
        <div className="code-execution-controls">
          <div className="language-selector">
            <label htmlFor="language-select">Language:</label>
            <select
              id="language-select"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              disabled={isExecuting || isLoading}
            >
              {languages.map((lang) => (
                <option key={lang.id} value={lang.id}>
                  {lang.name}
                </option>
              ))}
            </select>
          </div>
          
          <div className="code-execution-buttons">
            <button
              className="run-button"
              onClick={handleExecuteCode}
              disabled={isExecuting || isLoading || !code.trim()}
            >
              {isExecuting ? 'Running...' : 'Run Code'}
            </button>
            
            <button
              className="save-button"
              onClick={handleSaveFile}
              disabled={isExecuting || isLoading || !code.trim()}
            >
              Save
            </button>
            
            <button
              className="load-button"
              onClick={handleLoadFile}
              disabled={isExecuting || isLoading}
            >
              {isLoading ? 'Loading...' : 'Load'}
            </button>
            
            <button
              className="theme-button"
              onClick={handleToggleTheme}
              disabled={isExecuting || isLoading}
            >
              {theme === 'vs-dark' ? 'Light Theme' : 'Dark Theme'}
            </button>
            
            <button
              className="clear-button"
              onClick={handleClearOutput}
              disabled={isExecuting || isLoading || !output}
            >
              Clear Output
            </button>
          </div>
        </div>
        
        <div className="package-installer">
          <input
            type="text"
            value={packages}
            onChange={(e) => setPackages(e.target.value)}
            placeholder="Package names (space or comma separated)"
            disabled={isInstalling || isLoading}
          />
          <button
            onClick={handleInstallPackages}
            disabled={isInstalling || isLoading || !packages.trim()}
          >
            {isInstalling ? 'Installing...' : 'Install Packages'}
          </button>
        </div>
      </div>
      
      <div className="code-execution-editor">
        {isLoading && (
          <div className="loading-overlay">
            <div className="loading-progress">
              <div className="loading-bar">
                <div 
                  className="loading-bar-fill" 
                  style={{ width: `${loadingProgress}%` }}
                ></div>
              </div>
              <div className="loading-text">
                Loading file: {loadingProgress.toFixed(0)}%
              </div>
            </div>
          </div>
        )}
        <MonacoEditor
          width="100%"
          height="400"
          language={language}
          theme={theme}
          value={code}
          options={editorOptions}
          onChange={setCode}
          editorDidMount={handleEditorDidMount}
        />
      </div>
      
      <div className="code-execution-output">
        <div className="output-header">
          <h3>Output</h3>
          {fileName && <span className="current-file">Current file: {fileName}</span>}
        </div>
        <pre ref={outputRef} className="output-content">
          {output || 'Run your code to see output here...'}
        </pre>
      </div>
    </div>
  );
};

export default CodeExecutionComponent;
