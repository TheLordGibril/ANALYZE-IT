// src/hooks/usePrediction.js
import { useEffect, useState } from 'react';

export default function usePrediction({ country, virus, dateStart, dateEnd }) {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!country || !virus || !dateStart || !dateEnd) return;

    setLoading(true);
    setError(null);

    fetch('http://localhost:4000/graphql', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
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
  }, [country, virus, dateStart, dateEnd]);

  return { prediction, loading, error };
}
