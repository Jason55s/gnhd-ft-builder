# Build and publish your Docker image without installing Docker Desktop

This project is set up for jason65/gnhd-ft and builds remotely with GitHub Actions.

1. Create a **public** Docker Hub repository named `gnhd-ft` at https://hub.docker.com/.
2. Create a GitHub account (if needed) and create a new GitHub repository named `gnhd-ft-builder` at https://github.com/new. You can choose Public for no-cost Actions on standard public runners.
3. Extract this ZIP on your PC. In your GitHub repository, choose **Add file > Upload files** and drag in the *contents* of this extracted folder, including the `.github` folder, not the ZIP itself. Make sure `Dockerfile` appears at the repository root and `.github/workflows/publish.yml` is present. Commit the files.
4. At https://hub.docker.com/, open Account settings > Personal access tokens, create a token with **Read & Write repository** permissions, and copy it once. Do not share it or upload it into GitHub files.
5. In the GitHub repository choose **Settings > Secrets and variables > Actions > New repository secret**. Name it `DOCKERHUB_TOKEN` and paste the token into the value.
6. Open **Actions > Publish gnhd-ft to Docker Hub > Run workflow**. After the run succeeds, the image is `docker.io/jason65/gnhd-ft:latest` (and `:1.0`).

The repository must contain all project files, not just the ZIP. The UUID is supplied at runtime in an **authorized** deployment environment; this image has no embedded UUID. Google Skills org policies can still block your Docker Hub image even after a successful build and push.
