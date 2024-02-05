function download1() {

    result = confirm('해당 파일을 다운로드하시겠습니까?');
    let filename = $('#filename').val();
    let wav_filename = $('#wav_filename').val();
    let filepath_date = $('#filepath_date').val();

    if(result) {
        if(wav_filename == 'None') {
            $('#media').attr('href', '/media/' + filepath_date + '/' + filename);
        } else {
            $('#media').attr('href', '/media/' + filepath_date + '/' + wav_filename);
        }

        location.reload();
    } else {
        return;
    }
}

//여기서부터 삭제요청 부분

$('.btnradio3').click(function() {
    $('.deleteDetail').css('display', 'block');
}); // end $('.btnradio3').click

$('.btnradio1, .btnradio2').click(function() {
    $('.deleteDetail').css('display', 'none');
}); // end $('.btnradio1, 2').click

function test(e) {
    if(e.value.length >= e.maxLength) {
        alert("최대 입력 크기를 초과하였습니다.");
        e.value = e.value.slice(0, -1);
    }
}

$('.close').click(function() {
    $("input:radio[name='btnradio']:radio[value='동의철회']").prop('checked', true);
    $('.deleteDetail').css('display', 'none');
    $('#deleteReason').val('');
}); // end $('.close').click


$('#deleteSubmit').click(function() {

    let num = $('#num').val();
    let reason = $('input[name="btnradio"]:checked').val();
    let reason2;

    if(reason == '기타') {
        reason2 = $('#deleteReason').val().trim();

        if(reason2 != '') {
            reason = reason2;
        }
    }

    result = confirm('해당 파일을 삭제 요청하시겠습니까?');
    if(!result) {
        return;
    }


    let countperpage = $("#hidden_countperpage").val();
    let department = $("#hidden_department").val();
    let startdate = $("#hidden_startdate").val();
    let enddate = $("#hidden_enddate").val();
    let pagenum = $("#hidden_pagenum").val();
    let condition = $("#hidden_condition").val();
    let pstatus = $("#hidden_pstatus").val();
    let patientnum = $("#hidden_patientnum").val();
    let order = $("#hidden_order").val();

    $.ajax({
      url: "/file/delete",
      data: {
        num: num,
        reason: reason
      },
      method: "POST",
      success: function(data) {
        console.log("성공");

        if(data == 'fail') {
            alert("확인요청 중인 파일은 삭제가 불가능합니다.");
            $('#reason').modal('hide');
            $("#btnradio1").prop("checked", true);
            return;
        }

        alert("삭제요청이 완료되었습니다.");
        location.replace('/list/' + countperpage + '/' + pagenum + '/' + department + '/' + startdate + '/' + enddate + '/' + condition + '/' + pstatus + '/' + patientnum + '/' + order);
      },
      error: function(request, status, error) {
        console.log("에러: ", error);
        alert("잘못된 요청입니다.");
      },
      complete: function() {
        console.log("완료");
      }
    }); //end ajax

}); // end $('#delete').click


$('#delete_cancel').click(function() {

    result = confirm('삭제요청을 취소하시겠습니까?');
    if(!result) {
        return;
    }

    let num = $('#num').val();

    let countperpage = $("#hidden_countperpage").val();
    let department = $("#hidden_department").val();
    let startdate = $("#hidden_startdate").val();
    let enddate = $("#hidden_enddate").val();
    let pagenum = $("#hidden_pagenum").val();
    let condition = $("#hidden_condition").val();
    let pstatus = $("#hidden_pstatus").val();
    let order = $("#hidden_order").val();

    $.ajax({
      url: "/file/cancel",
      data: {
        num: num
      },
      method: "POST",
      success: function(data) {
        //console.log("성공");
        if(data.message == 'fail') {
            alert(data.patient_id + '번 환자 정보가 삭제 요청 중이어서 해당 글은 삭제 요청 취소가 불가능합니다.');
            return;
        }
        alert("삭제요청이 취소되었습니다.");
        //location.replace('/list/' + countperpage + '/' + pagenum + '/' + department + '/' + startdate + '/' + enddate + '/' + condition + '/' + pstatus);
        location.reload();
      },
      error: function(request, status, error) {
        //console.log("에러: ", error);
        alert("잘못된 요청입니다.");
      },
      complete: function() {
        //console.log("완료");
      }
    }); //end ajax

}); // end $('#delete_cancel').click


//여기서부터 녹취정보수정 파트
$("#patientInfoModal").on("shown.bs.modal", function (e) {
    var loadurl = $(e.relatedTarget).data('load-url');
    $(this).find('.modal-body').load(loadurl);
});

$('#department').change(function() {
    let value = $(this).val();
    $.ajax({
        url: "/doctor",
        method: "POST",
        data: {
            value : value
        },
        dataType : "json",
        success: function(data) {
            let strAdd = '';
            if(data.list.length == 0) {
                $('#doctor').html(strAdd);
                return;
            }
            for(var i=0; i<data.list.length; i++) {
                strAdd += '<option value="' + data.list[i].doctor_id +'">' + data.list[i].doctor_name +'</option>';
            }
            $('#doctor').html(strAdd);
        },
        error: function(request, status, error) {
        }
    }); //end ajax
});

$('#regNum').keyup(function(){
    $('#regDate').css('text-decoration', 'none');
    $('#regDate').siblings('label').addClass('text-primary');
    $('#regDate').siblings('label').removeClass('red');
    $('#patientNum').attr('hidden', true);
    $("#regDate").val('');
    $("#patientNum").val('');
    $("#name").val('');
    $("#age").val('');

    var inputLength = $(this).val().length; //입력한 값의 글자수
    var reg_id = $('#regNum').val();

    if(inputLength == 8) { //8자리숫자를 입력했을 경우
        $.ajax({
            url: "/patient/check",
            method: "POST",
            dataType : "json",
            data: JSON.stringify(reg_id),
            success: function(data) {
                //console.log("성공");
                if(data.is_rejected == 'Y') {
                    alert('🚨 녹취 거부 대상자입니다.');
                    $('#name').val(data.patient_name);
                    $('#age').val(data.patient_age);
                    $('#gender').val(data.patient_gender);
                    $('#regDate').siblings('label').addClass('red');
                    $('#regDate').siblings('label').removeClass('text-primary');
                    return;
                }

                if(data.is_rejected == 'N') {
                    $('#name').val(data.patient_name);
                    $('#gender').val(data.patient_gender);
                    $('#age').val(data.patient_age);
                    $('#regDate').val(data.registered_at);
                    return;
                }

                if(data.patient_id != null) { //db에 등록되어 있는 환자정보이면
                    $('#gender').val(data.patient_gender);
                    $('#age').val(data.patient_age);
                    $('#regDate').val(data.registered_at);
                    if(data.is_new == false) { //이미 등록된 환자
                        $('#patientNum').val(data.patient_id);
                        $('#patientNum').removeAttr('hidden');
                        if(data.is_deleted == 'Y') {
                            alert('🚨 동의서가 만료된 환자입니다.');
                            $('#regDate').css('text-decoration', 'line-through');
                            $('#regDate').siblings('label').addClass('red');
                            $('#regDate').siblings('label').removeClass('text-primary');
                        }
                    } else { //처음 등록하는 환자
                        $('#patientNum').val(data.patient_id);
                        $('#patientNum').attr('hidden', true);
                    }
                    $('#name').val(data.patient_name);
                    $('#regDate').attr('disabled', true);
                    $('#patientNum').attr('disabled', true);
                } else { //db에 등록되어 있지 않은 환자정보이면
                    $('#regDate').val(data.registered_at);
                    $('#patientNum').val(data.patient_id);
                }
                if(data.list == null || data.list.length == 0) {
                    return;
                }
            },
            error: function(request, status, error) {
                //console.log("에러: ", error);
                alert("잘못된 요청입니다. 다시 시도해 주세요.");
            }
        }); //end ajax

    } else { //8자리숫자를 입력하지 않았을 경우
    }
});


//환자번호 입력하는 input창에 오로지 숫자만 입력되도록
{document.addEventListener("input", onlyNumber, true); //onlyNumber은 함수 이름
    function onlyNumber(evt) {
        const origin = evt.target;
        if(origin.id === "regNum" || origin.id === 'age') { //class이름이 patientId이면.. 숫자만 입력받도록
            origin.value = origin.value
            .replace(/[^0-9]$/i, "");
        }
    }
}


$('#patientModBtn').click(function() {

    let regNum = $('#regNum').val();
    let name = $('#name').val().trim();
    let age = $('#age').val();
    let gender = $('#gender').val();

    if($('#regDate').siblings('label').hasClass('red')) {
        alert('🚨 녹취가 불가한 환자입니다.');
        return;
    }

    var inputLength = regNum.length;
    if(inputLength < 8) {
        alert('등록번호를 기입하여 주세요.');
        return;
    }
    if(name == '') {
        alert('성명을 입력하여 주세요.');
        return;
    } else if(age == '') {
        alert('연령을 입력하여 주세요.');
        return;
    } else if(gender == '') {
        alert('성별을 선택하여 주세요.');
        return;
    }

    var result = confirm("정말 변경하시겠습니까?");
    if(!result){
        return;
    }

    /*
    let patient_id = $('#patient_id').val();
    let number_of_people = $('#number_of_people').val();
    let new_patient_id = $('#patientId').val();
    let count = $('#count').val();
    let type = '';
    */

    let count = $('#count').val();
    let department = $('#department').val();
    let doctor = $('#doctor').val();

    let oldRegNum = $('#oldRegNum').val();
    let oldName = $('#oldName').val();
    let oldAge = $('#oldAge').val();
    let oldGender = $('#oldGender').val();
    let oldCount = $('#oldCount').val();
    let oldDepartment = $('#oldDepartment').val();
    let oldDoctor = $('#oldDoctor').val();

    let regNumArea = true;
    let patientArea = true;
    let recordArea = true;

    if(regNum == oldRegNum) {
        regNumArea = false; //변경사항없음
    }
    if(name == oldName && age == oldAge && gender == oldGender) {
        patientArea = false; //변경사항없음
    }
    if(count == oldCount && department == oldDepartment && doctor == oldDoctor) {
        recordArea = false; //변경사항없음
    }

    if(regNumArea == false && patientArea == false && recordArea == false) {
        alert('변경사항이 없습니다.');
        $('#patientInfoModal').modal('hide');
        return;
    }

    let num = $('#num').val();
    let isNew = false;
    if($('#patientNum').is(':hidden')) { //새로운환자등록인지 여부
        console.log('환자번호가 숨겨짐');
        isNew = true;
    }

    console.log('is_new: ', isNew);

    $.ajax({
        url: "/detail/modPatientInfo/" + num,
        method: "POST",
        dataType : "text",
        data: {
            regNumArea : regNumArea,
            patientArea : patientArea,
            recordArea : recordArea,
            isNew : isNew,
            regNum : regNum,
            name : name,
            age: age,
            gender: gender,
            count: count,
            department: department,
            doctor: doctor
        },
        success: function(data) {
            //console.log("성공");
            alert('환자정보 변경이 완료되었습니다.');
            location.reload();
            //$('#patientInfoModal').modal('hide');
        },
        error: function(request, status, error) {
            //console.log("에러: ", error);
            alert("잘못된 요청입니다. 다시 시도해 주세요.");
        }
    }); //end ajax


}); // end $('#patientModBtn').click


/*
//녹취인수정(여기서부터하기)
$('#department').change(function() {
    if($(this).val() == '') {
        $('#id').addClass('inactive');
        return;
    }

    let d_code = $('#department').val();

    $.ajax({
        url: "/detail/getUserDept",
        method: "POST",
        data: {
            d_code: d_code
        },
        success: function(data) {
            //console.log("성공");
            console.log(data);
            let strAdd = '';
            strAdd += '<option value="">녹취인 ID</option>';
            if(data.list.length > 0) {
                for(var i = 0; i < data.list.length; i++) {
                    strAdd += '<option>' + data.list[i].user_id + '</option>';
                }
            }
            $('#id').html(strAdd);
            $('#id').removeClass('inactive');

        },
        error: function(request, status, error) {
            //console.log("에러: ", error);
            alert("잘못된 요청입니다. 다시 시도해 주세요.");
        }
    }); //end ajax

});
*/

$('#recordModBtn').click(function() {

    let userId = $('#userId').val();

    if(userId == '') {
        alert('변경하실 녹취인 ID를 선택하여 주세요.');
        return;
    }

    var result = confirm("정말 변경하시겠습니까?");
    if(!result){
        return;
    }

    //기존 녹취인과 바뀌는 녹취인이 동일하면 url타고 안넘어가게 검증해야함..
    let audio_user_id = $('#audio_user_id').val();
    if(userId == audio_user_id) { //녹취인을 변경하지 않았다면
        //alert('변경사항이 없습니다.');
        $('#recordInfoModal').modal('hide');
        return;
    }

    let num = $('#num').val();
    $.ajax({
        url: "/detail/modRecordInfo",
        method: "POST",
        data: {
            num: num,
            id : userId
        },
        success: function(data) {
            //console.log("성공");
            alert('녹취인 변경이 완료되었습니다.');
            location.reload();
        },
        error: function(request, status, error) {
            //console.log("에러: ", error);
            alert("잘못된 요청입니다. 다시 시도해 주세요.");
        }
    }); //end ajax


}); // end $('#recordModBtn').click



$("#recordInfoModal").on("hidden.bs.modal", function () {
    $("#department option:eq(0)").prop("selected", true);
    $("#id").addClass('inactive');
});


