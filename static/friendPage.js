$(document).ready(function () {
    update_myprofile();
    get_friend();
    $(".add-friend-button").click(function () {
        // 모달 창 열기
        $("#myModal").show();
    });

    $("#closeModal").click(function () {
        // 모달 창 닫기
        $("#myModal").hide();
    });

    $("#add").click(function () {
        // Add 버튼을 클릭했을 때 실행되는 함수
        var friendID = $("#username").val(); // 입력 필드에서 friendID를 가져옴

        // AJAX를 사용하여 /addFriend 엔드포인트로 데이터 전송
        $.ajax({
            type: 'POST',
            url: '/addFriend',
            data: {
                friendID: friendID
            },
            success: function (data) {
                // 서버에서 성공적으로 응답을 받았을 때의 동작
                console.log("Friend added successfully");
                // 추가로 필요한 동작 수행
                get_friend();
                // 모달 창 닫기
                $("#myModal").hide();
            },
            error: function (error) {
                // 서버에서 오류 응답을 받았을 때의 동작
                alert("친구가 존재하지 않거나, 이미 등록되어 있습니다.");
                // 추가로 필요한 동작 수행
            }
        });
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


    $(document).on("click", ".friendButton", function (event) {
        var userId = $(this).attr("id");

        $.ajax({
            type: 'GET',
            url: '/profilePage/' + userId,
            success: function (data) {
                window.location = "/profilePage/" + userId;  // 서버에서 반환한 데이터를 사용하지 않으므로 data는 사용하지 않음
            },
            error: function (error) {
                alert("Error loading user profile: " + error);
            }
        });
    });

});


function update_myprofile(){
    $.ajax({
        type: 'GET',
        url: '/get_user_info',
        xhrFields: {
            withCredentials: true // 쿠키를 서버에 보내기 위해 필요
        },
        success: function (data) {
            $(".myprofile").append("<input type='button' class='friendButton' id='" + data.id + "' value='" + data.username + "'><br />");

        },
        error: function (error) {
            alert(error);
        }
    });
}

function update_friend(friends){
    $(".friend").empty();
    $(".friend").append("Friends List");
    friends.forEach(item => {
        $(".friend").append("<input type='button' class='friendButton' id='" + item.friend_id + "' value='" + item.friend_name + "'><br />");
    })
}

function get_friend(){
    $.getJSON("/get_user_friends", update_friend);
}