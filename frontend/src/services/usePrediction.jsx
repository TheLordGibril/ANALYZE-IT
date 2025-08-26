import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';

export default function usePrediction({ country, virus, dateStart, dateEnd }) {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { token } = useAuth();
  const apiUrl = window.__ENV__.VITE_API_URL;
  const selectedCountry = window.__ENV__.VITE_COUNTRY;

  useEffect(() => {
    if (!country || !virus || !dateStart || !dateEnd) return;
    if (selectedCountry === "USA" && !token) return;

    setLoading(true);
    setError(null);

    if (selectedCountry === "USA") {
      fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          query: `
            query Query {
              predictPandemic(virus: "${virus.toLowerCase()}", country: "${country}", date_start: "${dateStart}", date_end: "${dateEnd}")
            }
          `,
        }),
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.errors) throw new Error(data.errors[0].message);
          setPrediction(data.data.predictPandemic);
        })
        .catch((err) => setError(err))
        .finally(() => setLoading(false));
    } else {
      const url = `${apiUrl}/predict?country=${encodeURIComponent(country)}&virus=${encodeURIComponent(virus)}&date_start=${encodeURIComponent(dateStart)}&date_end=${encodeURIComponent(dateEnd)}`;
      fetch(url, {
        method: 'GET',
      })
        .then((res) => res.json())
        .then((data) => {
          setPrediction(data);
        })
        .catch((err) => setError(err))
        .finally(() => setLoading(false));
    }
  }, [country, virus, dateStart, dateEnd, token, selectedCountry, apiUrl]);

  return { prediction, loading, error };
}