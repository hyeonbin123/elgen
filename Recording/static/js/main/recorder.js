// wavebell

var cvs = document.getElementById('cvs');
var context = cvs.getContext('2d');
var rng = document.getElementById('rng');
var txt2 = document.getElementById('txt2');

var bell;
/*
var bell = new WaveBell();
원래 이 지점에서 var bell = new WaveBell(); 작성해서
wavebell 객체 생성했는데 이렇게 하다보니까
audioContext객체가 미리 이 지점에서 생성된다
audioContext객체는 자동으로 생성되면 안되고 사용자의 어떠한 작동이 있을때 생성되어야한다.(크롬 정책임)
그래서 사용자가 record버튼 누를때 wavebell객체 생성되게 수정함
*/

window.addEventListener('load', function (e) {
    // start animation on loaded
    //bell.on('pause', function () {
    //    return;
    //});
    animate();
});

var currentValue = 0;

// buffered wave data
var BUF_SIZE = 500;
var buffer = new Array(BUF_SIZE).fill(0);
var cursor = 0;


function onbell() {
    bell.on('wave', function (e) {
    // update current wave value
    currentValue = e.value;

    //여기가 미터기
    rng.style.width = (e.value * 100) + '%';

    if($('#timer').text() == '00:30:00') { //녹음 30분 후 자동 종료
        stopRecording();
    }

    });

}


function statusBell() {
    bell.on('start', function () {
        var blob = bell.result;
        //console.log('blob: ', blob);
        blob = null;
        //console.log('blob: ', blob);
        //txt2.innerText = '녹음 중...';

        startTimer(); //타이머 시작
    });
    bell.on('resume', function () {
        //txt2.innerText = '녹음 중...';
    });
    bell.on('pause', function () {
        currentValue = 0;
        //txt2.innerText = '녹음 일시정지';
    });
}

function stopBell() {
    bell.on('stop', function () {
        var blob = bell.result;
        //console.log('blob: ', blob);
        createDownloadLink2(blob);
    });
}





function updateBuffer () {
    // loop update buffered data
    buffer[cursor++ % BUF_SIZE] = currentValue;
}

function drawFrame () {
    context.save();
    // empty canvas
    context.clearRect(0, 0, 500, 300);
    // draw audio waveform
    //context.strokeStyle = '#46BEFF';
    for (var i = 0; i < BUF_SIZE; i++) {
        var h = 250 * buffer[(cursor + i) % BUF_SIZE];

        var floorh = Math.floor(h);
        if(floorh > 255) {
            floorh = 255;
        }

        context.strokeStyle = 'rgb(' + floorh + ', 70, 222)';

        var x = i;
        context.beginPath();
        context.moveTo(x, 150.5 - 0.5 * h);
        context.lineTo(x, 150.5 + 0.5 * h);
        context.stroke();
    }
    // draw middle line
    context.beginPath();
    context.moveTo(0, 150.5);
    context.lineTo(500, 150.5);
    context.strokeStyle = '#000';
    context.stroke();
    context.restore();
}


function animate () {
    requestAnimationFrame(animate);
    // update wave data
    if(typeof(bell) == 'undefined' || bell.state === 'inactive' || bell.state === 'paused') {
        return;
    }

    onbell();
    updateBuffer();
    // draw next frame
    drawFrame();
}
//-------------------------------------------------------------------


$('#play').click(function() {
    $('#time-area').attr('class', 'active');

    //var aud = document.getElementById("audio_player");
    //var duration = Math.floor(aud.duration); //사실 var duration = aud.duration; 로 해도 돼.. 혹시 몰라서 내림함.
    //$('#duration').text(toHHMMSS(duration));

    if($('#play').text() == '듣기') {
        playAudio();
        $('#play').text('중지');
    } else if($('#play').text() == '중지') {
        //wavesurfer.pause();
        $('#play').text('듣기');
    }
});


//-------------------------------------------------------------------


function startRecording() {
    bell = new WaveBell();

    bell.start(1000/25);
    //startTimer(); //타이머 시작
    statusBell();

}

/*
function pauseRecording() {
    console.log("pauseButton clicked rec.recording=", rec.recording);
    if (rec.recording) {
        //pause
        rec.stop();
        pauseButton.innerHTML = "Resume";
    } else {
        //resume
        rec.record()
        pauseButton.innerHTML = "Pause";
    }
}
*/

function stopRecording() {
    console.log("stopButton clicked");

    bell.stop();
    stopTimer(); // 타이머 정지

    $('#area').attr('class', 'inactive');
    $('.screen').attr('class', 'inactive');

    $('#server-upload-area').attr('class', 'active');
    $('#infoTxt').text('');
    $('#txt2').text('녹음이 완료되었습니다.');

    alert("녹취 파일을 업로드 중입니다.\n'업로드 완료' 메시지가 뜰 때까지 잠시만 기다려주세요.");

    stopBell();

}


var getNewPatientId = function(reg_id) {
    var result = false;
    $.ajax({
        header:{"Content-Type":"application/json"},
        url: "/patient/check",
        method: "POST",
        dataType : "json",
        async: false,
        data: JSON.stringify(reg_id),
        success: function(data) {
            //console.log("성공");
            $("#patientNum").val(data.patient_id);
            result = data.patient_id;
        },
        error: function(request, status, error) {
            //console.log("에러: ", error);
            //alert("잘못된 요청입니다. 다시 시도해 주세요.");
            result = null; //무슨 값 넣어야될지 몰라서 일단 이렇게 함
        }
    }); //end ajax
    return result;
}


function createDownloadLink2(blob) {
    let id = $("#rec_id").val();
    let reg_id = $('#regNum').val();

    if($("#patientNum").attr('hidden')) { //신규등록환자일경우 업로드하기전에 환자번호 체크해줘야함
        $("#patientNum").val(getNewPatientId(reg_id));
        $("#patientNum").attr('hidden', false);
    }

    let patient_id = $("#patientNum").val();
    let gender = $('#gender option:selected').val();
    let age = $('#age').val();
    let count = $('#count option:selected').val();

    let reg_date = $('#regDate').val();
    let name = $('#name').val().trim();
    let department = $('#department').val();
    let doctor = $('#doctor').val();
    if(doctor == '') {
        doctor = department + '-00'; //의료진 선택 안했을때
    }

    $('#patientInfo').attr('data-patient', patient_id);
    $('#patientInfo').attr('data-count', count);

    let user_id = $("#user_id").val();

    //$('#upload_local_btn').removeAttr('disabled');

    var link = URL.createObjectURL(blob);
    $('#audio_player').attr("src", link); //녹음한거 들어보는 기능

    $('#download_button').wrap('<a id="aaa" download></a>');
    $('#aaa').attr('href', link);

    let filename;
    //if(d_code == '999') {
    //    filename = c_code + '_' + user_id + '_' + id + '_' + patient_id  + '_'  + count + '.weba';
    //} else {
        filename = doctor + '_' + user_id + '_' + id + '_' + patient_id  + '_'  + count + '.weba';
    //}

    $('#aaa').attr('download', filename);

    $('#download_button').click(); //녹음된 파일 자동 다운(네트워크 유실시 대비)

    // upload file
    let formdata = new FormData();

    formdata.append("data", blob);
    formdata.append("id", id);
    formdata.append("patient_id", patient_id);

    formdata.append("gender", gender);
    formdata.append("age", age);
    formdata.append("count", count);

    formdata.append("reg_id", reg_id);
    formdata.append("reg_date", reg_date);
    formdata.append("name", name);
    formdata.append("department", department);
    formdata.append("doctor", doctor);

    //let xhr = new XMLHttpRequest();
    //xhr.open("POST", "/rec/upload/" + id , false);
    //xhr.send(formdata);
    //console.log('전송완료');

    $.ajax({
      url: "/rec/upload/" + id,
      method: "POST",
      data: formdata,
      processData: false,
      contentType: false,
      success: function(data) {
        console.log('성공!');

        alert("업로드가 완료되었습니다😀");
        //$('.audio-element').attr('src', '/media/' + data);
        //$('#download').attr('href', '/media/' + data);

      },
      error: function(request, status, error) {
        console.log("에러: ", error);
        //alert("잘못된 입력입니다.");
        alert("업로드에 실패하였습니다😭");
      },
      complete: function() {
        console.log("완료");
        $('#server-upload-area').attr('class', 'inactive');
        $('#record-stop-area').attr('class', 'active');
        $('#audiocontrol-area').attr('class', 'active');
      }
    }); //end ajax

    //$('#gender').attr('disabled', true);
    //$('#age').attr('disabled', true);
    //$('#count').attr('disabled', true);
    $('#patientId').attr('disabled', true);

    $('#infoTxt').text('');

}
//-------------------------------------------------------------------end Recorderjs

function getCurrentDate() {
    var date = new Date();
    var year = date.getFullYear().toString();

    var month = date.getMonth() + 1;
    month = month < 10 ? '0' + month.toString() : month.toString();

    var day = date.getDate();
    day = day < 10 ? '0' + day.toString() : day.toString();

    var hour = date.getHours();
    hour = hour < 10 ? '0' + hour.toString() : hour.toString();

    var minites = date.getMinutes();
    minites = minites < 10 ? '0' + minites.toString() : minites.toString();

    var seconds = date.getSeconds();
    seconds = seconds < 10 ? '0' + seconds.toString() : seconds.toString();

    return year + month + day + hour + minites + seconds;
}


function getPlayId() {
    let id = $("#rec_id").val();
    console.log('id: ', id);
    return '/rec/play/' + id;
}


$('#logout_btn').click(function() {
    var result = confirm('로그아웃 하시겠습니까?');
    if(result) { //확인 누르면(true이면)
        location.replace('/logout');
    } else { //취소 누르면
        //아무일 일어나지 않는다.
    }
});


$('#cancel').click(function() {
    location.replace('/');
});


$('#delete').click(function() {
    result = confirm('해당 파일을 삭제 요청하시겠습니까?');
    if(!result) {
        return;
    }

    let id = $("#rec_id").val();
    let patient_id = $('#patientInfo').attr('data-patient');
    let count = $('#patientInfo').attr('data-count');

    $.ajax({
      url: "/rec/delete/" + id,
      method: "POST",
      data: {
        patient_id : patient_id,
        count : count
      },
      success: function(data) {
        console.log("성공");
        alert("삭제요청이 완료되었습니다.");
        location.replace('/');
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


$('#record').click(function() {
    if($('#record').text() == 'mic') {
        if($('#regDate').siblings('label').hasClass('red')) {
            alert('🚨 녹취가 불가한 환자입니다.');
            return;
        }

        let keyup_txt = $('#keyupTxt').text();
        let txt = $('#txt').text();
        let info_txt = $('#infoTxt').text();

        var inputLength = $('#regNum').val().length;
        if(inputLength < 8) {
            alert('등록번호를 기입하여 주세요.');
            return;
        }

        /*
        if(info_txt == '수정하기' && txt != '🧡') {
            alert('환자정보 수정을 완료하여 주세요.');
            return;
        } else if(info_txt == '환자정보등록' && txt != '🧡') {
            alert('환자정보 등록을 완료하여 주세요.');
            return;
        } else if(!(keyup_txt == '🧡' && txt == '🧡')) {
            alert('녹취정보를 기입해 주세요.');
            return;
        }*/

        let id = getCurrentDate();

        //$('.range').attr('style', 'visibility: visible;');

        //mediaRecorder.start();
        startRecording();

        $('.inner-circle2').css({opacity: 0, visibility: 'visible'}).animate({opacity: 1}, 700);

        $("#rec_id").val(id);
        $('#record').text('stop');
        $('#upload_local_btn').attr('disabled', true);

    } else if($('#record').text() == 'stop') {
        var inputLength = $('#regNum').val().length;
        if(inputLength < 8) {
            alert('등록번호를 기입하여 주세요.');
            return;
        }

        if($('#name').val().trim() == '') {
            alert('성명을 입력하여 주세요.');
            return;
        } else if($('#age').val() == '') {
            alert('연령을 입력하여 주세요.');
            return;
        } else if($('#gender').val() == '') {
            alert('성별을 선택하여 주세요.');
            return;
        } else if($('#count').val() == '') {
            alert('총녹취인원을 선택하여 주세요.');
            return;
        } else if($('#department').val() == '') {
            alert('부서를 선택하여 주세요.');
            return;
        } //else if($('#doctor').val() == '') {
          //  alert('의료진을 선택하여 주세요.');
          //  return;
        //}

        $('#regNum').attr('disabled', true);
        $('#name').attr('disabled', true);
        $('#age').attr('disabled', true);
        $('#gender').attr('disabled', true);
        $('#count').attr('disabled', true);
        $('#department').attr('disabled', true);
        $('#doctor').attr('disabled', true);
        stopRecording();
    }
});


$('#pause').click(function() {

    let id = $("#rec_id").val();

    if($('#pause').text() == 'radio_button_unchecked') {
        //mediaRecorder.resume();
        bell.resume();
        //rec.record();
        //wavesurfer.microphone.start();
        restartTimer(); // 타이머 다시시작
        statusBell();

        $('#pause').text('pause');
    } else if($('#pause').text() == 'pause') {
        //mediaRecorder.pause();
        bell.pause();
        //rec.stop();
        //wavesurfer.microphone.pause();
        pauseTimer(); //타이머 일시정지
        statusBell();

        $('#pause').text('radio_button_unchecked');
    }
});

$('#gender,#age,#count').change(function() {
    let gender = $('#gender option:selected').val();
    let age = $('#age option:selected').val();
    let count = $('#count option:selected').val();
    let info_txt = $('#infoTxt').text();

    if($('#infoTxt').text() == '환자정보등록' && gender != '' && age != '' && count != '') {
        $('#txt').text('환자정보 등록을 완료하여 주세요.');
        $('#txt2').text('');
    }

    if(info_txt == '환자정보수정' && count == '') {
        $('#txt').text('총녹취인원을 선택해 주세요.');
    } else if(info_txt == '수정하기' && count == '' && gender != '' && age != '') {
        $('#txt').text('총녹취인원을 선택해 주세요.');
    } else if(gender == '' || age == '' || count == '') {
        $('#txt').text('성별, 연령, 총녹취인원을 선택해 주세요.');
    } else if(!gender == '' && !age == '' && !count == '' && info_txt == '수정하기') {
        $('#txt').text('환자정보 수정을 완료하여 주세요(수정하기 또는 수정취소를 선택해 주세요).');
    } else if(!gender == '' && !age == '' && !count == '' && info_txt == '환자정보수정') {
        $('#txt').text('🧡');
    } else if(!gender == '' && !age == '' && !count == '' && info_txt == '') {
        $('#txt').text('🧡');
    }

    if($('#txt').text() =='🧡' && $('#keyupTxt').text() =='🧡') {
        $("#txt2").text('녹음 버튼을 눌러주세요.');
    } else {
        $("#txt2").text('');
    }

});







$('#infoTxt').click(function() {
    if($(this).text() == '환자정보등록') {
        $('#infoTxt').css('color', 'orange');
        $('#infoTxt2').text('');

        let patient_id = $('#patientId').val();
        let gender = $('#gender').val();
        let age = $('#age').val();
        let count = $('#count').val();

        if(gender == '' || age == '') {
            alert('성별 또는 연령을 선택하여 주세요.');
            return;
        }

        $.ajax({ //등록하기 요청
            url: "/patient/regist",
            method: "POST",
            data: {
                gender : gender,
                age : age,
                patient_id : patient_id
            },
            success: function(data) {
                console.log("성공");
                alert('환자정보 등록이 완료되었습니다.');
                if(count != '') {
                    $('#txt').text('🧡');
                    $('#txt2').text('녹음 버튼을 눌러주세요.');
                } else {
                    $('#txt').text('총녹취인원을 선택해 주세요.');
                }
                $('#infoTxt').text('환자정보수정');

                $('#patientId').attr('disabled', false);
                $('#gender').attr('disabled', true);
                $('#age').attr('disabled', true);

                $('#upload_local_btn').attr('disabled', false);

                $('#patient_gender').val(gender);
                $('#patient_age').val(age);
            },
            error: function(request, status, error) {
                console.log("에러: ", error);
                alert("잘못된 요청입니다. 다시 시도해 주세요.");
            }
        }); //end ajax


    } else if($(this).text() == '환자정보수정') {
        $('#patientId').attr('disabled', true);
        $('#gender').attr('disabled', false);
        $('#age').attr('disabled', false);

        $('#infoTxt').text('수정하기');
        $('#infoTxt').css('color', '#B9062F');
        $('#infoTxt2').text('수정취소');
        $('#upload_local_btn').attr('disabled', true);

        if($('#txt').text() == '🧡') {
            $('#txt').text('환자정보 수정을 완료하여 주세요(수정하기 또는 수정취소를 선택해 주세요).');
            $('#txt2').text('');
        }
    } else if($(this).text() == '수정하기') {
        let patient_gender = $('#patient_gender').val();
        let patient_age = $('#patient_age').val();
        let gender = $('#gender').val();
        let age = $('#age').val();
        let count = $('#count').val();
        let patient_id = $('#patientId').val();
        $('#upload_local_btn').attr('disabled', false);

        if(!gender == '' && !age == '' && !count == '') {
            $('#txt').text('🧡');
            $('#txt2').text('녹음 버튼을 눌러주세요.');
        }

        if(gender == '' && age == '') {
            alert('성별과 연령을 선택하여 주세요.');
            return;
        } else if(gender == '') {
            alert('성별을 선택하여 주세요.');
            return;
        } else if(age == '') {
            alert('연령을 선택하여 주세요.');
            return;
        }


        if(patient_gender == gender && patient_age == age) { //수정된 내용이 없는데 수정하기 버튼 누를경우
            //alert('수정된 내용이 없습니다.'); //굳이 alert창 안띄워도 될것같아서 주석처리.
            $('#patientId').attr('disabled', false);
            $('#gender').attr('disabled', true);
            $('#age').attr('disabled', true);
            $('#infoTxt').text('환자정보수정');
            $('#infoTxt').css('color', 'orange');
            $('#infoTxt2').text('');
            return;
        }



        $.ajax({ //수정하기 요청
            url: "/patient/update",
            method: "POST",
            data: {
                gender : gender,
                age : age,
                patient_id : patient_id
            },
            success: function(data) {
                //console.log("성공");
                alert('환자정보 수정이 완료되었습니다.');
                $('#patient_gender').val(gender);
                $('#patient_age').val(age);

                $('#gender').attr('disabled', true);
                $('#age').attr('disabled', true);
                $('#infoTxt').text('환자정보수정');
                $('#infoTxt').css('color', 'orange');
                $('#infoTxt2').text('');
                $('#patientId').attr('disabled', false);
            },
            error: function(request, status, error) {
                //console.log("에러: ", error);
                alert("잘못된 요청입니다. 다시 시도해 주세요.");
            }
        }); //end ajax

    }
});



$('#infoTxt2').click(function() { //수정취소 클릭
    $('#patientId').attr('disabled', false);
    var patient_id = $('#patientId').val();

    let patient_gender = $('#patient_gender').val();
    let patient_age = $('#patient_age').val();
    let gender = $('#gender').val();
    let age = $('#age').val();
    let count = $('#count').val();

    $('#upload_local_btn').attr('disabled', false);

    if(!gender == '' && !age == '' && !count == '') {
        $('#txt').text('🧡');
        $('#txt2').text('녹음 버튼을 눌러주세요.');
    }


    if(patient_gender == gender && patient_age == age) { //수정된 내용이 없는 상태에서 수정취소 클릭하면
        $('#gender').attr('disabled', true);
        $('#age').attr('disabled', true);
        $('#infoTxt').text('환자정보수정');
        $('#infoTxt').css('color', 'orange');
        $('#infoTxt2').text('');
        return;
    }

    $.ajax({ //수정된 내용이 있는 상태에서 수정취소 클릭하면
        url: "/patient/check",
        method: "POST",
        dataType : "json",
        data: JSON.stringify(patient_id),
        success: function(data) {
            console.log("성공");

            $('#gender').val(data.patient_gender);
            $('#age').val(data.patient_age);

            if(data.patient_gender != null && data.patient_age != null) { //db에 등록되어 있는 환자정보이면
                $('#gender').attr('disabled', true);
                $('#age').attr('disabled', true);
            }

        },
        error: function(request, status, error) {
            console.log("에러: ", error);
            alert("잘못된 요청입니다. 다시 시도해 주세요.");

            $('#gender').attr('disabled', true);
            $('#age').attr('disabled', true);
        }
    }); //end ajax

    $('#infoTxt').text('환자정보수정');
    $('#infoTxt').css('color', 'orange');
    $('#infoTxt2').text('');

});



$(document).on('click', '#patientIdModBtn', function(e){
    $('#patientInfoModal').modal('show');
});

function rejectCancel() {
    var result = confirm('해당 환자를 거부 대상자 목록에서 정말 삭제하시겠습니까?\n삭제하시면 녹취가 가능합니다.');
    if(result) {
        let reg_id = $('#regNum').val();

        $.ajax({ //수정하기 요청
            url: "/patient/delete2",
            method: "POST",
            data: {
                reg_id : reg_id
            },
            success: function(data) {
                //console.log("성공");
                location.reload();
            },
            error: function(request, status, error) {
                //console.log("에러: ", error);
                alert("잘못된 요청입니다. 다시 시도해 주세요.");
            }
        }); //end ajax
    }
}