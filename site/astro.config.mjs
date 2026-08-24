import { defineConfig } from 'astro/config';

// ---------------------------------------------------------------------------
// Set these two to match your GitHub account and repository name.
// GITHUB_USER is your username; REPO is the repository name exactly as it
// appears in the URL. The site will publish to:
//     https://<GITHUB_USER>.github.io/<REPO>/
// ---------------------------------------------------------------------------
const GITHUB_USER = 'mcelrjo';
const REPO = 'turfgrass-robotic-mowing';

export default defineConfig({
  site: `https://${GITHUB_USER}.github.io`,
  base: `/${REPO}`,
});
