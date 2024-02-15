//전사 부분----------------------------------------------------------------------------------

$('.beginTranscription').click(function(e) {
    let board_id = $('#num').val();
    let wav_filepath = $('#wav_filepath').val();
    let order = $('#order').val();
    let thisBtn = $(this);
    let thisBtnHtml = $(this).html();

    if(thisBtnHtml == '전사시작' || thisBtnHtml == '분석시작' || thisBtnHtml == '전사재시작') {

        $.ajax({
            url: "/transcription/" + order + "/begin/",
            data: {
                board_id: board_id,
                wav_filepath: wav_filepath,
                thisBtnHtml: thisBtnHtml
            },
            method: "POST",
            success: function(data) {
                console.log("성공");
                //location.reload();
                thisBtn.removeClass('btn-light yellowgreen-background');
                thisBtn.addClass('btn-secondary');
                $('.completeTranscription').removeClass('trans');

                $('.deleteTd').html('<button type="button" class="btn btn-light green-background splitDeleteCancelBtn delete">삭제취소</button>');
                $('.soundTd').html('<button type="button" class="btn btn-light green-background soundModifyBtn sound">수정하기</button><button type="button" class="btn btn-light green-background textBtn sound">텍스트전사</button>');


                // $('#registrationBtnArea').html('&nbsp;<button type="button" class="btn btn-light yellowgreen-background registrationBtn">📝 미등록전사 확인</button>');
                if(order == '1') {

                    if(thisBtnHtml == '전사시작') {
                        $('.firstText').attr('disabled', false);
                        $('.firstTextCheck').css('visibility', 'visible');
                    } else if(thisBtnHtml == '전사재시작') {
                        $('.secondTr').html(''); //에트리부분 칸 없애야함.
                        $('.firstText').attr('disabled', true);
                        $('#saveTxtBtnArea').html('');
                    }

                    thisBtn.html('전사초기화');
                    $('.firstTranscriptionBtn').removeClass('trans');
                    $('.firstSpeakerArea').removeClass('trans');

                } else if(order == '2') {
                    let data_length = $('#hidden_data_length').val();
                    let data_total = $('#hidden_data_total').val();
                    let data_total2 = $('#hidden_data_total2').val();
                    let data_empty = $('#hidden_data_empty').val();

                    $('#completeTranscriptionArea').html('&nbsp;<button type="button" data-length="' + data_length + '" data-total="' + data_total +'" data-total2="' + data_total2 +'" data-empty="' + data_empty +'" class="btn btn-secondary completeTranscription">분석완료</button>');
                    // $('#requestBtnArea').html('&nbsp;<button type="button" class="btn btn-light skyblue-background requestBtn" data-btn="Y">🔔 확인요청만 보기</button>');
                    $('#answerBtnArea').html('');

                    thisBtn.html('분석초기화');
                    $('.secondTranscriptionBtn').removeClass('trans');
                    $('.secondConfirmBtn').removeClass('trans');
                    thisBtn.attr("onClick", "save('init')");

                    if($('.secondTranscriptionBtn').html() == '등록하기') {
                        $('.secondText').attr('disabled', false);
                        $('.secondTextCheck').css('visibility', 'visible');
                    }
                    //$('.secondSpeakerArea').removeClass('trans');
                    $('input[name^="secondSpeaker"]').attr('disabled', false);
                    $('.secondSelectSpeaker').removeAttr('style');
                    $('.secondSelectSpeaker').css('font-weight', 'bold');

                }
            },

            error: function(request, status, error) {
                console.log("에러: ", error);
                alert("잘못된 입력입니다.");
            },
            complete: function() {
                console.log("완료");
                $('#txtFile').css('visibility', 'hidden');
            }
        }); //end ajax

    } else if($(this).html() == '전사초기화' || $(this).html() == '분석초기화') {

        if($(this).html() == '전사초기화') {
            result = confirm('전사 작업을 취소하시겠습니까? 모든 내용은 초기화됩니다.');
        } else {
            result = confirm('분석 작업을 취소하시겠습니까? 모든 내용은 초기화됩니다.');
        }

        let countperpage = $("#hidden_countperpage").val();
        let department = $("#hidden_department").val();
        let startdate = $("#hidden_startdate").val();
        let enddate = $("#hidden_enddate").val();
        let pagenum = $("#hidden_pagenum").val();
        let condition = $("#hidden_condition").val();
        let pstatus = $("#hidden_pstatus").val();
        let orderBy = $("#hidden_order").val();

        if(result) {

            $.ajax({
                url: "/transcription/" + order + "/cancel/",
                data: {
                    board_id: board_id,
                    wav_filepath: wav_filepath
                },
                method: "POST",
                success: function(data) {
                    console.log("성공");
                    location.reload();
                    $('.speakerArea').addClass('trans');
                },

                error: function(request, status, error) {
                    console.log("에러: ", error);
                    alert("잘못된 입력입니다.");
                },
                complete: function() {
                    console.log("완료");
                }
            }); //end ajax

        } else {
            return;
        } //end if(result)


    }



}); // end $('#beginTranscription').click



$(document).on('click', '.transcriptionBtn', function(event){

    let split_num = $(this).attr("data-id");
    let split_filename = $(this).attr("data-filename");
    let order = $('#order').val();
    let thisBtn = $(this);

    let text = thisBtn.parent().siblings('.prevTd').children('.wrap').children('.textarea').val().trim();
    let checked =thisBtn.parent().siblings('.prevTd').children('.text_check').children('.check_div').children('.textCheckbox').is(':checked');

    let radioVal = '';

    if($(this).html() == '등록하기') {

        if(text.length <= 0 && checked == false){
            alert("😅텍스트를 입력하여 주세요. 입력하실 내용이 없으면 '전사할 텍스트 없음'에 체크하여 주세요.");
            return;
        } else if(text.length <= 0 && checked == true){
            text = '';
        }


        if(order == '1') {
            if(!$('input[name="firstSpeaker' + split_num + '"]').is(":checked")) {
                // alert('화자를 선택하여 주세요.');
                return;
            }
            radioVal = $('input[name="firstSpeaker' + split_num + '"]:checked').val();
        } else if(order == '2') {
            if(!$('input[name="secondSpeaker' + split_num + '"]').is(":checked")) {
                // alert('화자를 선택하여 주세요.');
                return;
            }
            radioVal = $('input[name="secondSpeaker' + split_num + '"]:checked').val();
        }


        $.ajax({
            url: "/transcription/" + order + "/regist/",
            data: {
                split_filename: split_filename,
                text: text,
                radioVal: radioVal
            },
            method: "POST",
            success: function(data) {
                console.log("성공");

                thisBtn.html('수정하기');
                thisBtn.removeClass('yellowgreen-background');
                thisBtn.addClass('yellow-background');
                thisBtn.parent().siblings('.prevTd').children('.wrap').children('.textarea').text(text);
                thisBtn.parent().siblings('.prevTd').children('.wrap').children('.textarea').attr('disabled', true);
                thisBtn.parent().siblings('.prevTd').children('.text_check').css('visibility', 'hidden');
                thisBtn.parent().siblings('.prevTd').children('.text_check').children('.check_div').children('.textCheckbox').prop('checked', false);

                $('#hiddenText' + split_num).val(text);


                //미등록전사 보기 모드가 아닌 전체보기일때는 이렇게처리함.
                if(order == '1') {
                    $('input[name="firstSpeaker' + split_num + '"]').attr('disabled', true);
                    $('#firstSelectSpeaker' + split_num).removeAttr('style');
                    $('#firstSelectSpeaker' + split_num).css('color', 'gray');
                }

                if(order == '2') {
                    $('#thirdText' + split_num).text(text); //충남대 확인요청 textarea에도 에트리에서 등록한 내용이 반영되도록

                    $('input[name="secondSpeaker' + split_num + '"]').attr('disabled', true);
                    $('#secondSelectSpeaker' + split_num).removeAttr('style');
                    $('#secondSelectSpeaker' + split_num).css('color', 'gray');
                }
                if(order == '3') {
                    thisBtn.parent().parent().css('background-color', '#A2F5E6');
                }

            },

            error: function(request, status, error) {
                console.log("에러: ", error);
                alert("잘못된 입력입니다.");
            },
            complete: function() {
                console.log("완료");
            }
        }); //end ajax
    } else if($(this).html() == '수정하기') { //수정하기 누르면
        thisBtn.html('수정완료');
        thisBtn.parent().siblings('.prevTd').children('.wrap').children('.textarea').attr('disabled', false);
        thisBtn.parent().siblings('.prevTd').children('.text_check').css('visibility', 'visible');
        thisBtn.parent().siblings('.prevTd').children('.speakerArea').children('.speakerRadio').children('span').attr('style', 'color:black;font-weight:bold;');
        thisBtn.parent().siblings('.prevTd').children('.speakerArea').children('.speakerRadio').children('.form-check').children('input').attr('disabled', false);
        thisBtn.next().removeClass('trans');
        if(order == '2') {
            thisBtn.next().next().addClass('trans');
        }

    } else if($(this).html() == '재등록하기') {
        $('#thirdTransBtn' + split_num).html('재등록완료');
        $('#thirdText' + split_num).attr('disabled', false);
        $('#thirdTextCheck' + split_num).css('visibility', 'visible');
        $('#thirdTransCancelBtn' + split_num).removeClass('trans');
        $('#thirdTransCancelBtn' + split_num).html('재등록취소');
        $('#thirdConfirmBtn' + split_num).addClass('trans');
    } else { //수정완료 또는 재등록완료

        if(text.length <= 0 && checked == false){
            alert("😅텍스트를 입력하여 주세요. 입력하실 내용이 없으면 '전사할 텍스트 없음'에 체크하여 주세요.");
            return;
        } else if(text.length <= 0 && checked == true){
            text = '';
        }

        // if(order == '1') {
        //     radioVal = $('input[name="firstSpeaker' + split_num + '"]:checked').val();
        // } else if(order == '2') {
        //     radioVal = $('input[name="secondSpeaker' + split_num + '"]:checked').val();
        // }

        $.ajax({
            url: "/transcription/" + order + "/modify/",
            data: {
                split_filename: split_filename,
                text: text,
                radioVal: radioVal
            },
            method: "POST",
            success: function(data) {
                console.log("성공");
                //location.reload();
                thisBtn.html('수정하기');
                thisBtn.next().addClass('trans');

                thisBtn.parent().siblings('.prevTd').children('.wrap').children('.textarea').text(text);
                thisBtn.parent().siblings('.prevTd').children('.wrap').children('.textarea').attr('disabled', true);
                thisBtn.parent().siblings('.prevTd').children('.text_check').css('visibility', 'hidden');
                thisBtn.parent().siblings('.prevTd').children('.text_check').children('.check_div').children('.textCheckbox').prop('checked', false);
                thisBtn.parent().siblings('.prevTd').children('.speakerArea').children('.speakerRadio').children('span').attr('style', 'color:gray;');
                thisBtn.parent().siblings('.prevTd').children('.speakerArea').children('.speakerRadio').children('.form-check').children('input').attr('disabled', true);

                $('#hiddenText' + split_num).val(text);

                if(order == '2') {
                    thisBtn.next().next().removeClass('trans');
                    $('#thirdText' + split_num).text(text); //충남대 확인요청 textarea에도 에트리에서 수정한 내용이 반영되도록
                }
                if(order == '3') {
                    thisBtn.parent().parent().css('background-color', '#A2F5E6');
                }
            },

            error: function(request, status, error) {
                console.log("에러: ", error);
                alert("잘못된 입력입니다.");
            },
            complete: function() {
                console.log("완료");
            }
        }); //end ajax

    }//end if문

}); // end $('.transcriptionBtn').click


$('.transcriptionCancelBtn').click(function() {

    let value = $(this).html();
    let split_num = $(this).attr("data-id");
    let split_filename = $(this).attr("data-filename");
    let order = $('#order').val();
    let thisBtn = $(this);

    $.ajax({
        url: "/transcription/" + order + "/modifyCancel/",
        data: {
            split_filename: split_filename
        },
        method: "POST",
        success: function(data) {
            console.log("성공");

            thisBtn.addClass('trans');

            if(value == '수정취소') {
                thisBtn.prev().html('수정하기');
            } else if(value == '재등록취소') {
                thisBtn.prev().html('재등록하기');
            }

            thisBtn.parent().siblings('.prevTd').children('.wrap').children('.textarea').attr('disabled', true);
            thisBtn.parent().siblings('.prevTd').children('.wrap').children('.textarea').val(data.text);
            thisBtn.parent().siblings('.prevTd').children('.text_check').css('visibility', 'hidden');

            thisBtn.parent().siblings('.prevTd').children('.text_check').children('.check_div').children('.textCheckbox').prop('checked', false);

            thisBtn.parent().siblings('.prevTd').children('.speakerArea').children('.speakerRadio').children('.form-check').children('input').attr('disabled', true);

            thisBtn.parent().siblings('.prevTd').children('.speakerArea').children('.speakerRadio').children('span').attr('style', 'color:gray;');
            let radio = thisBtn.parent().siblings('.prevTd').children('.speakerArea').children('.speakerRadio').children('.form-check');
            radio.children('input:radio[value="' + data.speaker +'"]').prop('checked', true);

            if(order == '2') {
                thisBtn.next().removeClass('trans'); //확인요청버튼 보여주기
            }

        },

        error: function(request, status, error) {
            console.log("에러: ", error);
            alert("잘못된 입력입니다.");
        },
        complete: function() {
            console.log("완료");
        }
    }); //end ajax


}); // end $('.transcriptionCancelBtn').click


$(".textCheckbox").change(function(){
    let split_num = $(this).attr("data-id");
    let split_filename = $(this).attr("data-filename");
    if($(this).is(":checked")){
        $(this).parent().parent().siblings('.textarea' + split_num).val('');
        $(this).parent().parent().siblings('.textarea' + split_num).attr('disabled', true);
        $('#split').modal('show');
        $('#split').attr('data-id', split_num);
        $('#split_filename').val(split_filename);
    }else{
        $(this).parent().parent().siblings('.textarea' + split_num).attr('disabled', false);
    }
}); // end $('.textCheckbox').change

$("#split").on("hidden.bs.modal", function () {
    $('#split').removeAttr('style');
    $('#split').removeClass('show');

    $('.modal-backdrop').removeAttr('class');
    $('.modal-open').removeAttr('style');
    $('.modal-open').removeAttr('class');

    $('#sound').val('');
    $("input:checkbox[name='textCheckbox']").prop("checked", false); //원래 name='textCheckbox'가 충남대병원밖에 없었는데 이 코드 실행하게 하려고 엘젠,에트리쪽에 이 속성넣음.. 혹시 나중에 문제되면 다시 빼기
});

$(document).on('click', '.completeTranscription', function(e){
    let board_id = $('#num').val();
    let wav_filepath = $('#wav_filepath').val();
    let split_length = $(this).attr("data-length");
    let is_empty_text_length;
    let confirm_length;
    let respond_length;
    let real_confirm_length;

    let flag = false;
    let value = $(this).html();
    let order = $('#order').val();

    if(value == '확인요청완료') {
        real_confirm_length = $(this).attr("data-total3");
        //console.log('real_confirm_length: ', real_confirm_length);
        if(real_confirm_length > 0) {

            for(var i = 0; i < real_confirm_length; i++) {
                let btnHtml = $($('.thirdTranscriptionBtn')[i]).html();
                let dataId = $($('.thirdTranscriptionBtn')[i]).attr('data-id');

                if(btnHtml == '등록하기') {
                    alert('등록 작업을 완료하여 주세요(' + dataId + '번).');
                    return;
                } else if(btnHtml == '수정완료') {
                    alert('수정 작업을 완료하여 주세요(' + dataId + '번).');
                    return;
                } else if(btnHtml == '재등록하기') {
                    alert('재등록하기 버튼을 눌러 재등록 작업을 진행하여 주세요(' + dataId + '번).');
                    return;
                } else if(btnHtml == '재등록완료') {
                    alert('재등록완료 버튼을 눌러 재등록 작업을 완료하여 주세요(' + dataId + '번).');
                    return;
                } //endif '재등록하기'
            } //endfor

        } //endif(real_confirm_length > 0)

    }

    if(value == '전사완료' || value == '분석완료') {
        is_empty_text_length = $(this).attr("data-empty");
        let length = split_length - is_empty_text_length

        let btn;
        if(value == '전사완료') {
            btn = $('.firstTranscriptionBtn');
        } else if(value == '분석완료') {
            btn = $('.secondTranscriptionBtn');
        }

        if(length > 0) {
            for(var i = 0; i < length; i++) {
                let btnHtml = $(btn[i]).html();
                let dataId = $(btn[i]).attr('data-id');

                if(btnHtml == '수정완료') {
                    alert('수정 작업을 완료하여 주세요(' + dataId + '번).');
                    return;
                }
            } //endfor
        } //endif
    }

    $.ajax({
        url: "/transcription/" + order + "/completeCheck/",
        data: {
            wav_filepath: wav_filepath
        },
        method: "POST",
        success: function(data) {
            console.log("성공");
            if(data == 'True') {
                //console.log('data: ', data);
                alert('작업을 완료하여 주세요.');
                return;
            } else if(data == 'True2') {
                //console.log('data: ', data);
                alert('확인요청 중이어서 완료할 수 없습니다.');
                return;
            } else if(data == 'True3') {
                //console.log('data: ', data);
                alert('확인요청 작업을 완료하여 주세요.');
                return;
            } else if(data == 'False') {
                complete(e, board_id, value);
            }
        },

        error: function(request, status, error) {
            console.log("에러: ", error);
            alert("잘못된 입력입니다.");
        },
        complete: function() {
            console.log("완료");
        }
    }); //end ajax
}); // end $('.completeTranscription').click


function complete(e, board_id, value) {

    if(value == '전사완료') {
        result = confirm('전사 작업을 완료하시겠습니까?');
    } else if(value == '분석완료') {
        result = confirm('분석 작업을 완료하시겠습니까?');
    } else if(value == '확인요청완료') {
        result = confirm('확인요청 작업을 완료하시겠습니까?');
    }

    let order = $('#order').val();
    let wav_filepath = $('#wav_filepath').val();

    if(result) {

        $.ajax({
            url: "/transcription/" + order + "/complete/",
            data: {
                board_id: board_id,
                wav_filepath: wav_filepath
            },
            method: "POST",
            success: function(data) {
                console.log("성공");
                let split_countperpage = $('#countperpage2 option:selected').val();
                let countperpage = $("#hidden_countperpage").val();
                let department = $("#hidden_department").val();
                let startdate = $("#hidden_startdate").val();
                let enddate = $("#hidden_enddate").val();
                let pagenum = $("#hidden_pagenum").val();
                let condition = $("#hidden_condition").val();
                let pstatus = $("#hidden_pstatus").val();
                let patientnum = $("#hidden_patientnum").val();
                let orderBy = $("#hidden_order").val();

                location.replace('/detail/' + board_id + '/' + countperpage + '/' + pagenum + '/' + department + '/' + startdate + '/' + enddate + '/' + condition + '/' + pstatus + '/' + patientnum + '/' + orderBy + '?split_pagenum=1' + '&split_countperpage=' + split_countperpage);
            },

            error: function(request, status, error) {
                console.log("에러: ", error);
                alert("잘못된 입력입니다.");
            },
            complete: function() {
                console.log("완료");
            }
        }); //end ajax

    } else {
        return;
    } //end if(result)
}


$(document).on('click', '.confirmBtn', function(e){
    let board_id = $('#num').val();
    let wav_filepath = $('#wav_filepath').val();
    let split_filename = $(this).attr("data-filename");
    let split_num = $(this).attr("data-id");
    let order = $('#order').val();
    let kind;
    let thisBtn = $(this)

    if($(this).html() == '확인요청') {
        kind = 'confirm2';
        result = confirm('충남대병원에게 확인을 요청하시겠습니까?');
    } else { //확인요청취소
        kind = 'cancel';
        result = confirm('확인요청을 취소하시겠습니까?');
    }

    if(result) {

        $.ajax({
            url: "/transcription/" + order + "/confirm/",
            data: {
                board_id: board_id,
                wav_filepath: wav_filepath,
                split_filename: split_filename,
                kind: kind
            },
            method: "POST",
            success: function(data) {
                console.log("성공");

                if(thisBtn.html() == '확인요청취소' && $('.requestBtn').attr('data-btn') == 'N') {
                    location.reload();
                    return;
                }

                let nextTr = thisBtn.parent().parent().next();
                let prevTr = thisBtn.parent().parent().prev();
                let content = $('#hiddenText' + split_num).val();

                nextTr.html('');
                if(thisBtn.html() == '확인요청') {
                    //location.reload();
                    nextTr.css('background-color', '#C0FFFF');
                    prevTr.children('.rowspan').attr('rowspan', '2');
                    let strAdd = '';

                    strAdd += '<td colspan="2" style="text-align:center;"><b>🔔 확인요청</b></td>';
                    strAdd += '<td>충남대병원</td>';
                    strAdd += '<td class="prevTd">';
                        strAdd += '<div class="wrap2">';
                            strAdd += '<textarea id="thirdText' + split_num + '" class="form-control col-sm-5 thirdText textarea" disabled>' + content +'</textarea>';
                        strAdd += '</div>'
                    strAdd += '</td>';
                    strAdd += '<td></td>';

                    nextTr.html(strAdd);

                    thisBtn.html('확인요청취소');
                } else { //확인요청취소
                    thisBtn.html('확인요청');
                }
            },

            error: function(request, status, error) {
                console.log("에러: ", error);
                alert("잘못된 입력입니다.");
            },
            complete: function() {
                console.log("완료");
            }
        }); //end ajax

    } else {
        return;
    } //end if(result)

}); // end $('.confirmBtn').click




$('#modalSubmit').click(function() {

    let value = $('input[name="split_btnradio"]:checked').val();
    let order = $('#order').val();
    let request;
    let split_filename = $('#split_filename').val();
    let sound = $('#sound').val().trim();
    let thisBtn = $(this);

    if(value == '1' && sound == '') {
        alert('소리를 기입하여 주세요.')
        return;
    } else if(value == '1' && sound != '') {
        request = 'sound'
    }


    if(value == '2') {
        result = confirm('해당 파일을 삭제하시겠습니까?');
        if(!result) {
            return;
        }
        request = 'delete'
    }


    $.ajax({
      url: "/transcription/" + order + "/" + request + "/",
      data: {
        split_filename: split_filename,
        sound: sound
      },
      method: "POST",
      success: function(data) {
        console.log("성공");

        if(value == '2') {
            alert("삭제가 완료되었습니다.");
        }

        $('#split').modal('hide');
        let split_num = $('#split').attr('data-id');

        //if(value == '2') {//삭제후 비동기처리
            //$('.audioTd' + split_num).html('');
            //$('.audioTd' + split_num).html('<b style="color: green;">삭제된 파일입니다.</b>');
            //$('.firmTd' + split_num).html('');
            //$('.prevTd' + split_num).html('');
            //$('.buttonTd' + split_num).html('<button type="button" class="btn btn-light green-background splitDeleteCancelBtn" data-filename="' + split_filename + '">삭제취소</button>');
        //}
        location.reload();

      },
      error: function(request, status, error) {
        console.log("에러: ", error);
        alert("잘못된 요청입니다.");
      },
      complete: function() {
        console.log("완료");
      }
    }); //end ajax

}); // end $('#modalSubmit').click

$(document).on('click', '.splitDeleteCancelBtn', function(){

    let order = $('#order').val();
    let split_filename;
    if($(this).hasClass('delete')){
        split_filename = $(this).parent().attr("data-filename");
    } else {
        split_filename = $(this).attr("data-filename");
    }


    $.ajax({
      url: "/transcription/" + order + "/deleteCancel/",
      data: {
        split_filename: split_filename
      },
      method: "POST",
      success: function(data) {
        console.log("성공");
        alert("삭제가 취소되었습니다.");
        location.reload();
      },
      error: function(request, status, error) {
        console.log("에러: ", error);
        alert("잘못된 요청입니다.");
      },
      complete: function() {
        console.log("완료");
      }
    }); //end ajax

}); // end $('.splitDeleteCancelBtn').click


$(document).on('click', '.soundModifyBtn', function(){

    let split_filename;
    if($(this).hasClass('sound')){
        split_filename = $(this).parent().attr("data-filename");
    } else {
        split_filename = $(this).attr("data-filename");
    }

    $('#split_filename').val(split_filename);
    $('#split').modal('show');

}); // end $('.soundModifyBtn').click


$(document).on('click', '.textBtn', function(){

    result = confirm('텍스트 전사로 전환하시겠습니까?');
    if(!result) {
        return;
    }

    let order = $('#order').val();

    let split_filename;
    if($(this).hasClass('sound')){
        split_filename = $(this).parent().attr("data-filename");
    } else {
        split_filename = $(this).attr("data-filename");
    }

    $.ajax({
      url: "/transcription/" + order + "/text/",
      data: {
        split_filename: split_filename
      },
      method: "POST",
      success: function(data) {
        console.log("성공");
        location.reload();
      },
      error: function(request, status, error) {
        console.log("에러: ", error);
        alert("잘못된 요청입니다.");
      },
      complete: function() {
        console.log("완료");
      }
    }); //end ajax

}); // end $('.textBtn').click

/*
$('.close_modal').click(function() {
    //data-bs-backdrop="static" data-bs-keyboard="false"
    //$('#split').removeAttr('data-bs-backdrop');
    //$('#split').removeAttr('data-bs-keyboard');
    $('#split').removeAttr('style');
    $('#split').removeClass('show');

    $('.modal-backdrop').removeAttr('class');
    $('.modal-open').removeAttr('style');
    $('.modal-open').removeAttr('class');

});
*/

$('.undo').click(function() {

    let order = $('#order').val();
    let split_num = $(this).attr("data-id");
    let split_filename = $(this).attr("data-filename");

    $.ajax({
      url: "/transcription/" + order + "/undo/",
      data: {
        split_filename: split_filename
      },
      method: "POST",
      success: function(data) {
        console.log("성공");
        console.log(data);
        if(order == '1') {
             $('#firstText' + split_num).val(data);
        } else if(order == '2') {
             $('#secondText' + split_num).val(data);
        } else if(order == '3') {
             $('#thirdText' + split_num).val(data);
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

}); // end $('.undo').click

//-----------------------------------------------------------------------------------------------
//전사리스트 검색조건
$('#countperpage2').change(function() {
    let split_pagenum = 1;
    let split_countperpage = $('#countperpage2 option:selected').val();
    let split_file_requested = $('#hidden_request').val();
    let split_file_not_registered = $('#hidden_regist').val();

    let board_id = $('#num').val();
    let countperpage = $("#hidden_countperpage").val();
    let department = $("#hidden_department").val();
    let startdate = $("#hidden_startdate").val();
    let enddate = $("#hidden_enddate").val();
    let pagenum = $("#hidden_pagenum").val();
    let condition = $("#hidden_condition").val();
    let pstatus = $("#hidden_pstatus").val();
    let patientnum = $("#hidden_patientnum").val();
    let orderBy = $("#hidden_order").val();

    location.replace('/detail/' + board_id + '/' + countperpage + '/' + pagenum + '/' + department + '/' + startdate + '/' + enddate + '/' + condition + '/' + pstatus + '/' + patientnum + '/' + orderBy + '?split_pagenum=' + split_pagenum + '&split_countperpage=' + split_countperpage + '&split_file_not_registered=' + split_file_not_registered + '&split_file_requested=' + split_file_requested);

}); // end $('#countperpage2').change

//페이징된 전사 버튼 클릭했을때 (1,2,3 등 클릭했을때)
$(document).on('click', '.page-link2', function(event){
    let order = $('#order').val();
    let split_countperpage = +$('#countperpage2 option:selected').val();
    let btnHtml;
    let btn;

    if(order == '1') {
        btn = $('.firstTranscriptionBtn');
    } else if(order == '2') {
        btn = $('.secondTranscriptionBtn');
    } else if(order == '3') {
        btn = $('.thirdTranscriptionBtn');
    }

    for(var i = 0; i < split_countperpage; i++) {
        btnHtml = $(btn[i]).html();
        let dataId = $(btn[i]).attr('data-id');
        if(btnHtml == '수정완료') {
            alert('수정 작업을 완료하여 주세요(' + dataId + '번).');
            return;
        } else if(btnHtml == '재등록하기') {
            alert('재등록을 완료하여 주세요(' + dataId + '번).');
            return;
        } //endif '재등록하기'
    } //endfor


    let split_pagenum = $(this).text().trim();
    //let split_countperpage = $('#countperpage2 option:selected').val();

    if(split_pagenum == '»') {
        let prev_pagenum = $(this).parent().prev().children('.page-link').text();
        split_pagenum = +prev_pagenum + 1;
    } else if(split_pagenum == '«') {
        let next_pagenum = $(this).parent().next().children('.page-link').text();
        split_pagenum = +next_pagenum - 1;
    }

    let board_id = $('#num').val();
    let countperpage = $("#hidden_countperpage").val();
    let department = $("#hidden_department").val();
    let startdate = $("#hidden_startdate").val();
    let enddate = $("#hidden_enddate").val();
    let pagenum = $("#hidden_pagenum").val();
    let condition = $("#hidden_condition").val();
    let pstatus = $("#hidden_pstatus").val();
    let patientnum = $("#hidden_patientnum").val();
    let split_file_requested = $('#hidden_request').val();
    let split_file_not_registered = $('#hidden_regist').val();
    let orderBy = $("#hidden_order").val();

    location.replace('/detail/' + board_id + '/' + countperpage + '/' + pagenum + '/' + department + '/' + startdate + '/' + enddate + '/' + condition + '/' + pstatus + '/' + patientnum + '/' + orderBy + '?split_pagenum=' + split_pagenum + '&split_countperpage=' + split_countperpage + '&split_file_not_registered=' + split_file_not_registered + '&split_file_requested=' + split_file_requested);

});

//-----------------------------------------------------------------------------------------------
//글 내용 크기에 따라 textarea창의 크기가 바뀜
$('.wrap').on('keyup', 'textarea', function(e){
    $(this).css('height', 'auto');
    $(this).height(this.scrollHeight);
});
$('.wrap').find('textarea').keyup();


$('#display').click(function() {
    $('#displayText').toggleClass('trans');
});

//-----------------------------------------------------------------------------------------------
//전사 3초 이동

const SECOND = 1; //전사 툴 몇초 이전,이후 다시듣기할건지 상수로 선언
$('.seconds').text(SECOND); //recording_detail.html에 해당 초 넣어줌

$(document).on('click', '.before', function(){
    let audio = $(this).parent('.arrowBtn').siblings('audio');

    if(audio[0].currentTime > SECOND) {
        audio[0].currentTime = audio[0].currentTime - SECOND;
    } else {
        audio[0].currentTime = 0;
    }
});

$(document).on('click', '.after', function(){
    let audio = $(this).parent('.arrowBtn').siblings('audio');

    if(audio[0].currentTime + SECOND > audio[0].duration) {
        audio[0].currentTime = audio[0].duration;
    } else {
        audio[0].currentTime = audio[0].currentTime + SECOND;
    }
});



$(document).on('keydown', 'textarea', function(e){
    if(e.altKey) {
        e.preventDefault();
        let num = $(this).attr('data-num');
        let audio = $('.transAudio' + num)[0];
        if(audio.paused) {
            setTimeout(function () {
                audio.play();
            }, 150);
        } else if(audio.played) {
            audio.pause();
        }
    } else if(e.which === 188 && e.ctrlKey) {
        e.preventDefault();
        let num = $(this).attr('data-num');
        $('.before' + num).click();
    } else if(e.which === 190 && e.ctrlKey) {
        e.preventDefault();
        let num = $(this).attr('data-num');
        $('.after' + num).click();
    }
});




//확인요청만 보기(확인요청 모아보기)

$(document).on('click', '.requestBtn', function(){
    let dataBtn = $(this).attr('data-btn');

    let split_pagenum = 1;
    let split_countperpage = $('#countperpage2 option:selected').val();
    console.log(split_countperpage);
    if(typeof(split_countperpage) == 'undefined') {
        split_countperpage = 10;
    }

    let board_id = $('#num').val();
    let countperpage = $("#hidden_countperpage").val();
    let department = $("#hidden_department").val();
    let startdate = $("#hidden_startdate").val();
    let enddate = $("#hidden_enddate").val();
    let pagenum = $("#hidden_pagenum").val();
    let condition = $("#hidden_condition").val();
    let pstatus = $("#hidden_pstatus").val();
    let patientnum = $("#hidden_patientnum").val();
    let orderBy = $("#hidden_order").val();

    location.replace('/detail/' + board_id + '/' + countperpage + '/' + pagenum + '/' + department + '/' + startdate + '/' + enddate + '/' + condition + '/' + pstatus + '/' + patientnum + '/' + orderBy + '?split_pagenum=' + split_pagenum + '&split_countperpage=' + split_countperpage + '&split_file_requested=' + dataBtn);
});


//분석완료 후 충남대병원 답변만 보기
$(document).on('click', '.answerBtn', function(){
    let dataBtn = $(this).attr('data-btn');

    let split_pagenum = 1;
    let split_countperpage = $('#countperpage2 option:selected').val();
    console.log(split_countperpage);
    if(typeof(split_countperpage) == 'undefined') {
        split_countperpage = 10;
    }

    let board_id = $('#num').val();
    let countperpage = $("#hidden_countperpage").val();
    let department = $("#hidden_department").val();
    let startdate = $("#hidden_startdate").val();
    let enddate = $("#hidden_enddate").val();
    let pagenum = $("#hidden_pagenum").val();
    let condition = $("#hidden_condition").val();
    let pstatus = $("#hidden_pstatus").val();
    let patientnum = $("#hidden_patientnum").val();
    let orderBy = $("#hidden_order").val();

    location.replace('/detail/' + board_id + '/' + countperpage + '/' + pagenum + '/' + department + '/' + startdate + '/' + enddate + '/' + condition + '/' + pstatus + '/' + patientnum + '/' + orderBy + '?split_pagenum=' + split_pagenum + '&split_countperpage=' + split_countperpage + '&split_file_requested=N&split_text3=' + dataBtn);
});



//미등록전사 모아보기

$(document).on('click', '.registrationBtn', function(){
    let board_id = $('#num').val();
    let order = $('#order').val();

    $.ajax({
        url: "/transcription/regConfirmModal/",
        data: {
            board_id: board_id,
            order: order
        },
        method: "POST",
        success: function(data) {
            //console.log("성공");

            strAdd = '';

            if(data.list.length == 0) {
                strAdd = '<p>모두 등록되었습니다(미등록 파일 없음).</p>'
            } else {
                for(var i=0; i<data.list.length ; i++) {
                    strAdd += '<p>' + data.list[i] +'번</p>'
                }
            }

            $('#splitNumBody').html(strAdd);
            $('#regConfirmModal').modal('show');
        },
        error: function(request, status, error) {
            //console.log("에러: ", error);
            alert("잘못된 요청입니다.");
        },
        complete: function() {
            //console.log("완료");
        }
    }); //end ajax

});


function getTxt() {
    result = confirm('해당 파일을 다운로드하시겠습니까?');
    let filename = $('#filename').val().replace(/(.weba|.wav)$/,'') + '.txt';
    let filepath_date = $('#filepath_date').val();

    if(result) {
        $('#txtFile').attr('href', '/media/' + filepath_date + '/' + filename);
    } else {
        return;
    }
}

$(document).on('click', '.wordTag', function(e){
    console.log('e.target: ', e.target);
    e.preventDefault();

    let num = $(this).parent().parent().parent('.sttTimestampContent').attr('data-num');
    let audio = $('.transAudio' + num)[0];
    let filename = $(this).parent().parent().parent('.sttTimestampContent').attr('data-filename');
    audio.src = '/transcription/stream/' + filename;

    let from = +($(this).attr('data-from'));
    let to = +($(this).attr('data-to'));

    if(from == to) { //시작지점과 끝점이 같으면 안멈추고 계속 재생됨
        to += 0.1;
    }

    audio.src += '#t=' + from + ',' + to;

    var playPromise = audio.play();
    if (playPromise !== undefined) { playPromise.then((_) => {}).catch((error) => {}); }

});


//오디오재생이멈추면 체크박스 체크 해제
//var transAudio = document.getElementsByClassName('transAudio')[1]; //001번 오디오
//var transAudio = document.getElementsByClassName('transAudio')[4]; //004번 오디오
//var transAudios = document.getElementsByClassName('transAudio');
var transAudios = $('.transAudio'); //바로 위와 동일한 코드
//console.log(transAudios);
//console.log(typeof(transAudios));

Array.from(transAudios).forEach((audio) => {
    //console.log(audio);
    audio.addEventListener("pause", function() {
        if($('.checkboxInput').is(':checked')){
            $('.checkboxInput').prop('checked',false);
            return;
        }
    });
});

var ConditionA = false;
var ConditionB = false;
$.fn.dragCheckbox = function(e) {
    var source = this;
    //var ConditionA = false;
    //var ConditionB = false;
    var input = source.parent().children('.checkboxInput');

    source.parent().css({
      '-webkit-user-select': 'none',
      '-moz-user-select': 'none',
      '-ms-user-select': 'none',
      '-o-user-select': 'none',
      'user-select': 'none'
    });
    source.mousedown(function(){
        if(input.is(':checked')){
            input.prop('checked',false);
        }
        ConditionA = true;
        ConditionB = true;
        //$(this).children('a').click();
    });
    source.mouseup(function(e){
        //e.stopPropagation();
        ConditionA = false;
        ConditionB = false;

        //여기서부터 드래그한 그 구간만 재생되도록
        var from_array = [];
        var to_array = [];
        var index_array = [];
        var num;
        var filename;

        $($('.checkboxInput')).each(function(){

            if($(this).is(':checked')) {
                var from = $(this).attr('data-from');
                var to = $(this).attr('data-to');
                var index = $(this).attr('data-index');

                from_array.push(from);
                to_array.push(to);
                index_array.push(index);
            }
            //console.log(from_array);
            //console.log(to_array);
            //console.log(index_array);
        });

        //(code0)여기서부터 드래그를 쭉 안하고 중간에 건너띄고 했을때 건너띈 부분도 선택되도록 하는 코드임
        var num = $(this).parent('.item').parent('.sttTimestampContent').attr('data-num');
        var new_index_array = [];

        if(index_array.length > 0) {
            //console.log(index_array[index_array.length-1]);
            for(var i=+(index_array[0]); i<index_array[index_array.length-1]; i++) {
                new_index_array.push(i);
            }

            //console.log('new_index_array: ', new_index_array);

            for(var j=0; j<new_index_array.length; j++) {
                let id = 'cb' + num + '_' + new_index_array[j];
                //console.log('id: ', id);
                $('#' + id).prop('checked', true);
            }

        } //(code0) end

        let wordTag = $(this).children('.wordTag');
        let from2 = wordTag.attr('data-from');
        let to2 = wordTag.attr('data-to');

        wordTag.attr('data-from', from_array[0]);
        //console.log('from_array[0]: ', from_array[0]);
        wordTag.attr('data-to', to_array[to_array.length - 1]);
        //console.log('to_array[to_array.length - 1]: ', to_array[to_array.length - 1]);
        wordTag.click();

        wordTag.attr('data-from', from2); //다시 원래값으로 복귀
        wordTag.attr('data-to', to2); //다시 원래값으로 복귀
    });
    source.mouseenter(function(){
        if(ConditionA != false) {
            $(this).trigger('click');
        }
    });
    source.mouseout(function(){
        if(ConditionA != false && ConditionB != false) {
            $(this).trigger('click');
            ConditionB = false;
        }
    });
}

$('.checkboxLabel').dragCheckbox();
//$('.checkboxLabel > .wordTag').dragCheckbox();
//$('.item').dragCheckbox();


//gstt쪽이 아닌 다른곳에서 mouseup event가 일어나면 체크박스 다 해제해준다.
window.addEventListener('mouseup', function(e) {
    //console.log(e.target);

    if(e.target.className != 'checkboxLabel'){
        if($('.checkboxInput').is(':checked')){
            $('.checkboxInput').prop('checked',false);
            //console.log(ConditionA);
            //console.log(ConditionB);
            ConditionA = false;
            ConditionB = false;
        }

        //다른곳에 mouseup하면 재생된것도 중지되도록
        Array.from(transAudios).forEach((audio) => {
            //console.log(audio.paused);
            if(!audio.paused) {
                audio.pause();
                return;
            }
        });
    }
});


// 전사파일 서버 저장
$(document).on('click', '.saveTxtFile', function(e){
    let status = $("#status").val();
    let wav_filepath = $('#wav_filepath').val();

    $.ajax({
        url: "/transcription/saveTxtFile/",
        data: {
            status: status,
            wav_filepath: wav_filepath
        },
        method: "POST",
        success: function(data) {
            //console.log("성공");
            alert('서버 저장을 완료하였습니다.📁😤')
        },
        error: function(request, status, error) {
            //console.log("에러: ", error);
            alert("잘못된 요청입니다.");
        },
        complete: function() {
            //console.log("완료");
        }
    }); //end ajax

});


// 전사보류 처리
$(document).on('click', '.stopTransBtn', function(e){

    let result = confirm('정말 전사보류 처리하시겠습니까?');
    if(!result) {
        return;
    }

    let board_id = $('#num').val();

    $.ajax({
        url: "/transcription/stop/",
        data: {
            board_id: board_id
        },
        method: "POST",
        success: function(data) {
            //console.log("성공");
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

});

// 전사보류취소 처리
$(document).on('click', '.stopTransCancelBtn', function(e){

    let board_id = $('#num').val();

    $.ajax({
        url: "/transcription/stopCancel/",
        data: {
            board_id: board_id
        },
        method: "POST",
        success: function(data) {
            //console.log("성공");
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

});
