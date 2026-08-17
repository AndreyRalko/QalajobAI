"""Preloaded accounts. Passwords are stored as MD5 hex digests.
Login format: Фамилия_Имя
"""

PRESET_ACCOUNTS = [
    {
        "login": "Иванов_Иван",
        "last_name": "Иванов",
        "first_name": "Иван",
        "role": "student",
        "student_id": "48958",
        # Student123
        "password_md5": "e4a6a34a2c625d52f26846f5e3d22064",
    },
    {
        "login": "Петров_Петр",
        "last_name": "Петров",
        "first_name": "Петр",
        "role": "employer",
        # Employer123
        "password_md5": "f29674388ee595866213c8b746d44558",
    },
    {
        "login": "Сидоров_Админ",
        "last_name": "Сидоров",
        "first_name": "Админ",
        "role": "admin",
        # Admin1234
        "password_md5": "751cb3f4aa17c36186f4856c8982bf27",
    },
]

OLD_PRESET_USERNAMES = [
    "student@qalajob.kz",
    "employer@qalajob.kz",
    "admin@qalajob.kz",
    "admin@mail.ru",
]
