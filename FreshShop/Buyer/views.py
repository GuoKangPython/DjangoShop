import time
from django.shortcuts import render
from django.shortcuts import HttpResponseRedirect,HttpResponse
from django.http import JsonResponse

from Buyer.models import *
from Store.views import setPassword
from Store.models import *

from alipay import AliPay

#登录校验器
def LoginVaild(fun):
    """
    进行登录校验
    如果cookie当中的username和session当中的username不一致，则认为用户不合法

    """
    def inner(request,*args,**kwargs):
        username = request.COOKIES.get("username")
        session_user = request.session.get("username")
        if username and session_user and username== session_user:
            return fun(request,*args,**kwargs)
        else:
            return HttpResponseRedirect('/Buyer/login/')
    return inner

#注册
def register(request):
    if request.method == "POST":
        #获取前端post请求的数据
        username = request.POST.get("user_name")
        password = request.POST.get("pwd")
        email = request.POST.get("email")
        #将数据存入数据库
        buyer = Buyer()
        buyer.username = username
        buyer.password = setPassword(password)
        buyer.email = email
        buyer.save()
        #注册成功后跳转到login页面
        return HttpResponseRedirect("/Buyer/login/")
    return render(request,"buyer/register.html")

#登录
def login(request):
    if request.method == "POST":
        #获取数据
        username = request.POST.get("username")
        password = request.POST.get("pwd")
        if username and password:
            #判断用户是否存在
            user = Buyer.objects.filter(username=username).first()
            if user:
                #密码加密对比
                web_password = setPassword(password)
                if user.password == web_password:
                    response = HttpResponseRedirect("/Buyer/index/")
                    #校验登录
                    response.set_cookie("username",user.username)
                    request.session["username"] = user.username
                    #f方便其他查询
                    response.set_cookie("user_id",user.id)
                    return response
    return render(request,"buyer/login.html")
# Create your views here.

#首页
@LoginVaild
def index(request):
    result_list = [] #定义一个容器来存放结果
    goods_type_list = GoodsType.objects.all()#查询所有类型
    for goods_type in goods_type_list:
        goods_list = goods_type.goods_set.values()[:4]
        if goods_list:
            goodsType={
                "id": goods_type.id,
                "name":goods_type.name,
                "description":goods_type.description,
                "picture":goods_type.picture,
                "goods_list":goods_list
            }
            result_list.append(goodsType)
    return render(request,"buyer/index.html",locals())

#退出
def logout(request):
    response = HttpResponseRedirect("/Buyer/index/")
    #删除所有的请求携带的cookie
    for key in request.COOKIES:
        response.delete_cookie(key)
    #删除session
    del request.session["username"]
    return response

def base(request):
    return render(request,"buyer/base.html")


def goods_list(request):
    """
    前台列表页
    :param reuqest:
    :return:
    """
    goodsList = []
    type_id = request.GET.get("type_id")
    #获取类型
    goods_type = GoodsType.objects.filter(id = type_id).first()
    if goods_type:
        #查询所有上架的产品
        goodsList = goods_type.goods_set.filter(goods_under=1)

    return render(request,"buyer/goods_list.html",locals())

def pay_order(request):
    money = request.GET.get("money")#获取订单金额
    order_id = request.GET.get("order_id")#获取订单号
    alipay_public_key_string = """-----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArPwRWXdLoaaWmE
    /s+Z7MRXEL5mzYolX+2CW9wT+kePp/bc549dX4jf8YNLpDIF1xjA1flLLhy
    b4x93tEggNA456X8sE6Q0PCXfDB/X1eAp4b+8xB1/7POdoBmUWjyZVKI3YE
    2Oidl5M6vX1h7N2q8zWTaj3URPSt8vYyxIzgXVPLk50MyfefwaahSyRTOKN
    F64ZuAvIBS1dp8zqap5Ig1v1Rv9LVJrcpxRx+88l3jlv1doV1212L52Lb8+
    Jkm2MA05xvURvefvMtxB32jVvp1n4WBbzP2HA+VQ1+s4RZPltbP7PnQa0GE
    Skes5aXX1lrOQp3LdQmzSEp2+QTEWL3QQIDAQAB
    -----END PUBLIC KEY-----"""

    app_private_key_string = """-----BEGIN RSA PRIVATE KEY-----
    MIIEogIBAAKCAQEArPwRWXdLoaaWmE/s+Z7MRXEL5mzYolX+2CW9wT+kePp/
    bc549dX4jf8YNLpDIF1xjA1flLLhyb4x93tEggNA456X8sE6Q0PCXfDB/X1e
    Ap4b+8xB1/7POdoBmUWjyZVKI3YE2Oidl5M6vX1h7N2q8zWTaj3URPSt8vYy
    xIzgXVPLk50MyfefwaahSyRTOKNF64ZuAvIBS1dp8zqap5Ig1v1Rv9LVJrcp
    xRx+88l3jlv1doV1212L52Lb8+Jkm2MA05xvURvefvMtxB32jVvp1n4WBbzP
    2HA+VQ1+s4RZPltbP7PnQa0GESkes5aXX1lrOQp3LdQmzSEp2+QTEWL3QQID
    AQABAoIBACtf9TW6vQMmk2JTwDcDQ3MyGmrH5jYmXAV0yTTYsXQIU8WD3T6/
    TVjFmxs1jTljVOJqRAo0JHuCrmLAzPfQuweYL7+WBfbx2Z3Wjb3zHoyHerrT
    h7sSUIHQEVCObrhQL8vefu6ovUNRjowPEWvkVUYwq+sa38v+klN2ulogfO3J
    eHPu9kWBv7P2qSk5O45K73YJgC0cpffrSNtF27nLBDZjYS8nxYBsfxWO2hyC
    GT/7z2pbqdFMQY6Oz2qlM4h4rkZtbhQiL9lXlvIRldKjSCwbLFuny2nwvG26
    X7Brp8Xt/ks0yQ9/A/5U1N4U6u/6ls6QykTEa8xVrvY5KZuCSwECgYEA3lXf
    PCBt+gtpa+Wj94f+BWYqR21w7XrTo+1Jw7sjiAwb942IiwGXBeZMncenyb8V
    AuIexs7g9Y02HGyJuQ91nuJI6zmusWxyw1JKgy/2R9DGnMd4zyt/po3bMvzk
    ZaGNH6VmaWV1oaOn2x8O9OgaeZ0xB8+hFDGuvY73ihqOX/ECgYEAxy1ExIT1
    kj5LleQV3hqyF6y+JrL3OQm+8Z5VTgKmneFdxKalYcZAyNhJIalQ/o0hWcS5
    XwnmRgRs7n2Rry50F9Gk87e1Zdjqv+HHnNy7uN6r/C6zTy3lQvpD/IAYUq2u
    PzLAdMYMD6UHdAvFM0DOhIq8JnPLx237TlBBfJmcXFECgYBdjxEjQhpFUCwK
    hVXcQdO4/eboq7sLk9YfcyjJPqSTCVVzdJFyvTaJ+wFem7eVg90Zm4GL815i
    tguBJoNF5qV+OIaqxVknvBUG8Ef+sF4YllgdfSrvMsTCl4sYB6csxTCXkohn
    7ZP0cuOdp5IpqMoLRwRs3whPcSCxD8pGySoEYQKBgBf0X9Lq0sYV6+1JE0A1
    IborMmthFs6rV2Wjz0qkkvlmA2sFR9qsh1ogeRstS+pxetNbD5hYjnNZUOiV
    /ZF+GsRKmHYfYBexsPoG44UAHyuqzDB2RWZ+dJZLlyWlGkfHT6+WIQNqVkUD
    ahQQ3lS9tJjIPry5LIb9uT2/9UBRETchAoGAa9oiEpjbWiHRyE+7pE8TtJGe
    g0m5vatEujj49H5B4FhpS3lC+9KuBwCvkB0TgxwKRP4ZLAoQXF0ER3NeiBjD
    64jQMtN6U7LV/kQSCcDbFKQU+GF8nhFbNuApyjlMMujJkm0fX5qB5RNbk5VZ
    Sjwsww0whs3BaZTi/CfDVWhT2Sw=
    -----END RSA PRIVATE KEY-----"""

    # 实例化支付应用
    alipay = AliPay(
        appid="2016101000652527",
        app_notify_url=None,
        app_private_key_string=app_private_key_string,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2"
    )

    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no="order_id", #订单号
        total_amount=str(money),  # 支付金额
        subject="生活消费",#交易主题
        return_url="http://127.0.0.1:8000/Buyer/pay_result/",  # 支付完成要跳转的本地路由
        notify_url="http://127.0.0.1:8000/Buyer/pay_result/"  # 支付完成要跳转的本地异步路由
    )

    return HttpResponseRedirect("https://openapi.alipaydev.com/gateway.do?" + order_string) #跳转支付路由

def pay_result(request):
    """
    支付宝成功支付自动用get请求返回的参数
    #编码
    charset=utf-8
    #订单号
    out_trade_no=10002
    #订单类型
    meithod=alipay.trade.page.pay.return
    #订单金额
    total_amount=1000.00
    #订单号
    trade_no=2019072622001422161000050134
    #用户的应用id
    auth_app_id=2016093000628355
    #版本
    version=1.0
    #商家的应用id
    app_id=2016093000628355
    #加密方式
    sign_type=RSA2
    #商家id
    seller_id=2088102177891440
    #时间
    timestamp=2019-07-26

    """
    return render(request,"buyer/pay_result.html",locals())

def goods_detail(request):
    goods_id = request.GET.get("goods_id")
    if goods_id:
        goods = Goods.objects.filter(id = goods_id).first()
        if goods:
            return  render(request,"buyer/detail.html",locals())
    return HttpResponse("没有找到指定商品")


def setOrderId(user_id,goods_id,store_id):
    """
    设置订单编号
    时间+用户id+商品的id+商铺+id
    """
    strtime = time.strftime("%Y%m%d%H%M%S",time.localtime())
    return strtime+str(user_id)+str(goods_id)+str(store_id)


def place_order(request):
    if request.method == "POST":
        #post数据
        count = int(request.POST.get("count"))
        goods_id = request.POST.get("goods_id")
        #cookie的数据
        user_id = request.COOKIES.get("user_id")
        #数据库的数据
        goods = Goods.objects.get(id = goods_id)
        store_id = goods.store_id.id
        price = goods.goods_price

        order = Order()
        order.order_id = setOrderId(str(user_id),str(goods_id),str(store_id))
        order.goods_count = count
        order.order_user = Buyer.objects.get(id = user_id)
        order.order_price = count*price
        order.order_status = 1
        order.save()

        order_detail = OrderDetail()
        order_detail.order_id = order
        order_detail.goods_id = goods_id
        order_detail.goods_name = goods.goods_name
        order_detail.goods_price = goods.goods_price
        order_detail.goods_number = count
        order_detail.goods_total = count*goods.goods_price
        order_detail.goods_store = store_id
        order_detail.goods_image = goods.goods_image
        order_detail.save()

        detail = [order_detail]
        return render(request, "buyer/place_order.html", locals())
    else:
        order_id = request.GET.get("order_id")
        if order_id:
            order = Order.objects.get(id = order_id)
            detail = order.orderdetail_set.all()
            return render(request,"buyer/place_order.html",locals())
        return HttpResponse("非法请求")

def cart(request):
    user_id = request.COOKIES.get("user_id")
    goods_list = Cart.objects.filter(user_id = user_id)
    if request.method == "POST":
        post_data = request.POST
        cart_data = [] #收集前端传递过来的商品
        for k,v in post_data.items():
            if k.startswith("goods_"):
                cart_data.append(Cart.objects.get(id=int(v)))
        goods_count = len(cart_data) #提交过来的数据的总数量
        goods_total = sum([int(i.goods_total) for i in cart_data])#订单的总价

        #保存订单
        order = Order()
        order.order_id = setOrderId(user_id,goods_count,"2")
        #订单中有多个商品或者多个店铺时，使用goods_count来代替商品id，用2来代替店铺id
        order.goods_count = goods_count
        order.order_user = Buyer.objects.get(id = user_id)
        order.order_price = goods_total
        order.order_status = 1
        order.save()

        #保存订单详情
        #这里的detail是购物车里的数据实例，不是商品的实例
        for detail in cart_data:
            order_detail = OrderDetail()
            order_detail.order_id = order #order是一条订单数据
            order_detail.goods_id = detail.goods_id
            order_detail.goods_name = detail.goods_name
            order_detail.goods_price = detail.goods_price
            order_detail.goods_number = detail.goods_number
            order_detail.goods_total = detail.goods_total
            order_detail.goods_store = detail.goods_store
            order_detail.goods_image = detail.goods_picture
            order_detail.save()

            #order是一条订单支付页
        url = "/Buyer/place_order/?order_id=%s"%order.id
        return HttpResponseRedirect(url)
    return render(request,"buyer/cart.html",locals())

def add_cart(request):
    result = {"state":"error","data":""}
    if request.method =="POST":
        count = int(request.POST.get("count"))
        goods_id = request.POST.get("goods_id")
        goods = Goods.objects.get(id = int(goods_id))

        user_id = request.COOKIES.get("user_id")

        cart = Cart()
        cart.goods_name = goods.goods_name
        cart.goods_price = goods.goods_price
        cart.goods_total = goods.goods_price*count
        cart.goods_number = count
        cart.goods_picture = goods.goods_image
        cart.goods_id = goods.id
        cart.goods_store = goods.store_id.id
        cart.user_id = user_id
        cart.save()
        result["state"] = "success"
        result["data"] = "商品添加成功"
    else:
        result["data"] = "请求错误"
    return JsonResponse(result)




