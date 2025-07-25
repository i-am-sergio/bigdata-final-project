import { useState } from "react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import "./App.css";

function App() {
  const [data, setData] = useState([]);
  const [sensorFilter, setSensorFilter] = useState("");
  const [fechaFilter, setFechaFilter] = useState("");
  const [turnoFilter, setTurnoFilter] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const turnos = ["mañana", "tarde", "noche"];
  const sensores = ["sound", "humidity", "light", "pressure", "temperature"];
  const filtered = data;

  const getHeaders = () => {
    if (filtered.length === 0) return [];
    return Object.keys(filtered[0]);
  };

  const formatLabel = (key) =>
    key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

  const handleSend = async () => {
    if (!sensorFilter || !fechaFilter || !turnoFilter) {
      setErrorMessage("Por favor selecciona todos los filtros.");
      setData([]);
      return;
    }

    const safeTurno = turnoFilter.replace("ñ", "n");
    const url = `http://localhost:5000/query?sensor=${sensorFilter}&fecha=${fechaFilter}&turno=${safeTurno}`;
    console.log("Consulta al backend:", url);

    setLoading(true);

    try {
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error("Error en el servidor");
      }

      const result = await response.json();

      if (Array.isArray(result) && result.length > 0) {
        setData(result);
        setErrorMessage("");
      } else {
        setData([]);
        setErrorMessage("No hay datos para los filtros seleccionados.");
      }
    } catch (error) {
      console.error("Error details:", error);
      setData([]);
      setErrorMessage("Error en el servidor o conexión fallida.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <h1 className="app-title">Monitor de Sensores</h1>

      <div className="filter-container">
        <select
          className="filter-select"
          value={sensorFilter}
          onChange={(e) => setSensorFilter(e.target.value)}
        >
          <option value="">Escoge sensor</option>
          {sensores.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>

        <DatePicker
          className="filter-select"
          selected={
            fechaFilter
              ? new Date(
                  parseInt(fechaFilter.split("-")[0]),
                  parseInt(fechaFilter.split("-")[1]) - 1,
                  parseInt(fechaFilter.split("-")[2])
                )
              : null
          }
          onChange={(date) => {
            const localDate = new Date(
              date.getTime() - date.getTimezoneOffset() * 60000
            )
              .toISOString()
              .split("T")[0];
            setFechaFilter(localDate);
          }}
          minDate={new Date("2025-07-24")}
          maxDate={new Date("2030-12-31")}
          placeholderText="Selecciona una fecha"
          dateFormat="yyyy-MM-dd"
        />

        <select
          className="filter-select"
          value={turnoFilter}
          onChange={(e) => setTurnoFilter(e.target.value)}
        >
          <option value="">Escoge turno</option>
          {turnos.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>

        <button className="send-button" onClick={handleSend}>
          Enviar
        </button>
      </div>

      {errorMessage && <div className="error-message">{errorMessage}</div>}

      {filtered.length > 0 && (
        <table className="sensor-table">
          <thead>
            <tr>
              {getHeaders().map((key) => (
                <th key={key} className="table-header">
                  {formatLabel(key)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((d, idx) => (
              <tr key={idx}>
                {getHeaders().map((key) => (
                  <td key={key} className="table-cell">
                    {typeof d[key] === "number"
                      ? d[key].toFixed(2)
                      : d[key] || ""}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {loading && (
        <div className="overlay">
          <div className="spinner"></div>
        </div>
      )}
    </div>
  );
}

export default App;
