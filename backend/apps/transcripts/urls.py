from django.urls import path

from .views import TranscriptListView, TranscriptSummaryView

app_name = "transcripts"

urlpatterns = [
    path("transcripts/", TranscriptListView.as_view(), name="transcript-list"),
    path("transcripts/summary/", TranscriptSummaryView.as_view(), name="transcript-summary"),
]
