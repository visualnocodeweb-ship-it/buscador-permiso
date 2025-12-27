import React, { useState, useEffect } from 'react';

const API_URL = 'http://localhost:8000'; // Asumiendo que el backend corre en el puerto 8000

function AdminDashboard({ apiKey }) {
    const [stats, setStats] = useState(null);
    const [history, setHistory] = useState([]);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            try {
                const headers = { 'X-API-Key': apiKey };

                const statsRes = await fetch(`${API_URL}/admin/stats`, { headers });
                if (!statsRes.ok) {
                    throw new Error(`Error ${statsRes.status}: No se pudieron cargar las estadísticas.`);
                }
                const statsData = await statsRes.json();
                setStats(statsData);

                const historyRes = await fetch(`${API_URL}/admin/history`, { headers });
                if (!historyRes.ok) {
                    throw new Error(`Error ${historyRes.status}: No se pudo cargar el historial.`);
                }
                const historyData = await historyRes.json();
                setHistory(historyData);

            } catch (err) {
                setError(err.message);
            }
        };

        if (apiKey) {
            fetchData();
        } else {
            setError("Clave de API no proporcionada.");
        }
    }, [apiKey]);

    if (error) {
        return <div><h2>Error</h2><p>{error}</p></div>;
    }

    if (!stats) {
        return <div>Cargando...</div>;
    }

    return (
        <div>
            <h2>Panel de Administración</h2>
            
            <h3>Estadísticas</h3>
            <p>Total de Búsquedas: {stats.query_count}</p>
            <p>Total de Registros (Postgres): {stats.record_count}</p>

            <h3>Historial de Búsquedas Recientes</h3>
            <table>
                <thead>
                    <tr>
                        <th>Fecha y Hora</th>
                        <th>Email</th>
                        <th>Consulta</th>
                        <th>Resultados</th>
                        <th>Fuente</th>
                        <th>Primer Resultado</th>
                    </tr>
                </thead>
                <tbody>
                    {history.map((item) => (
                        <tr key={item.id}>
                            <td>{new Date(item.timestamp).toLocaleString()}</td>
                            <td>{item.email}</td>
                            <td>{item.query}</td>
                            <td>{item.results_count}</td>
                            <td>{item.first_result_source}</td>
                            <td>{item.first_result_name}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default AdminDashboard;
