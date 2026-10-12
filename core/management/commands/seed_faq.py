from django.core.management.base import BaseCommand

from core.models import FaqItem

# متن‌های شروع‌اند. قبل از انتشار بخوانید و با کار واقعی تیم یکی کنید (از ادمین، بخش Faq items).
DATA = [
    (
        "بعد از ثبت درخواست چه اتفاقی می‌افتد؟",
        "What happens after I send a request?",
        "با شماره‌ای که نوشته‌اید با شما تماس می‌گیریم. درباره‌ی پروژه حرف می‌زنیم و بعد یک پلن و قیمت مشخص پیشنهاد می‌دهیم. تا وقتی شما تأیید نکنید، کاری شروع نمی‌شود.",
        "We call the number you wrote. We talk about the project and then suggest a plan and a clear price. Nothing starts until you say yes.",
    ),
    (
        "قیمت نهایی چطور مشخص می‌شود؟",
        "How is the final price decided?",
        "عدد روی هر پلن نقطه‌ی شروع است. بعد از گفتگو درباره‌ی نیازهای پروژه‌تان، قیمت دقیق را می‌گوییم.",
        "The number on each plan is a starting point. After we talk about what your project needs, we tell you the exact price.",
    ),
    (
        "نمونه‌کارهایتان را می‌توانم از نزدیک ببینم؟",
        "Can I take a closer look at your work?",
        "بله. روی هر نمونه‌کار بزنید تا جزئیاتش را ببینید. لینک دمو و سورس هرکدام که موجود باشد کنارش هست.",
        "Yes. Open any project to see its details. The demo and source links are there when they exist.",
    ),
    (
        "سایت من می‌تواند فارسی و انگلیسی باشد؟",
        "Can my site be in Persian and English?",
        "بله. همین سایت دوزبانه است. جزئیات را در بخش پلن‌ها ببینید یا در فرم ثبت درخواست بنویسید.",
        "Yes. This site is bilingual. See the plans for the details, or write it in the order form.",
    ),
    (
        "اطلاعاتی که در فرم می‌نویسم کجا می‌رود؟",
        "Where does the information I write in the form go?",
        "فقط تیم ما آن‌ها را می‌بیند و برای تماس با شما استفاده می‌کنیم. ۱۲ ماه نگه می‌داریم و بعد پاک می‌کنیم. جزئیاتش در صفحه‌ی حریم خصوصی است.",
        "Only our team sees it, and we use it to contact you. We keep it for 12 months and then delete it. The details are on the privacy page.",
    ),
]


class Command(BaseCommand):
    help = "Adds the starter FAQ items (skips the ones that already exist)."

    def handle(self, *args, **options):
        for i, (q_fa, q_en, a_fa, a_en) in enumerate(DATA):
            _, created = FaqItem.objects.get_or_create(
                question_fa=q_fa,
                defaults={"question_en": q_en, "answer_fa": a_fa, "answer_en": a_en, "order": i},
            )
            self.stdout.write(("added: " if created else "exists: ") + q_en)