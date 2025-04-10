import React, { useState, useRef } from 'react';
import { useSupabase } from '../Providers/SupabaseProvider';
import { useNavigate } from 'react-router-dom';

const Login: React.FC = () => {
  const { supabase } = useSupabase();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const errorRef = useRef<HTMLParagraphElement>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const { error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) {
        setError(error.message);
        errorRef.current?.focus();
      } else {
        setSuccess('Login successful! Redirecting...');
        setTimeout(() => navigate('/chat'), 1000);
      }
    } catch (err: any) {
      setError('Network error. Please try again.');
      errorRef.current?.focus();
    }
    setLoading(false);
  };

  const handleOAuthLogin = async (provider: 'google' | 'github') => {
    setLoading(true);
    setError(null);
    try {
      const { error } = await supabase.auth.signInWithOAuth({ provider });
      if (error) {
        setError(error.message);
        errorRef.current?.focus();
      }
    } catch {
      setError('Network error during OAuth login.');
      errorRef.current?.focus();
    }
    setLoading(false);
  };

  return (
    <form onSubmit={handleLogin} aria-labelledby="login-title">
      <h2 id="login-title">Login</h2>
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
        aria-label="Email"
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
        aria-label="Password"
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
      <button type="button" onClick={() => handleOAuthLogin('google')} disabled={loading}>
        Login with Google
      </button>
      <button type="button" onClick={() => handleOAuthLogin('github')} disabled={loading}>
        Login with GitHub
      </button>
      {error && (
        <p ref={errorRef} style={{ color: 'red' }} role="alert" tabIndex={-1}>
          {error}
        </p>
      )}
      {success && <p style={{ color: 'green' }}>{success}</p>}
    </form>
  );
};

export default Login;
