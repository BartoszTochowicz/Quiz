import { useContext } from "react";
import Logout from "../components/Logout";
import AuthContext from "../utils/authProvider";

function Account(){
    const {username,email} = useContext(AuthContext)
    return (
        <div>
            <div>
                <h1>Welcome {username}!</h1>
                <p>Email:{email}</p>
            </div>
            <div>
                <Logout/>
            </div>
        </div>
    );
}
export default Account;