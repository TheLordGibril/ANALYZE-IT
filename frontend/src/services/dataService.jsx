const graphqlUrl = import.meta.env.VITE_API_URL || 'http://localhost:4000/graphql';

const dataService = {
    getAllPays: async (token) => {
        const response = await fetch(graphqlUrl, {
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
    },

    getAllVirus: async (token) => {
        const response = await fetch(graphqlUrl, {
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
    }
};

export default dataService;