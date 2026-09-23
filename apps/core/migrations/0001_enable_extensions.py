from django.db import migrations


def enable_available_extensions(apps, schema_editor):
    # The directory retains its existing PostgreSQL database. Qdrant provides
    # vector storage; enable optional PostgreSQL extensions only when installed.
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT name FROM pg_available_extensions WHERE name IN ('vector', 'pg_stat_statements')")
        available = {row[0] for row in cursor.fetchall()}
        for name in ("vector", "pg_stat_statements"):
            if name in available:
                cursor.execute(f'CREATE EXTENSION IF NOT EXISTS "{name}"')


class Migration(migrations.Migration):
    dependencies = []
    operations = [migrations.RunPython(enable_available_extensions, migrations.RunPython.noop)]
