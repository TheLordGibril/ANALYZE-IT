import './App.css'
import AnalyzeIt from './pages/Home'
import Login from './pages/Login';
import Register from './pages/Register';
import {AuthProvider, useAuth} from "./context/AuthContext.jsx";
import {useState} from "react";

const AuthWrapper = () => {
    const [isLogin, setIsLogin] = useState(true);
    const { isAuthenticated } = useAuth();

    if (isAuthenticated) {
        return <AnalyzeIt />;
    }

    return (
        <>
            {isLogin ? (
                <Login onSwitchToRegister={() => setIsLogin(false)} />
            ) : (
                <Register onSwitchToLogin={() => setIsLogin(true)} />
            )}
        </>
    );
};

function App() {
    return (
        <AuthProvider>
            <AuthWrapper />
        </AuthProvider>
    );
}

export default App;
