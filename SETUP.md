# Setup — start to deployed site

One person, one branch, public repo. About 20 minutes.

---

## 1. Create the repository on github.com

Go to **github.com/new**.

- **Repository name:** `turfgrass-robotic-mowing` (or your choice — write it down, step 3 needs it)
- **Visibility:** **Public** ← required for free GitHub Pages
- **Do not** tick "Add a README", "Add .gitignore", or "Choose a license" — this package has them

Click **Create repository**. Leave the page open; you'll want the URL.

## 2. Open the folder in PyCharm

Unzip this package somewhere permanent — not Downloads. Rename the folder to match your
repository name.

In PyCharm: **File → Open**, select the folder, **Open in New Window**.

Set up the interpreter: **Settings → Project → Python Interpreter → Add Interpreter →
Add Local Interpreter → Virtualenv → New**, location `<project>/.venv`.

Open the terminal (`Alt+F12`) and install:

```powershell
pip install -r requirements.txt
```

## 3. Point the site at your repository

Open `site/astro.config.mjs` and edit the two lines at the top:

```js
const GITHUB_USER = 'mcelrjo';
const REPO = 'turfgrass-robotic-mowing';
```

These must match your GitHub username and the repository name exactly, or the deployed CSS
and links will 404.

## 4. Push it

In the PyCharm terminal:

```powershell
git init -b main
git add -A
git commit -m "Initial commit"
git remote add origin https://github.com/<username>/<repo-name>.git
git push -u origin main
```

If git asks who you are:

```powershell
git config --global user.name "Scott McElroy"
git config --global user.email "you@auburn.edu"
```

## 5. Turn on Pages

On github.com, in your repository: **Settings → Pages**.

Under **Build and deployment → Source**, choose **GitHub Actions**. Nothing else to configure.

## 6. Watch the first deploy

Click the **Actions** tab. A run called "Build and deploy" should be going. It takes about two
minutes: checks the data, builds the site, publishes it.

When it goes green, your site is at:

```
https://<username>.github.io/<repo-name>/
```

If it fails, click the red run and read the failing step. The most common cause is a data file
that doesn't validate — the log names the file and the problem.

---

## Your workflow from here

```powershell
git pull                              # start of session
# ...edit files...
python scripts/validate.py            # check before pushing
git add -A
git commit -m "what changed"
git push                              # site redeploys in ~2 min
```

Or entirely in PyCharm: `Ctrl+K` to commit, `Ctrl+Shift+K` to push.

## Previewing before you push

```powershell
cd site
npm install        # first time only
npm run dev
```

Opens `localhost:4321` and reloads as you edit data files. Requires Node 20+
(`winget install OpenJS.NodeJS.LTS`).

## When your assistant sends you a filled workbook

```powershell
python scripts/import_from_xlsx.py path\to\filled.xlsx --dry-run   # preview
python scripts/import_from_xlsx.py path\to\filled.xlsx             # apply
python scripts/validate.py
git add -A && git commit -m "Import specs from RA" && git push
```

## Retiring the old repository

Once this one is deploying, delete the private one so there's no confusion about which is
current: **Settings → Danger Zone → Delete this repository**.
