// Event listener for adding a new card
document.addEventListener('DOMContentLoaded', function() {
    // Create socket
    var socket = io.connect('https://' + document.domain + ':' + location.port + '/board');

    // Updates all users on newly created card
    socket.on('new_card', function(cardData) {
        // Append new card to the correct list
        const listId = cardData.list_id;
        const description = cardData.description;
        const cardId = cardData.card_id;
    
        // Create new card element
        const cardElement = document.createElement("div");
        cardElement.setAttribute("card_id", cardId);
        cardElement.className = "card draggable"; // Ensure the 'draggable' class is added
        cardElement.innerHTML = `
            <p>${description}</p>
            <button class="editButton">Edit</button>
            <button class="deleteButton">Delete</button>
        `;
    
        // Append to the correct list
        const listContainer = document.querySelector(`#list_${listId}`);
        listContainer.appendChild(cardElement);
    
        // Make the newly created card draggable
        makeCardDraggable(cardElement);
    });

    // Updates all users on newly edited card
    socket.on('edit_card', function(cardData) {
        // Extract card ID and new description from the data
        const cardId = cardData.card_id;
        const newDescription = cardData.description;

        // Find the card element in the UI based on card ID
        const cardElement = document.querySelector('[card_id="' + cardId + '"]');

        if (cardElement) {
            // Assuming each card has a description element with a specific class
            var descriptionElement = cardElement.querySelector('p');

            // Update the description of the card in the UI
            descriptionElement.textContent = newDescription;
        } else {
            console.log("Card with ID " + cardId + " not found in the UI.");
        }
    });

    // Updates all users on newly deleted card
    socket.on('delete_card', function(cardData) {
        // Extract card ID and new description from the data
        const cardId = cardData.card_id;

        // Find the card element in the UI based on card ID
        const cardElement = document.querySelector('[card_id="' + cardId + '"]');

        if (cardElement) {
            cardElement.remove();
        } else {
            console.log("Card with ID " + cardId + " not found in the UI.");
        }
    });

    // Updates all users on newly moved card
    socket.on('move_card', function(moveData) {
        // Extract necessary data
        const cardId = moveData.card_id;
        const listId = moveData.list_id;

        // Find the card element in the UI based on card ID
        const cardElement = document.querySelector('[card_id="' + cardId + '"]');

        if (cardElement) {
            // Remove the card from its current list
            cardElement.remove();

            // Append the card to the new list
            const newList = document.querySelector('#list_' + listId);
            if (newList) {
                newList.appendChild(cardElement);
            } else {
                console.log("List with ID " + listId + " not found in the UI.");
            }
        } else {
            console.log("Card with ID " + cardId + " not found in the UI.");
        }
    });

    // Get all add card buttons
    const addCardButtons = document.querySelectorAll(".addCardButton");
    addCardButtons.forEach(button => {
        // Add event listeners based on the button list id
        button.addEventListener("click", function () {
            const listId = button.getAttribute("list_id");
            addCard("addCardForm_" + listId);
        });
    });

    // Event delegation for edit and delete buttons
    document.addEventListener('click', function(event) {
        const target = event.target;
        // Check if the clicked element is an edit or delete button
        if (target.classList.contains('editButton')) {
            // Get the card ID
            const cardId = target.closest('.card').getAttribute("card_id");
            // Handle edit button click with the card ID
            editCard(target, cardId);
        } else if (target.classList.contains('deleteButton')) {
            // Get the card ID
            const cardId = target.closest('.card').getAttribute("card_id");
            // Handle delete button click with the card ID
            deleteCard(target, cardId);
        }
    });

    // Define draggable elements
    $(".draggable").draggable({
        // If card is dropped somewhere invalid then revert to original spot
        revert: "invalid",
        start: function(event, ui) {
            $(this).addClass("dragging");
        },
        stop: function(event, ui) {
            $(this).removeClass("dragging");
        }
    });

    // Define droppable elements
    $(".droppable").droppable({
        drop: function(event, ui) {
            // Get card attributes
            const droppedCard = ui.draggable;
            var newParentList = $(this);
            const cardId = droppedCard.attr("card_id");
            const listId = newParentList.attr("id").split("_")[1];

            // Remove the card from its current list
            droppedCard.detach();

            // Calculate the position to append the dropped card within the new list
            var existingCards = newParentList.find('.card');
            if (existingCards.length > 0) {
                // Append the dropped card after the last existing card, always add to end of list
                existingCards.last().after(droppedCard);
            } else {
                // If there are no existing cards, simply append the dropped card to the new list
                newParentList.append(droppedCard);
            }

            // Updates the card on the backend
            moveCard(cardId, listId);

            // Update the card's appearance to make sure it appears corectly
            droppedCard.css({
                left: 0,
                top: 0
            });
        },
        over: function(event, ui) {
            $(this).addClass("highlight");
        },
        out: function(event, ui) {
            $(this).removeClass("highlight");
        }
    });
});

// Adds the card by calling the route
function addCard(formId) {
    // Get all information from the form about the card and its list
    const form = document.getElementById(formId);
    const data = new FormData(form);
    const list_id = data.get("list_id");
    const description = data.get("description");

    // package data in a JSON object
    var data_d = {'list_id': list_id, 'description': description};

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

// Function to handle edit button click
function editCard(button, cardId) {
    // Get the parent card element
    const cardElement = button.closest('.card');
    // Get the description element
    const descriptionElement = cardElement.querySelector('p');
    // Get the delete button
    const deleteButton = cardElement.querySelector('.deleteButton');

    // Hide the edit button
    button.style.display = 'none';
    // Hide the delete button
    deleteButton.style.display = 'none';

    // Get the current description text
    const currentDescription = descriptionElement.textContent;

    // Replace the <p> element with a <textarea> for editing
    const textarea = document.createElement('textarea');
    textarea.value = currentDescription;
    descriptionElement.replaceWith(textarea);

    // Create a save button
    const saveButton = document.createElement('button');
    saveButton.textContent = 'Save';
    saveButton.classList.add('saveButton');
    cardElement.appendChild(saveButton);

    // Create a cancel button
    const cancelButton = document.createElement('button');
    cancelButton.textContent = 'Cancel';
    cancelButton.classList.add('cancelButton');
    cardElement.appendChild(cancelButton);

    // Save function called by button and enter
    function save(){
        // Get the updated description
        const updatedDescription = textarea.value;

        // Save the new card
        // package data in a JSON object
        var data_d = {'card_id': cardId, 'description' : updatedDescription};
        console.log('data_d', data_d);
        
        // SEND DATA TO SERVER VIA jQuery.ajax({})
        jQuery.ajax({
            url: "/processeditcard",
            data: data_d,
            type: "POST",
            success:function(returned_data){
                returned_data = JSON.parse(returned_data);
                // If the board is navigated to successfully
                if (returned_data.success === 1) {
                    
                // If some issues occurs
                }else {
                    alert("Error editing the card, please try again.");
                }
            }
        });
        
        // Replace the textarea with the <p> element
        textarea.replaceWith(descriptionElement);
        // Show the edit button
        button.style.display = '';
        // Show the delete button
        deleteButton.style.display = '';
        // Remove the save button
        saveButton.remove();
        // Remove the cancel button
        cancelButton.remove();
    }

    // Add event listener to the save button
    saveButton.addEventListener('click', save);

    // Add event listener to the textarea for Enter key press
    textarea.addEventListener('keydown', function(event) {
        if (event.keyCode === 13) { // Check if Enter key is pressed
            event.preventDefault(); // Prevent default behavior (adding newline)
            save(); // Trigger save action
        }
    });

    // Add event listener to the cancel button
    cancelButton.addEventListener('click', function() {
        // Replace the textarea with the <p> element
        textarea.replaceWith(descriptionElement);
        // Show the edit button
        button.style.display = '';
        // Show the delete button
        deleteButton.style.display = '';
        // Remove the save button
        saveButton.remove();
        // Remove the cancel button
        cancelButton.remove();
    });
}

// Function to handle delete button click
function deleteCard(button, cardId) {
    // Get the parent card element
    const cardElement = button.closest('.card');

    // package data in a JSON object
    var data_d = {'card_id': cardId};
    console.log('data_d', data_d);
        
    // SEND DATA TO SERVER VIA jQuery.ajax({})
    jQuery.ajax({
        url: "/processdeletecard",
        data: data_d,
        type: "POST",
        success:function(returned_data){
            returned_data = JSON.parse(returned_data);
            // If the board is navigated to successfully
            if (returned_data.success === 1) {
                
            // If some issues occurs
            }else {
                alert("Error deleting the card, please try again.");
            }
        }
    });
}

// Function to handle delete button click
function moveCard(cardId, listId) {
    // package data in a JSON object
    var data_d = {'card_id': cardId, 'list_id': listId};
    console.log('data_d', data_d);
    
    // SEND DATA TO SERVER VIA jQuery.ajax({})
    jQuery.ajax({
        url: "/processmovecard",
        data: data_d,
        type: "POST",
        success:function(returned_data){
            returned_data = JSON.parse(returned_data);
            // If the card is moved successfully on the backend
            if (returned_data.success === 1) {

            // If some issues occurs
            }else {
                alert("Error moving the card, please refresh and try again.");
            }
        }
    });

}

// Function to make cards draggable, fixes problem of newly created cards not being draggable
function makeCardDraggable(cardElement) {
    $(cardElement).draggable({
        // If card is dropped somewhere invalid then revert to original spot
        revert: "invalid",
        start: function(event, ui) {
            $(this).addClass("dragging");
        },
        stop: function(event, ui) {
            $(this).removeClass("dragging");
        }
    });
}