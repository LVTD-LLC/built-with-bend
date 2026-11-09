"""Correct the MyLSM API description without replacing later editorial changes."""

from django.db import migrations

PROJECT_ID = "9576a3ed-d4d3-46bd-9e4c-6ca7f7f6e517"
REPOSITORY = "https://github.com/FabianVegaA/mylsm"
BEFORE = "An experimental log-structured merge-tree key-value store implemented in Bend 2. Its durable storage path combines a write-ahead log, MemTable, SSTables, Bloom filters, compaction, and recovery.\n\nThe repository exposes reusable storage components and an in-memory hub facade, alongside demos, fuzzing, benchmarks, and machine-checked laws for parts of the pure core. Storage I/O stays on the CPU. MyLSM is a developer prototype and research project, not a production-ready substitute for RocksDB or LevelDB."
AFTER = "An experimental log-structured merge-tree key-value store implemented in Bend 2. The reviewed 0.6.0.0 API offers MyLSM.Bytes for binary keys and values and MyLSM.Utf8 for strict text access over the same durable database, with scans, snapshots, backups, and migration from the supported older format.\n\nApplications must flush explicitly; this release has no automatic flush or levelled compaction. The release notes record acceptance on Apple Silicon macOS and partial Linux x86-64 validation. Formal laws cover pure decisions, not the filesystem or host effects. Treat MyLSM as a developer prototype, not a production-ready substitute for RocksDB or LevelDB."


def replace_description(apps, schema_editor, expected, replacement):
    projects = apps.get_model("directory", "Project").objects.using(schema_editor.connection.alias)
    project = projects.select_for_update().filter(pk=PROJECT_ID).first()
    if project is None:
        return
    if project.slug != "mylsm" or project.repository_url != REPOSITORY:
        raise RuntimeError("MyLSM identity changed; reconcile the editorial migration.")
    if project.description == replacement:
        return
    if project.description != expected:
        raise RuntimeError(
            "MyLSM description changed; preserve it and reconcile before deployment."
        )
    projects.filter(pk=project.pk).update(description=replacement)


def forwards(apps, schema_editor):
    replace_description(apps, schema_editor, BEFORE, AFTER)


def backwards(apps, schema_editor):
    replace_description(apps, schema_editor, AFTER, BEFORE)


class Migration(migrations.Migration):
    dependencies = [("directory", "0007_restore_jendhub_destinations")]
    operations = [migrations.RunPython(forwards, backwards)]
