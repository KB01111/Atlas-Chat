import React, { useState } from 'react';

const CodeExecutionComponent: React.FC = () => {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [output, setOutput] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validateCode = () => {
    if (!code.trim()) {
      setError('Code cannot be empty.');
      return false;
    }
    if (code.length > 10000) {
      setError('Code is too long.');
      return false;
    }
    setError(null);
    return true;
  };

  const handleExecute = async () => {
    if (!validateCode()) return;

    setLoading(true);
    setOutput(null);
    try {
      const response = await fetch('/api/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language }),
      });
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      const data = await response.json();
      if (data.error) {
        setOutput(`Execution error: ${data.error}`);
      } else {
        setOutput(data.output);
      }
    } catch (err: any) {
      setOutput('Network or server error during code execution.');
    }
    setLoading(false);
  };

  return (
    <div>
      <h2>Run Code</h2>
      <label>
        Language/Runtime:
        <select value={language} onChange={(e) => setLanguage(e.target.value)}>
          <option value="python">Python</option>
          <option value="javascript">JavaScript</option>
          <option value="bash">Bash</option>
        </select>
      </label>
      <br />
      <textarea
        rows={8}
        cols={80}
        value={code}
        onChange={(e) => setCode(e.target.value)}
        placeholder="Enter your code here"
        style={{ fontFamily: 'monospace', background: '#f9f9f9' }}
      />
      <br />
      <button onClick={handleExecute} disabled={loading}>
        {loading ? 'Running...' : 'Run Code'}
      </button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {output && (
        <pre style={{ background: '#eee', padding: '10px', overflowX: 'auto' }}>
          <code>{output}</code>
        </pre>
      )}
    </div>
  );
};

export default CodeExecutionComponent;