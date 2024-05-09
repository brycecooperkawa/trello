var socket;
$(document).ready(function(){
    // User connects
    socket = io.connect('https://' + document.domain + ':' + location.port + '/chat');
    socket.on('connect', function() {
        const boardName = document.getElementById("data").getAttribute("board_name");
        socket.emit('joined', {room: boardName});
    });
    
    // Handles recieved status
    socket.on('status', function(data) {     
        displayMessage(data.msg, data.sender);
    });

    // Handles received message
    socket.on('message', function(data) {
        displayMessage(data.msg, data.sender);
    });

    // Handles send button press, sends message in chat
    document.getElementById("send").addEventListener("click", function() {
        const message = document.getElementById("message").value;
        const boardName = document.getElementById("data").getAttribute("board_name");
        socket.emit('message', {message: message, room: boardName});
        document.getElementById("message").value = "";
    });

    // When the user navigates away from the board page, leave the chat room
    window.addEventListener('beforeunload', function() {
        const boardName = document.getElementById("data").getAttribute("board_name");
        socket.emit('left', {room: boardName});
    });
});

// Function to display messages with appropriate styling based on sender
function displayMessage(message, sender) {
    const chatElement = document.getElementById("chat");
    const messageElement = document.createElement("p");
    messageElement.textContent = message;

    const currentUser = document.getElementById("data").getAttribute("user");

    if (sender === currentUser) {
        messageElement.style.cssText = 'width: 100%; color: blue; text-align: right';
    } else {
        messageElement.style.cssText = 'width: 100%; color: grey; text-align: left';
    }

    chatElement.appendChild(messageElement);
    chatElement.scrollTop = chatElement.scrollHeight;
}