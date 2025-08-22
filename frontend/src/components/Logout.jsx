import { useContext } from "react"
import AuthContext from "../utils/authProvider"
import Cookies from "js-cookie"
import { useNavigate } from "react-router-dom"
import authApi from "../utils/authApi";
import axios from "axios";

const Logout = () => {
    const {setAuthenticated} = useContext(AuthContext);
    const navigate = useNavigate();

    async function logoutUser(event){
        event.preventDefault();
        const csrfToken = Cookies.get('csrf_refresh_token');

        await authApi.delete("/api/v1/auth/logout/access")
        .then(response => {
            console.log(response.data);
            console.log("logged out access token");
        }).catch(error => {
            console.log("There was an error logging out!", error);
            alert("An error occurred! Please try again later.")
        });
        localStorage.removeItem("access_token");
        await axios.delete("http://localhost:5000/api/v1/auth/logout/refresh",{
            headers:{
                'X-CSRF-Token':csrfToken,
            },
            withCredentials : true
        }).then(response => {
            console.log(response.data);
            console.log("logged out refresh token");
        }).catch(error =>{
            console.log("There was an error logging out!",error)
            alert("An error occurred! Please try again later.");
        }).finally(() =>{
            setAuthenticated(false);
        })
        navigate('/');
    }
    return <button onClick={logoutUser}>Logout</button>
}
export default Logout;