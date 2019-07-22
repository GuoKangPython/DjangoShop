from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from Store.models import *

#密码加密
import hashlib
def setPassword(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    return md5.hexdigest()

#登录装饰器
def LoginVaild(fun):
    """
    进行登录校验
    如果cookie当中的username和session当中的username不一致，则认为用户不合法

    """
    def inner(request,*args,**kwargs):
        username = request.COOKIES.get("username")
        session_user = request.session.get("username")
        if username and session_user:
            user = Seller.objects.filter(username=username).first()
            if user and username == session_user:
                return fun(request,*args,**kwargs)
        return HttpResponseRedirect('/Store/login/')
    return inner


#注册
def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            seller = Seller()
            seller.username = username
            seller.password = setPassword(password)
            seller.save()
            return HttpResponseRedirect("/Store/login/")
    return render(request,'store/register.html')

#登录
def login(request):
    """

    登录功能，如果登陆成功，跳转到首页
    如果失败，跳转到登录页

    """
    response = render(request,"store/login.html")
    response.set_cookie("login_form","login_page")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username and password:
            user = Seller.objects.filter(username=username).first()
            if user:
                web_password = setPassword(password)
                cookies = request.COOKIES.get("login_form")
                if user.password == web_password and cookies =="login_page":
                    response = HttpResponseRedirect('/Store/index/')
                    response.set_cookie("username",username)
                    request.session['username'] = username
                    return response
    return response

def index(request):
    return render(request,'store/index.html')
# Create your views here.
