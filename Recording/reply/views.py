import math

from django.http import HttpResponse, JsonResponse
from django.utils import timezone, dateformat
from rest_framework import status
from rest_framework.views import APIView

from reply import models

def calculate_page(pagenum, countperpage, total_count):
    button_num = 10 #버튼 한페이지에 10개만 보여줌
    #print('total_count: ', total_count)
    end_page = (math.ceil(pagenum / button_num)) * button_num
    #print('end_page: ', end_page)
    begin_page = (end_page - button_num) + 1
    #print('begin_page: ', begin_page)
    prev = False if begin_page == 1 else True
    #print('prev: ', prev)
    next = False if end_page * countperpage >= total_count else True
    #print('next: ', next)
    if next == False :
        end_page = math.ceil(total_count / countperpage)
        #print('end_page: ', end_page)

    nums = []
    for num in range(begin_page, end_page + 1):
        nums.append(num)

    #print('nums: ', nums)

    calculate_list = dict(end_page=end_page, begin_page=begin_page, nums=nums, prev=prev, next=next)
    return calculate_list

class Reply(APIView):
    def post(self, request, condition):
        if condition == 'regist':
            user_id = request.session.get('id_session', None)
            board_id = request.POST.get('board_id', None)
            content = request.POST.get('reply_content', None)
            #print('content: ', content)
            split_filename = request.POST.get('split_filename', None)
            if split_filename == '':
                split_filename = None
            models.Reply.objects.create(user_id=user_id, board_id=board_id, content=content, split_filename=split_filename)
            return HttpResponse(status=status.HTTP_200_OK)
        elif condition == 'list':
            board_id = request.POST.get('board_id', None)
            #print('board_id: ', board_id)
            split_filename = request.POST.get('split_filename', None)
            select_order = request.POST.get('select_order', None)
            countperpage = int(request.POST.get('countperpage', None))
            pagenum = int(request.POST.get('pagenum', 1))

            if select_order == 'new':
                order = '-id'
            else:  # select_order == 'old'
                order = 'id'

            if split_filename == 'splitEtc':
                split_filename = None

            if split_filename == 'splitTotal':
                reply_list = models.Reply.objects.filter(board_id=board_id).order_by(order)
                total_count = len(reply_list)
                #print('total_count: ', total_count)
            else:
                reply_list = models.Reply.objects.filter(board_id=board_id, split_filename=split_filename).order_by(order)
                total_count = len(reply_list)
                #print('total_count: ', total_count)

            if total_count == 0:
                return JsonResponse({'message': 'fail'})


            calculate_list = calculate_page(pagenum, countperpage, total_count)

            #-----------------------------------------------------------------
            # 1페이지고 10개씩 보기라면 글은 0~9번 인덱스를 불러와야함..그거 계산해주는 것임 (sql문이었다면 일종의 ..rownum매긴 후에 10개씩 불러오는..그런거..?_ㅇ
            begin_index = (pagenum - 1) * countperpage
            end_index = (pagenum * countperpage)
            print(begin_index, end_index)

            if pagenum == calculate_list['end_page'] and calculate_list['next'] is False:
                end_index = total_count
            #------------------------------------------------------------------

            list = []


            for i in range(begin_index, end_index):
            #for reply in reply_list:

                re_reply_list = models.ReReply.objects.filter(reply_id=reply_list[i].id).order_by('id')  # 해당 댓글의 대댓글목록 출력
                list2 = []
                for re_reply in re_reply_list:
                    rcreated_at = dateformat.format(re_reply.created_at, 'Y-m-d H:i')

                    if '\n' in re_reply.content:
                        rcontent = re_reply.content.replace('\n', '<br>')
                    else:
                        rcontent = re_reply.content

                    re_re_reply_list = []
                    re_re_reply_list.append(dict(id=re_reply.id,
                                                 reply_id=re_reply.reply_id,
                                                 user_id=re_reply.user_id,
                                                 content=rcontent,
                                                 created_at=rcreated_at))
                    list2.append(re_re_reply_list)


                #print('reply: ', reply)
                created_at = dateformat.format(reply_list[i].created_at, 'Y-m-d H:i')
                if reply_list[i].modified_at == None:
                    modified_at = None
                else:
                    modified_at = dateformat.format(reply_list[i].modified_at, 'Y-m-d H:i')

                if reply_list[i].split_filename == None:
                    split_filename_num = None
                else:
                    split_filename_num = reply_list[i].split_filename.split('_')[-1].split('.')[0]

                if '\n' in reply_list[i].content:
                   content = reply_list[i].content.replace('\n', '<br>')
                else:
                   content = reply_list[i].content

                list.append(dict(id=reply_list[i].id,
                                 user_id=reply_list[i].user_id,
                                 content=content,
                                 created_at=created_at,
                                 modified_at=modified_at,
                                 split_filename_num=split_filename_num,
                                 list2=list2))



            page_list = dict(countperpage=countperpage, pagenum=pagenum, total_count=total_count)

            #print('page_list: ', page_list)
            #print('calculate_list: ', calculate_list)
            #print('list: ', list)

            return JsonResponse({'list': list, 'page_list': page_list, 'calculate_list': calculate_list, 'message': 'success'})

        elif condition == 'modify':
            reply_id = request.POST.get('reply_id', None)
            content = request.POST.get('reply_content', None)
            modified_at = timezone.now()
            models.Reply.objects.filter(id=reply_id).update(content=content, modified_at=modified_at)
            return HttpResponse(status=status.HTTP_200_OK)

        elif condition == 'delete':
            reply_id = request.POST.get('reply_id', None)
            models.Reply.objects.filter(id=reply_id).delete()
            models.ReReply.objects.filter(reply_id=reply_id).delete()
            return HttpResponse(status=status.HTTP_200_OK)


class ReReply(APIView):
    def post(self, request, condition, reply_id):
        if condition == 'regist':
            user_id = request.session.get('id_session', None)
            reply_id = reply_id
            content = request.POST.get('re_reply_content', None)
            models.ReReply.objects.create(user_id=user_id, reply_id=reply_id, content=content)
            return HttpResponse(status=status.HTTP_200_OK)

        elif condition == 'list':
            re_reply_list = models.ReReply.objects.filter(reply_id=reply_id).order_by('id')

            list = []
            for re_reply in re_reply_list:
                created_at = dateformat.format(re_reply.created_at, 'Y-m-d H:i')

                if '\n' in re_reply.content:
                    rcontent = re_reply.content.replace('\n', '<br>')
                else:
                    rcontent = re_reply.content

                list.append(dict(id=re_reply.id,
                                 user_id=re_reply.user_id,
                                 content=rcontent,
                                 created_at=created_at))
            return JsonResponse({'list': list})

        elif condition == 'delete':
            re_reply_id = request.POST.get('re_reply_id', None)
            models.ReReply.objects.filter(id=re_reply_id).delete()
            return HttpResponse(status=status.HTTP_200_OK)
