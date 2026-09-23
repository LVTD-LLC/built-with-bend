from django.db import transaction
from django.utils import timezone

from .models import Project, SourceLink, Submission, source_kind


@transaction.atomic
def create_project(
    *,
    title,
    description,
    author="",
    category="other",
    website_url="",
    repository_url="",
    sources=(),
    publish=False,
):
    canonical = website_url or repository_url or (sources[0] if sources else "")
    project = Project(
        title=title,
        description=description,
        author=author,
        category=category,
        website_url=website_url,
        repository_url=repository_url,
        canonical_url=canonical,
        status=Project.Status.PUBLISHED if publish else Project.Status.DRAFT,
    )
    project.full_clean()
    project.save()
    for url in dict.fromkeys(sources):
        source = SourceLink(project=project, url=url, kind=source_kind(url))
        source.full_clean()
        source.save()
    return project


@transaction.atomic
def approve_submission(submission_id, reviewer):
    submission = Submission.objects.select_for_update().get(pk=submission_id)
    if submission.status != Submission.Status.PENDING:
        return submission.project
    canonical = submission.website_url or submission.repository_url or submission.source_url
    project = Project.objects.filter(canonical_url=canonical).first()
    if project is None:
        project = create_project(
            title=submission.title,
            description=submission.description,
            author=submission.author,
            category=submission.category,
            website_url=submission.website_url,
            repository_url=submission.repository_url,
            sources=[submission.source_url],
            publish=True,
        )
    else:
        SourceLink.objects.get_or_create(
            project=project,
            url=submission.source_url,
            defaults={"kind": source_kind(submission.source_url)},
        )
        project.status = Project.Status.PUBLISHED
        project.full_clean()
        project.save()
    submission.status = Submission.Status.APPROVED
    submission.project = project
    submission.reviewed_by = reviewer
    submission.reviewed_at = timezone.now()
    submission.save()
    return project
