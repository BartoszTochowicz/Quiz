import React, { useEffect, useState } from "react";
import { data, useNavigate } from "react-router-dom";
import axios from "axios";
import LobbyForm from "../components/LobbyForm";
import socketService from "../utils/socketService";

function LobbyCreator() {
    const [lobbyData, setLobbyData] = useState(null);
    const navigation = useNavigate();

    useEffect(() => {
        if(!socketService || !socketService.getConnectionStatus()){
            console.error("Socket service is not connected");
            return;
        }
        socketService.updateCallbacks({
            onLobbyCreated:(data) => {
                console.log('Lobby created: ',data);
                navigation(`/lobby/${data['lobby_id']}`)
            }
        })
    })

    const handleFormSubmit = async (params) =>{
        // try{
        //     axios.post("http://localhost:5000/api/v1/multiplayer/lobby/create",params,{
        //         headers:{
        //             "Content-Type": "application/json",
        //             "Authorization" : `Bearer ${localStorage.getItem("access_token")}`  
        //         }
        //     }).then(res => {
        //         setLobbyData(res.data.data);
        //         socketService.emit('lobby_details',{lobby_id:lobbyData});
        //         console.log("Lobby created successfully:");
        //         console.log(res.data.data);
        //         navigation(`/lobby/${res.data.data.lobby_id}`)
        //     })
        // }
        // catch(error){
        //     console.error("Error creating lobby:", error);
        // }
        console.log(params);
        if (!socketService.getConnectionStatus()){
            console.error("Socket is not connected. Cannot create lobby.")
            return;
        }
        socketService.emit('create_lobby',params,(response) => {
            // console.log("Lobby created successfully:", response);
            // setLobbyData(response);
            // navigation(`/lobby/${response.lobby_id}`); // Navigate to the new lobby
        }).catch((error) => {
            console.error("Error createing lobby: ",error,". Please try again");
            alert("Failed to create lobby. Please try again")
        })
        // console.error("Error creating lobby:", error);
    }
    return(
        <div>
            <LobbyForm onSubmit={handleFormSubmit}/>
        </div>
    )
}
export default LobbyCreator;