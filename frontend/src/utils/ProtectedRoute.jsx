import React, { useContext, useEffect } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import AuthContext from "./authProvider";

const ProtectedRoute = ({ children }) => {
    const { isAuthenticated, triggerAuthCheck } = useContext(AuthContext);
	const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        triggerAuthCheck();
    }, [triggerAuthCheck, location.pathname]);

	// Redirect if not authenticated
	useEffect(() => {
		if (isAuthenticated === false) {
			navigate("/login");
		}
	}, [isAuthenticated, navigate]);

	if (isAuthenticated === false) return null; // Or a loading spinner

    return children;
};

export default ProtectedRoute;