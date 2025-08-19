import axios from "axios";
import { useNavigate, useLocation } from "react-router-dom";
import React, { useState,useContext } from "react";
import AuthContext from "../utils/authProvider";

function Login(){
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [email, setEmail] = useState("");
    const [isRegisterMode, setIsRegisterMode] = useState(false);
    const {setAuthenticated, setGlobalEmail, setGlobalUsername} = useContext(AuthContext);
    const navigate = useNavigate();
    const location = useLocation();
    const from = location.state?.from?.pathname || "/account";

    function loginUser(event){
        event.preventDefault();
        const logindData = {
            username: username,
            password:password
        };
        axios.post("http://localhost:5000/api/v1/auth/login", logindData, {
            headers: {
                'Content-Type': 'application/json',
            },
            withCredentials: true
        })
        .then((response)=>{
            console.log(response);
            console.log(response.data); // Log the response to see its structure
            if(response.status == 200){
                const newAccessToken = response.data.access_token;
                localStorage.setItem('access_token',newAccessToken);
                setAuthenticated(true); // Set the authenticated state to true
                setGlobalUsername(response.data.data.username || ''); // Set username from response
                setGlobalEmail(response.data.data.email || ''); // Set email from response
                navigate(from, {replace: true}); // Redirect to intended page
            } else{
                alert("Login failed. Please check your credentials.");
            }
        })
        .catch(error => {
            console.error("There was an error logging in!", error);
            alert("An error occurred. Please try again later.");
        })
    }
    function registerUser(event){
        event.preventDefault();
        const registerData = {
            username:username,
            password:password,
            email:email
        };
        axios.post("http://localhost:5000/api/v1/auth/register", registerData,{
            headers:{
                'Content-Type':'application/json'
            },
            withCredentials: true
        })
        .then((response) =>{
            console.log(response)
            console.log(response.data);
            if(response.status==200 || response.status== 201){
                alert("Registration successful! Please login with your credentials.");
                setIsRegisterMode(false); // Switch back to login mode
                // Clear form fields
                setUsername("");
                setPassword("");
                setEmail("");
            }else{
                alert("Registration failed. Please try again.");
            }
        })
        .catch(error =>{
            console.error("There was an error registering!", error);
            alert("An error occurred during registration. Please try again later.");
        });
    }
    return(
        <div>
            <h1>
                {isRegisterMode ? "Register for Quiz App":"Login to Quiz App"}
            </h1>
            <form onSubmit={isRegisterMode ? registerUser:loginUser}>
                <div>
                    <label>Username</label>
                    <input
                        type="text"
                        id="username"
                        required
                        value={username}
                        onChange={(event) => setUsername(event.target.value)}
                        className=""
                        placeholder="Enter your username"
                    />
                </div>
                {isRegisterMode && (
                    <div>
                        <label htmlFor="email">Email</label>
                        <input
                            type="email"
                            id="email"
                            required
                            value={email}
                            onChange={(event) => setEmail(event.target.value)}
                            placeholder="Enter your email"
                        />
                    </div>
                )}
                <div>
                    <label htmlFor="passwor">Password</label>
                    <input 
                        type="password" 
                        id="password" 
                        required
                        value={password}
                        onChange={(event) => setPassword(event.target.value)}
                        placeholder="Enter your password"
                    />
                </div>
                <button 
                    type="submit">
                    {isRegisterMode ? "Register":"Login"}
                </button>
            </form>
            <button 
                onClick={()=> {
                    setIsRegisterMode(!isRegisterMode)
                    setUsername("")
                    setEmail("")
                    setPassword("") 
                }}>
                {isRegisterMode ? "Switch to Login":"Switch to Register"}
            </button>
        </div>
    )
};
export default Login;