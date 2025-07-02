import React, { useState } from "react";
import Input from "../components/Input";
import GraphCard from "../components/GraphCard";
import NumberCard from "../components/NumberCard";
import TextCard from "../components/TextCard";
import { fetchPrediction } from "../services/ApiService";

const AnalyzeIt = () => {
  const [selectedModels, setSelectedModels] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Variables d'exemple à envoyer à l'API
  const variables = {
    country: "France",
    virus: "covid",
    date: "2025-07-01",
  };

  const numbers = ["total_cases", "total_deaths", "new_cases", "new_deaths", "cases_in_30d", "deaths_in_30d", "new_countries_next_week"];
  const graphs = ["transmission_rate", "mortality_rate"];
  const text = ["geographic_spread", "peak_date", "estimated_duration_days"];

  const renderModelComponent = (model) => {
    if (numbers.includes(model)) {
      return <NumberCard key={model} name={model} value={prediction?.[model] || "N/A"} />;
    } else if (graphs.includes(model)) {
      return <GraphCard key={model} name={model} value={prediction?.[model] || "N/A"} />;
    } else if (text.includes(model)) {
      return <TextCard key={model} name={model} text={prediction?.[model] || "N/A"} />;
    } else {
      return null;
    }
  };

  const handleFetch = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchPrediction(variables);
      setPrediction(result);
      setSelectedModels(Object.keys(result)); // On sélectionne les clés du résultat pour afficher
    } catch (err) {
      setError("Erreur lors de la récupération");
    }
    setLoading(false);
  };

  return (
    <div className="h-screen flex flex-col bg-white text-black">
      <div className="bg-blue-600 p-2 flex justify-between items-center text-white">
        <div>Analyze-it</div>
        <button onClick={handleFetch} disabled={loading} className="bg-white text-blue-600 px-3 py-1 rounded">
          {loading ? "Chargement..." : "Charger Prédiction"}
        </button>
      </div>

      <div className="flex flex-1">
        <Input selectedModels={selectedModels} setSelectedModels={setSelectedModels} />
        <div className="flex flex-wrap p-4 overflow-y-auto">
          {error && <div className="text-red-500">{error}</div>}
          {!error && prediction && selectedModels.map((model) => renderModelComponent(model))}
        </div>
      </div>
    </div>
  );
};

export default AnalyzeIt;
