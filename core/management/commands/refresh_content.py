from django.core.management.base import BaseCommand

from core.management.commands.seed_faq import DATA as FAQ_DATA
from core.models import FaqItem
from portfolio.management.commands.seed_portfolio import STARTERS
from portfolio.models import Project

# متن‌های قدیمی: همان‌هایی که seed قبلی گذاشته بود، به همان ترتیبِ FAQ_DATA.
# فقط ردیف‌هایی که هنوز عین این‌ها هستند عوض می‌شوند.
OLD_FAQ = [
    (
        "What happens after I send a request?",
        "We call the number you wrote. We talk about the project and then suggest a plan and a clear price. Nothing starts until you say yes.",
    ),
    (
        "How is the final price decided?",
        "The number on each plan is a starting point. After we talk about what your project needs, we tell you the exact price.",
    ),
    (
        "Can I take a closer look at your work?",
        "Yes. Open any project to see its details. The demo and source links are there when they exist.",
    ),
    (
        "Can my site be in Persian and English?",
        "Yes. This site is bilingual. See the plans for the details, or write it in the order form.",
    ),
    (
        "Where does the information I write in the form go?",
        "Only our team sees it, and we use it to contact you. We keep it for 12 months and then delete it. The details are on the privacy page.",
    ),
]

OLD_PROJECT_DESC_EN = {
    "django-gaming-shop": "Gaming-gear store with secure checkout, coupons, stock locking and a seller panel.",
    "lavagame-store": "Gaming store with cart, orders, payments and customer chat.",
    "carzone": "Car accessories shop with a catalog and product pages.",
    "beauty-store": "The backend of a beauty online shop, built with Django. It handles products, carts and users, with JWT login.",
}


class Command(BaseCommand):
    help = (
        "Replaces the old starter texts (FAQ and project descriptions) with the new ones. "
        "Anything you edited yourself in the admin is left alone."
    )

    def handle(self, *args, **options):
        self._faq()
        self._projects()

    def _faq(self):
        for index, ((old_q, old_a), (q_fa, q_en, a_fa, a_en)) in enumerate(zip(OLD_FAQ, FAQ_DATA)):
            row = (
                FaqItem.objects.filter(question_en=old_q).first()
                or FaqItem.objects.filter(question_en=q_en).first()
            )
            if row is None:
                FaqItem.objects.create(
                    question_fa=q_fa, question_en=q_en,
                    answer_fa=a_fa, answer_en=a_en, order=index,
                )
                self.stdout.write(f"faq added: {q_en}")
            elif row.question_en == old_q and row.answer_en == old_a:
                row.question_fa, row.question_en = q_fa, q_en
                row.answer_fa, row.answer_en = a_fa, a_en
                row.save()
                self.stdout.write(f"faq updated: {q_en}")
            elif row.question_en == q_en and row.answer_en == a_en:
                self.stdout.write(f"faq already new: {q_en}")
            else:
                self.stdout.write(f"faq left alone (you edited it): {row.question_en}")

    def _projects(self):
        for data in STARTERS:
            slug = data["slug"]
            project = Project.objects.filter(slug=slug).first()
            if project is None:
                self.stdout.write(f"project not in the database yet (run seed_portfolio): {slug}")
            elif project.desc_en == data["desc_en"]:
                self.stdout.write(f"project already new: {slug}")
            elif project.desc_en == OLD_PROJECT_DESC_EN.get(slug):
                project.desc_fa = data["desc_fa"]
                project.desc_en = data["desc_en"]
                project.save(update_fields=["desc_fa", "desc_en"])
                self.stdout.write(f"project updated: {slug}")
            else:
                self.stdout.write(f"project left alone (you edited it): {slug}")