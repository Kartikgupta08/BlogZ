# BlogZ

A lightweight static front-end for a blogging/dashboard UI. Built with plain HTML, CSS and vanilla JS. Useful as a starter template for writer dashboards (stories, stats, library, profile, collaborate).

## Features
- Home feed with category cards
- Stories manager (Drafts, Published, Unlisted, Submissions) with tabbed UI
- Library, Profile, Stats and Collaborate pages (single-page show/hide navigation)
- Responsive sidebar with hamburger toggle for small screens
- Simple right-side recommendations panel

## Project structure
- index.html — main markup and per-page sections
- style.css — styles and responsive rules
- main.js — page behavior and interactions (menu toggle, page switching, small helpers)
- /assets (optional) — images or extra files

## Getting started (local)
Requirements: modern browser. Optional: Python or VS Code Live Server for a local HTTP server.

1. Open the project folder in VS Code or your editor.
2. Run locally:
   - Quick (no server): open `index.html` in the browser.
   - HTTP server (recommended):
     - PowerShell / Command Prompt:
       ```
       python -m http.server 8000
       ```
     - Then visit: `http://localhost:8000/`

3. Edit `index.html`, `style.css` or `main.js` to customize.

## How pages work
The app uses a simple page switcher: each major page is a section with an id (`homePage`, `storiesPage`, `libraryPage`, etc.). Navigation items have `data-page` attributes and show/hide the corresponding section. Tabs inside Stories use `data-tab` attributes to switch content.

## Common edits
- To change stories content: edit the `#storiesPage` section in `index.html`.
- To change layout/spacing: update `style.css` (search for `.stories-content-container`, `.stories-nav-tabs`).
- To fix hamburger/sidebar issues: check the toggle script near the bottom of `index.html` and `.sidebar` styles in `style.css`.

## Troubleshooting
- If a section shows on every page, ensure it has `class="hidden"` by default and the page-switcher script correctly adds/removes `.hidden`.
- If the hamburger isn't clickable, inspect z-index and pointer-events for `.menu-btn` and `.sidebar` in `style.css` and the console for JS errors.

## Contributing
- Fork the repo, make changes, and open a pull request.
- Report bugs via issues with steps to reproduce and console logs/screenshots.

