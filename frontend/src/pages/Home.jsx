import { useState } from "react";
import Input from "../components/Input";
import GraphCard from "../components/GraphCard";
import NumberCard from "../components/NumberCard";
import TextCard from "../components/TextCard";
import usePrediction from '../services/usePrediction';

const AnalyzeIt = () => {
    const [selectedModels, setSelectedModels] = useState([]);
    const [parameters, setParameters] = useState({
        country: "France",
        virus: "Covid",
        date_start: "2019-09-01",
        date_end: "2021-03-01"
    });

    const numbers = ["total_cases", "total_deaths", "cases_in_30d", "deaths_in_30d", "new_countries_next_week", "estimated_duration_days"];
    const graphs = ["transmission_rate", "mortality_rate", "new_cases", "new_deaths", "geographic_spread"];
    const text = ["peak_date"];

    const { prediction, loading, error } = usePrediction({
        country: parameters.country,
        virus: parameters.virus,
        dateStart: parameters.date_start,
        dateEnd: parameters.date_end
    });

    const officialData = prediction?.official ?? {};
    const predictionData = prediction?.predictions ?? {};
    const fieldTitles = prediction?.field_titles ?? {};

    const renderModelComponent = (model) => {
        if (numbers.includes(model)) {
            const value = officialData[model];
            return <NumberCard key={model} name={model} value={value} parameters={parameters} />;
        } else if (graphs.includes(model)) {
            const officialObj = officialData[model] ?? {};
            const predictionObj = predictionData[model] ?? {};

            const allDates = Array.from(new Set([...Object.keys(officialObj), ...Object.keys(predictionObj)])).sort();

            const officialPoints = allDates.map(date => officialObj[date] ?? null);
            const predictionPoints = allDates.map(date => predictionObj[date] ?? null);

            return (
                <GraphCard
                    key={model}
                    labels={allDates}
                    title={fieldTitles[model] || model}
                    datasets={[{ label: "Données officielles", data: officialPoints, color: "#3b82f6", dashed: false },
                    { label: "Prédictions", data: predictionPoints, color: "#f59e0b", dashed: true }]} />
            );
        } else if (text.includes(model)) {
            const value = officialData[model];
            return <TextCard key={model} name={model} value={value} parameters={parameters} />;
        } else {
            return null;
        }
    };

    return (
        <div className="h-screen flex flex-col bg-white text-white">
            <div className="bg-blue-600 p-2 flex justify-between items-center text-white">
                <div>Analyze-it</div>
            </div>
            <div className="flex flex-1">
                <Input selectedModels={selectedModels} setSelectedModels={setSelectedModels} parameters={parameters} setParameters={setParameters} />
                <div className="flex flex-wrap p-4 overflow-y-auto w-full">
                    {loading ? (
                        <div className="flex justify-center items-center w-full h-96 text-blue-600 text-xl font-bold animate-pulse">
                            Chargement...
                        </div>
                    ) : (
                        selectedModels.map((model) => renderModelComponent(model))
                    )}
                </div>
            </div>
        </div>
    );
};

export default AnalyzeIt;
