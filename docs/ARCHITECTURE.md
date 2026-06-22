# Atlas Support Site Architecture

This repository is a small static support site for Atlas. It is intended for
GitHub Pages-style hosting and contains only public HTML documents.

## Routes

- `/` is the entry page. It introduces Atlas and links to the two public
  support routes.
- `/privacy/` is the privacy policy. It is the canonical public description of
  Atlas data handling for users and App Store review.
- `/support/` is the support page. It gives users a public issue tracker and
  reminds them not to post private workout, health, or personal details.

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

The privacy policy currently states that the public build of Atlas:

- Does not require an account.
- Does not use ads or analytics SDKs.
- Does not track users across apps or websites.
- Does not send workout data to a developer-operated server.
- Stores workout data, preferences, optional heart-rate samples, and export
  preferences locally on device.
- Does not use HealthKit or request access to Apple Health.
- Lets users choose export and restore destinations through iOS controls.
- Is a fitness tracking and training review app, not a medical device.

The support page should stay aligned with those claims. If the app changes data
handling, HealthKit usage, backend usage, analytics, or export behavior, update
the privacy policy, support page, and tests together.

## Testing

The repository has no package manifest. The added tests use Python standard
library `unittest` so they can run without dependency or project-file changes:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
```

The tests parse the HTML and check public-page metadata, route links, privacy
claims, support guidance, and the absence of client-side runtime surfaces.
