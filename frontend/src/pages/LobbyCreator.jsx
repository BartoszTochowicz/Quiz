import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import LobbyForm from "../components/LobbyForm";

function LobbyCreator() {
    const [lobbyData, setLobbyData] = useState(null);
    const navigation = useNavigate();
    const handleFormSubmit = async (params) =>{
        try{
            axios.post("http://localhost:5000/api/v1/multiplayer/lobby/create",params,{
                headers:{
                    "Content-Type": "application/json",
                    "Authorization" : `Bearer ${localStorage.getItem("access_token")}`  
                }
            }).then(res => {
                setLobbyData(res.data.data);
                console.log(res.data.data);
                navigation(`/lobby/${res.data.data.lobby_id}`)
            })
        }
        catch(error){
            console.error("Error creating lobby:", error);
        }
    }
    return(
        <div>
            <LobbyForm onSubmit={handleFormSubmit}/>
        </div>
    )
}
export default LobbyCreator;