import React, { useContext, useEffect, useState } from "react";
import { data, useNavigate } from "react-router-dom";
import axios from "axios";
import LobbyForm from "../components/LobbyForm";
import socketService from "../utils/socketService";
import AuthContext from "../utils/authProvider";

function LobbyCreator() {
    const [lobbyData, setLobbyData] = useState(null);
    const {isAuthenticated,authToken,triggerAuthCheck} = useContext(AuthContext)
    const navigation = useNavigate();

    useEffect(() => {
        if(!socketService || !socketService.getConnectionStatus()){
            console.error("Socket service is not connected");
            return;
        }
        socketService.updateCallbacks({
            onLobbyCreated:(data) => {
                console.log('Lobby created: ',data);
                // Backend: {message: ... , data:{lobby_id: ...}}
                navigation(`/lobby/${data.data.lobby_id}`)
            }
        })
    });
    // useEffect(() => {
    //     if(!socketService.getConnectionStatus()){
    //         socketService.reconnect(authToken);
    //     }
    // }, [authToken]);

    const handleFormSubmit = async (params) =>{
        console.log(params);
        if (!socketService.getConnectionStatus()){
            console.error("Socket is not connected. Cannot create lobby.")
            return;
        }
        socketService.emit('create_lobby',params)
            .catch((error) => {
                console.error("Error createing lobby: ",error,". Please try again");
                alert("Failed to create lobby. Please try again")
            });
        // console.error("Error creating lobby:", error);
    }
    return(
        <div>
            <LobbyForm onSubmit={handleFormSubmit}/>
        </div>
    )
}
export default LobbyCreator;