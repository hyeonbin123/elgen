$('#mainCheckbox').click(function() {
    if($('#mainCheckbox').is(':checked')) {
        $('input[name="checkbox"]').each(function(){ //checkbox 이름을 갖고 있는 체크박스를 반복 실행
            var disabled = $(this).prop("disabled"); //비활성화 여부 체크
            if(!disabled){ //비활성화가 아니라면
            $(this).prop('checked', true); //체크 실행
            }
        });
    }else {
        $('input:checkbox').prop("checked", false);
    }
});

$('input[name="checkbox"]').click(function() {
    var total = $('input[name="checkbox"]:not(:disabled)').length;
    var checked = $('input[name="checkbox"]:checked').length;

    if(total != checked) $("#mainCheckbox").prop("checked", false);
    else $("#mainCheckbox").prop("checked", true);
});

//$('.box').click(function() {
//    $("input:radio[name=language]:checked")[0].checked = false;
//});

$('input[name="box"]').click(function() {
    let thisBtn = $(this);
    let checkVal = $('input[name="box"]:checked').val();
    let condition = $('#hidden_condition').val();
    if(checkVal === condition) { //radio Button을 체크 해제할 경우
        thisBtn.prop('checked', false);
        $('.box').css('background', '#fff');

        let startdate = $("#startDate").val();
        let enddate = $("#endDate").val();

        if(startdate == '') {
            startdate = 'from';
        }

        if(enddate == '') {
            enddate = 'to';
        }

        let countperpage = $("#hidden_countperpage").val();
        let department = $("#hidden_department").val();
        let doctor_id = $("#hidden_doctor").val();
        if(doctor_id != '') {
            department = doctor_id;
        }
        let condition = $("#hidden_condition").val();
        let pstatus = $("#hidden_pstatus").val();
        let order = $("#hidden_order").val();

        let patientnum = $("#patientNum").val().trim();
        if(patientnum == '') {
            patientnum = 'patient';
        }

        location.href = '/list/' + countperpage + '/1/' + department + '/' + startdate + '/' + enddate + '/all' + '/' + pstatus + '/' + patientnum + '/' + order;
    }
});

//여기서부터 삭제요청 부분
$(document).on('show.bs.modal','#reason', function () { //파일들 선택 후 삭제요청 누르면 모달창이 열림. 모달창이 열렸을때 삭제요청한 파일들 목록을 보여줌
    var numArray = [];

    $("input[name='checkbox']:checked").each(function(index) {
        let num = $(this).val();
        let filename = $(this).attr("data-id");
        let obj = {num: num, filename: filename}
        numArray.push(obj);
    });

    for (var i = 0; i < numArray.length; i++) {
        let fileObj = numArray[i];
        //console.log('fileObj: ', fileObj);
        makelist(i, fileObj);
    }
});

function makelist(i, fileObj) {

    $("#fileList").append('<div id=fileList' + i + ' class="fileList"><div id=fileName' + i + ' class="fileName">' + fileObj.filename + '</div><div id=deleteArea' + i + '></div></div>');
    $("#deleteArea" + i).append($(".deleteArea").html());

    $("#btnradio1").attr('name', 'btnradio' + i);
    $("#btnradio2").attr('name', 'btnradio' + i);
    $("#btnradio3").attr('name', 'btnradio' + i);

    $("#btnradio1").attr('id', 'btnradio' + i + '_1');
    $("#btnradio2").attr('id', 'btnradio' + i + '_2');
    $("#btnradio3").attr('id', 'btnradio' + i + '_3');

    $("#btnradio" + i + '_1').next().attr('for', 'btnradio' + i + '_1');
    $("#btnradio" + i + '_2').next().attr('for', 'btnradio' + i + '_2');
    $("#btnradio" + i + '_3').next().attr('for', 'btnradio' + i + '_3');

    $("#deleteDetail").attr('id', 'deleteDetail' + i);
    $("#deleteDetail" + i).attr('class', 'deleteDetail btnradio' + i + '_3');
    $("#deleteReason").attr('id', 'deleteReason' + i);

}

function test(e) {
    if(e.value.length >= e.maxLength) {
        alert("최대 입력 크기를 초과하였습니다.");
        e.value = e.value.slice(0, -1);
    }
}

$('.close-btn').click(function() {
    $('#fileList').html('');
    $("input:checkbox[name='checkbox']").prop("checked", false);
    $("input:checkbox[id='mainCheckbox']").prop("checked", false);
}); // end $('.close').click


$('#delete').click(function() {
    var numArray = [];

    $("input[name='checkbox']:checked").each(function() {
        numArray.push($(this).val());
    });


    if(numArray.length < 1){
      alert("파일을 선택해주시기 바랍니다.");
      return;
    }

    $.ajax({
      url: "/file/check_delete",
      dataType : "json",
      data: JSON.stringify(numArray),
      method: "POST",
      success: function(data) {
        console.log("성공");

        if(data.message == 'success') {
            $('#reason').modal('show');
        } else {
            alert("확인요청 중인 파일은 삭제가 불가능합니다.");
        }

      },
      error: function(request, status, error) {
        console.log("에러: ", error);
        alert("잘못된 요청입니다.");
      },
      complete: function() {
        console.log("완료");
      }
    }); //end ajax



});


$('#deleteSubmit').click(function() {

    result = confirm('선택하신 파일을 삭제 요청하시겠습니까?');
    if(!result) {
        return;
    }

    let numArray = [];
    let obj;

    $("input[name='checkbox']:checked").each(function() {
        obj = {num: $(this).val()}
        numArray.push(obj);
    });

    $("input[name^='btnradio']:checked").each(function(index) {
        let reason = $(this).val();
        let reason2;

        if(reason == '기타') {
            reason2 = $('#deleteReason' + index).val().trim();

            if(reason2 != '') {
                reason = reason2;
            }
        }
        //console.log('numArray[index].num: ', numArray[index].num);
        numArray[index].reason = reason; //numArray에 reason이라는 프로퍼티를 만들고 그 값에 위의 변수 reason을 넣어줌.
    });

    let countperpage = $("#hidden_countperpage").val();
    let department = $("#hidden_department").val();
    let doctor_id = $("#hidden_doctor").val();
    if(doctor_id != '') {
        department = doctor_id;
    }
    let startdate = $("#hidden_startdate").val();
    let enddate = $("#hidden_enddate").val();
    let pagenum = $("#hidden_pagenum").val();
    let condition = $("#hidden_condition").val();
    let pstatus = $("#hidden_pstatus").val();
    let patientnum = $("#hidden_patientnum").val();
    let order = $("#hidden_order").val();

    $.ajax({
      url: "/file/multi_delete",
      dataType : "json",
      data: JSON.stringify(numArray),
      method: "POST",
      success: function(data) {
        console.log("성공");
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


//동적 삭제 부분
// click이벤트
$(document).on({
    click: function (e) {
        if(e.target.className == 'btn-check btnradio3') {
            $('.' + e.target.id).css('display', 'block');
        } else if(e.target.className == 'btn-check btnradio1' || e.target.className == 'btn-check btnradio2') {
            let target_id = e.target.id;
            target_id = target_id.split('_')[0] + '_3';
            $('.' + target_id).css('display', 'none');
        } //if(e.target... 끝
    } //click이벤트 끝
}); // $(document).on 끝


$('#download').click(function() {

    var numArray = [];

    $("input[name='checkbox']:checked").each(function() {
        numArray.push($(this).val());
    });


    if(numArray.length < 1){
      alert("파일을 선택해주시기 바랍니다.");
      return;
    }

    result = confirm('선택하신 파일을 다운로드하시겠습니까?');
    if(result) {
        for(const num of numArray) {
            $('#download_' + num).click();
            fnSleep(1000); //각 파일별 시간 텀을 준다
        }
        $("input:checkbox[name='checkbox']").prop("checked", false); //체크해제
        $("input:checkbox[id='mainCheckbox']").prop("checked", false);
    } else {
        $("input:checkbox[name='checkbox']").prop("checked", false);
        $("input:checkbox[id='mainCheckbox']").prop("checked", false);
        return;
    }
}); // end $('#download').click

fnSleep = function (delay){
   var start = new Date().getTime();
   while (start + delay > new Date().getTime());
};

$('#dateSearchBtn').click(function() {

    let startdate = $("#startDate").val();
    let enddate = $("#endDate").val();
    let countperpage = $("#hidden_countperpage").val();
    let department = $("#hidden_department").val();
    let doctor_id = $("#hidden_doctor").val();
    if(doctor_id != '') {
        department = doctor_id;
    }
    let condition = $("#hidden_condition").val();
    let pstatus = $("#hidden_pstatus").val();
    let order = $("#hidden_order").val();

    let patientnum = $("#patientNum").val().trim();
    if(patientnum == '') {
        patientnum = 'patient';
    }

    if(startdate == '' || enddate == ''){
      alert("날짜를 선택해주시기 바랍니다.");
      $("#startDate").val('');
      $("#endDate").val('');
      return;
    }

    location.href = '/list/' + countperpage + '/1/' + department + '/' + startdate + '/' + enddate + '/' + condition + '/' + pstatus + '/' + patientnum + '/' + order;
}); // end $('#dateSearchBtn').click



$('#patientSearchBtn').click(function() {
    let patientnum = $('#patientNum').val().trim();
    if(patientnum == '') {
        alert('환자번호를 입력하여 주세요.');
        return;
    }

    let startdate = $("#startDate").val();
    let enddate = $("#endDate").val();

    if(startdate == '') {
        startdate = 'from';
    }

    if(enddate == '') {
        enddate = 'to';
    }

    let countperpage = $("#hidden_countperpage").val();
    let department = $("#hidden_department").val();
    let doctor_id = $("#hidden_doctor").val();
    if(doctor_id != '') {
        department = doctor_id;
    }
    let condition = $("#hidden_condition").val();
    let pstatus = $("#hidden_pstatus").val();
    let order = $("#hidden_order").val();

    location.href = '/list/' + countperpage + '/1/' + department + '/' + startdate + '/' + enddate + '/' + condition + '/' + pstatus + '/' + patientnum + '/' + order;

}); // end $('#patientSearchBtn').click



//검색창 체크박스 부분
/*
function checkOnlyOne(element) {
    const checkboxes = document.getElementsByName("search_checkbox");
    console.log('안녕: ', checkboxes);
    checkboxes.forEach((cb) => {
        if(element.checked) {
            cb.checked = false;
            element.checked = true;
        }
    });
};
*/
/*
$('input[name="search_checkbox"]').change(function(e){
    checkOnlyOne(e.target);

    let startdate = $("#hidden_startdate").val();
    let enddate = $("#hidden_enddate").val();
    let countperpage = $("#hidden_countperpage").val();
    let department = $("#hidden_department").val();
    let pstatus = $("#hidden_pstatus").val();
    let patientnum = $("#hidden_patientnum").val();
    let order = $("#hidden_order").val();

    if($("#localCheckbox").is(":checked")){ //로컬 업로드 파일만 보기 체크
        location.href = '/list/' + countperpage + '/1/' + department + '/' + startdate + '/' + enddate + '/local' + '/' + pstatus + '/' + patientnum + '/' + order;
    } else if($("#deleteCheckbox").is(":checked")){ //삭제 요청 파일만 보기 체크
        location.href = '/list/' + countperpage + '/1/' + department + '/' + startdate + '/' + enddate + '/delete' + '/' + pstatus + '/' + patientnum + '/' + order;
    } else if($("#confirmCheckbox").is(":checked")){ //확인 요청 파일만 보기 체크
        location.href = '/list/' + countperpage + '/1/' + department + '/' + startdate + '/' + enddate + '/confirm' + '/' + pstatus + '/' + patientnum + '/' + order;
    } else if($("#confirmCheckbox2").is(":checked")){ //나에게 확인 요청 파일만 보기 체크
        location.href = '/list/' + countperpage + '/1/' + department + '/' + startdate + '/' + enddate + '/userConfirm' + '/' + pstatus + '/' + patientnum + '/' + order;
    } else { //체크 해제
        location.href = '/list/' + countperpage + '/1/' + department + '/' + startdate + '/' + enddate + '/all' + '/' + pstatus + '/' + patientnum + '/' + order;
    }

});
*/

$("input[name='box']").change(function(){
	let radioBtn = $("input[name='box']:checked").attr('id');

	let startdate = $("#hidden_startdate").val();
    let enddate = $("#hidden_enddate").val();
    let countperpage = $("#hidden_countperpage").val();
    let department = $("#hidden_department").val();
    let doctor_id = $("#hidden_doctor").val();
    if(doctor_id != '') {
        department = doctor_id;
    }
    let pstatus = $("#hidden_pstatus").val();
    let patientnum = $("#hidden_patientnum").val();
    let order = $("#hidden_order").val();

    if(radioBtn == 'localBtn'){ //로컬 업로드 파일만 보기 체크
        location.href = '/list/' + countperpage + '/1/' + department + '/' + startdate + '/' + enddate + '/local' + '/' + pstatus + '/' + patientnum + '/' + order;
    } else if(radioBtn == 'deleteBtn'){ //삭제 요청 파일만 보기 체크
        location.href = '/list/' + countperpage + '/1/' + department + '/' + startdate + '/' + enddate + '/delete' + '/' + pstatus + '/' + patientnum + '/' + order;
    } else if(radioBtn == 'confirmBtn'){ //확인 요청 파일만 보기 체크
        location.href = '/list/' + countperpage + '/1/' + department + '/' + startdate + '/' + enddate + '/confirm' + '/' + pstatus + '/' + patientnum + '/' + order;
    } else if(radioBtn == 'confirmBtn2'){ //나에게 확인 요청 파일만 보기 체크
        location.href = '/list/' + countperpage + '/1/' + department + '/' + startdate + '/' + enddate + '/userConfirm' + '/' + pstatus + '/' + patientnum + '/' + order;
    } //else { //체크 해제
        //location.href = '/list/' + countperpage + '/1/' + department + '/' + startdate + '/' + enddate + '/all' + '/' + pstatus + '/' + patientnum + '/' + order;
    //}
});

$('#logout_btn').click(function() {
    var result = confirm('로그아웃 하시겠습니까?');
    if(result) { //확인 누르면(true이면)
        location.replace('/logout');
    } else { //취소 누르면
        //아무일 일어나지 않는다.
    }
});


//wav파일로 convert, split

$(document).on('click', '.convertWAV', function(){
    if($(this).text() == 'done') {
        return;
    }

    $(this).html('<img src="/static/image/loading.gif" width="30px">');
    $('#convertArea').removeClass('inactive');

    let audio_id = $(this).parent().siblings('.audioId').text();

    $.ajax({
        url: "/file/convert",
        method: "POST",
        data: {
            audio_id : audio_id
        },
        success: function(data) {
            console.log("성공");
            alert('wav파일 변환이 완료되었습니다.');

            $("#convertWAV" + audio_id).html('<span class="material-icons-outlined splitWAV call_split">call_split</span>');
            //$("#splitWAV" + audio_id).children('.visible').text('call_split');
            $("#filename" + audio_id).text(data.wav_filename);

            if(data.duration != null) {
                console.log('duration: ', data.duration);
                $("#duration" + audio_id).text(data.duration);

                let prev_total_seconds = +$('#total_seconds').val();
                let total_seconds = data.total_seconds + prev_total_seconds;
                let seconds = parseInt(total_seconds%60);
                let minutes = parseInt((total_seconds/60)%60);
                let hours = parseInt(total_seconds/(60*60));

                //console.log('data.total_seconds: ', data.total_seconds);
                //console.log('prev_total_seconds: ', prev_total_seconds);
                //console.log('total_seconds: ', total_seconds);
                //console.log('seconds: ', seconds);
                //console.log('minutes: ', minutes);
                //console.log('hours: ', hours);

                $('#duration').text(hours + '시간 ' + minutes + '분 ' + seconds + '초');

                splitWAV(audio_id, data.duration);
            } else {
                splitWAV(audio_id, $("#duration" + audio_id).text());
            }

        },
        error: function(request, status, error) {
            console.log("에러: ", error);
            alert("잘못된 요청입니다. 다시 시도해 주세요.");
            $("#convertWAV" + audio_id).html('<span class="material-icons-outlined convertWAV cached">cached</span>');
        },
        complete: function() {
            $('#convertArea').addClass('inactive');
        }
    }); //end ajax

}); // end $('.convertWAV').click



function splitWAV(audio_id, duration) {

    if(duration == '00:00:00' || duration == '00:00:01' || duration == '00:00:02' || duration == '00:00:03' || duration == '00:00:04') {
        alert('5초 미만의 녹취 파일은 split 불가합니다.');
        return;
    }

    $('#splitModal').modal('show');
    //let audio_id = $(this).parent().siblings('.audioId').text();

    $.ajax({
        url: "/file/split",
        method: "POST",
        data: {
            audio_id : audio_id
        },
        success: function(data) {
            console.log("성공");
            alert('wav파일 split이 완료되었습니다.');

            $("#convertWAV" + audio_id).html('<span class="material-icons-outlined splitWAV done2">done</span>');
            //$('#splitModal').modal('hide');
        },
        error: function(request, status, error) {
            console.log("에러: ", error);
            alert("잘못된 요청입니다. 다시 시도해 주세요.");

            //$('#splitModal').modal('hide');
        },
        complete: function() {
            $('#splitModal').modal('hide');
        }
    }); //end ajax
}


//convert와 split을 한번에 처리하는 로직으로 바꿨지만.. 혹시나 경우에따라(convert하다가 에러나서 split 안될수도 있으니..) split버튼 클릭했을 떄도 split되도록
$(document).on('click', '.splitWAV', function(){

    if($(this).text() == 'done') {
        return;
    }

    let duration = $(this).parent().siblings('.duration').text();

    if(duration == '00:00:00' || duration == '00:00:01' || duration == '00:00:02' || duration == '00:00:03' || duration == '00:00:04') {
        alert('5초 미만의 녹취 파일은 split 불가합니다.');
        return;
    }

    $('#splitModal').modal('show');
    let audio_id = $(this).parent().siblings('.audioId').text();

    $.ajax({
        url: "/file/split",
        method: "POST",
        data: {
            audio_id : audio_id
        },
        success: function(data) {
            console.log("성공");
            alert('wav파일 split이 완료되었습니다.');

            $("#convertWAV" + audio_id).html('<span class="material-icons-outlined splitWAV done2">done</span>');
            //$('#splitModal').modal('hide');
        },
        error: function(request, status, error) {
            console.log("에러: ", error);
            alert("잘못된 요청입니다. 다시 시도해 주세요.");

            //$('#splitModal').modal('hide');
        },
        complete: function() {
            $('#splitModal').modal('hide');
        }
    }); //end ajax

}); // end $('.splitWAV').click


$('#dateDownloadBtn').click(function() {
    let startdate = $('#startDate').val();
    let enddate = $('#endDate').val();

    if(startdate == '' || enddate == ''){
        alert("날짜를 선택해주시기 바랍니다.");
        $("#startDate").val('');
        $("#endDate").val('');
        return;
    }

    $('#downloadArea').removeClass('inactive');

    $.ajax({
        url: "/list/fileDownloadList",
        method: "POST",
        data: {
            startdate : startdate,
            enddate: enddate
        },
        success: function(data) {
            //console.log("성공");
            if(data.message == 'fail') {
                alert('파일 다운로드가 불가합니다.');
                return;
            }

            //data.message == 'success'인 경우
            if(data.audio_list.length == 0) {
                alert('해당 기간에 다운 가능한 파일이 존재하지 않습니다.');
                $('#downloadArea').addClass('inactive');
                return;
            }
            saveZip(data.audio_list);

        },
        error: function(request, status, error) {
            //console.log("에러: ", error);
            alert("잘못된 요청입니다. 다시 시도해 주세요.");
            $('#downloadArea').addClass('inactive');
        },
        complete: function() {
            //console.log("완료");
        }
    }); //end ajax
});

function urlToPromise(url) {
    return new Promise(function (resolve, reject) {
        JSZipUtils.getBinaryContent(url, function (err, data) {
            if (err) {
                reject(err);
            } else {
                resolve(data);
            }
        });
    });
}

function saveZip(list) {
    let startdate = $('#startDate').val();
    let enddate = $('#endDate').val();

    var zip = new JSZip();

    for(var i=0; i < list.length; i++) {
        zip.file(list[i].filename, urlToPromise("/stream/" + list[i].filename), { binary: true }); //wav파일
        if(list[i].text_filename != null) {
            zip.file(list[i].text_filename, urlToPromise("/media/" + list[i].filepath_date + '/' + list[i].text_filename), { binary: true }); //txt파일
        }
    }

    zip.generateAsync({ type: "blob" })
        .then(function callback(blob) {
            // see FileSaver.js
            saveAs(blob, startdate + '_' + enddate + ".zip");
            $('#downloadArea').addClass('inactive');
        });
}


function patientList() {
    let department = $('#department2').val();

    $.ajax({
        url: "/list/patientList",
        method: "POST",
        data: {
            department: department
        },
        success: function(data) {
            //console.log("성공");

            let strAdd = '';
            if(data.message == 'fail') {
                alert('조회 결과가 없습니다.');
                strAdd += '<tr>';
                    strAdd += '<td colspan="4">' + '조회 결과가 없습니다.' + '</td>';
                strAdd += '</tr>';
                $('#patient').html(strAdd);
                $('#totalPatients').text('0');
                return;
            }

            for(var i = 0; i < data.patient_list.length; i++) {
                strAdd += '<tr>';
                    strAdd += '<td>' + (i+1) + '</td>';
                    strAdd += '<td>' + data.patient_list[i].patient_id + '</td>';
                    strAdd += '<td>' + data.patient_list[i].patient_gender + '</td>';
                    strAdd += '<td>' + data.patient_list[i].patient_age + '</td>';
                strAdd += '</tr>';
            }

            $('#totalPatients').text(data.patient_list.length);

            $('#patient').html(strAdd);
            $('#patientModal').modal('show');

        },
        error: function(request, status, error) {
            //console.log("에러: ", error);
            alert("잘못된 요청입니다. 다시 시도해 주세요.");
        },
        complete: function() {
            //console.log("완료");
        }
    }); //end ajax
}

$('.patient-btn').click(function() {
    patientList();
});

$('#department2').change(function() {
    patientList();
});


$(document).on('click', '#responseBtn, #nonResponseBtn', function(e){
    let thisBtn = $(this);
    let id = thisBtn.attr('id');

    let url;
    let background;
    if(id == 'responseBtn') {
        url = '/list/confirmList';
        background = 'orange-background';
    } else { //id == 'nonResponseBtn'
        url = '/list/confirmList2';
        background = 'yellow-background';
    }

    $.ajax({
        url: url,
        method: "POST",
        success: function(data) {
            //console.log("성공");
            //console.log(data.list);

            let strAdd = '';
            let strAdd2 = '';

            strAdd += '<h5>' + thisBtn.html() +'&nbsp;&nbsp;<button type="button" id="downloadBtn" class="btn btn-sm btn-info" onclick="excelFileExport();">엑셀파일 다운로드</button></h5>';
            strAdd += '<div class="table-responsive">';
                strAdd += '<table id="confirmTable" class="table">';
                    strAdd += '<thead class="thead-light ' + background + '">';
                        strAdd += '<tr>';
                            strAdd += '<th width="10%" scope="col">환자번호</th>';
                            strAdd += '<th width="25%" scope="col">파일명</th>';
                            strAdd += '<th width="8%" scope="col">글번호</th>';
                            strAdd += '<th width="7%" scope="col">split번호</th>';
                            strAdd += '<th width="45%" scope="col">text</th>';
                            strAdd += '<th width="5%" scope="col">보기</th>';
                        strAdd += '</tr>';
                    strAdd += '</thead>';
                    strAdd += '<tbody id="confirmTbody" class="customtable">';
                    strAdd += '</tbody>';
                strAdd += '</table>';
            strAdd += '</div>';

            $('#confirmContentArea').html(strAdd);

            if(data.message == 'fail') {
                strAdd2 += '<tr>';
                    strAdd2 += '<td colspan="6" style="text-align: center;">조회 결과가 없습니다.</td>';
                strAdd2 += '</tr>';
                $('#confirmTbody').html(strAdd2);
                return;
            }

            for(var i=0; i<data.list.length; i++) {
                strAdd2 += '<tr>';
                    strAdd2 += '<td>' + data.list[i].patient_id +'</td>';
                    strAdd2 += '<td>' + data.list[i].filename +'</td>';
                    strAdd2 += '<td>' + data.list[i].id +'</td>';
                    strAdd2 += '<td>' + data.list[i].split_num +'</td>';
                    strAdd2 += '<td>' + data.list[i].text +'</td>';

                    let num= +(data.list[i].split_num);
                    let page = parseInt(num/10) + 1;
                    strAdd2 += '<td>' + '<a href="/detail/' + data.list[i].id +'/10/1/dept/from/to/all/all/patient/new?split_pagenum=' + page + '#splitTd' + data.list[i].split_num +'"><button type="button" id="detailBtn' + i +'" class="btn btn-light detailBtn ' + background + '">보기</button></a>' +'</td>';
                strAdd2 += '</tr>';
            }

            $('#confirmTbody').html(strAdd2);
        },
        error: function(request, status, error) {
            //console.log("에러: ", error);
            alert("잘못된 요청입니다. 다시 시도해 주세요.");
        },
        complete: function() {
            //console.log("완료");
        }
    }); //end ajax
});


$('#confirmModal').on('hidden.bs.modal', function() {
    $('#confirmContentArea').html('');
});


//확인요청현황 엑셀파일로 다운로드
function excelFileExport() {
    // step 1. workbook 생성
    let wb = XLSX.utils.book_new();

    // step 2. 시트 만들기
    let newWorksheet = excelHandler.getWorksheet();

    // step 3. workbook에 새로만든 워크시트에 이름을 주고 붙인다.
    XLSX.utils.book_append_sheet(wb, newWorksheet, excelHandler.getSheetName());

    // step 4. 엑셀 파일 만들기
    let wbout = XLSX.write(wb, {bookType:'xlsx',  type: 'binary'});

    // step 5. 엑셀 파일 내보내기
    saveAs(new Blob([s2ab(wbout)],{type:"application/octet-stream"}), excelHandler.getExcelFileName());

}

const excelHandler = {
    getExcelFileName : function(){
        return '확인요청현황.xlsx';
    },
    getSheetName : function(){
        return 'sheet1';
    },
    getExcelData : function(){
        return document.getElementById('confirmTable');
    },
    getWorksheet : function(){
        return XLSX.utils.table_to_sheet(this.getExcelData());
    }
}

function s2ab(s) {
    let buf = new ArrayBuffer(s.length); //convert s to arrayBuffer
    let view = new Uint8Array(buf);  //create uint8array as viewer
    for (let i=0; i<s.length; i++) view[i] = s.charCodeAt(i) & 0xFF; //convert to octet
    return buf;
}

//weba파일들 한번에 wav파일로 변환
function convert() {
    $('#convertArea').removeClass('inactive');
    $.ajax({
        url: "/list/convert",
        method: "POST",
        success: function(data) {
            //console.log("성공");
            alert('wav파일로 변환이 완료되었습니다.');
            location.reload();
        },
        error: function(request, status, error) {
            //console.log("에러: ", error);
            alert("잘못된 요청입니다. 다시 시도해 주세요.");
        }
    }); //end ajax
}


