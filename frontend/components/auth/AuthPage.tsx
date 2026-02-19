'use client';

import { useState } from 'react';
import { SignInForm } from './SignInForm';
import { SignUpForm } from './SignUpForm';

export function AuthPage() {
  const [mode, setMode] = useState<'signin' | 'signup'>('signin');

  return (

    <div className="split-screen">
      <section className="visual-side">
        <div className="visual-overlay"></div>
        <div className="brand-identity">
          <div className="logo-container">
            <svg className="swan-icon" viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg">
              <path d="M20 50 C 20 20, 50 10, 50 30 C 50 50, 80 50, 80 30" stroke="white" fill="none" strokeWidth="3" />
              <line x1="10" y1="55" x2="90" y2="55" stroke="white" strokeWidth="2" />
            </svg>
            <span className="brand-name">BlackWeave</span>
          </div>
        </div>
        <div className="marketing-copy">
          <h1>Half code, Half culture.<br />Designed with AI. Felt in real life.</h1>
        </div>
      </section>

      <section className="form-side">
        <div className="form-wrapper">
          <header className="form-header">
            <h2>{mode === 'signin' ? 'Welcome Back!' : 'Create account'}</h2>
          </header>

          {mode === 'signin' ? <SignInForm /> : <SignUpForm />}

          <footer className="footer-link">
            {mode === 'signin'
              ? <>New to BlackWeave? <button onClick={() => setMode('signup')}>Sign up</button></>
              : <>Already a member? <button onClick={() => setMode('signin')}>Log in</button></>
            }
          </footer>
        </div>
      </section>
    </div>
  );
}