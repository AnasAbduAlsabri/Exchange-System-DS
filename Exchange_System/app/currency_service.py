import zeep

# تحديد عنوان WSDL
wsdl_path = "FxtopServices.wsdl"

# إنشاء عميل Zeep
client = zeep.Client(wsdl=wsdl_path)

# بيانات الطلب
original_amount = "100"  # المبلغ الأصلي
currency_from = "USD"  # العملة الأصلية
currency_to = "EUR"  # العملة المستهدفة
date = ""  # يمكنك تركه فارغًا لاستخدام التاريخ الحالي
user = ""  # اختياري، يمكنك تركه فارغًا
password = ""  # اختياري، يمكنك تركه فارغًا

# إرسال طلب تحويل العملات
result = client.service.Convert(
    OriginalAmount=original_amount,
    C1=currency_from,
    C2=currency_to,
    Date=date,
    User=user,
    Password=password,
)

# طباعة النتيجة
print(result)
