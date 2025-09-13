import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function SignIn({ onSignInSuccess }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSignIn = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        try {
            await axios.post('http://localhost:5000/api/login', { username, password }, {
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            // Call the prop to notify the parent about successful sign-in
            onSignInSuccess();
            
            // --- The crucial addition to manually navigate ---
            navigate('/home');

        } catch (err) {
            setError(err.response?.data?.error || 'Login failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <h2>Sign In</h2>
            <form onSubmit={handleSignIn}>
                <input
                    type="text"
                    placeholder="Username"
                    className="auth-input"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                />
                <input
                    type="password"
                    placeholder="Password"
                    className="auth-input"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <button type="submit" disabled={loading} className="auth-button">
                    {loading ? 'Signing In...' : 'Sign In'}
                </button>
            </form>
            {error && <p className="error-message">{error}</p>}
            <p className="auth-link-text">
                Don't have an account?{' '}
                <button className="link-button" onClick={() => navigate('/signup')}>
                    Sign Up
                </button>
            </p>
        </div>
    );
}

export default SignIn;