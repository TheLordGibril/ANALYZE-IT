import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import dataService from '../services/dataService';

export default function Input({ selectedModels, setSelectedModels, parameters, setParameters, isMenuOpen, setIsMenuOpen, fieldTitles }) {
    const { logout, user, token } = useAuth();
    const [pays, setPays] = useState([]);
    const [virus, setVirus] = useState([]);
    const [loadingData, setLoadingData] = useState(true);

    // Créer un nom d'affichage à partir de nom et prénom
    const displayName = user ? `${user.prenom || ''} ${user.nom || ''}`.trim() || user.email : '';

    const allModels = [
        "total_cases", "total_deaths",
        "peak_date", "estimated_duration_days", "cases_in_30d",
        "deaths_in_30d", "new_countries_next_week", "new_cases", "new_deaths",
        "transmission_rate", "mortality_rate", "geographic_spread"
    ];

    // Charger les données au montage du composant
    useEffect(() => {
        const loadData = async () => {
            if (!token) return;

            try {
                setLoadingData(true);
                const [paysData, virusData] = await Promise.all([
                    dataService.getAllPays(token),
                    dataService.getAllVirus(token)
                ]);

                setPays(paysData);
                setVirus(virusData);

                // Si aucun pays n'est sélectionné, prendre le premier
                if (!parameters.country && paysData.length > 0) {
                    setParameters(prev => ({
                        ...prev,
                        country: paysData[0].nom_pays
                    }));
                }

                // Si aucun virus n'est sélectionné, prendre le premier
                if (!parameters.virus && virusData.length > 0) {
                    setParameters(prev => ({
                        ...prev,
                        virus: virusData[0].nom_virus
                    }));
                }
            } catch (error) {
                console.error('Erreur lors du chargement des données:', error);
            } finally {
                setLoadingData(false);
            }
        };

        loadData();
    }, [token, parameters.country, parameters.virus, setParameters]);

    const handleSetSelectedModels = (model) => {
        setSelectedModels((prev) =>
            prev.includes(model)
                ? prev.filter((m) => m !== model)
                : [...prev, model]
        );
    };

    const handleParameterChange = (e) => {
        const { name, value } = e.target;
        setParameters((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    return (
        <>
            {isMenuOpen && (
                <div
                    className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
                    onClick={() => setIsMenuOpen(false)}
                />
            )}

            <div className={`
                fixed lg:relative top-0 left-0 h-full w-64 bg-gray-100 text-black p-4 space-y-4 z-50
                transform transition-transform duration-300 ease-in-out
                ${isMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
            `}>
                <div className="flex justify-between items-center lg:hidden mb-4">
                    <span className="text-sm font-medium">Bonjour {displayName}</span>
                    <button
                        onClick={() => setIsMenuOpen(false)}
                        className="text-gray-600 hover:text-gray-800 text-xl font-bold"
                    >
                        ×
                    </button>
                </div>

                <div className="hidden lg:block mb-4">
                    <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Bonjour {displayName}</span>
                        <button
                            onClick={logout}
                            className="text-xs text-red-600 hover:text-red-800"
                        >
                            Déconnexion
                        </button>
                    </div>
                </div>

                {loadingData ? (
                    <div className="flex justify-center items-center py-8">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                        <span className="ml-2 text-sm text-gray-600">Chargement...</span>
                    </div>
                ) : (
                    <>
                        <div>
                            <label className="block text-sm font-medium">Pays</label>
                            <select
                                name="country"
                                className="w-full p-1 rounded"
                                value={parameters.country}
                                onChange={handleParameterChange}
                            >
                                {pays.map((paysItem) => (
                                    <option key={paysItem.id_pays} value={paysItem.nom_pays}>
                                        {paysItem.nom_pays}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium">Virus</label>
                            <select
                                name="virus"
                                className="w-full p-1 rounded"
                                value={parameters.virus}
                                onChange={handleParameterChange}
                            >
                                {virus.map((virusItem) => (
                                    <option key={virusItem.id_virus} value={virusItem.nom_virus}>
                                        {virusItem.nom_virus}
                                    </option>
                                ))}
                            </select>
                        </div>
                    </>
                )}

                <div className="space-y-1">
                    <label className="block text-sm font-medium">Début</label>
                    <input
                        type="date"
                        name="date_start"
                        value={parameters.date_start}
                        onChange={handleParameterChange}
                        className="w-full border rounded px-2 py-1"
                    />
                    <label className="block text-sm font-medium">Fin</label>
                    <input
                        type="date"
                        name="date_end"
                        value={parameters.date_end}
                        onChange={handleParameterChange}
                        className="w-full border rounded px-2 py-1"
                    />
                </div>

                <div>
                    <h4 className="text-sm font-semibold mt-4 mb-2">Models</h4>

                    <div className="flex items-center space-x-2 mb-2">
                        <input
                            type="checkbox"
                            checked={selectedModels.length === allModels.length}
                            onChange={(e) => {
                                if (e.target.checked) {
                                    setSelectedModels(allModels);
                                } else {
                                    setSelectedModels([]);
                                }
                            }}
                        />
                        <span className="text-sm font-medium">Tout sélectionner</span>
                    </div>

                    <div className="space-y-1 max-h-72 overflow-y-auto pr-1">
                        {allModels.map((model) => (
                            <div key={model} className="flex items-center space-x-2">
                                <input
                                    type="checkbox"
                                    checked={selectedModels.includes(model)}
                                    onChange={() => handleSetSelectedModels(model)}
                                />
                                <span className="text-sm">{fieldTitles?.[model] || model}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </>
    );
}