const apiUrl = window.__ENV__.VITE_API_URL;

const dataService = {
    getAllPays: async (token) => {
        if (window.__ENV__.VITE_COUNTRY === "USA") {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': token ? `Bearer ${token}` : '',
                },
                body: JSON.stringify({
                    query: `
                    query GetAllPays {
                        allPays {
                            id_pays
                            nom_pays
                        }
                    }
                    `,
                }),
            });

            const data = await response.json();

            if (data.errors) {
                throw new Error(data.errors[0].message);
            }

            return data.data.allPays;
        } else {
            const response = await fetch(`${apiUrl}/countries`, {
                method: 'GET',
            });

            const data = await response.json();
            return data.countries.map(nom_pays => ({ nom_pays }));
        }
    },

    getAllVirus: async (token) => {
        if (window.__ENV__.VITE_COUNTRY === "USA") {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': token ? `Bearer ${token}` : '',
                },
                body: JSON.stringify({
                    query: `
                    query GetAllVirus {
                        allVirus {
                            id_virus
                            nom_virus
                        }
                    }
                    `,
                }),
            });

            const data = await response.json();

            if (data.errors) {
                throw new Error(data.errors[0].message);
            }

            return data.data.allVirus;
        } else {
            const response = await fetch(`${apiUrl}/viruses`, {
                method: 'GET',
            });

            const data = await response.json();
            return data.viruses.map(nom_virus => ({ nom_virus }));
        }
    }
};

export default dataService;