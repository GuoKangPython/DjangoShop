from django.urls import path,re_path
from Store.views import *

urlpatterns = [
    path('register/',register),
    path('login/',login),
    path('index/',index),
    path('logout/',logout),
    path('register_store/',register_store),
    path('goods_add/',goods_add),
    re_path(r'lists_goods/(?P<state>\w+)',lists_goods),
    re_path(r"^goods/(?P<goods_id>\d+)",goods),
    re_path(r"update_goods/(?P<goods_id>\d+)",update_goods),
    re_path(r'set_goods/(?P<state>\w+)',set_goods),
    path('list_goods_type/', list_goods_type),  # 设置商品状态
    path('delete_goods_type/', delete_goods_type),  # 设置商品状态
    path('order_list/',order_list),#订单管理页面
]

urlpatterns += [
    path('base/', base),
    path('gt/', test_type_goods_type),
]