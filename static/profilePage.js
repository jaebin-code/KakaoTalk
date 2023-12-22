$(document).ready(function () {
    $('.settings-button').click(function () {
        openSettingsPopup();
    });

    $('.close-button').click(function () {
        closePopup('settings-popup');
    });

    $('#update-status-button').click(function () {
        updateStatus();
    });

    $('#update-image-button').click(function () {
        updateImage();
    });

    $(".close-button").click(function (event) {
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
    })
    $(".chat-button").click(function () {
        console.log(myid);
        $.ajax({
            type: "POST",
            url: "/join_chat",
            data: { target_user: myid },
            success: function (response) {
                // On success, redirect to chatroom.html with the obtained room_number
                var room_number = response.room_number;
                window.location = "/chatroom/" + room_number;
            },
            error: function (error) {
                console.error(error);
                // Handle the error as needed
            }
        });
    });


});

function openSettingsPopup() {
    $('#settings-popup').show();
}

function updateStatus() {
    var newStatus = $('#status-input').val();

    // 상태 메시지가 15자 이하인 경우에만 업데이트 요청을 보냅니다.
    if (newStatus.length <= 15) {
        // AJAX를 사용하여 백엔드에 상태 메시지 업데이트 요청을 보냅니다.
        $.ajax({
            type: 'POST',
            url: '/update_status',
            data: { new_status: newStatus },
            success: function (response) {
                console.log(response);


                $('#statusstatus').text(newStatus);

            },
            error: function (error) {
                console.error(error);
                // 실패한 경우에 대한 처리를 여기에 추가할 수 있습니다.
            }
        });
    }

    // 팝업 창 닫기
    closePopup('settings-popup');
}

function updateImage() {
    var formData = new FormData();
    var imageInput = $('#image-input')[0].files[0];

    // 이미지 파일을 선택한 경우에만 업데이트 요청을 보냅니다.
    if (imageInput) {
        formData.append('image', imageInput);
        var randomParam = Math.random();
        // AJAX를 사용하여 백엔드에 프로필 이미지 업데이트 요청을 보냅니다.
        $.ajax({
            type: 'POST',
            url: '/update_image?rand=' + randomParam,// url: '/update_image',
            data: formData,
            contentType: false,
            processData: false,
            success: function (response) {
                $('#profile-image').attr('src', '').attr('src', "http://127.0.0.1:8000/" + response.message + "?rand=" + randomParam);
                // $('#profile-image').attr('src', '').attr('src', "http://127.0.0.1:8000/" + response.message);
                
            },
            error: function (error) {
                console.error(error);
                // 실패한 경우에 대한 처리를 여기에 추가할 수 있습니다.
            }
        });
    }

    // 팝업 창 닫기
    closePopup('settings-popup');
}

function closePopup(popupId) {
    $('#' + popupId).hide();
}

