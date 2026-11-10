# موقع نتائج الطلاب

## النشر لأول مرة
1. أنشئ مستودعًا على GitHub وارفع محتويات هذا المجلد (لا ترفع ملف الإكسل — `.gitignore` يمنعه).
2. Settings ← Pages ← Source: **Deploy from a branch** ← Branch: `main` ← Folder: **/docs**.

## تحديث الدرجات
1. ضع ملف الإكسل المحدّث بجوار `build.py`.
2. شغّل:  `pip install openpyxl cryptography`  (مرة واحدة)  ثم  `python build.py اسم_الملف.xlsx`
3. ارفع التغييرات (`git add . && git commit -m update && git push`). يظهر التحديث بعد دقيقة تقريبًا.

للدخول بالكود + الرقم القومي (أأمن): أضف `--nid` في أمر البناء.
> حافظ على ترتيب الأعمدة كما هو في الملف الحالي.
