import { useState } from 'react';

export default function Auth({ onLogin }) {
    const [loading, setLoading] = useState(false);
    const [email, setEmail] = useState('');

    const handleLogin = (e) => {
        e.preventDefault();
        setLoading(true);
        // Simulate a short loading time for better UX
        setTimeout(() => {
            onLogin(email);
            setLoading(false);
        }, 500);
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <img src="/Captura de pantalla 2025-10-13 021011.png" alt="Logo" className="auth-logo" />
                <h2>Buscador de Permisos</h2>
                <p className="auth-subtitle">Ingresa tu correo para continuar</p>

                {loading ? (
                    <div className="loader">Cargando...</div>
                ) : (
                    <>
                        <form onSubmit={handleLogin} className="auth-form">
                            <input
                                id="email"
                                className="auth-input"
                                type="email"
                                placeholder="Tu email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                            <button className="auth-button" type="submit" disabled={loading}>
                                Ingresar
                            </button>
                        </form>
                    </>
                )}
            </div>
        </div>
    );
}
