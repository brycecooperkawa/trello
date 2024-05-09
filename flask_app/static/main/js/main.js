// Make sure these are added after everything is loaded, was having problems with this not working before
document.addEventListener('DOMContentLoaded', function() {
    // Add event listener to the submit button
    if (document.getElementById("submitButton") != null){
        document.getElementById("submitButton").addEventListener("click", checkCredentials);
    }

    // Add event listener to the sign up button
    if (document.getElementById("signUpButton") != null){
        document.getElementById("signUpButton").addEventListener("click", redirectSignUp);
    }

    // Add event listener to the create account button
    if (document.getElementById("createAccountButton") != null){
        document.getElementById("createAccountButton").addEventListener("click", createAccount);
    }

    // Add event listener to the existing board button
    if (document.getElementById("openExistingButton") != null){
        document.getElementById("openExistingButton").addEventListener("click", displayExistingBoards);
    }

    // Add event listener to the new board button
    if (document.getElementById("createNewBoardButton") != null){
        document.getElementById("createNewBoardButton").addEventListener("click", displayCreateBoard);
    }

    // Add event listener for the submit board button
    if (document.getElementById("createBoardButton") != null){
        document.getElementById("createBoardButton").addEventListener("click", createNewBoard);
    }

    // Add event listener for the add email button
    if (document.getElementById("addEmailButton") != null){
        document.getElementById("addEmailButton").addEventListener("click", addEmail);
    }

    // Get all board links
    const boardLinks = document.querySelectorAll(".board-link");
    // Add click event listeners to each board link
    boardLinks.forEach(function(link) {
        link.addEventListener("click", redirectToExistingBoard);
    });

});

// Holds number of authentication fails
let count = 0;

// Checks the users credentials on login
function checkCredentials() {
    // Get email and password entered in form
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    // package data in a JSON object
    var data_d = {'email': email, 'password': password};
    console.log('data_d', data_d);

    // SEND DATA TO SERVER VIA jQuery.ajax({})
    jQuery.ajax({
        url: "/processlogin",
        data: data_d,
        type: "POST",
        success:function(returned_data){
            returned_data = JSON.parse(returned_data);
            // If the user is authenticated
            if (returned_data.success === 1) {
                // Redirect to home page
                window.location.href = "/home";
            // If the authentication fails increment the count
            } else {
                // Increment count and stay on login page
                count++;
                document.getElementById("authFail").innerText = "Authentication Failure: " + count;
            }
        }
    });
}

// Redirects the user to the Sign Up page
function redirectSignUp() {
    window.location.href = "/signup";
}

// Creates user account
function createAccount() {
    // Get email and password entered in form
    const email = document.getElementById("emailSignUp").value;
    const password = document.getElementById("passwordSignUp").value;
    const password2 = document.getElementById("passwordSignUp2").value;

    // Make sure the user entered an email
    if (email === ""){
        // Clear form
        document.getElementById("emailSignUp").value = "";
        document.getElementById("passwordSignUp").value = "";
        document.getElementById("passwordSignUp2").value = "";

        alert("Please enter an email address");
        return;
    }

    // Make sure the user entered a password
    if (password === "") {
        // Clear form
        document.getElementById("emailSignUp").value = "";
        document.getElementById("passwordSignUp").value = "";
        document.getElementById("passwordSignUp2").value = "";

        alert("Please enter a password");
        return;
    }

    // Check that entered passwords match
    if (password == password2){
        // package data in a JSON object
        var data_d = {'email': email, 'password': password};
        console.log('data_d', data_d);

        // SEND DATA TO SERVER VIA jQuery.ajax({})
        jQuery.ajax({
            url: "/processsignup",
            data: data_d,
            type: "POST",
            success:function(returned_data){
                returned_data = JSON.parse(returned_data);
                // If the user is created successfully
                if (returned_data.success === 1) {
                    // Redirect to home page
                    window.location.href = "/home";
                // If the user creation fails
                } else {
                    // Hide old message if existing
                    document.getElementById("passwordMatch").innerText = "";
                    // Display user exists message
                    document.getElementById("userExists").innerText = "A user with this email already exists. Please login.";
                }
            }
        });
    }else{
        // Hide old message if existing
        document.getElementById("userExists").innerText = "";
        // If passwords don't match display message
        document.getElementById("passwordMatch").innerText = "Passwords do not match, please try again.";

        // Clear form
        document.getElementById("emailSignUp").value = "";
        document.getElementById("passwordSignUp").value = "";
        document.getElementById("passwordSignUp2").value = "";
    }
}

// When the user selects the existing boards button display links to their existing boards
function displayExistingBoards() {
    // SEND POST REQUEST TO SERVER VIA jQuery.ajax({})
    jQuery.ajax({
        url: "/processgetexistingboards",
        type: "POST",
        success:function(returned_data){
            returned_data = JSON.parse(returned_data);
            // If successful then redirect to the existing boards page
            if (returned_data.success === 1) {
                window.location.href = "/existingboards";
            // If fails display message
            } else {
                alert("User has no existing boards. Please create a new board.");
            }
        }
    });
}

// Displays the create board form
function displayCreateBoard() {
    // Display the create board form
    document.getElementById("createBoardForm").style.display = "block";
}

// Displays the added emails
function addEmail() {
    var emailInput = document.getElementById("memberEmailInput");
    var email = emailInput.value.trim();

    if (email === "") {
      alert("Please enter a valid email address.");
      return;
    }

    // Create a new div to display the email
    var emailDiv = document.createElement("div");
    emailDiv.textContent = email;

    // Append the email div and remove button to the emails container
    var emailsContainer = document.getElementById("emailsContainer");
    emailsContainer.appendChild(emailDiv);

    // Clear the email input
    emailInput.value = "";
}

// When the user selects the create board button, provide a form with inputs to create new board
function createNewBoard() {
    // Get the project name
    var projectName = document.getElementById("projectNameInput").value;

    if (projectName === ""){
        alert("Please enter a board name.");
        return;
    }

    // Get all displayed emails
    var displayedEmails = [];
    var emailDivs = document.querySelectorAll("#emailsContainer div");
    emailDivs.forEach(function(emailDiv) {
      displayedEmails.push(emailDiv.textContent);
    });

    // package data in a JSON object
    var data_d = {'name': projectName, 'users': JSON.stringify(displayedEmails)};
    console.log('data_d', data_d);
    
    // SEND DATA TO SERVER VIA jQuery.ajax({})
    jQuery.ajax({
        url: "/processcreateboard",
        data: data_d,
        type: "POST",
        success:function(returned_data){
            returned_data = JSON.parse(returned_data);
            // If the board is created successfully
            if (returned_data.success === 1) {
                // Redirect to the board page
                navigateToBoard(projectName);
            // If the users included on the board are invalid
            }else if (returned_data.failure === 0){
                alert("User included on board is invalid or does not exist, please try again");
            // If a board with this name already exists
            }else if (returned_data.failure === 1){
                alert("A board with this name already exists. Please choose a new name.");
            // If some other issue occurs
            }else {
                alert("Error creating board, please try again.");
            }
        }
    });

    // Clear the inputs and displayed emails
    document.getElementById("projectNameInput").value = "";
    document.getElementById("emailsContainer").innerHTML = "";
}

// Function to handle existing board link being clicked
function redirectToExistingBoard(event) {
    // Get the board name from the link that was clicked
    const boardName = event.target.textContent;
    
    navigateToBoard(boardName);
}

// Given a name, redirects the user to that boards page
function navigateToBoard(name){
    // package data in a JSON object
    var data_d = {'name': name};
    console.log('data_d', data_d);
    
    // SEND DATA TO SERVER VIA jQuery.ajax({})
    jQuery.ajax({
        url: "/processboardname",
        data: data_d,
        type: "POST",
        success:function(returned_data){
            returned_data = JSON.parse(returned_data);
            // If the board is navigated to successfully
            if (returned_data.success === 1) {
                window.location.href = "/board";
            // If some issues occurs
            }else {
                alert("Error navigating to board, please try again.");
            }
        }
    });
}

function addCard(formId) {
    // Get all information from the form about the card and its list
    const form = document.getElementById(formId);
    const data = new FormData(form);
    const list_id = data.get("list_id");
    const description = data.get("description");

    // package data in a JSON object
    var data_d = {'list_id': list_id, 'description': description};
    console.log('data_d', data_d);
    
    // SEND DATA TO SERVER VIA jQuery.ajax({})
    jQuery.ajax({
        url: "/processcreatecard",
        data: data_d,
        type: "POST",
        success:function(returned_data){
            returned_data = JSON.parse(returned_data);
            // If the card is created successfully
            if (returned_data.success === 1) {
                form.reset();
            // If some issues occurs
            }else {
                alert("Error creating card, please try again.");
            }
        }
    });
}
