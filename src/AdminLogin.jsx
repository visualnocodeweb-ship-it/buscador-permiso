import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function AdminLogin({ setApiKey }) {
    const [key, setKey] = useState('');
    const navigate = useNavigate();

    const handleSubmit = (e) => {
        e.preventDefault();
        setApiKey(key);
        navigate('/admin/dashboard');
    };

    return (
        <div>
            <h2>Acceso de Administrador</h2>
            <form onSubmit={handleSubmit}>
                <label>
                    Clave de API:
                    <input type="password" value={key} onChange={(e) => setKey(e.target.value)} />
                </label>
                <button type="submit">Ingresar</button>
            </form>
        </div>
    );
}

export default AdminLogin;
