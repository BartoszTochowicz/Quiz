
import { useState, useEffect, useContext} from "react";
import socketService from "../utils/socketService";
import { useNavigate, useParams } from "react-router-dom";
import AuthContext from "../utils/authProvider";
import {toast} from 'react-toastify';


function Lobby() {
    const [players, setPlayers] = useState([]);
    const {lobbyId} = useParams();
    const {username} = useContext(AuthContext);
    const [hostUsername, setHostUsername] = useState("");
    const [maxPlayers, setMaxPlayers] = useState(0);
    const [currentPlayers, setCurrentPlayers] = useState(0);
    const {isAuthenticated, authToken, triggerAuthCheck} = useContext(AuthContext);
    const [lobbyName, setLobbyName] = useState("");
    const navigator = useNavigate();
    useEffect(() => {
        
        if(!socketService.getConnectionStatus()){
            console.log('Socket not connected')
        }

        socketService.updateCallbacks({
            onLobbyUpdated: (data) => {
                console.log(`update lobby ${data}`);
                if (!data || !data.players) {
                    console.warn("Invalid lobby update payload:", data);
                    return;
                }
                setPlayers(data.players);
                setCurrentPlayers(data.players.length);
                setHostUsername(data.host_username || "");
                setMaxPlayers(data.max_players || 0);
                setLobbyName(data.lobby_name || "");
            },
            onLobbyDeleted: () => {
                setHostUsername("");
                setPlayers([]);
                setMaxPlayers(0);
                setCurrentPlayers(0);
                setLobbyName("");
                toast.info("Lobby has been deleted");
                navigator('/lobby');
            },
            onQuizStarted: (data) => {
                toast.dark("Quiz is starting!");
                localStorage.setItem("categry",data.category);
                // localStorage.setItem("lobby_id",lobbyId);
                navigator(`/quiz/${lobbyId}`);
            },
            onPlayerLeft: (data) => {
                // socketService.emit('get_lobby_details')
                // const deletedUsername = data.username;
                // setPlayers((prev) => prev.filter((player) => player !== deletedUsername));
                // setCurrentPlayers((prev) => prev - 1);
                console.log("Player left");
                // socketService.emit('get_lobby_details',{lobby_id:lobbyId});
            },
            onPlayerJoined: (data) => {
                console.log("Player joined")
                // socketService.emit('get_lobby_details', {lobby_id:lobbyId});
            },
            onLobbyDetails: (data) => {
                setHostUsername(data.host_username);
                setPlayers(data.players);
                setMaxPlayers(data.max_players);
                setCurrentPlayers(data.current_players);
                setLobbyName(data.lobby_name);
                console.log(`Lobby details updated: ${data}`);
            },
            onError: (data) => {
                console.log(`Error occuerrd: ${data.message}`);
                toast.error(`❌ ${data.message}`);
            }
        });

        return () => {
            // socketService.emit('leave_lobby', { lobby_id: lobbyId, username: username });
        };
    },[lobbyId]);

    useEffect(() => {
        if (socketService.getSocket() !== null || (socketService.getConnectionStatus() && lobbyId)){
            socketService.emit('get_lobby_details',{lobby_id: lobbyId});
        }
    },[lobbyId]);

    useEffect(() => {
        if(!socketService.getConnectionStatus()){
            socketService.reconnect(authToken);
            socketService.emit('get_lobby_details',{lobby_id: lobbyId});
        }
        // socketService.reconnect(authToken);
        // socketService.emit('get_lobby_details',{lobby_id: lobbyId});
    }, [authToken]);

    const handleLeaveLobby = () => {
        console.log(username,' is living lobby')
        socketService.emit('leave_lobby', { lobby_id: lobbyId, username: username });
    }

    const handleDeleteLobby = () => {
        socketService.emit('delete_lobby',{lobby_id : lobbyId, username: username});
    }

    const handleStartQuiz = () => {
        socketService.emit('start_quiz', {lobby_id : lobbyId, username: username});
    }
    return (
        <div>
            <h2>Lobby {lobbyName} | Host: {hostUsername}</h2>
            <h2>Players in Lobby:</h2>
            <div>
                <table>
                    <thead>
                        <tr>
                            <th scope="col">Index</th>
                            <th scope="col">Player Name</th>
                        </tr>
                    </thead>
                    <tbody>
                        {players.map((p,index) => (
                            <tr key={index}>
                                <th scope="row">{index+1}</th>
                                <th scope="row">{p}</th>
                            </tr>
                            
                        ))}
                    </tbody>
                </table>
                <button onClick={handleLeaveLobby}>Leave Lobby</button>
                {username===hostUsername && (
                    <div>
                        <button onClick={handleDeleteLobby}>Delete Lobby</button>
                        <button onClick={handleStartQuiz}>Start Quiz</button>
                    </div>
                )}
            </div>
            {/* <ul>
                <li>Host: <b>{hostUsername}</b> {hostUsername===username}</li>
                <li>Players: {currentPlayers} / {maxPlayers}</li>
            </ul>
            <ul>
                {players.map((player,index) => (
                    <li key={index}>{player}</li>
                ))}
            </ul>
                {username === hostUsername && (
                    <div>
                        <button onClick={handleDeleteLobby}>Delete Lobby</button>
                        <button onClick={handleStartQuiz}>Start Quiz</button>
                    </div>
                )}
            <ul>
                <li>
                    <button onClick={handleLeaveLobby}>Leave Lobby </button>
                </li>
            </ul> */}
        </div>
    );
}
export default Lobby;