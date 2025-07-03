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

    const renderModelComponent = (model) => {
        if (numbers.includes(model)) {
            return <NumberCard key={model} name={model} value={model} parameters={parameters} />;
        } else if (graphs.includes(model)) {
            const dataObj = prediction?.predictions?.[model] ?? {};
            const labels = Object.keys(dataObj);
            const dataPoints = Object.values(dataObj);
            return (
                <GraphCard key={model} labels={labels} dataPoints={dataPoints} label={model} />
            );
        } else if (text.includes(model)) {
            return <TextCard key={model} name={model} value={model} parameters={parameters} />;
        } else {
            return null;
        }
    };

    return (
        <div className="h-screen flex flex-col bg-white text-white">
            <div className="bg-blue-600 p-2 flex justify-between items-center text-white">
                <div>Analyze-it</div>
            </div>

            {loading ? (
                <div className="flex justify-center items-center flex-grow text-black">
                    Chargement...
                </div>
            ) : (
                <div className="flex flex-1">
                    <Input selectedModels={selectedModels} setSelectedModels={setSelectedModels} parameters={parameters} nsetParameters={setParameters} />
                    <div className="flex flex-wrap p-4 overflow-y-auto">
                        {selectedModels.map((model) => renderModelComponent(model))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default AnalyzeIt;
