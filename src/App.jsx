import { useState, useEffect } from 'react';
import { Routes, Route, Link, Navigate } from 'react-router-dom';
import './App.css';

import Auth from './Auth';
import SearchPage from './SearchPage';
import AdminLogin from './AdminLogin';
import AdminDashboard from './AdminDashboard';

function ProtectedRoute({ apiKey, children }) {
    if (!apiKey) {
        return <Navigate to="/admin" replace />;
    }
    return children;
}

function App() {
    const [session, setSession] = useState(null);
    const [apiKey, setApiKey] = useState(null); // For admin panel
    const [isNavOpen, setIsNavOpen] = useState(false);

    useEffect(() => {
        const savedEmail = localStorage.getItem('userEmail');
        if (savedEmail) {
            setSession({ user: { email: savedEmail } });
        }
    }, []);

    const handleLogin = (email) => {
        localStorage.setItem('userEmail', email);
        setSession({ user: { email } });
    };

    const handleLogout = () => {
        localStorage.removeItem('userEmail');
        setSession(null);
        setIsNavOpen(false);
    };

    return (
        <div>
            {session && (
                <nav className="main-nav">
                    <div className="nav-logo">
                        <Link to="/">Buscador</Link>
                    </div>
                    <div className="hamburger" onClick={() => setIsNavOpen(!isNavOpen)}>
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                    <div className={`nav-links ${isNavOpen ? 'open' : ''}`}>
                        <Link to="/admin" onClick={() => setIsNavOpen(false)}>Admin</Link>
                        <span>{session.user.email}</span>
                        <button onClick={handleLogout}>Cerrar Sesión</button>
                    </div>
                </nav>
            )}
            <main>
                <Routes>
                    <Route path="/admin" element={<AdminLogin setApiKey={setApiKey} />} />
                    <Route
                        path="/admin/dashboard"
                        element={
                            <ProtectedRoute apiKey={apiKey}>
                                <AdminDashboard apiKey={apiKey} />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/"
                        element={!session ? <Auth onLogin={handleLogin} /> : <SearchPage session={session} />}
                    />
                    <Route path="*" element={<Navigate to="/" />} />
                </Routes>
            </main>
        </div>
    );
}

export default App;
