from django.shortcuts import redirect
from django.views.generic import TemplateView

from apps.users.models import UserRole
from apps.web.access import RoleRequiredMixin


VALID_AI_MODES = {
    "resume": "resume",
    "cover-letter": "cover_letter",
    "interview": "interview",
    "mock-interview": "mock_interview",
}


class StudentRequiredMixin(RoleRequiredMixin):
    allowed_roles = (UserRole.STUDENT, UserRole.ADMIN)


class StudentAIWorkspaceView(StudentRequiredMixin, TemplateView):
    template_name = "web/student/workspace.html"

    def dispatch(self, request, *args, **kwargs):
        mode = kwargs.get("mode", "resume")
        if mode not in VALID_AI_MODES:
            return redirect("web:student-ai", mode="resume")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        from apps.web.i18n import get_messages, resolve_request_locale, translate

        ctx = super().get_context_data(**kwargs)
        mode_slug = self.kwargs.get("mode", "resume")
        msgs = get_messages(resolve_request_locale(self.request))
        ctx["mode_slug"] = mode_slug
        ctx["mode_api"] = VALID_AI_MODES[mode_slug]
        ctx["modes"] = [
            ("resume", translate(msgs, "aiPage.modeResume")),
            ("cover-letter", translate(msgs, "aiPage.modeCover")),
            ("interview", translate(msgs, "aiPage.modeInterview")),
            ("mock-interview", translate(msgs, "web.modeMock")),
        ]
        return ctx


class StudentJobsView(StudentRequiredMixin, TemplateView):
    template_name = "web/student/jobs.html"


class StudentSettingsView(StudentRequiredMixin, TemplateView):
    template_name = "web/student/settings.html"


def employer_stub(request):
    from django.shortcuts import render
    from apps.web.i18n import get_messages, resolve_request_locale, translate

    msgs = get_messages(resolve_request_locale(request))
    return render(
        request,
        "web/public/stub.html",
        {
            "title": translate(msgs, "web.employerTitle"),
            "message": translate(msgs, "web.employerStub"),
        },
    )
