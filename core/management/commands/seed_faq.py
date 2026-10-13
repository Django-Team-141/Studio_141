from django.core.management.base import BaseCommand

from core.models import FaqItem

# متن‌های شروع‌اند. قبل از انتشار بخوانید و با کار واقعی تیم یکی کنید (از ادمین، بخش Faq items).
# ترتیب این پنج تا با OLD_FAQ در refresh_content یکی است. اگر ترتیب را عوض کنید، آن فایل را هم عوض کنید.
DATA = [
    (
        "بعد از ثبت درخواست چه می‌شود؟",
        "What happens after I send a request?",
        "با همان شماره‌ای که نوشته‌اید تماس می‌گیریم و درباره‌ی پروژه حرف می‌زنیم. بعد یک پلن و یک قیمت مشخص پیشنهاد می‌دهیم. تا وقتی شما بله نگویید، کاری شروع نمی‌شود.",
        "We call the number you wrote and talk through the project. Then we suggest a plan and a clear price. Nothing starts until you say yes.",
    ),
    (
        "قیمت نهایی چطور مشخص می‌شود؟",
        "How is the final price decided?",
        "عدد روی هر پلن نقطه‌ی شروع است. وقتی بدانیم پروژه‌تان دقیقاً چه چیزهایی لازم دارد، قیمت نهایی را می‌گوییم و قبل از شروع کار روی آن توافق می‌کنیم.",
        "The number on each plan is a starting point. Once we know what your project needs, we tell you the final price and agree on it before any work starts.",
    ),
    (
        "از چه فناوری‌هایی استفاده می‌کنید؟",
        "What technologies do you use?",
        "بک‌اند همه‌ی پروژه‌هایمان با Django ساخته شده. وقتی پروژه رابط کاربری جدا لازم داشته، از React هم استفاده کرده‌ایم؛ مثل دو فروشگاه گیمینگ در بخش نمونه‌کارها.",
        "The backend of all our projects is built with Django. When a project needed a separate front end, we've used React too, like the two gaming stores in our work section.",
    ),
    (
        "سایت من می‌تواند فارسی و انگلیسی باشد؟",
        "Can my site be in Persian and English?",
        "بله، می‌شود. همین سایت هم دوزبانه است. اگر برای سایت خودتان هم این را می‌خواهید، در فرم ثبت درخواست بنویسید.",
        "Yes. This very site is bilingual. If you want that for yours too, just mention it in the order form.",
    ),
    (
        "اطلاعاتی که در فرم می‌نویسم کجا می‌رود؟",
        "Where does the information I write in the form go?",
        "فقط اعضای تیم ما آن را می‌بینند و فقط برای تماس با شما استفاده می‌کنیم. ۱۲ ماه نگهش می‌داریم و بعد پاک می‌کنیم. جزئیاتش در صفحه‌ی حریم خصوصی است.",
        "Only our team sees it, and we only use it to get in touch with you. We keep it for 12 months and then delete it. The details are on the privacy page.",
    ),
]


class Command(BaseCommand):
    help = "Adds the starter FAQ items to an empty database (skips the ones that already exist)."

    def handle(self, *args, **options):
        for i, (q_fa, q_en, a_fa, a_en) in enumerate(DATA):
            _, created = FaqItem.objects.get_or_create(
                question_fa=q_fa,
                defaults={"question_en": q_en, "answer_fa": a_fa, "answer_en": a_en, "order": i},
            )
            self.stdout.write(("added: " if created else "exists: ") + q_en)