from django.urls import path

from apps.web import views_auth, views_public, views_student, views_admin

app_name = "web"

urlpatterns = [
    path("", views_public.HomeView.as_view(), name="home"),
    path("about/", views_public.AboutView.as_view(), name="about"),
    path("contact/", views_public.ContactView.as_view(), name="contact"),
    path("login/", views_auth.login_view, name="login"),
    path("logout/", views_auth.logout_view, name="logout"),
    path("password/", views_auth.change_password_view, name="change-password"),
    path("i18n/set-language/", views_auth.set_language_view, name="set-language"),
    path("lang/", views_auth.set_language_get_view, name="set-language-get"),
    path(
        "app/student/ai/",
        views_student.StudentAIWorkspaceView.as_view(),
        {"mode": "resume"},
        name="student-ai-root",
    ),
    path(
        "app/student/ai/<slug:mode>/",
        views_student.StudentAIWorkspaceView.as_view(),
        name="student-ai",
    ),
    path(
        "app/student/jobs/",
        views_student.StudentJobsView.as_view(),
        name="student-jobs",
    ),
    path(
        "app/student/settings/",
        views_student.StudentSettingsView.as_view(),
        name="student-settings",
    ),
    path("app/employer/", views_student.employer_stub, name="employer"),
    path("app/admin/", views_admin.AdminHomeView.as_view(), name="admin-home"),
    path("app/admin/users/", views_admin.AdminUsersView.as_view(), name="admin-users"),
    path(
        "app/admin/vacancies/",
        views_admin.AdminVacanciesView.as_view(),
        name="admin-vacancies",
    ),
    path(
        "app/admin/lms-sync/",
        views_admin.AdminLmsSyncView.as_view(),
        name="admin-lms-sync",
    ),
    path(
        "app/admin/ai-logs/",
        views_admin.AdminAiLogsView.as_view(),
        name="admin-ai-logs",
    ),
    path(
        "app/admin/settings/",
        views_admin.AdminSettingsView.as_view(),
        name="admin-settings",
    ),
]
