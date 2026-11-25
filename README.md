# notary.augello.net

A one-page notary site (home + FAQ). Edit text in `src/pages/`, styles in `src/assets/css/site.css`.

## Put it online (GitHub Pages)
1. On GitHub, create a **new repository** named `notary` (public). Do not reuse the career site's repo.
2. Upload everything in this folder, including the hidden `.github` folder (drag the whole folder contents).
   If `.github` won't upload, create the file `.github/workflows/pages.yml` in the web editor and paste in `pages-workflow.yml`.
3. Repository **Settings > Pages > Build and deployment > Source = GitHub Actions**.
4. Open the **Actions** tab and confirm "Build and deploy site" succeeded.
5. In **Settings > Pages > Custom domain**, enter `notary.augello.net` and save.
6. At your DNS provider add: **CNAME**, name `notary`, value `charles-augello.github.io`.
7. When DNS resolves, tick **Enforce HTTPS** in the same Pages screen.

The `CNAME` file is added automatically by the build. This does not affect the career site.

## Before you go live
- Confirm your commission, bond, E&O and online-notary registration details are current.
- Add the site to your SigningAgent.com profile if it has a website field.
- Set `STRICT_LAUNCH_CHECK` to "true" in `pages.yml` if you add yellow placeholders later.

## Build locally
`python3 build.py --github` (use `--strict` to fail on unfinished items).
