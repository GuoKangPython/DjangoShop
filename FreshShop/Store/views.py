from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from Store.models import *
from django.core.paginator import Paginator
from Buyer.models import *

#密码加密
import hashlib
#密码加密
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
        if username and session_user and username== session_user:
            user = Seller.objects.filter(username=username).first()
            if user:
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
            seller.nickname = username
            seller.save()
            return HttpResponseRedirect("/Store/login/")
    return render(request,'store/register.html')

#登录
def login(request):
    """
    登陆功能，如果登陆成功，跳转到首页
    如果失败，跳转到登陆页
    """
    response = render(request,"store/login.html")
    response.set_cookie("login_from","login_page")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username and password:
            user = Seller.objects.filter(username = username).first()
            if user:
                web_password = setPassword(password)
                cookies = request.COOKIES.get("login_from")
                if user.password == web_password and cookies == "login_page":
                    response = HttpResponseRedirect("/Store/index/")
                    response.set_cookie("username",username)
                    response.set_cookie("user_id", user.id) #cookie提供用户id方便其他功能查询
                    request.session["username"] = username
                    #校验是否有店铺
                    store = Store.objects.filter(user_id=user.id).first()
                    if store:
                        response.set_cookie('has_store',store.id)
                    else:
                        response.set_cookie("has_store","")
                    return response
    return response

#首页
@LoginVaild
def index(request):
    """
    添加检查账号是否有店铺的逻辑
    """
    #查询当前用户是谁
    return render(request,"store/index.html")
# Create your views here.

#模板页
def base(request):
    return render(request,"store/base.html")

#注册店铺
@LoginVaild
def register_store(request):
    type_list = StoreType.objects.all()
    if request.method == "POST":
        post_data = request.POST #接收post数据
        store_name = post_data.get("store_name")
        store_description = post_data.get("store_description")
        store_phone = post_data.get("store_phone")
        store_money = post_data.get("store_money")
        store_address = post_data.get("store_address")

        user_id =int(request.COOKIES.get("user_id")) #通过cookie来得到user_id
        type_list = post_data.get("type") #通过request.post得到类型，但是是一个列表

        store_logo = request.FILES.get("store_logo") #通过request.FILES得到

        #保存非多对多数据
        store = Store()
        store.store_name = store_name
        store.store_description = store_description
        store.store_phone = store_phone
        store.store_money = store_money
        store.store_address = store_address
        store.user_id = user_id
        store.store_logo = store_logo #django1.8之后图片可以直接保存
        store.save() #保存，生成了数据库当中的一条数据
        #在生成的数据当中添加多对多字段。
        for i in type_list: #循环type列表，得到类型id
            store_type = StoreType.objects.get(id = i) #查询类型数据
            store.type.add(store_type) #添加到类型字段，多对多的映射表
        store.save() #保存数据
        response = HttpResponseRedirect("/Store/index/")
        response.set_cookie("has_store",store.id)
        return response
    return render(request,"store/register_store.html",locals())

@LoginVaild
#添加商品
def goods_add(request):
    """
    负责添加商品

    """
    goods_type_list = GoodsType.objects.all()
    if request.method=="POST":
        #获取POST请求
        goods_name = request.POST.get("goods_name")
        goods_price = request.POST.get("goods_price")
        goods_number = request.POST.get("goods_number")
        goods_description = request.POST.get("goods_description")
        goods_date = request.POST.get("goods_date")
        goods_safeDate = request.POST.get("goods_safeDate")
        goods_type = request.POST.get("goods_type")
        goods_store = request.POST.get("goods_store")
        goods_image = request.FILES.get("goods_image")
        #开始保存数据
        goods = Goods()
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number = goods_number
        goods.goods_description = goods_description
        goods.goods_date = goods_date
        goods.goods_safeDate = goods_safeDate
        goods.goods_image = goods_image
        goods.goods_type = GoodsType.objects.get(id=int(goods_type))
        goods.store_id = Store.objects.get(id=int(goods_store))
        goods.save()
        return HttpResponseRedirect("/Store/lists_goods/up/")
    return render(request,'store/goods_add.html',locals())

@LoginVaild
#商品列表
def lists_goods(request,state):
    """

    :param request:
    :param state: 商品状态
        up 在售
        down 下架
    :return:
    """
    if state == "up":
        state_num = 1
    else:
        state_num = 0
    keywords = request.GET.get("keywords","")#根据关键字进行模糊查询
    page_num = request.GET.get("page_num",1)#分页

    #查询店铺
    store_id = request.COOKIES.get("has_store")
    store = Store.objects.get(id=int(store_id))
    if keywords:
        goods_lists = store.goods_set.filter(goods_name__contains=keywords,goods_under=state_num)
    else:
        goods_lists = store.goods_set.filter(goods_under=state_num)
    #分页 每页3条信息
    paginator = Paginator(goods_lists,3)
    page = paginator.page(int(page_num))
    page_range = paginator.page_range

    return render(request, 'store/lists_goods.html',locals())

@LoginVaild
#商品详情
def goods(request,goods_id):
    goods_data = Goods.objects.filter(id = goods_id).first()
    return render(request,"store/goods.html",locals())

@LoginVaild
#修改商品详情
def update_goods(request,goods_id):
    goods_data = Goods.objects.filter(id=goods_id).first()
    if request.method == "POST":
        # 获取post请求
        goods_name = request.POST.get("goods_name")
        goods_price = request.POST.get("goods_price")
        goods_number = request.POST.get("goods_number")
        goods_description = request.POST.get("goods_description")
        goods_date = request.POST.get("goods_date")
        goods_safeDate = request.POST.get("goods_safeDate")
        goods_image = request.FILES.get("goods_image")
        # 开始修改数据
        goods = Goods.objects.get(id = int(goods_id)) #获取当前商品
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number = goods_number
        goods.goods_description = goods_description
        goods.goods_date = goods_date
        goods.goods_safeDate = goods_safeDate
        if goods_image: #如果有上传图片再发起修改
            goods.goods_image = goods_image
        goods.save()
        return HttpResponseRedirect("/Store/goods/%s/"%goods_id)
        # 保存多对多数据
    return render(request, "store/update_goods.html", locals())

#商品状态功能
def set_goods(request,state):
    """
    商品上下架以及销毁

    """
    if state == "up":
        state_num = 1
    else:
        state_num = 0

    id = request.GET.get("id")#get获取id
    referer = request.META.get("HTTP_REFERER")#返回当前请求的来源地址
    if id:
        goods = Goods.objects.filter(id = id).first()
        if state == "delete":
            goods.delete()
        else:
            goods.goods_under = state_num #修改状态
            goods.save()
    return HttpResponseRedirect(referer)


def logout(request):
    response = HttpResponseRedirect("/Store/login")
    for key in request.COOKIES:#获取当前所有的cookie
        response.delete_cookie(key)
    return response

@LoginVaild
def list_goods_type(request):
    goods_type_list = GoodsType.objects.all()
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        picture = request.FILES.get("picture")

        goods_type = GoodsType()
        goods_type.name = name
        goods_type.description = description
        goods_type.picture = picture
        goods_type.save()
    return render(request,"store/goods_type_list.html",locals())

@LoginVaild
def delete_goods_type(request):
    id = int(request.GET.get("id"))
    goods = GoodsType.objects.get(id = id)
    goods.delete()
    return HttpResponseRedirect("/Store/list_goods_type/")

def test_type_goods_type(request):
    name_list = [
        ("新鲜水果", "新鲜的水果，多vc多活力", "store/banner01.jpg"),
        ("海鲜水产", "水煮不用盐，高蛋白", "store/banner02.jpg"),
        ("猪牛羊肉", "刀刀见血，生性", "store/banner03.jpg"),
        ("禽类蛋品", "吃我的肉，吃我的蛋，我没有意见", "store/banner04.jpg"),
        ("新鲜蔬菜", "可以生吃，可以煮", "store/banner05.jpg"),
        ("速冻食品", "冻得刚刚好，不软也不硬", "store/banner06.jpg"),
    ]
    for name,description,img in name_list:
        goods = GoodsType()
        goods.name = name
        goods.description = description
        goods.picture = img
        goods.save()
    return HttpResponseRedirect("/Store/list_goods_type/")

def order_list(request):
    store_id = request.COOKIES.get("has_store")
    order_list = OrderDetail.objects.filter(order_id__order_status=2,goods_store=store_id)
    return render(request,"store/order_list.html",locals())


