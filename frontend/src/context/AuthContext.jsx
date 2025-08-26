import { createContext, useContext, useEffect, useState } from 'react';
import authService from '../services/authService';

const AuthContext = createContext();

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(null);
    const [loading, setLoading] = useState(true);

    const selectedCountry = window.__ENV__.VITE_COUNTRY;
    const isAuthRequired = selectedCountry === "USA";
    const isAuthenticated = isAuthRequired ? !!token : true;

    useEffect(() => {
        if (!isAuthRequired) {
            setLoading(false);
            return;
        }
        const auth = authService.getCurrentUser();
        if (auth) {
            setUser(auth.user);
            setToken(auth.token);
        }
        setLoading(false);
    }, [isAuthRequired]);

    const login = async (email, password) => {
        const data = await authService.login(email, password);
        setUser(data.user);
        setToken(data.token);
        authService.saveAuth(data.token, data.user);
    };

    const register = async (email, password, nom, prenom) => {
        const data = await authService.register(email, password, nom, prenom);
        setUser(data.user);
        setToken(data.token);
        authService.saveAuth(data.token, data.user);
    };

    const logout = () => {
        setUser(null);
        setToken(null);
        authService.logout();
    };

    const value = {
        user,
        token,
        login,
        register,
        logout,
        isAuthenticated,
        isAuthRequired
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Chargement...</p>
                </div>
            </div>
        );
    }

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};