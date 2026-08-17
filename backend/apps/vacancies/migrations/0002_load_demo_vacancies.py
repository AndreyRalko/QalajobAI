from django.db import migrations


def load_rows(apps, schema_editor):
    from apps.vacancies.seed_data import load_demo_vacancies

    load_demo_vacancies()


def unload_rows(apps, schema_editor):
    Vacancy = apps.get_model("vacancies", "Vacancy")
    titles = [
        "Учитель истории",
        "Учитель географии",
        "Методист образовательных программ",
        "Куратор учебной практики",
        "Специалист по цифровым технологиям в образовании",
        "Frontend-разработчик",
    ]
    Vacancy.objects.filter(title__in=titles).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("vacancies", "0001_initial"),
        ("users", "0007_demo_student_id_48958"),
    ]

    operations = [
        migrations.RunPython(load_rows, unload_rows),
    ]
