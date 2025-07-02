import React, { useState } from "react";
import Input from "../components/Input";

const models = [
    "total_cases",
    "total_deaths",
    "new_cases",
    "new_deaths",
    "transmission_rate",
    "mortality_rate",
    "geographic_spread",
    "peak_date",
    "estimated_duration_days",
    "cases_in_period",
    "deaths_in_period",
];

const DisplayCard = ({ title, value }) => (
    <Card className="w-40 h-24 flex flex-col justify-center items-center">
        <div className="text-sm text-gray-500">{title}</div>
        <div className="text-xl font-bold">{value}</div>
    </Card>
);

const AnalyzeIt = () => {
    const [selectedModels, setSelectedModels] = useState([]);

    const toggleModel = (model) => {
        setSelectedModels((prev) =>
            prev.includes(model) ? prev.filter((m) => m !== model) : [...prev, model]
        );
    };

    return (
        <div className="h-screen flex flex-col bg-black text-white">
            {/* Header */}
            <div className="bg-blue-600 p-2 flex justify-between items-center text-white">
                <div>Analyze-it</div>
                <div>username</div>
            </div>

            <div className="flex flex-1">
                {/* Sidebar */}
                <Input />

                {/* Main Content */}
                <div className="flex-1 bg-white p-6 text-black grid grid-cols-3 gap-4">
                    {selectedModels.includes("total_cases") && (
                        <DisplayCard title="Cas totaux" value="28.3k" />
                    )}
                    {selectedModels.includes("total_deaths") && (
                        <DisplayCard title="Mort totales" value="7.8k" />
                    )}
                    {selectedModels.includes("new_cases") && (
                        <DisplayCard title="Nouveaux cas" value="2.3k" />
                    )}
                    {selectedModels.includes("transmission_rate") && (
                        <Card className="col-span-2">
                            <CardContent>
                                <div className="text-sm mb-2">Taux de transmission</div>
                                <div className="h-24 bg-gray-200">[Graph Placeholder]</div>
                            </CardContent>
                        </Card>
                    )}
                    {selectedModels.includes("geographic_spread") && (
                        <DisplayCard title="Répartition géo" value="France\nItalie" />
                    )}
                    {selectedModels.includes("estimated_duration_days") && (
                        <DisplayCard title="Durée estimée" value="47d" />
                    )}
                    {selectedModels.includes("deaths_in_period") && (
                        <DisplayCard title="Mort sur la période" value="6.6k" />
                    )}
                    {/* Add other cards here as needed */}
                </div>
            </div>
        </div>
    );
};

export default AnalyzeIt;
