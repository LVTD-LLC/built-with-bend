"""Restore curated JendHub destinations without overwriting later editorial changes."""

from django.db import migrations

PROJECT_ID = "9da424ac-3e64-494d-a468-081bc5dfb07b"
SOURCE_ID = 233
REPOSITORY = "https://github.com/LeeeeT/JendHub"
WEBSITE = "https://jend.leeeet.dev/"
OLD_SOURCE = REPOSITORY + "/blob/main/src/jend/build.py"
NEW_SOURCE = (
    REPOSITORY + "/blob/73c4451810ee63a48f8c4c5321fdeea36cebe082/src/jendhub/services/site/app.py"
)


def replace_destinations(apps, schema_editor, *, reverse=False):
    alias = schema_editor.connection.alias
    projects = apps.get_model("directory", "Project").objects.using(alias)
    sources = apps.get_model("directory", "SourceLink").objects.using(alias)
    project = projects.select_for_update().filter(pk=PROJECT_ID).first()
    if project is None:
        return
    if project.slug != "jendhub" or project.repository_url != REPOSITORY:
        raise RuntimeError("JendHub identity changed; reconcile the editorial migration.")
    source = sources.select_for_update().filter(pk=SOURCE_ID).first()
    if source is None or source.project_id != project.pk or source.kind != "github":
        raise RuntimeError("JendHub source identity changed; reconcile before deployment.")
    before = (WEBSITE, NEW_SOURCE) if reverse else ("", OLD_SOURCE)
    after = ("", OLD_SOURCE) if reverse else (WEBSITE, NEW_SOURCE)
    current = (project.website_url, source.url)
    if current == after:
        return
    if current != before:
        raise RuntimeError("JendHub destinations changed; preserve them and reconcile.")
    projects.filter(pk=project.pk).update(website_url=after[0])
    sources.filter(pk=source.pk).update(url=after[1])


def forwards(apps, schema_editor):
    replace_destinations(apps, schema_editor)


def backwards(apps, schema_editor):
    replace_destinations(apps, schema_editor, reverse=True)


class Migration(migrations.Migration):
    dependencies = [("directory", "0006_correct_knot_release_status")]
    operations = [migrations.RunPython(forwards, backwards)]
