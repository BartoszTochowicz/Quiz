

const URL = "http://localhost:5000"; 

class SocketService {
    constructor(){
        this.socket = null;
        this.isConnected = false;
        this.authToken = null;
        this.callbacks = {
            onConnect : null,
            onDisconnect : null,
            onRefresh : null,
            onPlayerJoined : null,
            onPlayerLeft : null,
            onAuthFail : null,
            onQuizStart : null,
            onNewQuestion : null,
            onAnswerResult : null,
            onQuizEnd : null,
            onError : null
        };
        console.log("SocketService constructor called");
        this.reconnectCounter = 0;        
    }

    initialize(callbacks = {}){
        this.callbacks = {...this.callbacks,...callbacks};
    }
}