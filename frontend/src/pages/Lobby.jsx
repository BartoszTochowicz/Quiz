
import { useState, useEffect, useContext} from "react";
import socketService from "../utils/socketService";
import { useNavigate, useParams } from "react-router-dom";
import AuthContext from "../utils/authProvider";

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
            onLobbyDetails: (response) => {
                setHostUsername(response.host_username);
                setPlayers(response.players);
                setMaxPlayers(response.max_players);
                setCurrentPlayers(response.current_players);
                setLobbyName(response.lobby_name);
                console.log("Lobby details updated:", response);
            }
        });

        socketService.updateCallbacks({
            onLobbyUpdated: (updatedPlayers) => {
                setPlayers(updatedPlayers);
                setCurrentPlayers(players.length)
            },
            onLobbyDeleted: () => {
                setHostUsername(NaN);
                setPlayers(NaN);
                setMaxPlayers(NaN);
                setCurrentPlayers(NaN);
                setLobbyName(NaN);
                alert("Lobby has been deleted");
                navigator('/lobby');
            },
            onQuizStarted: () => {
                alert("Quiz is starting!");
                navigator(`/quiz/${lobbyId}`);
            },
            onPlayerLeft: (data) => {
                const deletedUsername = data.username;
                setPlayers((prev) => prev.filter((player) => player !== deletedUsername));
                console.log("Lobby deleted",data);
                navigator('/lobby');
            }
        });

        return () => {
            socketService.emit('leave_lobby', { lobby_id: lobbyId });
        };
    },[lobbyId]);

    useEffect(() => {
        socketService.emit('get_lobby_details',{lobby_id: lobbyId});
    },[])

    const handleLeaveLobby = () => {
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
                        {players.map((p,index) => {
                            <tr key={index}>
                                <th scope="row">{index+1}</th>
                                <th scope="row">{p}</th>
                            </tr>
                            
                        })}
                    </tbody>
                </table>
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