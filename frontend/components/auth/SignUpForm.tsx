'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { GoogleOAuthButton } from './GoogleOAuthButton';
import { VerificationPending } from './VerificationPending';
import { formatPhoneNumber, isValidPhoneNumber } from '@/lib/utils/phone';

export function SignUpForm() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    phone: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showVerification, setShowVerification] = useState(false);

  const validateForm = () => {
    if (formData.password.length < 12) {
      setError('Password must be at least 12 characters long');
      return false;
    }
    if (!/[A-Z]/.test(formData.password)) {
      setError('Password must contain at least one uppercase letter');
      return false;
    }
    if (!/[a-z]/.test(formData.password)) {
      setError('Password must contain at least one lowercase letter');
      return false;
    }
    if (!/[0-9]/.test(formData.password)) {
      setError('Password must contain at least one number');
      return false;
    }
    if (!/[^A-Za-z0-9]/.test(formData.password)) {
      setError('Password must contain at least one special character');
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return false;
    }
    if (!isValidPhoneNumber(formData.phone)) {
      setError('Please enter a valid phone number in international format (e.g., +919876543210)');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
          phone: formData.phone,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Sign up failed');
      }

      // Show verification pending screen
      setShowVerification(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sign up failed');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: string, value: string) => {
    if (field === 'phone') {
      // Format phone number to ensure it's in E.164 format
      const formattedValue = formatPhoneNumber(value);
      setFormData((prev) => ({ ...prev, [field]: formattedValue }));
    } else {
      setFormData((prev) => ({ ...prev, [field]: value }));
    }
    setError('');
  };

  if (showVerification) {
    return <VerificationPending email={formData.email} phone={formData.phone} />;
  }

  return (
    <form id="signupForm" onSubmit={handleSubmit}>
      {error && (
        <div className="rounded-md bg-red-50 p-4 mb-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      <div className="input-group">
        <label>Email</label>
        <input
          type="email"
          name="email"
          className="input-field"
          placeholder="name@example.com"
          required
          value={formData.email}
          onChange={(e) => handleChange('email', e.target.value)}
          disabled={loading}
        />
      </div>

      <div className="input-group">
        <label>Phone Number</label>
        <input
          type="tel"
          name="phone"
          className="input-field"
          placeholder="Phone number (with country code)"
          required
          value={formData.phone}
          onChange={(e) => handleChange('phone', e.target.value)}
          disabled={loading}
        />
      </div>

      <div className="input-group">
        <label>Password</label>
        <input
          type="password"
          name="password"
          className="input-field"
          placeholder="Create password"
          required
          value={formData.password}
          onChange={(e) => handleChange('password', e.target.value)}
          disabled={loading}
        />
        <p className="text-xs text-gray-500 mt-1">Min 12 chars, 1 uppercase, 1 number, 1 special</p>
      </div>

      <div className="input-group">
        <label>Confirm Password</label>
        <input
          type="password"
          name="confirmPassword"
          className="input-field"
          placeholder="Repeat password"
          required
          value={formData.confirmPassword}
          onChange={(e) => handleChange('confirmPassword', e.target.value)}
          disabled={loading}
        />
      </div>

      <div className="button-group">
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? 'Creating account...' : 'Create account'}
        </button>
        <div className="btn-google">
          <GoogleOAuthButton mode="signup" iconOnly={true} />
        </div>
      </div>
    </form>
  );
}
