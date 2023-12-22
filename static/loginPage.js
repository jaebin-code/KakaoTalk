$(document).ready(function () {
        $("#btn_submit").click(function(event){
            var username = $("#username").val();
            var password = $("#password").val();

            var data = { "username":username,"password":password};
            console.log(data);
            $.ajax({
                url: "/token",
                type: "post",
                data: data,
                success: function(data, txtStatus, xhr){
                    window.location = "/friendPage";
                },
                error: function(e){
                    alert("Login fail")
                }
            })
        })
});