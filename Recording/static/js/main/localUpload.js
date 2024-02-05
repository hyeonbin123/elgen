//환자번호 입력하는 input창에 오로지 숫자만 입력되도록
{document.addEventListener("input", onlyNumber, true); //onlyNumber은 함수 이름
    function onlyNumber(evt) {
        const origin = evt.target;
        if(origin.className === "patientId" || origin.id === "regNum" || origin.id === 'age' || origin.id == "regNum2" || origin.id == "age2") { //class이름이 patientId이면.. 숫자만 입력받도록
            origin.value = origin.value
            .replace(/[^0-9]$/i, "");
        }
    }
}

$('#regNum').keyup(function(){
    $('#regDate').css('text-decoration', 'none');
    $('#regDate').siblings('label').addClass('text-primary');
    $('#regDate').siblings('label').removeClass('red');

    $("#gender option:eq(0)").prop("selected", true);
    $("#count option:eq(0)").prop("selected", true);
    $('#patientNum').attr('hidden', true);
    $("#regDate").val('');
    $("#patientNum").val('');
    $("#name").val('');
    $("#age").val('');
    $('#rejectCancelBtn').addClass('d-none');

    $('#upload_local_btn').attr('disabled', false);
    $('#tableArea').html('');

    var inputLength = $(this).val().length; //입력한 값의 글자수
    var reg_id = $('#regNum').val();

    /*
    if(inputLength < 5) {
        $(this).siblings('#keyupTxt').text('환자번호(다섯자리수)를 입력하여 주세요.');
    } else {
        $(this).siblings('#keyupTxt').text('🧡');
    }

    if($('#txt').text() =='🧡' && $('#keyupTxt').text() =='🧡') {
        $("#txt2").text('녹음 버튼을 눌러주세요.');
    } else {
        $("#txt2").text('');
    }
    */
    if (inputLength == 8) { // 8자리 숫자를 입력했을 경우
    $.ajax({
        url: "/patient/check",
        method: "POST",
        dataType: "json",
        data: JSON.stringify(reg_id),
        success: function(data) {
            // 필터링 함수를 정의하여 is_deleted가 'Y'인 데이터를 필터링
            function filterDeleted(data) {
                return data.filter(function(patient) {
                    return patient.is_deleted !== 'Y';
                });
            }

            if (data.is_rejected == 'Y') {
                alert('🚨 녹취 거부 대상자입니다.');
                $('#name').val(data.patient_name);
                $('#age').val(data.patient_age);
                $('#gender').val(data.patient_gender);
                $('#regDate').siblings('label').addClass('red');
                $('#regDate').siblings('label').removeClass('text-primary');
                $('#rejectCancelBtn').removeClass('d-none');
                return;
            }

            if (data.patient_id != null) { // db에 등록되어 있는 환자 정보이면
                var filteredData = filterDeleted(data); // 필터링 수행

                if (filteredData.length > 0) {
                    var patient = filteredData[0]; // 첫 번째 환자 정보 사용
                    $('#name').val(patient.patient_name);
                    $('#gender').val(patient.patient_gender);
                    $('#age').val(patient.patient_age);
                    $('#regDate').val(patient.registered_at);

                    if (patient.is_new == false) { // 이미 등록된 환자
                        $('#patientNum').val(patient.patient_id);
                        $('#patientNum').removeAttr('hidden');
                        $('#regDate').attr('disabled', true);
                        $('#patientNum').attr('disabled', true);
                    } else { // 처음 등록하는 환자
                        $('#patientNum').val(patient.patient_id);
                        $('#patientNum').attr('hidden', true);
                    }

                    $('#regDate').attr('disabled', true);
                }
            } else { // db에 등록되어 있지 않은 환자 정보이면
                $('#regDate').val(data.registered_at);
                $('#patientNum').val(data.patient_id);
                $('#upload_local_btn').attr('disabled', true);
            }

            if (data.list == null || data.list.length == 0) {
                return;
            }
        }
    });
}

                //환자의 녹취 이력 조회
                let strAdd = '';
                strAdd += '<table class="table table-sm table-bordered text-nowrap" width="100%" cellspacing="0">';
                    strAdd += '<div class="mb-3">연구번호 <b class="text-primary">' + data.patient_id +'</b>님의 녹취파일개수:<b class="left-spacing-8 text-primary">' + data.list.length +'</b>개</div>';
                    strAdd += '<thead class="table-primary">';
                        strAdd += '<tr>';
                            strAdd += '<th></th>';
                            strAdd += '<th>부서</th>';
                            strAdd += '<th>DB저장시각</th>';
                        strAdd += '</tr>';
                    strAdd += '</thead>';
                    strAdd += '<tbody>';
                    for(var i=0; i<data.list.length; i++) {
                        strAdd += '<tr>';
                            strAdd += '<td>' + (i+1) +'</td>';
                            strAdd += '<td>' + data.list[i].department +'</td>';
                            strAdd += '<td>' + data.list[i].date +'</td>';
                        strAdd += '</tr>';
                    }
                    strAdd += '</tbody>';
                strAdd += '</table>';

                $('#tableArea').html(strAdd);

            },
            error: function(request, status, error) {
                //console.log("에러: ", error);
                alert("잘못된 요청입니다. 다시 시도해 주세요.");
            }
        }); //end ajax

    } else { //8자리숫자를 입력하지 않았을 경우
    }

});



$("#fileUpload").off().on("change", function(){ //업로드하는 파일 용량 체크
    var files = Array.from(this.files);
    var file;
    var maxSize = 100 * 1024 * 1024;
    var fileSize;
    var totalFileSize = 0;

    for (var i = 0; i < files.length; i++) {
        fileSize = files[i].size;
        totalFileSize = totalFileSize + fileSize;
    }

     if(totalFileSize > maxSize){
        alert("첨부파일 사이즈는 100MB 이내로 등록 가능합니다.");
        $(this).val('');
        return false;
     }
});


function get_name(tempFileName) {

    let arr = [];
    let filename = tempFileName.split('_');

    var style1 = /^[0-9]{5}$/;
    var style2 = /^[0-9]{1}$/;

    let length = filename.length;

    if(length != 5) {
        return arr; //빈 array를 반환 (즉 arr의 length는 0)
    }

    let count = filename[4].split('.')[0];

    if(style1.test(filename[3]) && style2.test(count)) {
        //alert("숫자지롱");
    } else if(count == 10) {
        //alert("숫자지롱");
    } else {
        return arr; //빈 array를 반환
    }

    let patient_id = filename[length-2];
    //let count = filename[length-1].charAt(0, -1);
    console.log('count: ', count);
    let rfilename = filename[0] + '_' + filename[1] + '_' + filename[2] + '.wav';

    arr.push(patient_id, count, rfilename);

    return arr;
}

function patient_check(i, patientId) {
    $.ajax({
        url: "/patient/check",
        method: "POST",
        dataType : "json",
        data: JSON.stringify(patientId),
        success: function(data) {
            //console.log("성공");
            if(data.patient_gender == '' || data.patient_gender == null || data.patient_age == '' || data.patient_age == null) {
                $('#uploadGender' + i).siblings('.infoTxt').text('환자정보등록');
                $('#uploadGender' + i).val('');
                $('#uploadAge' + i).val('');
                $('#uploadGender' + i).removeAttr('disabled');
                $('#uploadAge' + i).removeAttr('disabled');
            } else {
                $('#uploadGender' + i).val(data.patient_gender);
                $('#uploadAge' + i).val(data.patient_age);
                $('#patient_gender' + i).val(data.patient_gender);
                $('#patient_age' + i).val(data.patient_age);
            }
        },
        error: function(request, status, error) {
            //console.log("에러: ", error);
            alert("잘못된 요청입니다. 다시 시도해 주세요.");
        }
    }); //end ajax
}

$("#fileUpload").on("change", function(e) {
    $("#fileList").text('');

    //파일 업로드 input창에 파일을 선택하면 몇 개의 파일을 선택했는지 보여줌
    var files = Array.from(this.files);
    var filename = '파일 ' + files.length + '개';
    $("#userfile").val(filename);

    var file;
    for (var i = 0; i < files.length; i++) {
        file = files[i];
        arr = get_name(file.name);
        if(arr.length == 0) {
            localupload2(i, file.name);
        } else {
            localupload1(i, file.name);
        }
    }
});

function localupload1(i, filename) {
    $("#fileList").append('<div id=fileList' + i + ' class="patientArea2"><div id=fileName' + i + ' class="fileName">' + filename + '<span id=status' + i + ' class="waiting" style="font-size: 13px; color: red;">😄</span></div><div id=patientArea' + i + '></div></div>');
    $("#patientArea" + i).append($(".patientArea").html()); //#patientArea1,2,,,에 .patientArea의 html코드를 append함.

    $("#patientId").attr('id', 'uploadPatientId' + i); //patientId를 uploadPatientId0, uploadPatientId1 이런식으로 바꿈.
    $("#uploadPatientId" + i).val(arr[0]);
    patient_check(i, arr[0]);
    $("#uploadPatientId" + i).attr('disabled', true);

    $('#gender').attr('class', arr[0] + 'Gender');
    $("#gender").attr('id', 'uploadGender' + i);
    $('#uploadGender' + i).attr('disabled', true);

    $('#patient_gender').attr('class', arr[0] + 'Gender');
    $("#patient_gender").attr('id', 'patient_gender' + i);

    $("#age").attr('class', arr[0] + 'Age');
    $("#age").attr('id', 'uploadAge' + i);
    $('#uploadAge' + i).attr('disabled', true);

    $("#patient_age").attr('class', arr[0] + 'Age');
    $("#patient_age").attr('id', 'patient_age' + i);

    $("#count").attr('id', 'uploadCount' + i);
    $('#uploadCount' + i).val(arr[1]);
    $('#uploadCount' + i).attr('disabled', true);

    $("#keyupTxt").remove();
    $("#infoTxt").text('환자정보수정');
    $("#infoTxt").attr('id', 'uploadInfoTxt' + i);
    $("#infoTxt2").attr('id', 'cancelInfoTxt' + i);
    $("#txt").remove();
    $("#txt2").remove();
}

function localupload2(i, filename) {
    console.log('여기들어옴: ', i, ' *** ', filename);
    $("#fileList").append('<div id=fileList' + i + ' class="patientArea3"><div id=fileName' + i + ' class="fileName">' + filename + '<span id=status' + i + ' class="waiting" style="font-size: 13px; color: red;">😊</span></div><div id=patientArea' + i + '></div></div>');
    $("#patientArea" + i).append($(".patientArea").html());

    $("#patientId").attr('id', 'uploadPatientId' + i);
    $("#gender").attr('id', 'uploadGender' + i);
    $('#uploadGender' + i).attr('disabled', true);

    $("#patient_gender").attr('id', 'patient_gender' + i);
    $("#patient_age").attr('id', 'patient_age' + i);

    $("#age").attr('id', 'uploadAge' + i);
    $('#uploadAge' + i).attr('disabled', true);

    $("#count").attr('id', 'uploadCount' + i);
    $('#uploadCount' + i).val('');
    $('#localCount' + i).attr('disabled', true);

    $("#keyupTxt").text('환자번호(다섯자리수)를 입력하여 주세요.');
    $("#keyupTxt").attr('id', 'uploadKeyupTxt' + i);

    $("#infoTxt").text('');
    $("#infoTxt").attr('class', 'infoTxt label orange local');
    $("#infoTxt").attr('id', 'uploadInfoTxt' + i);

    $("#infoTxt2").text('');
    $("#infoTxt2").attr('class', 'infoTxt2 cancelInfoTxt');
    $("#infoTxt2").attr('id', 'cancelInfoTxt' + i);

    $("#txt").text('');
    $("#txt").attr('id', 'uploadTxt' + i);

    $("#txt2").remove();
}


$('#upload_btn').click(function(e) {
    if($("#fileUpload").val() == '') {
        alert('파일을 선택해 주세요.');
        return;
    }

    if($("[id^='uploadInfoTxt']").text().includes('환자정보등록')) {
        alert('환자정보 등록을 완료하여 주세요.');
        return;
    } else if($("[id^='uploadInfoTxt']").text().includes('수정하기')) {
        alert('환자정보 수정을 완료하여 주세요.');
        return;
    } else if($("[id^='uploadKeyupTxt']").text().includes('환자번호(다섯자리수)를 입력하여 주세요.')) {
        alert('녹취정보를 기입해 주세요.');
        return;
    } else if($("[id^='uploadTxt']").text().includes('총녹취인원을 선택해 주세요.')) {
        alert('녹취정보를 기입해 주세요.');
        return;
    }

    var fileUploadInput = document.getElementById('fileUpload');

    $('#close_btn').attr('disabled', 'disabled');
    //$('#btn-close').attr('disabled', 'disabled');
    $('#upload_btn').attr('disabled', 'disabled');
    $('#fileUpload').attr('disabled', 'disabled');
    $("[id^='uploadInfoTxt']").text('');

    var ins = fileUploadInput.files.length;
    var fd = new FormData();
    for (var x = 0; x < ins; x++) {
        fd.append("fileUpload[]", document.getElementById('fileUpload').files[x]);
        //console.log('뭘까: ', document.getElementById('fileUpload').files[x]);

        let filename = document.getElementById('fileUpload').files[x].name;
        let patient_id = $('#uploadPatientId' + x).val();
        let count = $('#uploadCount' + x).val();

        new_arr = []
        new_arr.push(filename, patient_id, count);
        //console.log('new_arr: ', new_arr);
        fd.append("arr[]", new_arr);
    }

    $('#uploadMessage').removeClass('hidden');
    $('#uploadMessage').html("<b>업로드 완료</b> 메시지가 뜰 때까지 잠시만 기다려주세요<b style=color:red;>(창을 닫지 마세요)</b>.");

    $.ajax({
        url: "/file/upload",
        method: "POST",
        data: fd,
        processData: false,
        contentType: false,
        success: function(data) {
            console.log("성공");
            let message = audioFileInfo(data.audio_file_info);
            alert(message);
        },
        error: function(request, status, error) {
            console.log("에러: ", error);
            alert("잘못된 요청입니다. 다시 시도해 주세요.");
        },
        complete: function() {
            console.log("완료");
            $('#localFileUploadModal').modal('hide');
            $("#fileUpload").val('');
            $("#fileList").text('');
            $('#close_btn').removeAttr('disabled');
            //$('#btn-close').removeAttr('disabled');
            $('#upload_btn').removeAttr('disabled');
            $('#fileUpload').removeAttr('disabled');
            $('#uploadMessage').text('');
            $("#userfile").val('');
        }
    }); //end ajax

});

function audioFileInfo(infos) {
    let success_arr = [];
    let fail_arr = [];
    let message;

    for (var i = 0; i < infos.length; i++) {
        info = infos[i];
        if(info[3] == 'Y') {
            fail_arr.push(info[0]);
        } else {
            success_arr.push(info[0]);
        }
    }

    if(success_arr.length == infos.length) {
        message = '업로드가 완료되었습니다.';
    } else {
        if(success_arr.length == 0) {
            message = '등록하시려는 파일과 동일한 파일명이 이미 존재하여 업로드에 실패하였습니다.';
        } else {
            message = '<😆업로드 성공파일>\n' + success_arr +'\n\n<😭업로드 실패파일>\n' + fail_arr + '\n(동일한 파일명이 이미 존재하여 업로드에 실패하였습니다)';
        }
    }

    return message;

}


$('#close_btn').click(function() {
    $("#fileUpload").val('');
    $("#fileList").text('');
    $("#userfile").val('');
});


$('.btn-close').click(function() {
    $("#fileUpload").val('');
    $("#fileList").text('');
    $("#userfile").val('');
});



//여기서부터는 로컬파일 업로드 부분에서 동적으로 생성된 태그에 이벤트 건 내용

//1. id가 patientId0인 태그에서 keyup이벤트
$(document).on({
    keyup: function (e) {
        //console.log(e.target.id);
        if(e.target.id.includes('uploadPatientId')) { //id가 uploadPatientId인 태그에서 keyup이벤트가 발생하면
            let patientId = document.getElementById(e.target.id);
            let keyupTxt = patientId.nextElementSibling;
            //console.log('keyupTxt: ', keyupTxt.innerText);

            let patient02 = patientId.parentNode.nextElementSibling.childNodes;
            let patient03 = patientId.parentNode.nextElementSibling.nextElementSibling.childNodes;

            let patient_gender = patientId.parentNode.parentNode.childNodes[1];
            let patient_age = patientId.parentNode.parentNode.childNodes[3];

            let gender = patient02[1]; //value
            let age = patient02[3];
            let infoTxt = patient02[5]; //innerText
            let infoTxt2 = patient02[7];
            let count = patient03[1];
            let txt = patient03[3];
            let txt2 = patient03[5];

            infoTxt2.innerText = '';
            txt.innerText = '';
            //$("#count option:eq(0)").prop("selected", true);
            count.querySelectorAll('option')[0].selected = 'selected'
            gender.disabled = true;
            age.disabled = true;
            count.disabled = true;

            gender.removeAttribute("class");
            age.removeAttribute("class");

            patient_gender.removeAttribute("class");
            patient_age.removeAttribute("class");

            var inputLength = e.target.value.length; //입력한 값의 글자수
            var patient_id = e.target.value;

            if(inputLength < 5) {
                keyupTxt.innerText = '환자번호(다섯자리수)를 입력하여 주세요.';
            } else {
                keyupTxt.innerText = '🧡';
            }

            if(txt.innerText =='🧡' && keyupTxt.innerText =='🧡') {
                txt2.innerText = '업로드 버튼을 눌러주세요.';
            } else {
                txt2.innerText = '';
            }


            if(keyupTxt.innerText =='🧡') { //텍스트가 하트일 경우(즉 다섯자리숫자를 입력했을 경우)

                $.ajax({
                    url: "/patient/check",
                    method: "POST",
                    dataType : "json",
                    data: JSON.stringify(patient_id),
                    success: function(data) {
                        console.log("성공");
                        gender.value = data.patient_gender;
                        age.value = data.patient_age;

                        if(data.patient_gender != null && data.patient_age != null) { //db에 등록되어 있는 환자정보이면
                            infoTxt.innerText = '환자정보수정';
                            txt.innerText = '총녹취인원을 선택해 주세요.';

                            gender.disabled = true;
                            age.disabled = true;

                            patient_gender.value = data.patient_gender;
                            patient_age.value = data.patient_age;

                            gender.className = patientId.value + 'Gender';
                            age.className = patientId.value + 'Age';

                            patient_gender.className = patientId.value + 'Gender';
                            patient_age.className = patientId.value + 'Age';
                        } else { //db에 등록되어 있지 않은 환자정보이면 (녹음버튼 누르면 환자정보가 등록됨)
                            infoTxt.innerText = '환자정보등록';

                            gender.disabled = false;
                            age.disabled = false;
                            gender.options[0].selected = true;
                            age.options[0].selected = true;
                            txt.innerText = '성별, 연령, 총녹취인원을 선택해 주세요.';
                        }

                        count.disabled = false;

                    },
                    error: function(request, status, error) {
                        console.log("에러: ", error);
                        alert("잘못된 요청입니다. 다시 시도해 주세요.");
                    }
                }); //end ajax

            } else { //텍스트가 하트가 아닐경우(즉 다섯자리숫자를 입력하지 않았을 경우)
                gender.options[0].selected = true;
                age.options[0].selected = true;
                infoTxt.innerText = '';
            } // if(keyupTxt.innerText =='🧡') 끝


        } // if(e.target.id.includes('uploadPatientId')) 끝
    } //keyup이벤트 끝
}); // $(document).on 끝



//2. id가 uploadInfoTxt가 포함된 태그에서 click이벤트
$(document).on({
    click: function (e) {
        if(e.target.id.includes('uploadInfoTxt')) { //!!!id가 uploadInfoTxt가 포함된 태그 클릭!!!
            let patient01 = e.target.parentNode.previousElementSibling.childNodes;
            let patientId = patient01[1];
            let keyupTxt = patient01[3];


            let patient02 = e.target.parentNode.childNodes;
            let gender = patient02[1];
            let age = patient02[3];
            let infoTxt = patient02[5];
            let infoTxt2 = patient02[7];

            let patient03 = e.target.parentNode.nextElementSibling.childNodes;
            let count = patient03[1];
            let txt = patient03[3];

            let patient_gender = e.target.parentNode.parentNode.childNodes[1];
            let patient_age = e.target.parentNode.parentNode.childNodes[3];

            let fileName = e.target.parentNode.parentNode.parentNode;

            if(e.target.innerText == '환자정보등록') { //1.infoTxt 값이 환자정보등록일 경우
                infoTxt.style.color = "orange";
                infoTxt2.innerText = '';

                if(gender.value == '' || age.value == '') {
                    alert('성별 또는 연령을 선택하여 주세요.');
                    return;
                }

                $.ajax({ //등록하기 요청
                    url: "/patient/regist",
                    method: "POST",
                    data: {
                        gender : gender.value,
                        age : age.value,
                        patient_id : patientId.value
                    },
                    success: function(data) {
                        console.log("성공");
                        alert('환자정보 등록이 완료되었습니다.');
                        if(count.value != '') {
                            txt.innerText = '🧡';
                        } else {
                            txt.innerText = '총녹취인원을 선택해 주세요.';
                        }
                        infoTxt.innerText = '환자정보수정';

                        if(fileName.className == 'patientArea2') {
                            patientId.disabled = true;
                        } else {
                            patientId.disabled = false;
                        }

                        gender.disabled = true;
                        age.disabled = true;

                        patient_gender.value = gender.value;
                        patient_age.value = age.value;
                    },
                    error: function(request, status, error) {
                        console.log("에러: ", error);
                        alert("잘못된 요청입니다. 다시 시도해 주세요.");
                    }
                }); //end ajax

            } else if(e.target.innerText == '환자정보수정') { //2.infoTxt 값이 환자정보수정일 경우
                patientId.disabled = true;
                gender.disabled = false;
                age.disabled = false;

                infoTxt.innerText = '수정하기';
                infoTxt.style.color = "#B9062F";
                infoTxt2.innerText = '수정취소';

                //if(txt.innerText == '🧡') {
                //    txt.innerText = '환자정보 수정을 완료하여 주세요(수정하기 또는 수정취소를 선택해 주세요).';
                //    txt2.innerText = '';
                //}

            } else if(e.target.innerText == '수정하기') { //3.infoTxt 값이 수정하기일 경우
                //if(gender.value != '' && age.value != '' && count.value != '') {
                //    txt.innerText = '🧡'
                //    txt2.innerText = '업로드 버튼을 눌러주세요.';
                //}

                if(gender.value == '' && age.value == '') {
                    alert('성별과 연령을 선택하여 주세요.');
                    return;
                } else if(gender.value == '') {
                    alert('성별을 선택하여 주세요.');
                    return;
                } else if(age.value == '') {
                    alert('연령을 선택하여 주세요.');
                    return;
                }

                if(patient_gender.value == gender.value && patient_age.value == age.value) { //수정된 내용이 없는데 수정하기 버튼 누를경우
                    //alert('수정된 내용이 없습니다.'); //굳이 alert창 안띄워도 될것같아서 주석처리.
                    //patientId.disabled = false;
                    gender.disabled = true;
                    age.disabled = true;

                    infoTxt.innerText = '환자정보수정';
                    infoTxt.style.color = "orange";
                    infoTxt2.innerText = '';

                    if(infoTxt.className == 'infoTxt label orange local') {
                        patientId.disabled = false;
                    }
                    return;
                }

                $.ajax({ //수정하기 요청
                    url: "/patient/update",
                    method: "POST",
                    data: {
                        gender : gender.value,
                        age : age.value,
                        patient_id : patientId.value
                    },
                    success: function(data) {
                        console.log("성공");
                        alert('환자정보 수정이 완료되었습니다.');

                        $('.' + patientId.value + 'Gender').val(gender.value);
                        $('.' + patientId.value + 'Age').val(age.value);

                        patient_gender.value = gender.value;
                        patient_age.value = age.value;

                        if($("#patientId").val() == patientId.value) {
                            $("#gender").val(gender.value);
                            $("#age").val(age.value);
                        }
                    },
                    error: function(request, status, error) {
                        console.log("에러: ", error);
                        alert("잘못된 요청입니다. 다시 시도해 주세요.");
                    }
                }); //end ajax

                infoTxt.innerText = '환자정보수정';
                infoTxt.style.color = "orange";
                infoTxt2.innerText = '';

                if(infoTxt.className == 'infoTxt label orange local') {
                    patientId.disabled = false;
                }

                //patientId.disabled = false;
                gender.disabled = true;
                age.disabled = true;
            }
        } else if(e.target.id.includes('cancelInfoTxt')) { //id가 cancelInfoTxt가 포함된 태그 클릭(수정취소 클릭)
            let patient01 = e.target.parentNode.previousElementSibling.childNodes;
            let patientId = patient01[1];
            let keyupTxt = patient01[3];

            let patient02 = e.target.parentNode.childNodes;
            let gender = patient02[1];
            let age = patient02[3];
            let infoTxt = patient02[5];
            let infoTxt2 = patient02[7];

            let patient03 = e.target.parentNode.nextElementSibling.childNodes;
            let count = patient03[1];
            //let txt = patient03[3];
            //let txt2 = patient03[5];

            let patient_gender = e.target.parentNode.parentNode.childNodes[1];
            let patient_age = e.target.parentNode.parentNode.childNodes[3];

            //patientId.disabled = false;

            //if(gender.value != '' && age.value != '' && count.value != '') {
            //    txt.innerText = '🧡'
            //    txt2.innerText = '업로드 버튼을 눌러주세요.';
            //}

            if(patient_gender.value == gender.value && patient_age.value == age.value) { //수정된 내용이 없는 상태에서 수정취소 클릭하면
                gender.disabled = true;
                age.disabled = true;

                infoTxt.innerText = '환자정보수정';
                infoTxt.style.color = "orange";
                infoTxt2.innerText = '';

                if(infoTxt2.className == 'infoTxt2 cancelInfoTxt') {
                    patientId.disabled = false;
                }
                return;
            }

            $.ajax({ //수정된 내용이 있는 상태에서 수정취소 클릭하면
                url: "/patient/check",
                method: "POST",
                dataType : "json",
                data: JSON.stringify(patientId.value),
                success: function(data) {
                    console.log("성공");

                    gender.value = data.patient_gender;
                    age.value = data.patient_age

                    if(data.patient_gender != null && data.patient_age != null) { //db에 등록되어 있는 환자정보이면
                        gender.disabled = true;
                        age.disabled = true;
                    }

                },
                error: function(request, status, error) {
                    console.log("에러: ", error);
                    alert("잘못된 요청입니다. 다시 시도해 주세요.");

                    gender.disabled = true;
                    age.disabled = true;
                }
            }); //end ajax

            infoTxt.innerText = '환자정보수정';
            infoTxt.style.color = "orange";
            infoTxt2.innerText = '';

            if(infoTxt2.className == 'infoTxt2 cancelInfoTxt') {
                patientId.disabled = false;
            }

        } //if(e.target.id == 'infoTxt'),else if(e.target.id == 'infoTxt2') 끝
    } //click이벤트 끝
}); // $(document).on 끝


//3. id가 uploadGender, uploadAge, uploadCount인 태그에서 change이벤트
$(document).on({
    change: function (e) {
        if(e.target.id.includes('uploadGender') || e.target.id.includes('uploadAge') || e.target.id.includes('uploadCount')) {
            let patient01;
            let patient02;
            let patient03;
            if(e.target.id.includes('uploadGender') || e.target.id.includes('uploadAge')) {
                patient01 = e.target.parentNode.previousElementSibling.childNodes;
                patient02 = e.target.parentNode.childNodes;
                patient03 = e.target.parentNode.nextElementSibling.childNodes;
            } else { //e.target.id.includes('uploadCount')
                patient01 = e.target.parentNode.previousElementSibling.previousElementSibling.childNodes;
                patient02 = e.target.parentNode.previousElementSibling.childNodes;
                patient03 = e.target.parentNode.childNodes;
            }
            let patientId = patient01[1];
            let keyupTxt = patient01[3];

            let gender = patient02[1];
            let age = patient02[3];
            let infoTxt = patient02[5];
            let infoTxt2 = patient02[7];

            let count = patient03[1];
            let txt = patient03[3];
            //console.log('txt: ', txt);


            if(infoTxt.innerText == '환자정보등록' && gender.value != '' && age.value != '' && count.value != '') {
                txt.innerText = '환자정보 등록을 완료하여 주세요.';
            }

            if(infoTxt.innerText == '환자정보수정' && count.value == '') {
                txt.innerText = '총녹취인원을 선택해 주세요.';
            } else if(gender.value != '' && age.value != '' && count.value == '' && infoTxt.innerText == '수정하기') {
                txt.innerText = '총녹취인원을 선택해 주세요.';
            } else if(gender.value == '' || age.value == '' || count.value == '') {
                txt.innerText = '성별, 연령, 총녹취인원을 선택해 주세요.';
            } else if(gender.value != '' && age.value != '' && count.value != '' && infoTxt.innerText == '수정하기') {
                txt.innerText = '환자정보 수정을 완료하여 주세요(수정하기 또는 수정취소를 선택해 주세요).';
            } else if(gender.value != '' && age.value != '' && count.value != '' && infoTxt.innerText == '환자정보수정') {
                txt.innerText = '';
            } else if(gender.value != '' && age.value != '' && count.value != '' && infoTxt.innerText == '') {
                txt.innerText = '';
            }
        }//if(e.target.id.includes('uploadGender') || e.target.id.includes('uploadAge') || e.target.id.includes('uploadCount')) 끝
    } //change이벤트 끝

    //$('#upload_btn').attr('disabled', false);


}); // $(document).on 끝



//$("#fileUpload").on('change', function(){

//});



$('#regNum2').keyup(function(){

    var inputLength = $(this).val().length; //입력한 값의 글자수
    var reg_id = $('#regNum2').val();

    if(inputLength == 8) { //8자리숫자를 입력했을 경우
        $.ajax({
            url: "/patient/check2",
            method: "POST",
            dataType : "json",
            data: JSON.stringify(reg_id),
            success: function(data) {
                //console.log("성공");

                if(data.is_new == false && data.is_rejected == 'N') { //거부 취소 환자
                    $('#gender2').val(data.patient_gender);
                    $('#age2').val(data.patient_age);
                    $('#name2').val(data.patient_name);
                    $('#submitBtn').attr('disabled', false);
                    return;
                }

                if(data.is_new == false) { //이미 등록된 환자
                    if(data.is_rejected == null) {
                        alert('이미 동의서를 취득한 환자로 거부대상자가 될 수 없습니다.');
                    } else if(data.is_rejected == 'Y') {
                        alert('이미 거부 대상자로 등록된 환자입니다.');
                    }
                    $('#gender2').val(data.patient_gender);
                    $('#age2').val(data.patient_age);
                    $('#name2').val(data.patient_name);
                    $('#submitBtn').attr('disabled', true);
                    return;
                }

                //data.is_new == true
                $('#submitBtn').attr('disabled', false);

            },
            error: function(request, status, error) {
                //console.log("에러: ", error);
                alert("잘못된 요청입니다. 다시 시도해 주세요.");
            }
        }); //end ajax

    } else { //8자리숫자를 입력하지 않았을 경우
        $('#name2').val('');
        $('#age2').val('');
        $('#gender2').val('');
        $('#submitBtn').attr('disabled', true);
    }

});

$("#rejectModal").on('hide.bs.modal', function(){
    $('#regNum2').val('');
    $('#name2').val('');
    $('#age2').val('');
    $('#gender2').val('');
    $('#submitBtn').attr('disabled', true);
});

function rejectModalSubmit() {

    let regId = $('#regNum2').val();
    let name = $('#name2').val().trim();
    let age = $('#age2').val();
    let gender = $('#gender2').val();

    $.ajax({
        url: '/patient/regist2',
        method: "POST",
        data: {
            reg_id : regId,
            name: name,
            age: age,
            gender: gender
        },
        success: function(data) {
            alert('거부 환자 등록이 완료되었습니다.');
            $('#rejectModal').modal('hide');
        },
        error: function(request, status, error) {
            //console.log("에러: ", error);
            alert("잘못된 요청입니다. 다시 시도해 주세요.");
        }
    }); //end ajax
}



$('#expNum2').keyup(function(){

    var inputLength = $(this).val().length; //입력한 값의 글자수
    var reg_id = $('#expNum2').val();

    if(inputLength == 8) { //8자리숫자를 입력했을 경우
        $.ajax({
            url: "/patient/check2",
            method: "POST",
            dataType : "json",
            data: JSON.stringify(reg_id),
            success: function(data) {
                //console.log("성공");

                if(data.is_new == false && data.is_rejected == 'N') { //거부 취소 환자
                    $('#expgender2').val(data.patient_gender);
                    $('#expage2').val(data.patient_age);
                    $('#expname2').val(data.patient_name);
                    $('#expsubmitBtn').attr('disabled', false);
                    return;
                }

                if(data.is_new == false) { //이미 등록된 환자
                    if(data.is_rejected == null) {
                        alert('이미 동의서를 취득한 환자로 거부대상자가 될 수 없습니다.');
                    } else if(data.is_rejected == 'Y') {
                        alert('이미 거부 대상자로 등록된 환자입니다.');
                    }
                    $('#expgender2').val(data.patient_gender);
                    $('#expage2').val(data.patient_age);
                    $('#expname2').val(data.patient_name);
                    $('#expsubmitBtn').attr('disabled', true);
                    return;
                }

                //data.is_new == true
                $('#expsubmitBtn').attr('disabled', false);

            },
            error: function(request, status, error) {
                //console.log("에러: ", error);
                alert("잘못된 요청입니다. 다시 시도해 주세요.");
            }
        }); //end ajax

    } else { //8자리숫자를 입력하지 않았을 경우
        $('#expname2').val('');
        $('#expage2').val('');
        $('#expgender2').val('');
        $('#expsubmitBtn').attr('disabled', true);
    }

});


$("#expirationModal").on('hide.bs.modal', function(){
    $('#expNum2').val('');
    $('#expname2').val('');
    $('#expage2').val('');
    $('#expgender2').val('');
    $('#expsubmitBtncd com').attr('disabled', true);
});

function expirationModalSubmit() {

    let regId = $('#expNum2').val();
    let name = $('#expname2').val().trim();
    let age = $('#expage2').val();
    let gender = $('#expgender2').val();

    $.ajax({
        url: '/patient/expiration2',
        method: "POST",
        data: {
            reg_id : regId,
            name: name,
            age: age,
            gender: gender
        },
        success: function(data) {
            alert('dropout 환자 등록이 완료되었습니다.');
            $('#expirationModal').modal('hide');
        },
        error: function(request, status, error) {
            //console.log("에러: ", error);
            alert("잘못된 요청입니다. 다시 시도해 주세요.");
        }
    }); //end ajax
}