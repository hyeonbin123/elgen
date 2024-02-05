$('#login').click(function () {
    let id = $('#id').val();
    let password = $('#password').val();

    if(id == '' || password == ''){
        alert("아이디 또는 비밀번호를 입력해주세요.");
        return;
    }

    $.ajax({
        url: "/login",
        data: {
            id: id,
            password: password
        },
        method: "POST",
        success: function(data) {
            //console.log("성공");
            alert("어서오세요😀");
            if(data == 'N' || data == 'Y') {
                location.replace('/');
            } else { //전사작업자(is_admin = 'T'인 사용자)는 메인이 아닌 리스트로 접속되도록
                location.replace('/list');
            }
        },
        error: function(request, status, error) {
            //console.log("에러: ", error);
            //console.log("request: ", request);
            //console.log("메시지: ", request.responseJSON.message) //request 객체 안에 있음.
            alert(request.responseJSON.message);
        },
        complete: function() {
            console.log("완료");
        }
    }); //end ajax
}); //end login

$("#password").keydown(function(key) {
    if(key.keyCode == 13){
        $('#login').click();
    }
});