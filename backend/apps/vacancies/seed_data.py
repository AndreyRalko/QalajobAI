from django.contrib.auth.models import User

from apps.vacancies.models import Vacancy

EMPLOYER_LOGIN = "Петров_Петр"

DEMO_VACANCIES = [
    {
        "title": "Учитель истории",
        "company_name": "Средняя школа №12",
        "city": "Astana",
        "job_type": "full-time",
        "salary": "250 000 – 350 000 ₸",
        "description": "Преподавание истории Казахстана и всемирной истории в 5–11 классах.",
        "requirements": "Педагогическое образование, знание методики преподавания истории, опыт работы приветствуется.",
    },
    {
        "title": "Учитель географии",
        "company_name": "Лицей «Бilim»",
        "city": "Astana",
        "job_type": "full-time",
        "salary": "280 000 – 380 000 ₸",
        "description": "Преподавание физической географии, картографии и краеведения.",
        "requirements": "Профильное образование по географии, навыки работы с GIS и картографией.",
    },
    {
        "title": "Методист образовательных программ",
        "company_name": "Образовательный центр",
        "city": "Almaty",
        "job_type": "full-time",
        "salary": "300 000 – 420 000 ₸",
        "description": "Разработка учебных программ, критериальное оценивание, сопровождение педагогов.",
        "requirements": "Педагогика, инклюзивное образование, цифровые технологии в обучении.",
    },
    {
        "title": "Куратор учебной практики",
        "company_name": "Колледж педагогики",
        "city": "Astana",
        "job_type": "part-time",
        "salary": "180 000 – 240 000 ₸",
        "description": "Сопровождение студентов на учебной и педагогической практике.",
        "requirements": "Опыт педагогической практики, коммуникабельность, знание психологии обучения.",
    },
    {
        "title": "Специалист по цифровым технологиям в образовании",
        "company_name": "EdTech Kazakhstan",
        "city": "Astana",
        "job_type": "full-time",
        "salary": "350 000 – 500 000 ₸",
        "description": "Внедрение LMS, цифровых инструментов и ИКТ в учебный процесс.",
        "requirements": "ИКТ, цифровые технологии в образовании, навыки работы с платформами дистанционного обучения.",
    },
    {
        "title": "Frontend-разработчик",
        "company_name": "TechStart",
        "city": "Almaty",
        "job_type": "full-time",
        "salary": "450 000 – 700 000 ₸",
        "description": "Разработка интерфейсов на React и TypeScript для EdTech продукта.",
        "requirements": "React, TypeScript, Next.js, опыт коммерческой разработки от 1 года.",
    },
]


def load_demo_vacancies():
    employer = User.objects.filter(username=EMPLOYER_LOGIN).first()
    if not employer:
        return 0, 0

    created = 0
    updated = 0
    for item in DEMO_VACANCIES:
        _, was_created = Vacancy.objects.update_or_create(
            employer=employer,
            title=item["title"],
            defaults={
                **item,
                "status": "active",
                "is_approved": True,
            },
        )
        if was_created:
            created += 1
        else:
            updated += 1
    return created, updated
