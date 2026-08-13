PUBLIC DASHBOARD REPLACEMENT

Copy the package contents into the repository root.

This replaces the public dashboard frontend and adds:
- dashboard/frontend/index.html
- dashboard/frontend/app.js
- dashboard/frontend/style.css
- dashboard/data/dashboard-data.json
- scripts/export_dashboard_data.py
- .github/workflows/deploy_dashboard.yml

The dashboard supports:
- Last 7 Days
- Last 30 Days
- Today
- This Week
- This Month
- Specific date
- Custom From/To dates
- Author/MLA
- District
- Assembly
- Main Category
- Sub Category
- Event Type
- Party
- Leader
- Development Sector
- Government Scheme
- filtered post table
- CSV download

The dashboard uses the post date derived from Timestamp, not AI processing time.

IMPORTANT:
GitHub Pages is public. Any data placed in dashboard/data/dashboard-data.json is public.
Do not place API keys, service-account files, .env, or other secrets in the published directory.

The publish workflow:
1. runs manually, or automatically after the successful Daily Political Intelligence Scraper;
2. reads AI Analysis using the private Google service account secret;
3. creates dashboard/data/dashboard-data.json;
4. publishes dashboard/ to GitHub Pages.

After copying:
git add dashboard scripts .github/workflows/deploy_dashboard.yml DASHBOARD_PAGES_README.txt
git commit -m "Add public dashboard deployment"
git push origin main

Then:
GitHub -> Actions -> Publish Dashboard -> Run workflow

Expected URL:
https://politicalintelligence.github.io/Political-Intelligence-AI/
