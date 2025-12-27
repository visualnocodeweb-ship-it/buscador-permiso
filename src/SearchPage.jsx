import { useState } from 'react';

function ResultsDisplay({ results }) {
    if (results.length === 0) {
      return null;
    }
  
    const renderValue = (value) => value ?? 'No disponible';
    const getPermissionStatus = (status) => {
      if (!status) return 'No disponible';
      return String(status).toLowerCase() === 'completed' ? 'Permiso Pago' : 'Permiso no pagado';
    };
    const getFriendlySource = (source) => source === 'PostgreSQL' ? 'Base de Datos' : source;
  
    return (
      <div className="results-list">
        {results.map((result, index) => (
          <div key={index} className="result-card">
            <div className="card-header">
              <h3>{renderValue(result.data.customer_first_name)} {renderValue(result.data.customer_last_name)}</h3>
              <span className="source-tag">{getFriendlySource(result.source)}</span>
            </div>
            <div className="card-body">
              <p><strong>DNI:</strong> {renderValue(result.data.nro_documento)}</p>
              <p><strong>Email:</strong> {renderValue(result.data.customer_email)}</p>
              <p><strong>Teléfono:</strong> {renderValue(result.data.customer_phone)}</p>
              <p><strong>Permiso:</strong> {renderValue(result.data.line_item_name)}</p>
              <p><strong>Región de Pesca:</strong> {renderValue(result.data.region_pesca)}</p>
              <p><strong>Fecha de Creación:</strong> {new Date(result.data.date_created).toLocaleString()}</p>
              <p><strong>Estado:</strong> {getPermissionStatus(result.data.status)}</p>
            </div>
          </div>
        ))}
      </div>
    );
  }

function SearchPage({ session }) {
    const [searchTerm, setSearchTerm] = useState('');
    const [results, setResults] = useState([]);
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);
  
    const handleSearch = async (e) => {
      e.preventDefault();
      if (!searchTerm.trim()) {
        setMessage('Por favor, ingrese un término de búsqueda.');
        return;
      }
      setMessage('');
      setResults([]);
      setLoading(true);
  
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
        const response = await fetch(`${apiUrl}/search`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            query: searchTerm,
            email: session.user.email 
          }),
        });
  
        const data = await response.json();
        setResults(response.ok ? data : []);
        if (response.ok && data.length === 0) {
          setMessage('No se encontraron resultados.');
        } else if (!response.ok) {
          setMessage(data.detail || 'Ocurrió un error en la búsqueda.');
        }
      } catch (error) {
        console.error('Error al conectar con el backend:', error);
        setMessage('Error al conectar con el servidor.');
      } finally {
        setLoading(false);
      }
    };
  
    return (
      <div className="App">
        <div className="main-panel">
          <img src="/Guardafauna - 1.png" alt="Guardafauna - Dirección Provincial de Fauna" className="main-logo" />
          <header className="app-header">
            <svg className="header-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
            <h1>Sistema de Búsqueda Permiso de Pesca NQN</h1>
            <p className="subtitle">Consulte registros en la Base de Datos de Fauna NQN.</p>
          </header>
  
          <form onSubmit={handleSearch}>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Buscar por Nombre, Apellido o DNI..."
              disabled={loading}
            />
            <button type="submit" disabled={loading}>
              {loading ? 'Buscando...' : 'Buscar'}
            </button>
          </form>
  
          {message && <p className="message">{message}</p>}
        </div>
  
        <ResultsDisplay results={results} />
      </div>
    );
  }

  export default SearchPage;
