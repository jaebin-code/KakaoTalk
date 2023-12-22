$(document).ready(function () {
    $("#btn_submit").click(function () {
        var id = $("#id").val();
        var password = $("#password").val();
        var username = $("#username").val();

        // 데이터를 서버로 전송
        $.ajax({
            type: "POST",
            url: "/register",  // 서버의 등록 엔드포인트 경로
            data: {
                "username": id,
                "password": password,
                "name": username
            },
            success: function (response) {
                alert(response);  // 서버로부터의 응답을 알림으로 표시 (실제로는 적절한 처리를 해야 함)
                window.location = "/";
            },
            error: function (error) {
                alert("Failed to make ID!");  // 오류 발생 시 알림
            }
        });
    });
});
