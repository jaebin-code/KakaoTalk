$(document).ready(function () {
    get_friend();

    // 클릭한 버튼의 ID를 저장할 배열
    var clickedButtonIds = [];

    $(document).on("click", ".friendButton", function (event) {
        var userId = $(this).attr("id");

        // 클릭한 버튼의 ID를 토글하여 배열에 추가 또는 제거
        var index = clickedButtonIds.indexOf(userId);
        if (index === -1) {
            // 배열에 없는 경우 추가
            clickedButtonIds.push(userId);
        } else {
            // 배열에 있는 경우 제거
            clickedButtonIds.splice(index, 1);
        }

        // 버튼에 'selected' 클래스를 추가 또는 제거하여 색 변경
        $(this).toggleClass("selected");

        // 화면에 현재까지 선택한 버튼의 ID 목록을 표시
        console.log("Selected Button IDs:", clickedButtonIds);
    });

    // 제출 버튼을 눌렀을 때 선택한 버튼의 ID 목록을 서버로 전송
    $(".chatButton").on("click", function () {
        console.log("Submitted Button IDs:", clickedButtonIds);

        // 선택한 버튼의 ID 목록을 서버로 전송
        if (clickedButtonIds.length === 1) {
            // 하나의 ID인 경우 /join_chat 엔드포인트로 전송
            $.ajax({
                type: "POST",
                url: "/join_chat",
                data: { target_user: clickedButtonIds[0] },
                success: function (data) {
                    console.log(data);
                    window.location = "/chatroom/" + data.room_number;
                },
                error: function (error) {
                    // 실패한 경우에 대한 처리
                    console.error('Error:', JSON.stringify(error));
                }
            });
        } else if (clickedButtonIds.length > 1) {
            console.log(clickedButtonIds.join(","));
            // 여러 개의 ID인 경우 /create_chat_room 엔드포인트로 전송
            $.ajax({
                type: "POST",
                url: "/create_chat_room",
                data: { selected_friends: clickedButtonIds.join(",") },
                success: function (data) {
                    // 서버 응답에 대한 처리
                    console.log(data);
                    window.location = "/chatroom/" + data.room_id; // 적절한 서버 응답 필요
                },
                error: function (error) {
                    // 실패한 경우에 대한 처리
                    console.error('Error:', JSON.stringify(error));
                }
            });
        }

    });
});

function update_friend(friends) {
    $(".friend").empty();
    $(".friend").append("Friends List");
    friends.forEach(item => {
        $(".friend").append("<input type='button' class='friendButton' id='" + item.friend_id + "' value='" + item.friend_name + "'><br />");
    })
}

function get_friend() {
    $.getJSON("/get_user_friends", update_friend);
}