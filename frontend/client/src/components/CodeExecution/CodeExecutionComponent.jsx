import React, { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { useApi } from '../data-provider/simplified-api';

const CodeExecutionComponent = ({ agentId, threadId }) => {
  const [code, setCode] = useState('# Enter your Python code here\nprint("Hello, World!")');
  const [language, setLanguage] = useState('python');
  const [output, setOutput] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);
  const [error, setError] = useState(null);
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [packages, setPackages] = useState('');
  
  const api = useApi();
  
  // Execute code
  const executeCode = async () => {
    setIsExecuting(true);
    setError(null);
    setOutput('Executing code...\n');
    
    try {
      const result = await api.executeCode(code, language, threadId, agentId);
      
      if (result.success) {
        let outputText = '';
        if (result.stdout) {
          outputText += result.stdout;
        }
        if (result.stderr) {
          outputText += '\n' + result.stderr;
        }
        setOutput(outputText || 'Code executed successfully with no output.');
      } else {
        setError(result.error || 'An unknown error occurred');
        setOutput('Execution failed. See error details.');
      }
    } catch (err) {
      setError(err.message || 'Failed to execute code');
      setOutput('Execution failed. See error details.');
    } finally {
      setIsExecuting(false);
    }
  };
  
  // Install packages
  const installPackages = async () => {
    if (!packages.trim()) {
      setError('Please enter package names');
      return;
    }
    
    setIsExecuting(true);
    setError(null);
    setOutput('Installing packages...\n');
    
    try {
      const packageList = packages.split(/[ ,]+/).filter(pkg => pkg.trim());
      const result = await api.installPackages(packageList, language, threadId, agentId);
      
      if (result.success) {
        let outputText = 'Packages installed successfully.\n';
        if (result.stdout) {
          outputText += result.stdout;
        }
        if (result.stderr) {
          outputText += '\n' + result.stderr;
        }
        setOutput(outputText);
      } else {
        setError(result.error || 'An unknown error occurred');
        setOutput('Package installation failed. See error details.');
      }
    } catch (err) {
      setError(err.message || 'Failed to install packages');
      setOutput('Package installation failed. See error details.');
    } finally {
      setIsExecuting(false);
    }
  };
  
  // Save file
  const saveFile = async () => {
    if (!selectedFile) {
      const fileName = prompt('Enter file name:');
      if (!fileName) return;
      
      setIsExecuting(true);
      setError(null);
      
      try {
        const result = await api.writeFile(fileName, code, threadId, agentId);
        
        if (result.success) {
          setSelectedFile(fileName);
          setFiles(prevFiles => [...prevFiles, fileName]);
          setOutput(`File ${fileName} saved successfully.`);
        } else {
          setError(result.error || 'An unknown error occurred');
          setOutput('Failed to save file. See error details.');
        }
      } catch (err) {
        setError(err.message || 'Failed to save file');
        setOutput('Failed to save file. See error details.');
      } finally {
        setIsExecuting(false);
      }
    } else {
      setIsExecuting(true);
      setError(null);
      
      try {
        const result = await api.writeFile(selectedFile, code, threadId, agentId);
        
        if (result.success) {
          setOutput(`File ${selectedFile} updated successfully.`);
        } else {
          setError(result.error || 'An unknown error occurred');
          setOutput('Failed to update file. See error details.');
        }
      } catch (err) {
        setError(err.message || 'Failed to update file');
        setOutput('Failed to update file. See error details.');
      } finally {
        setIsExecuting(false);
      }
    }
  };
  
  // Load file
  const loadFile = async (fileName) => {
    setIsExecuting(true);
    setError(null);
    
    try {
      const result = await api.readFile(fileName, threadId, agentId);
      
      if (result.success) {
        setCode(result.content);
        setSelectedFile(fileName);
        setOutput(`File ${fileName} loaded successfully.`);
      } else {
        setError(result.error || 'An unknown error occurred');
        setOutput('Failed to load file. See error details.');
      }
    } catch (err) {
      setError(err.message || 'Failed to load file');
      setOutput('Failed to load file. See error details.');
    } finally {
      setIsExecuting(false);
    }
  };
  
  // Clear output
  const clearOutput = () => {
    setOutput('');
    setError(null);
  };
  
  // New file
  const newFile = () => {
    setSelectedFile(null);
    setCode('# Enter your Python code here\nprint("Hello, World!")');
    setOutput('');
    setError(null);
  };
  
  // Set editor language based on selected language
  const getEditorLanguage = () => {
    switch (language) {
      case 'python':
        return 'python';
      case 'javascript':
        return 'javascript';
      case 'typescript':
        return 'typescript';
      case 'bash':
        return 'shell';
      default:
        return 'python';
    }
  };
  
  return (
    <div className="code-execution-component">
      <div className="code-header">
        <div className="language-selector">
          <label htmlFor="language-select">Language:</label>
          <select 
            id="language-select"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            disabled={isExecuting}
          >
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="typescript">TypeScript</option>
            <option value="bash">Bash</option>
          </select>
        </div>
        
        <div className="file-controls">
          <button onClick={newFile} disabled={isExecuting}>New File</button>
          <button onClick={saveFile} disabled={isExecuting}>Save</button>
          <select 
            value={selectedFile || ''}
            onChange={(e) => e.target.value && loadFile(e.target.value)}
            disabled={isExecuting}
          >
            <option value="">Select File</option>
            {files.map((file, index) => (
              <option key={index} value={file}>{file}</option>
            ))}
          </select>
        </div>
        
        <div className="package-controls">
          <input
            type="text"
            placeholder="Package names (space or comma separated)"
            value={packages}
            onChange={(e) => setPackages(e.target.value)}
            disabled={isExecuting}
          />
          <button onClick={installPackages} disabled={isExecuting}>
            Install Packages
          </button>
        </div>
      </div>
      
      <div className="editor-container">
        <Editor
          height="400px"
          language={getEditorLanguage()}
          value={code}
          onChange={setCode}
          theme="vs-dark"
          options={{
            minimap: { enabled: false },
            lineNumbers: 'on',
            fontSize: 14,
            scrollBeyondLastLine: false,
            automaticLayout: true,
            readOnly: isExecuting
          }}
        />
      </div>
      
      <div className="execution-controls">
        <button 
          className="execute-button"
          onClick={executeCode}
          disabled={isExecuting}
        >
          {isExecuting ? 'Executing...' : 'Run Code'}
        </button>
        <button 
          className="clear-button"
          onClick={clearOutput}
          disabled={isExecuting}
        >
          Clear Output
        </button>
      </div>
      
      <div className="output-container">
        <div className="output-header">
          <span>Output</span>
          {error && <span className="error-indicator">Error</span>}
        </div>
        <pre className="output-content">
          {output}
          {error && <div className="error-message">Error: {error}</div>}
        </pre>
      </div>
      
      <style jsx>{`
        .code-execution-component {
          display: flex;
          flex-direction: column;
          border: 1px solid #ccc;
          border-radius: 4px;
          overflow: hidden;
          margin-bottom: 20px;
        }
        
        .code-header {
          display: flex;
          justify-content: space-between;
          padding: 10px;
          background-color: #f5f5f5;
          border-bottom: 1px solid #ccc;
        }
        
        .language-selector,
        .file-controls,
        .package-controls {
          display: flex;
          align-items: center;
          gap: 10px;
        }
        
        .editor-container {
          border-bottom: 1px solid #ccc;
        }
        
        .execution-controls {
          display: flex;
          padding: 10px;
          background-color: #f5f5f5;
          border-bottom: 1px solid #ccc;
          gap: 10px;
        }
        
        .execute-button {
          background-color: #4CAF50;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
        }
        
        .execute-button:disabled {
          background-color: #cccccc;
          cursor: not-allowed;
        }
        
        .clear-button {
          background-color: #f44336;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
        }
        
        .output-container {
          display: flex;
          flex-direction: column;
          min-height: 150px;
          max-height: 300px;
          overflow: auto;
        }
        
        .output-header {
          display: flex;
          justify-content: space-between;
          padding: 10px;
          background-color: #f5f5f5;
          border-bottom: 1px solid #ccc;
          font-weight: bold;
        }
        
        .error-indicator {
          color: #f44336;
        }
        
        .output-content {
          padding: 10px;
          white-space: pre-wrap;
          word-wrap: break-word;
          font-family: monospace;
          margin: 0;
          flex-grow: 1;
          overflow: auto;
        }
        
        .error-message {
          color: #f44336;
          margin-top: 10px;
          font-weight: bold;
        }
        
        button, select, input {
          padding: 6px 12px;
          border: 1px solid #ccc;
          border-radius: 4px;
        }
        
        input {
          min-width: 250px;
        }
      `}</style>
    </div>
  );
};

export default CodeExecutionComponent;
