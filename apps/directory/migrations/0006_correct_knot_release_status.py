"""Correct the source-verified Knot package availability claim, without replacing later edits."""

from django.db import migrations

PROJECT_ID = "a1e297db-9920-422c-914c-4bc9fe9700f9"
REPOSITORY = "https://github.com/MatheusBBarni/knot-node-tooling"
BEFORE = "An early native JavaScript toolchain written in Bend 2. Current functionality includes an npm-compatible package-management path, dependency inspection, TypeScript-subset transpilation, import scanning, and initial build/watch commands.\n\nBend coordinates the tooling while host effects provide platform operations; generated JavaScript runs in an external runtime. The repository documents deterministic lockfiles, package integrity, and isolated dependency layouts. There is no installable release yet, transpilation is not type-checking, and the proposed test runner remains design-only."
AFTER = "An early native JavaScript toolchain written in Bend 2. Current functionality includes an npm-compatible package-management path, dependency inspection, TypeScript-subset transpilation, import scanning, and initial build/watch commands.\n\nBend coordinates the tooling while host effects provide platform operations; generated JavaScript runs in an external runtime. The repository documents deterministic lockfiles, package integrity, and isolated dependency layouts. Knot 0.0.1 is published on npm as @matheusbbarni/knot; the repository documents installation and source builds. Transpilation is not type-checking, and the proposed test runner remains design-only."


def replace_description(apps, schema_editor, expected, replacement):
    Project = apps.get_model("directory", "Project")
    projects = Project.objects.using(schema_editor.connection.alias)
    project = projects.select_for_update().filter(pk=PROJECT_ID).first()
    # Fresh installations do not contain this curated production record.
    if project is None:
        return
    if project.slug != "knot" or project.repository_url != REPOSITORY:
        raise RuntimeError("Knot identity changed; reconcile the editorial migration.")
    if project.description == replacement:
        return
    if project.description != expected:
        raise RuntimeError("Knot description changed; preserve it and reconcile before deployment.")
    projects.filter(pk=project.pk).update(description=replacement)


def forwards(apps, schema_editor):
    replace_description(apps, schema_editor, BEFORE, AFTER)


def backwards(apps, schema_editor):
    replace_description(apps, schema_editor, AFTER, BEFORE)


class Migration(migrations.Migration):
    dependencies = [("directory", "0005_project_thumbnail_attempted_at_and_more")]
    operations = [migrations.RunPython(forwards, backwards)]
