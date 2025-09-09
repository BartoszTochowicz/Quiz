import { useContext, useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import socketService from "../utils/socketService";
import AuthContext from "../utils/authProvider";

function Lobbies() {
    const { isAuthenticated, authToken, triggerAuthCheck, username } = useContext(AuthContext);
    const socketInitialized = useRef(false);
    const navigation = useNavigate();
    const [lobbies, setLobbies] = useState([]);
    const [isJoining, setIsJoining] = useState(false);

    useEffect(() => {
        // Reset when auth status changes
        if (!isAuthenticated || !authToken) {
            socketInitialized.current = false;
            socketService.disconnect();
            return;
        }

        // Initialize socket only once after authentication
        if (socketInitialized.current) {
            console.log("Socket already initialized");
            return;
        }

        console.log("Initializing socket connection");
        socketInitialized.current = true;

        // Initialize socket service with callbacks
        socketService.initialize({
            onListLobbies: (data) => {
                console.log("Received lobby list:", data);
                setLobbies(data.lobbies);
            },
            onAuthFail: () => {
                setIsJoining(false);
                triggerAuthCheck();
            },
        });

        // Connect to socket server
        socketService.connect(authToken);

        return () => {
            console.log("Cleaning up socket connection");
            if (!isAuthenticated) {
                socketService.disconnect();
            }
        };
    }, [isAuthenticated, authToken, triggerAuthCheck]);

    useEffect(() => {
        socketService.reconnect(authToken);
    }, [authToken]);

    const joinLobby = (lobbyId) => {
        console.log("Joining lobby:", lobbyId);
        socketService.emit('join_lobby', { "lobby_id": lobbyId, 'username': username }, (response) => {
            if (response.status === 'ok') {
                console.log("Joined lobby successfully:", response);
                setIsJoining(true);
                navigation(`/lobby/${lobbyId}`);
            } else {
                console.error("Failed to join lobby:", response.message);
                alert(`Failed to join lobby: ${response.message}`);
            }
        });
    };

    return (
        <div>
            <div>
                <header>
                    <h1>Lobbies</h1>
                </header>

                <main>
                    <div>
                        <h2>Choose lobby to join</h2>
                        <div>
                            {lobbies.length === 0 && <p>No lobbies available. Create one!</p>}
                            {lobbies ? (
                                <ul>
                                    {lobbies.map((lobby) => (
                                        <li key={lobby.lobby_id}>
                                            <strong>{lobby.name}</strong>
                                            - {lobby.players} player{lobby.players !== 1 ? 's' : ''} / {lobby.max_players}
                                            <button onClick={() => joinLobby(lobby.lobby_id)} disabled={isJoining}>
                                                Join
                                            </button>
                                        </li>
                                    ))}
                                </ul>
                            ) : null}
                        </div>
                        {isJoining && <p>Joining lobby...</p>}
                    </div>
                    <h3>Do you want to create your own quiz?</h3>
                    <Link to={"/lobby/create"}>
                        <button>Create lobby</button>
                    </Link> 
                </main>
            </div>
        </div>
    );
}

export default Lobbies;