export default function Input({ selectedModels, setSelectedModels }) {
    const allModels = ["total_cases", "total_deaths", "new_cases", "new_deaths", "transmission_rate", "mortality_rate", "geographic_spread", "peak_date", "estimated_duration_days", "cases_in_30d", "deaths_in_30d", "new_countries_next_week"]

    const handleSetSelectedModels = (model) => {
        setSelectedModels((prev) =>
            prev.includes(model) ? prev.filter((m) => m !== model) : [...prev, model]
        )
    }
    // const api_url = http://127.0.0.1:8000/predict?country=France&virus=covid&date_start=2025-03-01&date_end=2025-07-01
    return (
        <div>
            <div className="w-64 bg-gray-100 text-black p-4 space-y-4">
                <div>
                    <label className="block text-sm font-medium">Pays</label>
                    <input defaultValue="France" />
                </div>
                <div>
                    <label className="block text-sm font-medium">Virus</label>
                    <input defaultValue="Covid" />
                </div>
                <div className="space-y-1">
                    <label className="block text-sm font-medium">Début</label>
                    <input type="date" defaultValue="2019-09-01" />
                    <label className="block text-sm font-medium">Fin</label>
                    <input type="date" defaultValue="2021-03-01" />
                </div>

                <div>
                    <h4 className="text-sm font-semibold mt-4 mb-2">Models</h4>
                    <div className="space-y-1">
                        {allModels.map((model) => (
                            <div key={model} className="flex items-center space-x-2">
                                <input
                                    type="checkbox"
                                    checked={selectedModels.includes(model)}
                                    onChange={() => handleSetSelectedModels(model)}
                                />
                                <span className="text-sm">{model}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    )
}