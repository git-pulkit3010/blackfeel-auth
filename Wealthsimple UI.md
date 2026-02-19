```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - BlackWeave</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        /* RESET & BASE */
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            outline: none;
        }

        body, html {
            height: 100%;
            font-family: 'Manrope', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            font-size: 16px;
            color: #32302F; /* Wealthsimple 'Dune' Color */
            -webkit-font-smoothing: antialiased;
        }

        /* LAYOUT CONTAINER */
        .split-screen {
            display: flex;
            height: 100vh;
            width: 100vw;
            overflow: hidden;
        }

        /* LEFT SIDE - VISUAL */
        .visual-side {
            width: 50%;
            background-color: #F7F5F2; /* Warm off-white base */
            position: relative;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 60px;
            background-image: url('https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop'); 
            /* Abstract Luxury Texture */
            background-size: cover;
            background-position: center;
        }

        .visual-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.2); /* Slight dim for text readability */
        }

        .visual-content {
            position: relative;
            z-index: 2;
            color: white;
            max-width: 480px;
        }

        .visual-content h1 {
            font-size: 3.5rem;
            line-height: 1.1;
            font-weight: 600;
            margin-bottom: 24px;
            letter-spacing: -0.03em;
        }

        .visual-content p {
            font-size: 1.125rem;
            line-height: 1.6;
            opacity: 0.9;
        }

        /* RIGHT SIDE - FORM */
        .form-side {
            width: 50%;
            background: #FFFFFF;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 40px;
            position: relative;
        }

        .form-container {
            width: 100%;
            max-width: 420px;
        }

        .header {
            margin-bottom: 40px;
        }

        .header h2 {
            font-size: 2rem;
            font-weight: 600;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
            color: #32302F;
        }

        /* FORM ELEMENTS */
        .input-group {
            margin-bottom: 20px;
            position: relative;
        }

        .input-group label {
            display: block;
            font-size: 0.875rem;
            font-weight: 600;
            margin-bottom: 8px;
            color: #32302F;
        }

        .input-field {
            width: 100%;
            padding: 16px;
            font-size: 1rem;
            border: 1px solid #E6E6E6;
            border-radius: 8px;
            background: #FFFFFF;
            transition: all 0.2s ease;
            color: #32302F;
            font-family: inherit;
        }

        .input-field::placeholder {
            color: #999;
        }

        .input-field:focus {
            border-color: #32302F;
            box-shadow: 0 0 0 1px #32302F;
        }

        .forgot-password {
            text-align: right;
            margin-top: -10px;
            margin-bottom: 24px;
        }

        .forgot-password a {
            color: #32302F;
            font-size: 0.875rem;
            text-decoration: underline;
            text-decoration-color: rgba(50, 48, 47, 0.3);
            text-underline-offset: 4px;
        }

        .forgot-password a:hover {
            text-decoration-color: #32302F;
        }

        /* BUTTONS */
        .btn-primary {
            width: 100%;
            padding: 16px;
            background-color: #32302F;
            color: #FFFFFF;
            font-size: 1rem;
            font-weight: 600;
            border: none;
            border-radius: 30px; /* Pill shape standard for WS */
            cursor: pointer;
            transition: transform 0.1s ease, background-color 0.2s ease;
        }

        .btn-primary:hover {
            background-color: #000000;
        }

        .btn-primary:active {
            transform: scale(0.98);
        }

        .divider {
            margin: 24px 0;
            text-align: center;
            position: relative;
        }

        .divider::before {
            content: "";
            position: absolute;
            top: 50%;
            left: 0;
            width: 100%;
            height: 1px;
            background: #E6E6E6;
            z-index: 0;
        }

        .divider span {
            background: #fff;
            padding: 0 10px;
            color: #767676;
            font-size: 0.875rem;
            position: relative;
            z-index: 1;
        }

        .btn-secondary {
            width: 100%;
            padding: 14px;
            background-color: transparent;
            color: #32302F;
            font-size: 1rem;
            font-weight: 600;
            border: 1px solid #E6E6E6;
            border-radius: 30px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            transition: background-color 0.2s ease;
        }

        .btn-secondary:hover {
            background-color: #FAFAFA;
            border-color: #d1d1d1;
        }

        /* FOOTER/LINKS */
        .bottom-link {
            margin-top: 32px;
            text-align: center;
            font-size: 0.95rem;
            color: #32302F;
        }

        .bottom-link a {
            color: #32302F;
            font-weight: 600;
            text-decoration: none;
        }

        .bottom-link a:hover {
            text-decoration: underline;
        }

        /* RESPONSIVE */
        @media (max-width: 900px) {
            .visual-side {
                display: none;
            }
            .form-side {
                width: 100%;
            }
        }
    </style>
</head>
<body>

<div class="split-screen">
    <div class="visual-side">
        <div class="visual-overlay"></div>
        
        <div class="visual-content" style="margin-bottom: auto;">
            <div style="font-weight: 700; font-size: 1.5rem; letter-spacing: -0.02em;">BlackWeave</div>
        </div>

        <div class="visual-content">
            <h1>Building wealth for the next generation.</h1>
            <p>Join over 3 million people using BlackWeave to invest, save, and grow their money.</p>
        </div>
    </div>

    <div class="form-side">
        <div class="form-container">
            <div class="header">
                <h2>Welcome back</h2>
            </div>

            <form action="#" method="POST">
                <div class="input-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" class="input-field" placeholder="name@example.com" autocomplete="email" required>
                </div>

                <div class="input-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" class="input-field" placeholder="Enter your password" required>
                </div>

                <div class="forgot-password">
                    <a href="#">Forgot password?</a>
                </div>

                <button type="submit" class="btn-primary">Log in</button>
            </form>

            <div class="divider">
                <span>or</span>
            </div>

            <button type="button" class="btn-secondary">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="2" y1="12" x2="22" y2="12"></line>
                    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
                </svg>
                Log in with a passkey
            </button>

            <div class="bottom-link">
                Don't have an account? <a href="#">Sign up</a>
            </div>
        </div>
    </div>
</div>

</body>
</html>

```