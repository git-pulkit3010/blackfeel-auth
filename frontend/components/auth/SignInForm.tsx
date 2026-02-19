'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { GoogleOAuthButton } from './GoogleOAuthButton';

export function SignInForm() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('/api/auth/signin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Sign in failed');
      }

      router.push('/dashboard');
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sign in failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form id="loginForm" onSubmit={handleSubmit}>
      {error && (
        <div className="rounded-md bg-red-50 p-4 mb-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      <div className="input-group">
        <label htmlFor="email">Email</label>
        <input
          id="email-address"
          name="email"
          type="email"
          autoComplete="email"
          required
          className="input-field"
          placeholder="name@example.com"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          disabled={loading}
        />
      </div>

      <div className="input-group">
        <label htmlFor="password">Password</label>
        <input
          id="password"
          name="password"
          type="password"
          autoComplete="current-password"
          required
          className="input-field"
          placeholder="••••••••"
          value={formData.password}
          onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          disabled={loading}
        />
      </div>

      <div className="form-utils">
        <a href="#" className="text-link">Forgot password?</a>
      </div>

      <div className="button-group">
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? 'Logging in...' : 'Log in'}
        </button>
        <div className="btn-google">
          <GoogleOAuthButton mode="signin" iconOnly={true} />
        </div>
      </div>
    </form>
  );
}
