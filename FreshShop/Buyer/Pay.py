from alipay import AliPay

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



#实例化支付应用
alipay = AliPay(
    appid="2016101000652527",
    app_notify_url = None,
    app_private_key_string = app_private_key_string,
    alipay_public_key_string = alipay_public_key_string,
    sign_type = "RSA2"
)


order_string = alipay.api_alipay_trade_page_pay(
    out_trade_no = "12312319",
    total_amount = str(10000),#支付金额
    subject = "生活消费",
    return_url=None,
    notify_url=None
)

print("https://openapi.alipaydev.com/gateway.do?"+order_string)