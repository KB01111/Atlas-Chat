import React, { useState, useRef } from 'react';
import { useSupabase } from '../Providers/SupabaseProvider';
import { useNavigate } from 'react-router-dom';

const Register: React.FC = () => {
  const { supabase } = useSupabase();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const errorRef = useRef<HTMLParagraphElement>(null);

  const getPasswordStrength = (pwd: string) => {
    let score = 0;
    if (pwd.length >= 8) score++;
    if (/[A-Z]/.test(pwd)) score++;
    if (/[0-9]/.test(pwd)) score++;
    if (/[^A-Za-z0-9]/.test(pwd)) score++;
    if (score <= 1) return 'Weak';
    if (score === 2) return 'Moderate';
    return 'Strong';
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      errorRef.current?.focus();
      setLoading(false);
      return;
    }

    try {
      const { error } = await supabase.auth.signUp({ email, password });
      if (error) {
        setError(error.message);
        errorRef.current?.focus();
      } else {
        setSuccess('Registration successful! Redirecting...');
        setTimeout(() => navigate('/chat'), 1000);
      }
    } catch {
      setError('Network error. Please try again.');
      errorRef.current?.focus();
    }
    setLoading(false);
  };

  const handleOAuthRegister = async (provider: 'google' | 'github') => {
    setLoading(true);
    setError(null);
    try {
      const { error } = await supabase.auth.signInWithOAuth({ provider });
      if (error) {
        setError(error.message);
        errorRef.current?.focus();
      }
    } catch {
      setError('Network error during OAuth.');
      errorRef.current?.focus();
    }
    setLoading(false);
  };

  return (
    <form onSubmit={handleRegister} aria-labelledby="register-title">
      <h2 id="register-title">Register</h2>
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
      <p>Password strength: {getPasswordStrength(password)}</p>
      <input
        type="password"
        placeholder="Confirm Password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        required
        aria-label="Confirm Password"
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Registering...' : 'Register'}
      </button>
      <button type="button" onClick={() => handleOAuthRegister('google')} disabled={loading}>
        Register with Google
      </button>
      <button type="button" onClick={() => handleOAuthRegister('github')} disabled={loading}>
        Register with GitHub
      </button>
      {error && (
        <p
          ref={errorRef}
          style={{ color: 'red' }}
          role="alert"
          tabIndex={-1}
        >
          {error}
        </p>
      )}
      {success && <p style={{ color: 'green' }}>{success}</p>}
    </form>
  );
};

export default Register;