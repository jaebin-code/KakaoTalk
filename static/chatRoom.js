var ws = new WebSocket("ws://localhost:8000/ws");

ws.onmessage = function (event) {
    get_chat(roomnumber);
}

$(document).ready(function () {
    get_chat(roomnumber);
    $("#leftSendButton").click(function (event) {
        
        var id = globalID;
        var content = $("#leftMessageInput").val().replace(/\n/g, '<br>');
        if (content.replace(/<br>/g, '').trim().length > 0) {
            var content = content.replace(/ /g, '&nbsp;');
            var currentTime = new Date();
            var data = { "id": id, "username":"a","contents": content, "create_date": currentTime, "roomnumber": roomnumber }
            $.ajax({
                url: "/posttalk",
                type: "post",
                contentType: "application/json",
                dataType: "json",
                data: JSON.stringify(data),
                success: function (talk) {
                    get_chat(roomnumber);
                    ws.send(JSON.stringify(data));
                },
                    error: function (error) {
                    // 에러 응답 처리
                    console.error(error.responseJSON);
                }
            });
        }
        
    });


    $("#leftMessageInput").on('keydown', function (event) {
        if (event.keyCode == 13) {
            if (!event.shiftKey) {
                event.preventDefault();
                var id = globalID;
                var content = $("#leftMessageInput").val().replace(/\n/g, '<br>');
                if (content.replace(/<br>/g, '').trim().length > 0) {
                    var content = content.replace(/ /g, '&nbsp;');
                    var currentTime = new Date();
                    var data = { "id": id, "username": "a", "contents": content, "create_date": currentTime, "roomnumber": roomnumber }
                    $.ajax({
                        url: "/posttalk",
                        type: "post",
                        contentType: "application/json",
                        dataType: "json",
                        data: JSON.stringify(data),
                        success: function (talk) {
                            get_chat(roomnumber);
                            ws.send(JSON.stringify(data));
                        },
                        error: function (error) {
                            // 에러 응답 처리
                            console.error(error.responseJSON);
                        }
                    });
                }
            }
        }
    });


    $('#photoSendButton').click(function () {
        $('#photoInput').click();
    });

    $(".chatButton").click(function (event) {
        $.ajax({
            type: 'GET',
            url: '/chatListPage',
            success: function (data) {
                window.location = "/chatListPage";
            },
            error: function (error) {
                alert(error);
            }
        })
    })

    $('#photoInput').change(function (e) {
        var formData = new FormData();
        var imageInput = e.target.files[0];
        // 이미지 파일을 선택한 경우에만 업데이트 요청을 보냅니다.
        var currentTime = new Date();
        if (imageInput) {
            formData.append('image', imageInput);

            // AJAX를 사용하여 백엔드에 프로필 이미지 업데이트 요청을 보냅니다.
            $.ajax({
                type: 'POST',
                url: '/update_conversationimage',
                data: formData,
                contentType: false,
                processData: false,
                success: function (response) {
                    console.log(response);
                    var data = { "id": globalID, "username": "a", "contents": response.message, "create_date": currentTime, "roomnumber": roomnumber }
                    $.ajax({
                        url: "/postphoto",
                        type: "post",
                        contentType: "application/json",
                        dataType: "json",
                        data: JSON.stringify(data),
                        success: function (talk) {
                            get_chat(roomnumber);
                            ws.send(JSON.stringify(data));
                        },
                        error: function (error) {
                            // 에러 응답 처리
                            console.error(error.responseJSON);
                        }
                    });
                },
                error: function (error) {
                    console.error(error);
                    // 실패한 경우에 대한 처리를 여기에 추가할 수 있습니다.
                }
            });
        }
    })
    
});


function update_chat(chats) {
    chats.forEach(item => {

        item.create_date = new Date(item.create_date);
        var hours = item.create_date.getHours() + 9;
        var minutes = item.create_date.getMinutes();
        var ampm = hours >= 12 ? '오후 ' : '오전 ';
        hours = hours % 12;
        hours = hours ? hours : 12;
        var timeString = ampm + hours + ':' + (minutes < 10 ? '0' : '') + minutes;
        if (item.id != globalID) {
            if(item.contenttype != "photo"){
                $("#chatboxLeft").append('<div class="message left">' + '<span class="text">' + item.contents + '</span>' + '<span class="time left">' + timeString + '</span>' + '<span class="nickname">' + item.username + '</span>' + '</div>');
            }
            else{
                // $('#chatboxLeft').append($('<div class="message left has-image">')
                //     .append($('<img>').attr('src', "http://127.0.0.1:8000/" + item.contents).attr('alt', 'Left Image'))
                //     .append($('<span class="time left">').text(timeString))
                //     .append($('<span class="nickname">').text(item.name))
                // );
                $('#chatboxLeft').append($('<div class="message left has-image">')
                    .append($('<img>').attr('src', "http://127.0.0.1:8000/" + item.contents).attr('alt', 'Left Image').on('click', function () {
                        // 이미지를 클릭했을 때 새 창으로 열기
                        window.open("http://127.0.0.1:8000/" + item.contents, "_blank");
                    }))
                    .append($('<span class="time left">').text(timeString))
                );

            }
        } else {
            if (item.contenttype != "photo") {
                $("#chatboxLeft").append('<div class="message right">' + '<span class="text">' + item.contents + '</span>' + '<span class="time right">' + timeString + '</span>' + '</div>');

            }
            else{
                console.log(item.contents);
                $('#chatboxLeft').append($('<div class="message right has-image">')
                    .append($('<img>').attr('src', "http://127.0.0.1:8000/" + item.contents).attr('alt', 'Right Image').on('click', function () {
                        // 이미지를 클릭했을 때 새 창으로 열기
                        window.open("http://127.0.0.1:8000/" + item.contents, "_blank");
                    }))
                    .append($('<span class="time right">').text(timeString))
                );

            }
        }
        $("#leftMessageInput").val("");
        setTimeout(function () {
            $('#chatboxLeft').scrollTop($('#chatboxLeft').prop("scrollHeight"));
        }, 10);
    })
}

function get_chat(roomnumber) {
    $.getJSON("/get_chat", { "roomnumber": roomnumber }, function (chats) {
        $("#chatboxLeft").empty();
        update_chat(chats);
    });
}
