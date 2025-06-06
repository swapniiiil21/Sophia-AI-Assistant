$(document).ready(function () {
    // Expose the 'DisplaySophiaMessage' function to the Python backend via eel.
    // This allows Python to call this JavaScript function to update the UI with SOPHIA's responses.
    // It now accepts an optional thinkingMessageId to update a previous message.
    eel.expose(DisplaySophiaMessage);
    function DisplaySophiaMessage(message, thinkingMessageId = null) {
        // Update the text content of the element with the class 'siri-message'.
        // This is used when SOPHIA is speaking and the SiriWave animation is active.
        $(".siri-message").text(message);
        
        // Trigger the textillate animation on the updated message.
        $('.siri-message').textillate('start');

        // Also add Sophia's message to the chat history.
        // If a thinkingMessageId is provided, it will update that specific message.
        // The addMessageToChatHistory function is defined and globally exposed in main.js.
        if (typeof addMessageToChatHistory === 'function') {
            if (thinkingMessageId) {
                // If a thinking message ID is provided, update that message in the chat history
                addMessageToChatHistory(message, 'sophia', thinkingMessageId);
            } else {
                // Otherwise, add a new message to the chat history
                addMessageToChatHistory(message, 'sophia');
            }
        } else {
            console.warn("addMessageToChatHistory function not found. Sophia's message not added to chat history.");
        }
    }

    // Expose the 'ShowHood' function to the Python backend via eel.
    // This allows Python to control the visibility of the main UI vs. the SiriWave UI.
    eel.expose(ShowHood);
    function ShowHood() {
        // Hide the SiriWave section and show the main 'Oval' UI section.
        $("#Oval").attr("hidden", false);
        $("#SiriWave").attr("hidden", true);
    }

    // IMPORTANT: You need to implement the 'sendUserMessage' function in your Python backend
    // to receive messages sent from the JavaScript frontend's chatbox.
    // It now expects a second argument: thinking_message_id
    // Example Python code for your backend (as provided in the previous response for command.py):
    // @eel.expose
    // def sendUserMessage(message, thinking_message_id=None):
    //     print(f"Python received user message: {message} with ID: {thinking_message_id}")
    //     # Process the message, generate a response,
    //     # then send it back to the UI using:
    //     # eel.DisplaySophiaMessage("Your response here", thinking_message_id)
});
