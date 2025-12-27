import { useState } from 'react';
import { supabase } from './supabaseClient';

export default function Auth() {
    const [loading, setLoading] = useState(false);
    const [email, setEmail] = useState('');

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const { error } = await supabase.auth.signInWithOtp({ email });
            if (error) throw error;
            alert('¡Revisa tu correo para el enlace de inicio de sesión!');
        } catch (error) {
            alert(error.error_description || error.message);
        } finally {
            setLoading(false);
        }
    };

    const handleGoogleLogin = async () => {
        setLoading(true);
        try {
            const { error } = await supabase.auth.signInWithOAuth({
                provider: 'google',
            });
            if (error) throw error;
        } catch (error) {
            alert(error.error_description || error.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <img src="/Captura de pantalla 2025-10-13 021011.png" alt="Logo" className="auth-logo" />
                <h2>Buscador de Permisos</h2>
                <p className="auth-subtitle">Inicia sesión para continuar</p>

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
                                Enviar enlace mágico
                            </button>
                        </form>

                        <div className="auth-divider">
                            <span>o</span>
                        </div>

                        <button
                            className="auth-button google"
                            onClick={handleGoogleLogin}
                            disabled={loading}
                        >
                            Iniciar sesión con Google
                        </button>
                        <p className="auth-reminder">
                            (Recuerda configurar el proveedor de Google en Supabase.)
                        </p>
                    </>
                )}
            </div>
        </div>
    );
}
