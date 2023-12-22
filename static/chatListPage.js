var ws = new WebSocket("ws://localhost:8000/ws");

ws.onmessage = function (event) {
    loadChatList();
}

$(document).ready(function () {

    loadChatList();

    $(".friendsButton").click(function (event) {
        $.ajax({
            type: 'GET',
            url: '/friendPage',
            success: function (data) {
                window.location = "/friendPage";
            },
            error: function (error) {
                alert(error);
            }
        })
    });

    $(document).on("click", ".friendButton", function (event) {
        var buttonId = $(this).attr("id");
        $.ajax({
            type: "POST",
            url: "/list_join_chat",
            data: { room_number: buttonId },
            success: function (response) {
                // On success, redirect to chatroom.html with the obtained room_number

                window.location = "/chatroom/" + buttonId;
            },
            error: function (error) {
                console.error(error);

                // If the server responded with JSON error message, log it
                if (error.responseJSON) {
                    console.error("Server error message:", error.responseJSON);
                }
            }
        });
    });

    $(".chatMakeButton").click(function (event) {
        $.ajax({
            type: 'GET',
            url: '/groupPage',
            success: function (data) {
                window.location = "/groupPage";
            },
            error: function (error) {
                alert(error);
            }
        })
    })


});

function loadChatList() {
    $(".friend").empty();
    var brElement = document.createElement('br');
    $(".friend").append('Chat List ').append(brElement);
    $.get("/get_chat_lists", function (data) {
        
        // data를 순회하면서 Chat List에 추가
        data.forEach(function (chat) {
            console.log(chat.message_type);
            // lastmessage가 not null일 경우에만 추가
            if (chat.lastmessage !== null) {
                
                if (chat.message_type == "photo"){
                    var button = $('<button class="friendButton" id=' + chat.roomnumber + '></button>');
                    button.append('<div class="name">' + chat.name + '</div>');
                    button.append('<div class="lasttalk">' + 'Image' + '</div>');
                    $(".friend").append(button);
                }
                else{
                    var button = $('<button class="friendButton" id=' + chat.roomnumber + '></button>');
                    button.append('<div class="name">' + chat.name + '</div>');
                    button.append('<div class="lasttalk">' + chat.lastmessage + '</div>');
                    $(".friend").append(button);
                }

            }
        });
    });
}