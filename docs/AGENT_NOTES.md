# Future Agent Notes

This repo is intentionally simple. Preserve that simplicity unless the product
requirements change.

## Before Changing Content

- Read `README.md`, `index.html`, `privacy/index.html`, `support/index.html`,
  `community/index.html`, and `docs/ARCHITECTURE.md`.
- Treat the privacy policy as a user-facing contract. Do not soften, remove, or
  add data-handling claims unless they match the actual app behavior.
- Keep support and community guidance consistent with the privacy policy,
  especially around local storage, optional Social accounts, Bluetooth
  heart-rate sensor use, sharing controls, account deletion, and the medical
  disclaimer.

## Adding Pages

- Prefer a directory route with `index.html`, for example `new-page/index.html`.
- Use relative links so pages work from local files and from GitHub Pages.
- Avoid JavaScript, forms, iframes, remote fonts, remote CSS, tracking pixels,
  analytics snippets, and third-party embeds unless the privacy policy is also
  reviewed and updated.
- Add or update tests for every new route and public navigation path.

## Test Workflow

Run the standalone test suite from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
```

The tests are deliberately dependency-free. If a future project adopts another
test framework, keep these checks or port them before deleting them.

## Coverage Priorities

High-value coverage for this site means protecting:

- Public route availability.
- Internal link integrity.
- Mobile metadata and expected page titles.
- The no-client-runtime privacy posture.
- The exact privacy, support, and community-safety claims users rely on.

Avoid placeholder tests. A test should fail only when a public route, claim, or
site invariant changes in a way that deserves review.
