//댓글부분----------------------------------------------------------------------------------

//댓글 등록하거나 수정할 때 글자수 세는 이벤트
$(document).on('keyup', '.replyWrite, .replyModify', function(event){
    let content = $(this).val(); // 글자수 세기
    if (content.length == 0 || content == '') {
        $(this).siblings('span').children('.textCount').text('0자');
    } else {
        $(this).siblings('span').children('.textCount').text(content.length + '자');
    } // 글자수 제한

    if (content.length > 500) { // 500자 부터는 타이핑 되지 않도록
        $(this).val($(this).val().substring(0, 500)); // 500자 넘으면 알림창 뜨도록
        //alert('글자수는 500자까지 입력 가능합니다.');
        $(this).siblings('span').children('.textCount').text('500자');
    };
});

//수정버튼 누르면 수정창 오픈되는 이벤트
$(document).on('click', '.modify', function(event){
    let parent = $(this).parent().parent().siblings('.modifyArea');

    $(this).parent().parent().siblings('.replyContent').toggleClass('inactive');
    parent.toggleClass('inactive');
    parent.children('.textLengthWrap').children('.textCount').text(parent.children('.replyModify').val().length + '자');
}); // end $('.modify').click


//수정 취소
$(document).on('click', '.modCancel', function(event){
    let replyContent = $(this).parent().siblings('.replyContent');

    replyContent.removeClass('inactive');
    //console.log('안녕: ', replyContent.children('.content').text());
    //console.log('안녕2: ', replyContent.children('.content').text().replace(/(\n|\r\n)/g, '<br>'));
    $(this).siblings('.replyModify').val(replyContent.children('.content').text());
    $(this).parent('.modifyArea').addClass('inactive');
}); // end $('.modCancel').click


$(document).on("click", ".reReplyCount", function(event){
    $(this).parent().siblings('.reReplyArea').toggleClass('inactive');
});

$(document).on("click", ".reReplyFold", function(event){
    $(this).parent().toggleClass('inactive');
});


$('.replyWrite').on('mousedown', function() {
    $(this).attr('rows', '5');
    $(this).css('width', '100%');
    $(this).parent().removeClass('flex');
    $(this).siblings('.textLengthWrap').removeClass('inactive');
});


$(document).on('mousedown', '.reReplyWrite', function(event){
    $(this).attr('rows', '3');
    $(this).css('width', '100%');
    $(this).parent().attr('class', 'reReplyWriteArea');
    $(this).siblings('.textLengthWrap').removeClass('inactive');
});


//대댓글 쓸때 글자수 세는 이벤트
$(document).on('keyup', '.reReplyWrite', function(event){
    let content = $(this).val(); // 글자수 세기
    if (content.length == 0 || content == '') {
        $(this).siblings('span').children('.textCount').text('0자');
    } else {
        $(this).siblings('span').children('.textCount').text(content.length + '자');
    } // 글자수 제한

    if (content.length > 300) { // 300자 부터는 타이핑 되지 않도록
        $(this).val($(this).val().substring(0, 300)); // 500자 넘으면 알림창 뜨도록
        //alert('글자수는 500자까지 입력 가능합니다.');
        $(this).siblings('span').children('.textCount').text('300자');
    };
});


//-----------------------------------------------------------------------------------------------
//댓글 목록 출력하는 함수
function getReplyList(board_id, pagenum) {
    let user_id = $('#user_id').val();

    let split_filename = $('#splitNumSelect2 option:selected').val();
    let select_order = $('#selectOrder option:selected').val();
    let countperpage = $('#countperpage option:selected').val();

    $.ajax({
        url: "/reply/list",
        method: "POST",
        data: {
            board_id: board_id,
            pagenum: pagenum,
            split_filename: split_filename,
            select_order: select_order,
            countperpage: countperpage
        },
        success: function(data) {
            console.log("성공");
            //console.log(data.list.length);
            //console.log(data.list);

            //input태그에 각각의 속성을 넣고 나중에 꺼내쓰려고 했는데 굳이 그럴필요성이 없어서 주석처리함.
            //$('#page_list').attr('data-countperpage', data.page_list.countperpage);
            if(data.page_list != undefined) {
                $('#page_list').attr('data-pagenum', data.page_list.pagenum);
            }

            //$('#calculate_list').attr('data-beginpage', data.calculate_list.begin_page);
            //$('#calculate_list').attr('data-endpage', data.calculate_list.end_page);
            //$('#calculate_list').attr('data-nums', data.calculate_list.nums);
            //$('#calculate_list').attr('data-prev', data.calculate_list.prev);
            //$('#calculate_list').attr('data-next', data.calculate_list.next);


            //글구 이부분은 댓글등록이나 검색할때 목록출력하는 경우이다.
            //맨처음에 detail페이지들어왔을때는 여기가 아닌 class Detail에서 페이징처리해줘야함.

            if(data.message == 'fail') {
                $('#replyList').html('');
                let strFailAdd = '';
                strFailAdd += '<div>조회 결과가 없습니다.</div>';
                $('#replyList').html(strFailAdd);

                $('#pageList').html('');
                $('#replyCount').text('0');
                return;
            }

            //여기서부터 data.message == success인 경우

            if(data.list.length <= 0) {
                $('#replyList').html('');
                $('#replyCount').text('0');
                return;
            }

            $('#replyCount').text(data.page_list.total_count);
            let strAdd = '';
            $('#replyList').html('');


            for(let i=0; i<data.list.length; i++) {

            strAdd += '<tr class="reply">';
                strAdd += '<td>';
                    strAdd += '<div class="replyArea">';
                        strAdd += '<div class="replyHead flex">&nbsp;';
                            strAdd += '<input type="hidden" class="replyId" value="' + data.list[i].id + '">';
                            strAdd += '<b class="user">' + data.list[i].user_id + '</b>';
                            strAdd += '<span class="bar">|</span>';

                            strAdd += '<span class="time">'+ data.list[i].created_at;
                            if(data.list[i].modified_at != null) {
                                strAdd += '<b class="modifyAlarm">수정됨. 최종수정시각:<span class="modifyTime">' + data.list[i].modified_at + '</span></b>';
                            }
                            strAdd += '</span>';


                            if(user_id == data.list[i].user_id) {
                                strAdd += '<span class="bar">|</span>';
                                strAdd += '<span class="modifyDeleteArea time flex">';
                                    strAdd += '<span class="modify" data-rid="' + data.list[i].id + '">수정</span>';
                                    strAdd += '<span class="deleteReply" data-rid="' + data.list[i].id + '">삭제</span>';
                                strAdd += '</span>';
                            }

                        strAdd += '</div>';

                        strAdd += '<div id="replyContent' + data.list[i].id + '" class="replyContent">';
                            if(data.list[i].split_filename_num != null) {
                                strAdd2 = data.list[i].split_filename_num;
                            } else {
                                strAdd2 = '기타';
                            }
                            strAdd += '<b class="at">' + strAdd2 +'</b>';
                            strAdd += '<span id="content' + data.list[i].id + '" class="content">' + data.list[i].content + '</span>';
                        strAdd += '</div>';

                        strAdd += '<div id="modifyArea' + data.list[i].id + '" class="modifyArea inactive">';
                            strAdd += '<textarea id="replyModify' + data.list[i].id + '" class="form-control col-sm-5 replyModify" data-rid="' + data.list[i].id + '" rows="5" style="margin:10px 0;" maxlength="500">' + data.list[i].content + '</textarea>';
                            strAdd += '<button type="button" class="btn btn-success mod" data-rid="' + data.list[i].id + '">수정하기</button>';
                            strAdd += '&nbsp;<button type="button" class="btn btn-success modCancel" data-rid="' + data.list[i].id + '">수정취소</button>';
                            strAdd += '<span class="textLengthWrap">';
                                strAdd += '<span id="modifyCount' + data.list[i].id + '" class="textCount">0자</span><span class="textTotal">/500자</span>';
                            strAdd += '</span>';
                        strAdd += '</div>';

                        strAdd += '<div data-id="' + data.list[i].id + '" class="reReplyCount">답글 <b class="count" id="count' + data.list[i].id + '">' + data.list[i].list2.length + '</b></div>';

                    strAdd += '</div>';

                    //if(data.list[i].list2.length <= 0) {
                        //$('#reReplyDiv'+ reply_id).html('');
                        //$('#count'+ reply_id).text('0'); //여기 다시적기..
                        //continue;
                    //}

                    strAdd += '<div id="reReplyArea' + data.list[i].id + '" class="reReplyArea inactive">';
                    strAdd += '<div class="reReplyDiv" id="reReplyDiv'+ data.list[i].id +'">';

                    //console.log('안녕: ', data.list[i].list2[0]);
                    //console.log('안녕1: ', data.list[i].list2[1]);

                    for(let j=0; j<data.list[i].list2.length; j++) {
                        if(data.list[i].list2[j] != undefined) { //대댓글 달린 것만 for문돌리기 (대댓글 안달렸으면 undefined로 뜸)
                            for(key in data.list[i].list2[j]) { //처음에는 j=0으로만해서 돌려봄..그랬더니 대댓글 1개만 출력함

                                strAdd += '<div class="reReply reReply' + data.list[i].list2[j][key].id + '">';
                                    strAdd += '<span class="reReplyHead">';
                                        strAdd += '<b class="user">' + data.list[i].list2[j][key].user_id + '</b>';
                                        strAdd += '<span class="bar">|</span>';
                                        strAdd += '<span class="time">' + data.list[i].list2[j][key].created_at + '</span>';
                                    strAdd += '</span>';

                                    strAdd += '<span class="reReplyContent">';
                                        strAdd += '<span class="span_content">' + data.list[i].list2[j][key].content +'</span>';
                                        strAdd += '&nbsp;<span class="deleteReReply time" data-id="' + data.list[i].list2[j][key].id +'" data-rid="' + data.list[i].id + '">삭제</span>';
                                    strAdd += '</span>';
                                strAdd += '</div>';

                            } //endfor
                        } //endif
                    }//endfor

                    strAdd += '</div>';

                    strAdd += '<div class="reReplyWriteArea flex">';
                        strAdd += '<input type="hidden" class="replyId" value="' + data.list[i].id +'">';
                        strAdd += '<textarea id="reReplyWrite' + data.list[i].id + '" class="form-control col-sm-5 reReplyWrite" rows="1" maxlength="300" style="margin:10px 0; width: 90%;" placeholder="🍉 답글을 작성해 주세요."></textarea>';
                        strAdd += '<button type="button" class="btn btn-success reReplyRegistBtn">답글등록</button>';
                        strAdd += '<span class="textLengthWrap inactive">';
                            strAdd += '<span id="textCount' + data.list[i].id + '" class="textCount">0자</span><span class="textTotal">/300자</span>';
                        strAdd += '</span>';
                    strAdd += '</div>';

                    strAdd += '<div id="reReplyFold' + data.list[i].id + '" class="reReplyFold" data-rid="' + data.list[i].id + '">';
                        strAdd += '<b style="color: #727272">답글접기 🛆</b>';
                    strAdd += '</div>';
                strAdd += '</div>';
                strAdd += '</td>';
            strAdd += '</tr>';

            }

            $('#replyList').html(strAdd);


            //댓글 페이징 처리
            let pageStrAdd = '';
            $('#pageList').html('');

            pageStrAdd += '<ul class="pagination justify-content-center">';

                if(data.calculate_list.prev) {
                    pageStrAdd += '<li class="page-item">';
                        pageStrAdd += '<a class="page-link" aria-label="Previous">';
                            pageStrAdd += '<span aria-hidden="true">&laquo;</span>';
                        pageStrAdd += '</a>';
                    pageStrAdd += '</li>';
                }

                for(let i=0; i<data.calculate_list.nums.length; i++) {

                    let reply_pagenum = data.calculate_list.nums[i];

                    if(reply_pagenum == data.page_list.pagenum) {
                        pageStrAdd += '<li class="page-item active"><a class="page-link">' + reply_pagenum+ '</a></li>';
                    } else {
                        pageStrAdd += '<li class="page-item"><a class="page-link">' + reply_pagenum + '</a></li>';
                    }

                }

                if(data.calculate_list.next) {
                    pageStrAdd += '<li class="page-item">';
                        pageStrAdd += '<a class="page-link" aria-label="Next">';
                            pageStrAdd += '<span aria-hidden="true">&raquo;</span>';
                        pageStrAdd += '</a>';
                    pageStrAdd += '</li>';
                }
            pageStrAdd += '</ul>';

            $('#pageList').html(pageStrAdd);

        },
        error: function(request, status, error) {
            console.log("에러: ", error);
            alert("잘못된 입력입니다.");
        },
        complete: function() {
            console.log("완료");
        }
    }); //end ajax
}

//댓글 등록
$('#replyRegistBtn').click(function() {
    let board_id = $('#num').val();
    let reply_content = $('#replyWrite').val();
    let trim_reply_content = reply_content.trim();
    let selected = $("#splitNumSelect option:selected");

    if(selected.text() == '선택') {
        alert('댓글 구분을 선택해 주세요.');
        return;
    }

    if(trim_reply_content.length <= 0){
        alert('댓글을 입력해 주세요.');
        return;
    }

    let split_filename;
    if(selected.text() == '선택' || selected.text() == '기타') {
        split_filename = null;
    } else {
        split_filename = selected.attr("data-filename");
    }


    $.ajax({
        url: "/reply/regist",
        data: {
            board_id: board_id,
            reply_content: reply_content,
            split_filename: split_filename
        },
        method: "POST",
        success: function(data) {
            console.log("성공");
            alert("댓글이 등록되었습니다.");

            // 비동기방식으로 댓글 등록하기
            $('#replyWrite').val(''); //댓글입력창 초기화
            $("#splitNumSelect option:eq(0)").prop('selected', true);
            $('.textCount').text('0자');

            $("#splitNumSelect2 option:eq(0)").prop('selected', true);
            $("#selectOrder option:eq(0)").prop('selected', true);

            getReplyList(board_id, 1);
        },
        error: function(request, status, error) {
            console.log("에러: ", error);
            alert("잘못된 입력입니다.");
        },
        complete: function() {
            console.log("완료");
        }
    }); //end ajax


}); // end $('#replyRegistBtn').click

//댓글 수정
$(document).on('click', '.mod', function(event){

    let board_id = $('#num').val();
    let reply_id = $(this).parent().siblings('.replyHead').children('.replyId').val();
    let reply_content = $(this).siblings('.replyModify').val();
    let trim_reply_content = reply_content.trim();
    let pagenum = $('#page_list').attr('data-pagenum');

    if(trim_reply_content.length <= 0){
        alert('댓글을 입력해 주세요.');
        return;
    }

    $.ajax({
        url: "/reply/modify",
        data: {
            reply_id: reply_id,
            reply_content: reply_content
        },
        method: "POST",
        success: function(data) {
            console.log("성공");
            alert("댓글이 수정되었습니다.");

            //비동기방식 댓글 수정
            getReplyList(board_id, pagenum);
        },

        error: function(request, status, error) {
            console.log("에러: ", error);
            alert("잘못된 입력입니다.");
        },
        complete: function() {
            console.log("완료");
        }
    }); //end ajax
}); // end $('.mod').click


//댓글 삭제
$(document).on('click', '.deleteReply', function(event){

    let board_id = $('#num').val();
    let reply_id = $(this).attr('data-rid');
    let pagenum = $('#page_list').attr('data-pagenum');

    let result = confirm('정말 삭제하시겠습니까?');
    if(!result) {
        return;
    }

    $.ajax({
        url: "/reply/delete",
        data: {
            reply_id: reply_id
        },
        method: "POST",
        success: function(data) {
            console.log("성공");
            alert("댓글이 삭제되었습니다.");
            getReplyList(board_id, 1);
        },

        error: function(request, status, error) {
            console.log("에러: ", error);
            alert("잘못된 입력입니다.");
        },
        complete: function() {
            console.log("완료");
        }
    }); //end ajax
}); // end $('.deleteReply').click


//대댓글목록 출력하는 함수
function getList(reply_id) {
    $.ajax({
        url: "/reReply/list/" + reply_id,
        method: "POST",
        success: function(data) {
            console.log("성공");
            //console.log(data.list.length);
            //console.log(data.list);

            if(data.list.length <= 0) {
                $('#reReplyDiv'+ reply_id).html('');
                $('#count'+ reply_id).text('0');
                return;
            }

            $('#count'+ reply_id).text(data.list.length);
            let strAdd = '';
            let user_id = $('#user_id').val();
            for(let i=0; i<data.list.length; i++) {

                strAdd += '<div class="reReply" id= reReply' + data.list[i].id + '>';
                    strAdd += '<span class="reReplyHead">';
                        strAdd += '<b class="user">' + data.list[i].user_id + '</b>';
                        strAdd += '<span class="bar">|</span>';
                        strAdd += '<span class="time">' + data.list[i].created_at + '</span>';
                    strAdd += '</span>';

                    strAdd += '<span class="reReplyContent">';
                        strAdd += '<span class="span_content">'+ data.list[i].content +'</span>';
                        if(user_id == data.list[i].user_id) {
                            strAdd += '&nbsp;<span class="deleteReReply time" data-id="' + data.list[i].id + '"data-rid="' + reply_id + '">삭제</span>';
                        }
                    strAdd += '</span>';
                strAdd += '</div>';

            }
            $('#reReplyDiv'+ reply_id).html(strAdd);


        },
        error: function(request, status, error) {
            console.log("에러: ", error);
            alert("잘못된 입력입니다.");
        },
        complete: function() {
            console.log("완료");
        }
    }); //end ajax
}

//대댓글 등록
$(document).on('click', '.reReplyRegistBtn', function(event){
    let reply_id = $(this).siblings('.replyId').val();
    let re_reply_content = $('#reReplyWrite' + reply_id).val();
    let trim_re_reply_content = re_reply_content.trim();

    if(trim_re_reply_content.length <= 0){
        alert('답글을 입력해 주세요.');
        return;
    }

    $.ajax({
        url: "/reReply/regist/" + reply_id,
        data: {
            re_reply_content: re_reply_content
        },
        method: "POST",
        success: function(data) {
            console.log("성공");
            alert("답글이 등록되었습니다.");

            // 비동기방식으로 댓글 등록하기
            $('#reReplyWrite' + reply_id).val(''); //댓글입력창 초기화
            $('#reReplyWrite' + reply_id).css('width', '90%');
            $('#reReplyWrite' + reply_id).attr('rows', '1');

            $('#reReplyWrite' + reply_id).parent().addClass('flex');
            $('#reReplyWrite' + reply_id).siblings('.textLengthWrap').addClass('inactive');
            $('#textCount' + reply_id).text('0자');

            getList(reply_id);
        },

        error: function(request, status, error) {
            console.log("에러: ", error);
            alert("잘못된 입력입니다.");
        },
        complete: function() {
            console.log("완료");
        }
    }); //end ajax

}); // end $('#reReplyRegistBtn').click


//대댓글 삭제
$(document).on('click', '.deleteReReply', function(event){

    let result = confirm('정말 삭제하시겠습니까?');
    if(!result) {
        return;
    }

    let reply_id = $(this).attr('data-rid');
    let re_reply_id = $(this).attr('data-id');

    $.ajax({
        url: "/reReply/delete/" + reply_id,
        data: {
            re_reply_id: re_reply_id
        },
        method: "POST",
        success: function(data) {
            console.log("성공");
            getList(reply_id);
        },

        error: function(request, status, error) {
            console.log("에러: ", error);
            alert("잘못된 입력입니다.");
        },
        complete: function() {
            console.log("완료");
        }
    }); //end ajax

}); // end $('.deleteReReply').click

//-----------------------------------------------------------------------------------------------
//댓글리스트 검색조건
$('#splitNumSelect2, #selectOrder, #countperpage').change(function() {
    let board_id = $('#num').val();
    getReplyList(board_id, 1);
}); // end $('#splitNumSelect2').click


//페이징된 댓글 버튼 클릭했을때 (1,2,3 등 클릭했을때)
$(document).on('click', '.page-link', function(event){
    if($(this).hasClass('page-link2')) {
        return;
    }
    let board_id = $('#num').val();
    let pagenum = $(this).text().trim();

    if(pagenum == '»') {
        let prev_pagenum = $(this).parent().prev().children('.page-link').text();
        pagenum = +prev_pagenum + 1;
    } else if(pagenum == '«') {
        let next_pagenum = $(this).parent().next().children('.page-link').text();
        pagenum = +next_pagenum - 1;
    }

    getReplyList(board_id, pagenum);
});
