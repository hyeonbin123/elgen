//id입력
$('#id').keyup(function() {
    $('#idText').text('아이디를 입력해주세요(영문, 숫자만 가능).');
    $('#idInfo').text('한글은 입력되지 않으니 영문 키로 전환하여 주세요.');
});

//id input창에 영문,숫자만 입력가능하도록
{document.addEventListener("input", validation, true); //validation은 함수 이름
    function validation(evt) {
        const origin = evt.target;
        if(origin.id === "id") { //id이름이 id이면.. 영문,숫자만 입력받도록
            origin.value = origin.value
            .replace(/[^a-zA-Z0-9]+$/i, "");
        }
    }
}

//id중복확인
$('#confirmId').click(function() {
    let id = $('#id').val();
    if(id == '') {
        alert('아이디를 입력해주세요.');
        return;
    }

    $.ajax({
        url: "/check/user",
        method: "POST",
        data: {
            id: id
        },
        success: function(data) {
            //console.log("성공");
            if(data == 'success') {
                alert('사용할 수 있는 아이디입니다.');
                $('#idText').text('✔');
                $('#idInfo').text('');
            } else {
                alert('이미 존재하는 아이디입니다.');
            }
        },
        error: function(request, status, error) {
            //console.log("에러: ", error);
            alert("잘못된 요청입니다. 다시 시도해 주세요.");
        }
    }); //end ajax
});

//회사명을 충남대병원으로 선택하면 부서 선택창이 나오도록
$('#company').change(function() {
    var result = $('#company option:selected').val();
    if (result == '03') {
        $('#departmentArea').removeClass('inactive');
    } else {
        $('#departmentArea').addClass('inactive');
        $('#department option:eq(0)').prop('selected', 'selected');
    }
});

//비밀번호 입력
$('#password').keyup(function() {
    let pw = $('#password').val();
    let reg_pw1 = /^[a-z0-9`~!@#$%^&*()-_=+]{4,18}$/; // 단순 4~18자리

    $('#confirmPw').val('');
    $('#conPwText').text('비밀번호를 다시 한번 입력해주세요(4-18자리).');

    if(pw.length < 4) {
        $('#pwText').text('비밀번호를 입력해주세요(4-18자리).');
    } else if(!reg_pw1.test(pw)) {
        $('#pwText').text('비밀번호를 입력해주세요(4-18자리).');
    } else {
        $('#pwText').text('✔');
    }
});

//비밀번호 확인
$('#confirmPw').keyup(function() {
    let pwText = $('#pwText').text();

    if(pwText != '✔') {
        alert('비밀번호 입력을 완료해주세요.');
        $('#confirmPw').val('');
        return;
    }

    let pw = $('#password').val();
    let conPw = $(this).val();

    $.ajax({
        url: "/check/password",
        method: "POST",
        data: {
            pw: pw,
            conPw: conPw
        },
        success: function(data) {
            //console.log("성공");
            if(data == 'success') {
                $('#conPwText').text('✔');
            } else {
                $('#conPwText').text('비밀번호를 다시 한번 입력해주세요(4-18자리).');
            }
        },
        error: function(request, status, error) {
            //console.log("에러: ", error);
            alert("잘못된 요청입니다. 다시 시도해 주세요.");
        }
    }); //end ajax
});

//input창 최대타이핑 길이
$(document).on('keyup', '#id, #name, #password, #confirmPw', function(){
    let id_value = $('#id').val();
    let name_value = $('#name').val();
    let pw_value = $('#password').val();
    let conPw_value = $('#confirmPw').val();
    if (id_value.length > 20) { // 20자 부터는 타이핑 되지 않도록
        $('#id').val(id_value.substring(0, 20));
    } else if (name_value.length > 10) {
        $('#name').val(name_value.substring(0, 10));
    } else if (pw_value.length > 18) {
        $('#password').val(pw_value.substring(0, 18));
    } else if (conPw_value.length > 18) {
        $('#confirmPw').val(conPw_value.substring(0, 18));
    }
});

//회원가입
$('#complete').click(function() {
    let id = $('#id').val();
    let idText = $('#idText').text();
    let name = $('#name').val();
    let reg_name1 = /^[가-힣]+$/; // 한글만

    //유효성 검증
    if(id == '') {
        alert('아이디를 입력해주세요.');
        return;
    } else if(idText != '✔') {
        alert('아이디 중복확인을 완료해주세요.');
        return;
    } else if(name == '') {
        alert('이름을 입력해주세요.');
        return;
    } else if(!reg_name1.test(name)) {
        alert('이름은 한글만 입력 가능합니다.');
        return;
    } else if($("#company option:selected").text() == '선택') {
        alert('회사명을 선택해주세요.');
        return;
    } else if($("#company option:selected").val() == '03' && $("#department option:selected").text() == '선택') {
        alert('부서명을 선택해주세요.');
        return;
    } else if($('#pwText').text() != '✔') {
        alert('비밀번호 입력을 완료해주세요.');
        return;
    } else if($('#conPwText').text() != '✔') {
        alert('비밀번호 입력 확인을 완료해주세요.');
        return;
    }

    result = confirm('회원가입을 하시겠습니까?');
    if(!result) {
        return;
    }

    let c_code = $("#company option:selected").val();
    let d_code = $("#department option:selected").val();
    let password = $('#password').val();
    let user_type = $('input[name="userType"]:checked').val();

    $.ajax({
        url: "/join",
        method: "POST",
        data: {
            id: id,
            name: name,
            c_code: c_code,
            d_code: d_code,
            user_type: user_type,
            password: password
        },
        success: function(data) {
            console.log("성공");
            alert('회원가입이 완료되었습니다.');
            location.href = '/login';
        },
        error: function(request, status, error) {
            console.log("에러: ", error);
            alert("잘못된 요청입니다. 다시 시도해 주세요.");
        }
    }); //end ajax
});