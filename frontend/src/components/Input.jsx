export default function Input({ selectedModels, setSelectedModels, parameters, setParameters, isMenuOpen, setIsMenuOpen }) {
    const allModels = [
        "total_cases", "total_deaths",
        "peak_date", "estimated_duration_days", "cases_in_30d",
        "deaths_in_30d", "new_countries_next_week", "new_cases", "new_deaths",
        "transmission_rate", "mortality_rate", "geographic_spread"
    ];

    const allVirus = [
        "Covid", "Monkeypox"]

    const allPays = [
        "Afghanistan",
        "Africa Eastern and Southern",
        "Africa Western and Central",
        "Albania",
        "Algeria",
        "Andorra",
        "Angola",
        "Antigua and Barbuda",
        "Argentina",
        "Armenia",
        "Aruba",
        "Australia",
        "Austria",
        "Azerbaijan",
        "Bahamas, The",
        "Bahrain",
        "Bangladesh",
        "Barbados",
        "Belarus",
        "Belgium",
        "Belize",
        "Benin",
        "Bermuda",
        "Bhutan",
        "Bolivia",
        "Bosnia and Herzegovina",
        "Botswana",
        "Brazil",
        "British Virgin Islands",
        "Brunei Darussalam",
        "Bulgaria",
        "Burkina Faso",
        "Burundi",
        "Cabo Verde",
        "Cambodia",
        "Cameroon",
        "Canada",
        "Cayman Islands",
        "Central African Republic",
        "Central Europe and the Baltics",
        "Chad",
        "Channel Islands",
        "Chile",
        "China",
        "Colombia",
        "Comoros",
        "Congo, Dem. Rep.",
        "Costa Rica",
        "Cote d'Ivoire",
        "Croatia",
        "Cuba",
        "Curacao",
        "Cyprus",
        "Czechia",
        "Denmark",
        "Djibouti",
        "Dominica",
        "Dominican Republic",
        "East Asia & Pacific",
        "Ecuador",
        "Egypt, Arab Rep.",
        "El Salvador",
        "Equatorial Guinea",
        "Eritrea",
        "Estonia",
        "Ethiopia",
        "Faroe Islands",
        "Fiji",
        "Finland",
        "Fragile and conflict affected situations",
        "France",
        "French Polynesia",
        "Gabon",
        "Gambia, The",
        "Georgia",
        "Germany",
        "Ghana",
        "Gibraltar",
        "Greece",
        "Greenland",
        "Grenada",
        "Guam",
        "Guatemala",
        "Guinea",
        "Guinea-Bissau",
        "Guyana",
        "Haiti",
        "Honduras",
        "Hong Kong SAR, China",
        "Hungary",
        "Iceland",
        "India",
        "Indonesia",
        "Iran, Islamic Rep.",
        "Iraq",
        "Ireland",
        "Isle of Man",
        "Israel",
        "Italy",
        "Jamaica",
        "Japan",
        "Jordan",
        "Kazakhstan",
        "Kenya",
        "Kiribati",
        "Korea, Dem. People's Rep.",
        "Kuwait",
        "Latvia",
        "Lebanon",
        "Lesotho",
        "Liberia",
        "Libya",
        "Liechtenstein",
        "Lithuania",
        "Luxembourg",
        "Macao SAR, China",
        "Madagascar",
        "Malawi",
        "Malaysia",
        "Maldives",
        "Mali",
        "Malta",
        "Marshall Islands",
        "Mauritania",
        "Mauritius",
        "Mexico",
        "Micronesia, Fed. Sts.",
        "Moldova",
        "Monaco",
        "Mongolia",
        "Montenegro",
        "Morocco",
        "Mozambique",
        "Myanmar",
        "Namibia",
        "Nauru",
        "Nepal",
        "Netherlands",
        "New Caledonia",
        "New Zealand",
        "Nicaragua",
        "Niger",
        "Nigeria",
        "North America",
        "North Macedonia",
        "Northern Mariana Islands",
        "Norway",
        "Oman",
        "Pakistan",
        "Palau",
        "Panama",
        "Papua New Guinea",
        "Paraguay",
        "Peru",
        "Philippines",
        "Poland",
        "Portugal",
        "Puerto Rico",
        "Qatar",
        "Romania",
        "Russian Federation",
        "Rwanda",
        "Samoa",
        "San Marino",
        "Sao Tome and Principe",
        "Saudi Arabia",
        "Senegal",
        "Serbia",
        "Seychelles",
        "Sierra Leone",
        "Singapore",
        "Sint Maarten (Dutch part)",
        "Slovenia",
        "Solomon Islands",
        "Somalia",
        "South Africa",
        "South Sudan",
        "Spain",
        "Sri Lanka",
        "St. Kitts and Nevis",
        "St. Lucia",
        "St. Martin (French part)",
        "St. Vincent and the Grenadines",
        "Sudan",
        "Suriname",
        "Sweden",
        "Switzerland",
        "Syrian Arab Republic",
        "Tajikistan",
        "Tanzania",
        "Thailand",
        "Timor-Leste",
        "Togo",
        "Tonga",
        "Trinidad and Tobago",
        "Tunisia",
        "Turkiye",
        "Turks and Caicos Islands",
        "Uganda",
        "Ukraine",
        "United Arab Emirates",
        "United Kingdom",
        "United States",
        "Uruguay",
        "Uzbekistan",
        "Vanuatu",
        "Venezuela, RB",
        "Vietnam",
        "World",
        "Yemen, Rep.",
        "Zambia",
        "Zimbabwe"]
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

                <div className="flex justify-end lg:hidden mb-4">
                    <button
                        onClick={() => setIsMenuOpen(false)}
                        className="text-gray-600 hover:text-gray-800 text-xl font-bold"
                    >
                        ×
                    </button>
                </div>

                <div>
                    <label className="block text-sm font-medium">Pays</label>
                    <select
                        name="country"
                        className="w-full p-1 rounded"
                        defaultValue={parameters.country}
                        onChange={handleParameterChange}
                    >
                        {allPays.map((pays) => (
                            <option key={pays} value={pays}>
                                {pays}
                            </option>
                        ))}
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium">Virus</label>
                    <select
                        name="virus"
                        className="w-full p-1 rounded"
                        defaultValue={parameters.virus}
                        onChange={handleParameterChange}
                    >
                        {allVirus.map((virus) => (
                            <option key={virus} value={virus}>
                                {virus}
                            </option>
                        ))}
                    </select>
                </div>

                <div className="space-y-1">
                    <label className="block text-sm font-medium">Début</label>
                    <input
                        type="date"
                        name="date_start"
                        defaultValue={parameters.date_start}
                        onChange={handleParameterChange}
                        className="w-full border rounded px-2 py-1"
                    />
                    <label className="block text-sm font-medium">Fin</label>
                    <input
                        type="date"
                        name="date_end"
                        defaultValue={parameters.date_end}
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
                                <span className="text-sm">{model}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </>
    );
}