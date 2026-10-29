# Reviewed directory content

These JSON files contain public editorial copy accepted by `ProjectIn` and the
existing `apps.directory.services.create_project` service. They are reviewable
publication inputs, not fixtures or an automatic database synchronizer.

After the owning PR passes CI, is merged and its exact revision is deployed,
apply a selected file through the existing directory service or admin API.
Check canonical URL, repository and slug for duplicates first. Never overwrite
an existing project or replay a payload over later editorial changes. A rerun
must inspect the existing entry and reuse it rather than insert another.

Do not include credentials, private research, analytic results or invented
popularity counts. Source links and first-hand claims require verification.
