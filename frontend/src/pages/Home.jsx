import React, { useState } from "react";
import Input from "../components/Input";
import GraphCard from "../components/GraphCard";
import NumberCard from "../components/NumberCard";
import TextCard from "../components/TextCard";

const AnalyzeIt = () => {
  const [selectedModels, setSelectedModels] = useState([]);
  const [parameters, setParameters] = useState({
    "country": "France",
    "virus": "Covid",
    "date_start": "2019-09-01",
    "date_end": "2021-03-01"
  });

  const numbers = ["total_cases", "total_deaths", "cases_in_30d", "deaths_in_30d", "new_countries_next_week", "estimated_duration_days"];
  const graphs = ["transmission_rate", "mortality_rate", "new_cases", "new_deaths",];
  const text = ["geographic_spread", "peak_date"];

  const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May']
  const values = [10, 20, 15, 30, 25]

  const renderModelComponent = (model) => {
    console.log(`Rendering model: ${model}`);
    if (numbers.includes(model)) {
      return (
        <NumberCard key={model} name={model} value={model} parameters={parameters} />
      );
    } else if (graphs.includes(model)) {
      return (
        <GraphCard key={model} name={model} value={model} parameters={parameters} />
      );
    } else if (text.includes(model)) {
      return (
        <TextCard key={model} name={model} value={model} parameters={parameters} />
      );
    } else {
      return null;
    }
  };

  return (
    <div className="h-screen flex flex-col bg-white text-white">
      {/* Header */}
      <div className="bg-blue-600 p-2 flex justify-between items-center text-white">
        <div>Analyze-it</div>
      </div>

      <div className="flex flex-1">
        {/* Sidebar */}
        <Input
          selectedModels={selectedModels}
          setSelectedModels={setSelectedModels}
          parameters={parameters}
          setParameters={setParameters}
        />

        {/* Main Content */}
        <div className="flex flex-wrap p-4 overflow-y-auto">
          {selectedModels.map((model) => (
            renderModelComponent(model)
          ))}
        </div>
      </div>

      <GraphCard labels={labels} dataPoints={values} label="Nouveaux cas" />
    </div>
  );
};

export default AnalyzeIt;
