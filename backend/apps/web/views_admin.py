from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView, View

from apps.admin_api.models import SystemSettings
from apps.ai.models import AiActionLog
from apps.lms_sync.models import LmsSyncLog, LmsSyncSchedule
from apps.lms_sync.services.sync import run_lms_sync
from apps.users.models import UserActivityLog, UserProfile, UserRole
from apps.vacancies.models import Vacancy
from apps.web.access import RoleRequiredMixin


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = (UserRole.ADMIN,)


class AdminHomeView(AdminRequiredMixin, TemplateView):
    template_name = "web/admin/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["users_count"] = User.objects.count()
        ctx["students_count"] = UserProfile.objects.filter(role=UserRole.STUDENT).count()
        ctx["employers_count"] = UserProfile.objects.filter(role=UserRole.EMPLOYER).count()
        ctx["vacancies_count"] = Vacancy.objects.count()
        ctx["ai_logs_count"] = AiActionLog.objects.count()
        ctx["activity_count"] = UserActivityLog.objects.count()
        return ctx


class AdminUsersView(AdminRequiredMixin, View):
    template_name = "web/admin/users.html"

    def get(self, request):
        from apps.users.crypto import login_to_username

        q = (request.GET.get("q") or "").strip()
        qs = UserProfile.objects.select_related("user").order_by("-user__date_joined")
        if q:
            qs = qs.filter(
                Q(user__username=login_to_username(q))
                | Q(user__username__iexact=q)
                | Q(user__email__icontains=q)
                | Q(student_id__icontains=q)
            )
        page = Paginator(qs, 40).get_page(request.GET.get("page"))
        return render(request, self.template_name, {"page": page, "q": q})

    def post(self, request):
        profile_id = request.POST.get("profile_id")
        action = request.POST.get("action")
        profile = get_object_or_404(UserProfile, pk=profile_id)
        if action == "ban":
            profile.is_banned = True
            profile.save(update_fields=["is_banned"])
        elif action == "unban":
            profile.is_banned = False
            profile.save(update_fields=["is_banned"])
        elif action == "delete" and profile.user_id != request.user.id:
            profile.user.delete()
        return redirect("web:admin-users")


class AdminVacanciesView(AdminRequiredMixin, View):
    template_name = "web/admin/vacancies.html"

    def get(self, request):
        qs = Vacancy.objects.all().order_by("-created_at")
        page = Paginator(qs, 40).get_page(request.GET.get("page"))
        return render(request, self.template_name, {"page": page})

    def post(self, request):
        vacancy_id = request.POST.get("vacancy_id")
        if vacancy_id:
            Vacancy.objects.filter(pk=vacancy_id).delete()
        return redirect("web:admin-vacancies")


class AdminLmsSyncView(AdminRequiredMixin, View):
    template_name = "web/admin/lms_sync.html"

    def get(self, request):
        return render(
            request,
            self.template_name,
            {
                "schedule": LmsSyncSchedule.load(),
                "logs": LmsSyncLog.objects.order_by("-started_at")[:50],
                "error": "",
            },
        )

    def post(self, request):
        error = ""
        action = request.POST.get("action")
        if action == "run":
            try:
                run_lms_sync(incremental=True)
            except Exception as exc:  # noqa: BLE001
                error = str(exc)
        elif action == "save_schedule":
            schedule = LmsSyncSchedule.load()
            schedule.enabled = request.POST.get("enabled") == "on"
            schedule.hour = int(request.POST.get("hour") or 2)
            schedule.minute = int(request.POST.get("minute") or 0)
            schedule.save()
            return redirect("web:admin-lms-sync")

        return render(
            request,
            self.template_name,
            {
                "schedule": LmsSyncSchedule.load(),
                "logs": LmsSyncLog.objects.order_by("-started_at")[:50],
                "error": error,
            },
        )


class AdminAiLogsView(AdminRequiredMixin, TemplateView):
    template_name = "web/admin/ai_logs.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = AiActionLog.objects.select_related("user").order_by("-created_at")
        ctx["page"] = Paginator(qs, 50).get_page(self.request.GET.get("page"))
        return ctx


class AdminActivityView(AdminRequiredMixin, TemplateView):
    template_name = "web/admin/activity.html"

    def get_context_data(self, **kwargs):
        import json

        ctx = super().get_context_data(**kwargs)
        daily = list(
            UserActivityLog.objects.annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(total=Count("id"))
            .order_by("day")
        )
        max_total = max((row["total"] for row in daily), default=1) or 1
        chart_rows = []
        for row in daily:
            chart_rows.append(
                {
                    "day": row["day"].isoformat() if row["day"] else "",
                    "label": row["day"].strftime("%d.%m") if row["day"] else "",
                    "total": row["total"],
                }
            )

        # SVG line chart geometry (viewBox coordinates).
        width, height = 920, 320
        pad_l, pad_r, pad_t, pad_b = 44, 16, 20, 36
        inner_w = width - pad_l - pad_r
        inner_h = height - pad_t - pad_b
        n = len(chart_rows)
        points = []
        for i, row in enumerate(chart_rows):
            x = pad_l if n == 1 else pad_l + (inner_w * i / (n - 1))
            y = pad_t + inner_h - (row["total"] / max_total) * inner_h
            points.append({"x": round(x, 2), "y": round(y, 2), **row})

        polyline = " ".join(f"{p['x']},{p['y']}" for p in points)
        area = ""
        if points:
            area = (
                f"{pad_l},{pad_t + inner_h} "
                + polyline
                + f" {points[-1]['x']},{pad_t + inner_h}"
            )

        # Y-axis ticks: 0, mid, max
        y_ticks = []
        for frac in (0, 0.5, 1):
            value = int(round(max_total * frac))
            y = pad_t + inner_h - frac * inner_h
            y_ticks.append({"value": value, "y": round(y, 2)})

        # X labels: first, ~quarter marks, last
        x_labels = []
        if points:
            indexes = {0, n - 1}
            if n > 4:
                indexes.update({n // 4, n // 2, (3 * n) // 4})
            for i in sorted(indexes):
                x_labels.append(
                    {"label": points[i]["label"], "x": points[i]["x"], "total": points[i]["total"]}
                )

        ctx["daily"] = chart_rows
        ctx["max_total"] = max_total
        ctx["chart"] = {
            "width": width,
            "height": height,
            "pad_l": pad_l,
            "pad_t": pad_t,
            "inner_h": inner_h,
            "baseline_y": pad_t + inner_h,
            "polyline": polyline,
            "area": area,
            "points": points,
            "y_ticks": y_ticks,
            "x_labels": x_labels,
        }
        ctx["chart_json"] = json.dumps(chart_rows, ensure_ascii=False)
        qs = UserActivityLog.objects.select_related("user").order_by("-created_at")
        ctx["page"] = Paginator(qs, 50).get_page(self.request.GET.get("page"))
        ctx["total_events"] = UserActivityLog.objects.count()
        return ctx


class AdminSettingsView(AdminRequiredMixin, View):
    template_name = "web/admin/settings.html"

    def get(self, request):
        settings_obj = SystemSettings.objects.first()
        return render(
            request,
            self.template_name,
            {"settings_obj": settings_obj, "error": "", "success": ""},
        )

    def post(self, request):
        settings_obj, _ = SystemSettings.objects.get_or_create(
            pk=1,
            defaults={"updated_by": request.user},
        )
        settings_obj.maintenance_mode = request.POST.get("maintenance_mode") == "on"
        settings_obj.support_email = (
            request.POST.get("support_email") or settings_obj.support_email
        )
        settings_obj.updated_by = request.user
        settings_obj.save()
        from apps.web.i18n import get_messages, resolve_request_locale, translate

        return render(
            request,
            self.template_name,
            {
                "settings_obj": settings_obj,
                "error": "",
                "success": translate(
                    get_messages(resolve_request_locale(request)),
                    "web.settingsSaved",
                ),
            },
        )
