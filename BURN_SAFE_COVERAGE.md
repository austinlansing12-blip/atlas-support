# Safe Coverage Pass

This pass added only new files. No existing source, test, manifest, project, or
configuration file was edited.

## New Files

- `tests/test_static_site_contract.py`
  - Adds dependency-free Python `unittest` coverage for the static HTML site.
  - Checks that all public pages exist with expected HTML metadata, titles, and
    headings.
  - Verifies internal links resolve to existing site files and external links
    are approved HTTPS destinations.
  - Protects the no-client-runtime privacy posture by asserting there are no
    scripts, forms, iframes, or remote stylesheet links.
  - Checks the home navigation, secondary-page back links, privacy policy
    section order, parseable effective date, current data-handling claims,
    local data categories, support issue link, privacy link, and warning against
    posting sensitive details.
  - Wiring: no manifest or project-file wiring needed. Run with
    `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`.

- `tests/test_static_site_accessibility.py`
  - Adds dependency-free structural and accessibility-adjacent checks for the
    public pages.
  - Verifies one main region per page, ordered heading structure, readable link
    text, safe handling for any future `_blank` links, baseline responsive CSS
    fragments, shared medical disclaimer language, and scan-friendly secondary
    page sections.
  - Wiring: no manifest or project-file wiring needed. Run with
    `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`.

- `docs/ARCHITECTURE.md`
  - Documents the static route structure, runtime model, public privacy
    contract, and test command.

- `docs/AGENT_NOTES.md`
  - Gives future agents a maintenance checklist for privacy/support content,
    static-route additions, and dependency-free test workflow.

- `BURN_SAFE_COVERAGE.md`
  - This report.

## Suspected Bugs

None found during this pass.

## Verification

Passed from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
```

Result: 18 tests passed.
