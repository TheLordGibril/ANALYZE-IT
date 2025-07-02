import React, { useState } from "react";
import Input from "../components/Input";
import GraphCard from "../components/GraphCard";
import NumberCard from "../components/TextCard";
import TextCard from "../components/TextCard";

const AnalyzeIt = () => {
    const [selectedModels, setSelectedModels] = useState([]);

    const numbers = ["total_cases", "total_deaths", "new_cases", "new_deaths", "case_in_30d", "deaths_in_30d", "new_countries_next_week"];
    const graphs = ["transmission_rate", "mortality_rate"];
    const text = ["geographic_spread", "peak_date", "estimated_duration_days"];

    const renderModelComponent = (model) => {
        if (numbers.includes(model)) {
            return (
                <NumberCard key={model} name={model} />
            );
        } else if (graphs.includes(model)) {
            return (
                <GraphCard key={model} name={model} />
            );
        } else if (text.includes(model)) {
            return (
                <TextCard key={model} name={model} />
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
                />

                {/* Main Content */}
                <div className="flex flex-wrap p-4 overflow-y-auto">
                    {selectedModels.map((model) => renderModelComponent(model))}
                </div>
            </div>
        </div>
    );
};

export default AnalyzeIt;
