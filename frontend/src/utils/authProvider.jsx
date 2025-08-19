import { createContext, useState, useEffect, useCallback, useRef } from "react";
import authApi from "./authApi";

const AuthContext = createContext({});

export const AuthProvider = ({ children }) => {
    const [isAuthenticated, setAuthenticated] = useState(() => {
        return localStorage.getItem('access_token') !== null;
    });
    const [refreshAuth, setRefreshAuth] = useState(false);
    const [authToken, setToken] = useState(localStorage.getItem('access_token'));
    const [username, setGlobalUsername] = useState('');
    const [email, setGlobalEmail] = useState('');
    
    // Add ref to track if auth check is in progress
    const authCheckInProgress = useRef(false);

    useEffect(() => {
        // Prevent multiple simultaneous auth checks
        if (authCheckInProgress.current) return;
        
        authCheckInProgress.current = true;
        
        authApi.get("/api/v1/auth/login")
        .then((response) => {
            const isAuth = response.status === 200;
            console.log("Auth check response:", response);
            setAuthenticated(isAuth);
            setToken(localStorage.getItem('access_token'));
            setGlobalUsername(response.data.username || '');
            setGlobalEmail(response.data.email || '');
        })
        .catch(() => {
            setAuthenticated(false);
        })
        .finally(() => {
            authCheckInProgress.current = false;
        });
    }, [refreshAuth]);

    const triggerAuthCheck = useCallback(() => {
        setRefreshAuth(prev => !prev);
    }, []);

    return (
        <AuthContext.Provider value={{ isAuthenticated, setAuthenticated, triggerAuthCheck, authToken, username, email, setGlobalUsername, setGlobalEmail }}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthContext;