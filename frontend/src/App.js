import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import './App.css';
import SignIn from './components/SignIn';
import SignUp from './components/SignUp';
import Home from './components/home';
import AnalysisResults from './components/AnalysisResults';

// A simple wrapper to protect routes
function PrivateRoute({ children, isAuthenticated }) {
    const location = useLocation();
    return isAuthenticated ? children : <Navigate to="/signin" state={{ from: location }} replace />;
}

function App() {
    // The initial state is always false, so the app starts on the sign-in page.
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    const handleSignInSuccess = () => {
        setIsAuthenticated(true);
    };

    const handleSignOut = () => {
        setIsAuthenticated(false);
    };

    return (
        <Router>
            <div className="App">
                <header className="App-header">
                    <h1>TALENTAI</h1>
                </header>
                <Routes>
    {/* Public routes */}
    <Route path="/signin" element={<SignIn onSignInSuccess={handleSignInSuccess} />} />
    <Route path="/signup" element={<SignUp />} />

    {/* Private routes (protected by the PrivateRoute component) */}
    <Route
        path="/home"
        element={
            <PrivateRoute isAuthenticated={isAuthenticated}>
                <Home onSignOut={handleSignOut} />
            </PrivateRoute>
        }
    />
    <Route
        path="/analysis"
        element={
            <PrivateRoute isAuthenticated={isAuthenticated}>
                <AnalysisResults />
            </PrivateRoute>
        }
    />
    
    {/* --- This is the corrected root path route --- */}
    <Route path="/" element={<Navigate to={isAuthenticated ? "/home" : "/signin"} />} />

    {/* Redirects any other invalid path to the correct starting point */}
    <Route path="*" element={<Navigate to={isAuthenticated ? "/home" : "/signin"} />} />
</Routes>
            </div>
        </Router>
    );
}

export default App;