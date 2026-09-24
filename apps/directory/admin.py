from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import AdminAPIKey, Project, SourceLink, Submission
from .services import approve_submission


class SourceInline(admin.TabularInline):
    model = SourceLink
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "category",
        "status",
        "featured",
        "github_stars",
        "x_likes",
        "published_at",
    ]
    list_filter = ["status", "category", "featured"]
    search_fields = ["title", "description", "author", "canonical_url"]
    inlines = [SourceInline]
    readonly_fields = ["id", "slug", "created_at", "github_stars_checked_at"]


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "category", "created_at"]
    list_filter = ["status", "category"]
    search_fields = ["title", "source_url", "contact"]
    readonly_fields = ["status", "project", "reviewed_by", "reviewed_at", "created_at"]
    actions = ["approve", "reject"]

    @admin.action(description="Approve and publish selected submissions")
    def approve(self, request, queryset):
        for pk in queryset.values_list("pk", flat=True):
            try:
                approve_submission(pk, request.user)
            except (ValidationError, IntegrityError):
                self.message_user(
                    request,
                    f"Submission {pk} could not be approved. Check its URLs and required fields.",
                    messages.ERROR,
                )

    @admin.action(description="Reject selected pending submissions")
    def reject(self, request, queryset):
        with transaction.atomic():
            queryset.filter(status=Submission.Status.PENDING).update(
                status=Submission.Status.REJECTED,
                reviewed_by=request.user,
                reviewed_at=timezone.now(),
            )


@admin.register(AdminAPIKey)
class AdminAPIKeyAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "active", "created_at"]
    readonly_fields = ["name", "user", "digest", "created_at"]

    def has_add_permission(self, request):
        return False


admin.site.site_header = "Built with Bend"
admin.site.site_title = "Built with Bend · Admin"
admin.site.index_title = "Curate the directory"
