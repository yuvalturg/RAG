# Contributing to RAG

Thank you for your interest in contributing to the RAG project!

## Table of Contents
- [Development Workflow](#development-workflow)
- [Release Process](#release-process)
- [Versioning](#versioning)
- [Building and Testing](#building-and-testing)

## Development Workflow

1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes
4. Test your changes locally (see [Local Setup Guide](docs/local_setup_guide.md))
5. Submit a pull request to the `main` branch

## Release Process

This project uses an automated release workflow that handles versioning, tagging, Docker image building, and GitHub releases.

### How Releases Work

The release process is triggered automatically when code is pushed to the `main` branch. The workflow:

1. **Version Determination**
   - Reads the current version from `deploy/helm/rag/Chart.yaml` (`appVersion` field)
   - Checks if a Git tag already exists for this version
   - If the tag exists: auto-increments the patch version (e.g., 0.2.22 → 0.2.23)
   - If the tag doesn't exist: uses the current version (manual bump detected)

2. **Version Update**
   - Updates both `version` and `appVersion` fields in `deploy/helm/rag/Chart.yaml`
   - Commits the change with message: `chore: bump version to X.Y.Z [skip ci]`
   - The `[skip ci]` tag prevents the workflow from triggering again on this commit

3. **Git Tagging**
   - Creates an annotated Git tag (e.g., `v0.2.23`)
   - Pushes the tag to the repository

4. **Docker Image Build**
   - Builds the frontend Docker image from `frontend/Containerfile`
   - Pushes to Quay.io with two tags:
     - Version tag: `quay.io/rh-ai-quickstart/llamastack-dist-ui:<version>`
     - Latest tag: `quay.io/rh-ai-quickstart/llamastack-dist-ui:latest`
   - Uses GitHub Actions cache for faster builds

5. **Helm Chart Packaging**
   - Updates Helm chart dependencies
   - Packages the chart from `deploy/helm/rag/`
   - Creates a `.tgz` artifact

6. **GitHub Release**
   - Creates a GitHub release with the version tag
   - Includes release notes with Docker image and Helm install instructions
   - Attaches the packaged Helm chart

### Versioning

We follow [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

#### Manual Version Bump

To manually control the version:

1. Edit `deploy/helm/rag/Chart.yaml`
2. Update the `appVersion` field to your desired version
3. Commit and push to `main`

The workflow will detect that no tag exists for this version and use it as-is.

#### Automatic Version Bump

If you don't manually update the version, the workflow will automatically increment the patch version when you push to `main`.

### Example Release Flow

**Scenario 1: Automatic patch increment**
```bash
# Current state: appVersion: "0.2.22", tag v0.2.22 exists
git push origin main
# Result: Version auto-incremented to 0.2.23, tag v0.2.23 created
```

**Scenario 2: Manual version bump**
```bash
# Edit Chart.yaml: appVersion: "0.3.0"
git add deploy/helm/rag/Chart.yaml
git commit -m "feat: major new feature"
git push origin main
# Result: Version 0.3.0 used, tag v0.3.0 created
```

## Building and Testing

### Local Testing

See the [Local Setup Guide](docs/local_setup_guide.md) for instructions on running the application locally.

### Building the Docker Image

To build the frontend image locally:

```bash
docker build -t llamastack-dist-ui:dev -f frontend/Containerfile frontend/
```

### Testing the Helm Chart

To test the Helm chart locally:

```bash
cd deploy/helm
helm dependency update rag/
helm template rag rag/ --debug
```

To install locally (requires a Kubernetes cluster):

```bash
helm install rag-test rag/ --namespace test --create-namespace
```

## Questions or Issues?

If you have questions or run into issues:
- Check existing [GitHub Issues](https://github.com/rh-ai-quickstart/RAG/issues)
- Review the [documentation](docs/)
- Open a new issue if needed
