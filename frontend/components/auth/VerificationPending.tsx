'use client';

import { useState } from 'react';

interface VerificationPendingProps {
  email: string;
  phone?: string;
}

export function VerificationPending({ email, phone }: VerificationPendingProps) {
  const [resending, setResending] = useState(false);
  const [message, setMessage] = useState('');

  const handleResend = async () => {
    setResending(true);
    setMessage('');

    try {
      const response = await fetch('/api/auth/resend-verification', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage('Verification email sent! Please check your inbox.');
      } else {
        setMessage(data.error || 'Failed to resend email');
      }
    } catch (err) {
      setMessage('Failed to resend email. Please try again.');
    } finally {
      setResending(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-blue-100">
            <svg
              className="h-6 w-6 text-blue-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
          </div>
          
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Check your messages
          </h2>
          
          <p className="mt-2 text-sm text-gray-600">
            We've sent a verification link to
            <br />
            <span className="font-medium text-gray-900">{email}</span>
            {phone && (
              <>
                <br />
                and via WhatsApp to
                <br />
                <span className="font-medium text-gray-900">{phone}</span>
              </>
            )}
          </p>
        </div>

        <div className="rounded-md bg-blue-50 p-4">
          <div className="text-sm text-blue-700">
            <p className="font-medium">Please verify your account to continue</p>
            <p className="mt-1">Click the link in the email or WhatsApp message to activate your account.</p>
          </div>
        </div>

        {message && (
          <div className={`rounded-md p-4 ${
            message.includes('sent') ? 'bg-green-50' : 'bg-red-50'
          }`}>
            <p className={`text-sm ${
              message.includes('sent') ? 'text-green-800' : 'text-red-800'
            }`}>
              {message}
            </p>
          </div>
        )}

        <div className="text-center">
          <p className="text-sm text-gray-600">
            Didn't receive the email?{' '}
            <button
              onClick={handleResend}
              disabled={resending}
              className="font-medium text-blue-600 hover:text-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {resending ? 'Sending...' : 'Resend verification email'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
