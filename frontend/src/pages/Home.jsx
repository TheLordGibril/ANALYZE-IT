import { useState } from "react";
import Input from "../components/Input";
import GraphCard from "../components/GraphCard";
import NumberCard from "../components/NumberCard";
import TextCard from "../components/TextCard";
import usePrediction from '../services/usePrediction';

const AnalyzeIt = () => {
    const [selectedModels, setSelectedModels] = useState([]);
    const [isMenuOpen, setIsMenuOpen] = useState(false);
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
        if (numbers.includes(model) || text.includes(model)) {
            const value = officialData[model];
            return <NumberCard key={model} name={fieldTitles[model] || model} value={value} parameters={parameters} />;
        } else if (graphs.includes(model)) {
            const officialObj = officialData[model] ?? {};
            const predictionObj = predictionData[model] ?? {};
            const allDates = Array.from(new Set([...Object.keys(officialObj), ...Object.keys(predictionObj)])).sort();
            const officialPoints = allDates.map(date => officialObj[date] ?? null);
            const predictionPoints = allDates.map(date => predictionObj[date] ?? null);
            return (
                <GraphCard
                    key={model}
                    id={model}
                    labels={allDates}
                    title={fieldTitles[model] || model}
                    datasets={[
                        { label: "Données officielles", data: officialPoints, color: "#3b82f6", dashed: false },
                        { label: "Prédictions", data: predictionPoints, color: "#f59e0b", dashed: true }
                    ]}
                />
            );
        } else {
            return null;
        }
    };

    return (
        <div className="h-screen flex flex-col bg-white text-white">

            <div className="bg-blue-600 p-2 flex justify-between items-center text-white">
                <div className="flex items-center space-x-3">

                    <button
                        onClick={() => setIsMenuOpen(!isMenuOpen)}
                        className="lg:hidden text-white hover:text-gray-300 focus:outline-none"
                    >
                        <svg
                            className="w-6 h-6"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2"
                                d="M4 6h16M4 12h16M4 18h16"
                            />
                        </svg>
                    </button>
                    <div>Analyze-it</div>
                </div>
            </div>


            <div className="flex flex-1 relative">

                <Input
                    selectedModels={selectedModels}
                    setSelectedModels={setSelectedModels}
                    parameters={parameters}
                    setParameters={setParameters}
                    isMenuOpen={isMenuOpen}
                    setIsMenuOpen={setIsMenuOpen}
                    fieldTitles={fieldTitles}
                />


                <div className="flex-1 flex flex-wrap p-4 overflow-y-auto lg:ml-0">
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