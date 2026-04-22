# APOEL Bowling Editable Site

This folder now contains a database-backed website with a private admin area.

## What changed

- The public website is rendered by `app.py`
- Content is stored in SQLite at `data/site.db`
- Uploaded images are stored in `uploads/`
- Only logged-in admins can edit the live website
- Public visitors can view the site but cannot change it

## Editable sections

Everything below is editable from the admin panel:

- site settings
- homepage hero and quick links
- venue section
- homepage leaders and FAQ
- news items
- team roster and player photos
- achievements
- schedule and events
- standings table
- gallery
- BBC teams page
- sponsors and logos
- coming soon page

## Run locally

```bash
cd "/Users/kyriakostsouloupas/Documents/CODEX PROJECTS/APOEL BOWLING WEBSITE/modern-site"
python3 app.py
```

Then open:

- public site: `http://127.0.0.1:8000/`
- admin: `http://127.0.0.1:8000/admin`

## First login

On first run, the app creates an admin user and writes the temporary login details to:

- `data/initial_admin_password.txt`

Default username:

- `admin`

After logging in, go to `/admin/account` and change the password immediately.

## Hosting notes

For deployment on a server, you can set:

```bash
HOST=0.0.0.0
PORT=8000
```

and run:

```bash
HOST=0.0.0.0 PORT=8000 python3 app.py
```

For production, the best setup is to place this behind a reverse proxy such as Nginx or Caddy.

## Important folders

- `app.py`: main website and admin application
- `data/site.db`: live content database
- `data/initial_admin_password.txt`: first-run credentials
- `uploads/`: images uploaded from the admin panel
- `assets/`: site styles and bundled images
