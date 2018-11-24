from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, reverse
from django.forms import model_to_dict
import json
# from utils import token as toto
from utils import token as toto
from user.models import AddCourse
from user.models import UserInfo
from action.models import CourseAction
from action.models import ActionLibrary
from user import models as user_models
from course import models as course_models
from . import models
from datetime import datetime

# Create your views here.
def index(request):
    pass

def getCourse(request):
    try:
        # 获取课程信息
        course = list(
            course_models.Course.objects.all().values('id', 'name', 'consume_total', 'minute_avg', 'machine__name',
                                                      'picture__url'))
        return HttpResponse(json.dumps(course[0:20], ensure_ascii=False))

    except Exception as ex:
        return JsonResponse({"code": "404"})


# 搜索课程
def search(request, index, cname):
    # 获取类型为tid的全部对象
    # 每页显示数据
    pagesize = 12
    # 当前页码索引
    index = int(index)
    # 开始页码
    start = pagesize * (index - 1)
    # 结束页码
    end = pagesize * index
    # 判断是否有搜索课程名
    if cname:
        # 获取课程数据
        courses = models.Course.objects.order_by('-useraddcount').filter(name__icontains=cname)[start:end].values('id', 'name', 'day',
                                                                                        'type__type_name',
                                                                                        'level__level', 'picture__url')
    else:
        courses = models.Course.objects.order_by('-useraddcount').all()[start:end].values('id', 'name', 'day', 'type__type_name', 'level__level',
                                                                'picture__url')

    # # 遍历每个对象
    for c in courses:
        # 获取课程用户添加数
        c["useradd"] = AddCourse.objects.filter(course_id=c["id"]).count()
        # 获取课程训练部位
        parts = models.CourseTrainPart.objects.filter(course_id=c["id"]).values('bodypart__bodypart')
        bodys = []
        # 一个课程可以训练多个部位
        for part in parts:
            bodys.append(part['bodypart__bodypart'])
        c["trainbody"] = bodys

    return HttpResponse(json.dumps(list(courses), ensure_ascii=False))


# 计算页码
def pagecount(request, con):
    try:
        # 判断是否有搜索内容
        if con:
            # 根据搜索内容模糊查询个数
            len = models.Course.objects.filter(name__icontains=con).count()
        else:
            # 查询所有个数
            len = models.Course.objects.all().count()
        return JsonResponse({"acount": len})
    except Exception as ex:
        return JsonResponse({"code": "500"})


# 获取课程类型
def getcoursefenlei(request):
    # 获取课程类型全部queryset对象
    types = models.CourseType.objects.all()
    # 新建list对数据封装
    types_list = []
    # 遍历每个对象
    for t in types:
        # 将每个对象转换为字典类型
        t_dict = model_to_dict(t)
        # 获取外键关联的url
        t_dict['picture_url'] = models.CoursePicture.objects.filter(id=t.picture_id).values('url')[0]['url']
        # 为字典添加key值
        t_dict['nums'] = models.Course.objects.filter(type_id=t.id).count()
        types_list.append(t_dict)

    return HttpResponse(json.dumps(types_list, ensure_ascii=False))


# 通过课程类型id获取课程
def getCourseByTypeid(request, index, tid):
    # 获取类型为tid的全部对象
    # 每页显示数据
    pagesize = 6
    # 当前索引
    index = int(index)
    # 开始位置
    start = pagesize * (index - 1)
    # 结束位置
    end = pagesize * index
    # 获取课程信息
    courses = models.Course.objects.filter(type_id=tid)[start:end].values('id', 'name', 'day', 'type__type_name',
                                                                          'level__level', 'picture__url')
    course_list = []
    # 遍历每个对象
    for c in courses:
        # 获取课程添加人数
        c["useradd"] = AddCourse.objects.filter(course_id=c["id"]).count()
        # 获取课程训练部位
        parts = models.CourseTrainPart.objects.filter(course_id=c["id"]).values('bodypart__bodypart')
        bodys = []
        # 一个课程训练多个动作
        for part in parts:
            bodys.append(part['bodypart__bodypart'])
        c["trainbody"] = bodys
    return HttpResponse(json.dumps(list(courses), ensure_ascii=False))


# 通过课程类型id获取课程数目
def pagecountbytid(request, con):
    try:
        if con:
            # 根据类型id 获取课程数
            len = models.Course.objects.filter(type_id=con).count()
        else:
            # 获取所有课程数
            len = models.Course.objects.all().count()
        return JsonResponse({"acount": len})
    except Exception as ex:
        return JsonResponse({"code": "500"})


# 根据课程id获取课程信息

def getCourseInfoById(request):
    # 获取类型为tid的全部对象
    try:
        # 获取前台数据
        data = json.loads(request.body.decode('utf-8'))
        # 获取类型id
        cid = int(data['cid'])
        courses = models.Course.objects.filter(id=cid)
        course_list = []
        #
        for course in courses:
            course_dict = model_to_dict(course)
            course_dict["picture"] = courses.values('picture__url')[0]['picture__url']
            course_dict["level"] = courses.values('level__level')[0]['level__level']
            course_dict["picture"] = courses.values('picture__url')[0]['picture__url']
            course_dict["machine"] = courses.values('machine__name')[0]['machine__name']
            course_dict['type_name'] = courses.values('type__type_name')[0]['type__type_name']
            # 默认用户没添加过该课程
            course_dict["add_flag"] = False
            # 如果带有token
            if data['headers']['token']:
                token = data['headers']['token']
                # 解析token
                res = toto.openToken(token)
                # 解析成功
                if res:
                    # 查询用户是否添加过该课程
                    result = AddCourse.objects.filter(course_id=cid, user_id=res['user_id'])
                    if result:
                        # 用户添加过该课程
                        course_dict["add_flag"] = True
            # 获取客户添加人数
            course_dict["useradd"] = AddCourse.objects.filter(course_id=cid).count()
            # 获取课程训练部位
            parts = models.CourseTrainPart.objects.filter(course_id=cid).values('bodypart__bodypart')
            bodys = []
            for part in parts:
                bodys.append(part['bodypart__bodypart'])
            course_dict["trainbody"] = bodys
            course_list.append(course_dict)

        return HttpResponse(json.dumps(course_list, ensure_ascii=False))
    except Exception as ex:
        print(ex)


# 根据课程id 获取动作信息
def getActionByCid(request, cid):
    # 获取类型为tid的全部对象
    course = models.Course.objects.filter(id=cid)[0]
    # 将queryset对象转化为字典类型
    course_dict = model_to_dict(course)
    # 获取课程天数
    daymax = CourseAction.objects.filter(course_id=cid).latest('day_num').day_num
    days = []
    # 获取每天的动作信息
    for i in range(1, int(daymax) + 1):
        actions = CourseAction.objects.filter(course_id=cid, day_num=i).values('action__id', 'action__name',
                                                                               'action__times', 'action__picture__url')
        # 将每天的动作集合放到days
        days.append(list(actions))
    course_dict['days'] = days
    return JsonResponse(course_dict)


# 获取课程最新评论信息
def getCourseComment(request):
    try:
        if request.method == "POST":
            # 获取课程类型全部queryset对象
            data = json.loads(request.body.decode('utf-8'))
            # 获取token
            token = data['headers']['token']
            res = toto.openToken(token)
            # 获取课程id
            cid = data['cid']
            comments = models.CourseComment.objects.order_by('-time').filter(course_id=cid)
            # 新建list对数据封装
            comment_list = []
            # 遍历每个对象
            for c in comments:
                # 将每个对象转换为字典类型
                c_dict = model_to_dict(c)
                c_dict['id'] = models.CourseComment.objects.filter(id=c.id).values('id')[0]['id']
                c_dict['time'] = str(models.CourseComment.objects.filter(id=c.id).values('time')[0]["time"])[0:19]
                c_dict['like'] = models.CourseCommentLike.objects.filter(comment_id=c.id).count()
                c_dict['replynum'] = models.CourseCommentReply.objects.filter(comment_id=c.id).count()
                c_dict['deletecomment_flag'] = False
                c_dict['like_flag'] = False
                if res:
                    flag = models.CourseComment.objects.filter(id=c.id, user_id=res['user_id']).count()
                    flag1 = models.CourseCommentLike.objects.filter(comment_id=c.id, user_id=res['user_id']).count()
                    if flag1:
                        c_dict['like_flag'] = True
                    if flag:
                        c_dict['deletecomment_flag'] = True

                c_dict['username'] = UserInfo.objects.filter(user_id=c.user_id).values('name')[0]['name']
                c_dict['icon'] = UserInfo.objects.filter(user_id=c.user_id).values('icon__icon_url')[0][
                    'icon__icon_url']
                reply_list = []
                reply = models.CourseCommentReply.objects.order_by('-time').filter(comment_id=c.id)
                for r in reply:
                    r_dict = model_to_dict(r)
                    r_dict['time'] = str(models.CourseCommentReply.objects.filter(id=r.id).values('time')[0]["time"])[0:19]
                    r_dict['username'] = UserInfo.objects.filter(user_id=r.user_id).values('name')[0]['name']
                    r_dict['icon'] = UserInfo.objects.filter(user_id=r.user_id).values('icon__icon_url')[0][
                        'icon__icon_url']
                    r_dict['content'] = models.CourseCommentReply.objects.filter(id=r.id).values('content')[0][
                        'content']
                    c_dict['reply_flag'] = False
                    r_dict['deletereply_flag'] = False

                    if res:
                        flag = models.CourseCommentReply.objects.filter(comment_id=c.id, user_id=res['user_id']).count()
                        flag1 = models.CourseCommentReply.objects.filter(id=r.id, comment_id=r.comment_id,
                                                                         user_id=res['user_id']).count()
                        if flag:
                            c_dict['reply_flag'] = True
                        if flag1:
                            r_dict['deletereply_flag'] = True
                    reply_list.append(r_dict)
                c_dict['commnetreply'] = reply_list
                comment_list.append(c_dict)
            print(comment_list)
            return HttpResponse(json.dumps(comment_list, ensure_ascii=False))
    except Exception as ex:
        print(ex)
        return JsonResponse({"code": "404"})


# 获取热门课程评论信息
def getHotCourseComment(request):
    try:
        if request.method == "POST":
            # 获取课程类型全部queryset对象
            data = json.loads(request.body.decode('utf-8'))
            cid = data['cid']
            token = data['headers']['token']
            res = toto.openToken(token)
            # 解析token
            # 判断是否登录
            comments = models.CourseComment.objects.order_by('-likes').filter(course_id=cid)
            # 新建list对数据封装
            comment_list = []
            # 遍历每个对象
            for c in comments:
                # 将每个对象转换为字典类型
                c_dict = model_to_dict(c)
                c_dict['id'] = models.CourseComment.objects.filter(id=c.id).values('id')[0]['id']
                c_dict['time'] = models.CourseComment.objects.filter(id=c.id).values('time').values('time')[0][
                    'time'].strftime('%Y-%m-%d %H:%I:%S')
                c_dict['like'] = models.CourseCommentLike.objects.filter(comment_id=c.id).count()
                c_dict['replynum'] = models.CourseCommentReply.objects.filter(comment_id=c.id).count()
                c_dict['deletecomment_flag'] = False
                c_dict['like_flag'] = False
                if res:
                    flag = models.CourseComment.objects.filter(id=c.id, user_id=res['user_id']).count()
                    flag1 = models.CourseCommentLike.objects.filter(comment_id=c.id, user_id=res['user_id']).count()
                    if flag1:
                        c_dict['like_flag'] = True
                    if flag:
                        c_dict['deletecomment_flag'] = True

                c_dict['username'] = UserInfo.objects.filter(user_id=c.user_id).values('name')[0]['name']
                c_dict['icon'] = UserInfo.objects.filter(user_id=c.user_id).values('icon__icon_url')[0][
                    'icon__icon_url']
                reply_list = []
                reply = models.CourseCommentReply.objects.order_by('-time').filter(comment_id=c.id)
                for r in reply:
                    r_dict = model_to_dict(r)
                    r_dict['time'] = models.CourseCommentReply.objects.filter(id=r.id).values('time').values('time')[0][
                        'time'].strftime('%Y-%m-%d %H:%I:%S')
                    r_dict['username'] = UserInfo.objects.filter(user_id=r.user_id).values('name')[0]['name']
                    r_dict['icon'] = UserInfo.objects.filter(user_id=r.user_id).values('icon__icon_url')[0][
                        'icon__icon_url']
                    r_dict['content'] = models.CourseCommentReply.objects.filter(id=r.id).values('content')[0][
                        'content']
                    c_dict['reply_flag'] = False
                    r_dict['deletereply_flag'] = False

                    if res:
                        flag = models.CourseCommentReply.objects.filter(comment_id=c.id, user_id=res['user_id']).count()
                        flag1 = models.CourseCommentReply.objects.filter(id=r.id, comment_id=r.comment_id,
                                                                         user_id=res['user_id']).count()
                        if flag:
                            c_dict['reply_flag'] = True
                        if flag1:
                            r_dict['deletereply_flag'] = True
                    reply_list.append(r_dict)
                c_dict['commnetreply'] = reply_list
                comment_list.append(c_dict)
            return HttpResponse(json.dumps(comment_list[0:3], ensure_ascii=False))
    except Exception as ex:
        print(ex)
        return JsonResponse({"code": "404"})


# 回复评论
def replyComment(request):
    try:
        # 需要 评论id 评论内容 token
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            content = data['content']
            comment_id = int(data['comment_id'])
            token = data['headers']['token']
            res = toto.openToken(token)
            if res:
                addcomment = {
                    'comment_id': comment_id,
                    'user_id': res['user_id'],
                    'content': content,
                    'time':datetime.utcnow()
                }
                models.CourseCommentReply.objects.create(**addcomment)
                return JsonResponse({"code": "210"})
            else:
                return JsonResponse({"code": "没登陆"})

    except Exception as ex:
        print(ex)
        return JsonResponse({"code": "404"})


# 删除课程评论
def delCourseComment(request):
    try:
        # 需要 评论id  token
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            comment_id = int(data['commentid'])
            token = data['headers']['token']
            res = toto.openToken(token)
            if res:
                models.CourseComment.objects.filter(id=comment_id).delete()
                return JsonResponse({"code": "210"})
            else:
                return JsonResponse({"code": "没登陆"})

    except Exception as ex:
        print(ex)
        return JsonResponse({"code": "404"})


# 删除回复
def delCourseReply(request):
    try:
        # 需要 回复id  token
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            replyid = int(data['replyid'])
            token = data['headers']['token']
            res = toto.openToken(token)
            if res:
                models.CourseCommentReply.objects.filter(id=replyid).delete()
                return JsonResponse({"code": "210"})
            else:
                return JsonResponse({"code": "没登陆"})

    except Exception as ex:
        print(ex)
        return JsonResponse({"code": "404"})


# 添加课程
def addCourse(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            course_id = int(data['cid'])
            token = data['headers']['token']
            # 解析token
            res = toto.openToken(token)
            if res:
                result = user_models.AddCourse.objects.filter(course_id=course_id, user_id=res['user_id']).values()
                addnum = models.Course.objects.filter(id=course_id).values('useraddcount')[0]['useraddcount']
                if result:
                    user_models.AddCourse.objects.filter(course_id=course_id, user_id=res['user_id']).delete()
                    res = addnum - 1
                    models.Course.objects.filter(id=course_id).update(useraddcount =res)
                    return JsonResponse({"code": "410"})
                else:
                    addcourse = {
                        'course_id': course_id,
                        'user_id': res['user_id']
                    }
                    user_models.AddCourse.objects.create(**addcourse)
                    res = addnum + 1
                    models.Course.objects.filter(id=course_id).update(useraddcount=res)
                    return JsonResponse({"code": "210"})
    except Exception as ex:
        print(ex)
        return JsonResponse({"code": "404"})


def delCourse(request):
    pass
