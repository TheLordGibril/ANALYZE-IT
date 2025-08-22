// src/hooks/usePrediction.js
import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';

export default function usePrediction({ country, virus, dateStart, dateEnd }) {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { token } = useAuth();
  const graphqlUrl = window.__ENV__.VITE_API_URL;

  useEffect(() => {
    if (!country || !virus || !dateStart || !dateEnd || !token) return;

    setLoading(true);
    setError(null);

    fetch(graphqlUrl, {
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
      .then(console.log(`
        query Query {
          predictPandemic(virus: "${virus}", country: "${country}", date_start: "${dateStart}", date_end: "${dateEnd}")
        }
                `,))
      .then((data) => {
        console.log(data)
        if (data.errors) {
          throw new Error(data.errors[0].message);
        }
        setPrediction(data.data.predictPandemic);
      })
      .catch((err) => setError(err))
      .finally(() => setLoading(false));
  }, [country, virus, dateStart, dateEnd, token]);

  return { prediction, loading, error };
}
