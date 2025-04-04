import React, { useState, useEffect, useRef } from 'react';
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
  const outputRef = useRef(null);

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
        setOutput(prev => prev + (result.stdout || '') + (result.stderr ? `\nErrors:\n${result.stderr}` : ''));
        if (result.exit_code !== 0) {
          setOutput(prev => prev + `\nExited with code ${result.exit_code}`);
        } else {
          setOutput(prev => prev + `\nPackages installed successfully`);
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

  // Handle file load
  const handleLoadFile = async () => {
    const filename = prompt('Enter filename to load:');
    if (!filename) return;
    
    setOutput(prev => prev + `\n--- Loading file: ${filename} ---\n`);
    
    try {
      const result = await readFile(filename, threadId, agentId);
      
      if (result.success && result.content) {
        setCode(result.content);
        setFileName(filename);
        setOutput(prev => prev + `File ${filename} loaded successfully`);
        
        // Auto-detect language based on file extension
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
      } else {
        setOutput(prev => prev + `\nFailed to load file: ${result.error || 'Unknown error'}`);
      }
    } catch (error) {
      setOutput(prev => prev + `\nError: ${error.message || 'Failed to load file'}`);
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
              disabled={isExecuting}
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
              disabled={isExecuting || !code.trim()}
            >
              {isExecuting ? 'Running...' : 'Run Code'}
            </button>
            
            <button
              className="save-button"
              onClick={handleSaveFile}
              disabled={isExecuting || !code.trim()}
            >
              Save
            </button>
            
            <button
              className="load-button"
              onClick={handleLoadFile}
              disabled={isExecuting}
            >
              Load
            </button>
            
            <button
              className="theme-button"
              onClick={handleToggleTheme}
              disabled={isExecuting}
            >
              {theme === 'vs-dark' ? 'Light Theme' : 'Dark Theme'}
            </button>
            
            <button
              className="clear-button"
              onClick={handleClearOutput}
              disabled={isExecuting || !output}
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
            disabled={isInstalling}
          />
          <button
            onClick={handleInstallPackages}
            disabled={isInstalling || !packages.trim()}
          >
            {isInstalling ? 'Installing...' : 'Install Packages'}
          </button>
        </div>
      </div>
      
      <div className="code-execution-editor">
        <MonacoEditor
          width="100%"
          height="400"
          language={language}
          theme={theme}
          value={code}
          options={editorOptions}
          onChange={setCode}
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
