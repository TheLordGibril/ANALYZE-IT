const graphqlUrl = window.__ENV__.VITE_API_URL;

const authService = {
    login: async (email, password) => {

        const response = await fetch(graphqlUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: `
                mutation Login($email: String!, $password: String!) {
                    login(email: $email, password: $password) {
                        token
                        user {
                            id_user
                            email
                            nom
                            prenom
                            role
                            created_at
                        }
                    }
                }
                `,
                variables: { email, password }
            }),
        });

        const data = await response.json();

        if (data.errors) {
            throw new Error(data.errors[0].message);
        }

        return data.data.login;
    },

    register: async (email, password, nom, prenom = '') => {
        const response = await fetch(graphqlUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: `
                mutation Register($email: String!, $password: String!, $nom: String, $prenom: String) {
                    register(email: $email, password: $password, nom: $nom, prenom: $prenom) {
                        token
                        user {
                            id_user
                            email
                            nom
                            prenom
                            role
                            created_at
                        }
                    }
                }
                `,
                variables: { email, password, nom, prenom }
            }),
        });

        const data = await response.json();

        if (data.errors) {
            throw new Error(data.errors[0].message);
        }

        return data.data.register;
    },

    logout: () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    },

    getCurrentUser: () => {
        const token = localStorage.getItem('token');
        const user = localStorage.getItem('user');

        if (token && user) {
            return { token, user: JSON.parse(user) };
        }

        return null;
    },

    saveAuth: (token, user) => {
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));
    }
};

export default authService;