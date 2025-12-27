import React, { useState, useEffect } from 'react';

function AdminDashboard({ apiKey }) {
    const [stats, setStats] = useState(null);
    const [history, setHistory] = useState([]);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(true);

    const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

    const formatDate = (dateString) => {
        if (!dateString) return 'No disponible';
        try {
            const date = new Date(dateString);
            if (isNaN(date.getTime())) { 
                const parts = dateString.split(/[-/]/); 
                let parsedDate;
                if (parts.length === 3) {
                    if (parts[0].length === 4) { 
                        parsedDate = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
                    } 
                    else if (parts[2].length === 4) {
                        parsedDate = new Date(parseInt(parts[2]), parseInt(parts[1]) - 1, parseInt(parts[0]));
                    }
                }
                if (!parsedDate || isNaN(parsedDate.getTime())) {
                    parsedDate = new Date(dateString);
                }

                if (parsedDate && !isNaN(parsedDate.getTime())) {
                    return parsedDate.toLocaleDateString('es-AR', { year: 'numeric', month: '2-digit', day: '2-digit' }) + ' ' +
                           parsedDate.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' });
                }
            } else {
                return date.toLocaleDateString('es-AR', { year: 'numeric', month: '2-digit', day: '2-digit' }) + ' ' +
                       date.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' });
            }
        } catch (e) {
            console.error("Error parsing date:", dateString, e);
        }
        return 'No disponible';
    };

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const headers = { 'X-API-Key': apiKey };

                const statsRes = await fetch(`${apiUrl}/admin/stats`, { headers });
                if (!statsRes.ok) {
                    throw new Error(`Error ${statsRes.status}: No se pudieron cargar las estadísticas.`);
                }
                const statsData = await statsRes.json();
                setStats(statsData);

                const historyRes = await fetch(`${apiUrl}/admin/history`, { headers });
                if (!historyRes.ok) {
                    throw new Error(`Error ${historyRes.status}: No se pudo cargar el historial.`);
                }
                const historyData = await historyRes.json();
                setHistory(historyData);

            } catch (err) {
                setError(err.message);
                console.error("Error fetching admin data:", err);
            } finally {
                setLoading(false);
            }
        };

        if (apiKey) {
            fetchData();
        } else {
            setError("Clave de API no proporcionada. Acceso denegado.");
            setLoading(false);
        }
    }, [apiKey, apiUrl]);

    if (loading) {
        return <div>Cargando panel de administración...</div>;
    }

    if (error) {
        return <div><h2>Error</h2><p>{error}</p></div>;
    }

    return (
        <div className="main-panel"> {/* Usar clase main-panel para centrado y estilo */}
            <h2>Panel de Administración</h2>
            
            <h3>Estadísticas Generales</h3>
            <p>Total de Búsquedas Registradas: {stats.query_count}</p>
            <p>Total de Registros en Base de Datos (Postgres): {stats.record_count}</p>

            <h3>Historial de Consultas Recientes</h3>
            {history.length === 0 ? (
                <p>No hay historial de consultas disponible.</p>
            ) : (
                <table>
                    <thead>
                        <tr>
                            <th>Fecha de la Consulta</th>
                            <th>Email que inició</th>
                            <th>Persona Consultada</th>
                            <th>Búsqueda Original</th>
                            <th>Resultados (Cant.)</th>
                            <th>Fuente</th>
                        </tr>
                    </thead>
                    <tbody>
                        {history.map((item) => (
                            <tr key={item.id}>
                                <td>{formatDate(item.timestamp)}</td>
                                <td>{item.email}</td>
                                <td>{item.first_result_name || 'No disponible'}</td>
                                <td>{item.query}</td>
                                <td>{item.results_count}</td>
                                <td>{item.first_result_source || 'No disponible'}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
}

export default AdminDashboard;
