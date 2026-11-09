# Atlas Support Site Architecture

This repository is a small static support site for Atlas. It is intended for
GitHub Pages-style hosting and contains only public HTML documents.

## Routes

- `/` is the entry page. It introduces Atlas and links to the three public
  support routes.
- `/privacy/` is the privacy policy. It is the canonical public description of
  Atlas data handling for users and App Store review.
- `/support/` is the support page. It gives users a public issue tracker and
  reminds them not to post private workout, health, or personal details.
- `/community/` is the Social community-standards page. It defines age,
  conduct, privacy, healthy-competition, reporting, and enforcement rules.

Each route is implemented as an `index.html` file. Internal links are relative
so the site can run locally from the repository or from a project path under
GitHub Pages.

## Runtime Model

The site has no client runtime. Pages use inline CSS and static HTML only:

- No JavaScript.
- No forms.
- No iframes.
- No remote stylesheets.
- No analytics, advertising, or tracking embeds.

That absence is part of the public privacy posture. If a future change adds any
runtime dependency, it should be reviewed against the privacy policy before it
ships.

## Content Contract

As of November 8, 2026, the privacy and support pages describe local-only Atlas. No account or backend is used. Exports go to the user's chosen destination and are not a full app-state backup. Historical Social beta data must not be represented as deleted without evidence. The community page is explicitly historical.

## Testing

The repository has no package manifest. The added tests use Python standard
library `unittest` so they can run without dependency or project-file changes:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
```

The tests parse the HTML and check public-page metadata, route links, privacy
claims, support guidance, and the absence of client-side runtime surfaces.
