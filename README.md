# agent-capability-core

Shared skills, scripts, and workspace metadata for reusable local agent capabilities.

## Overview

`agent-capability-core` is a source-of-truth workspace for portable skills and their supporting assets. It packages reusable capabilities such as document handling, screenshot capture, slide generation, speech, transcription, video tooling, browser automation, and workflow solidification into a single repo that can be exported into a provider-neutral runtime and, when supported, mounted into a specific AI runtime home.

This repository is intended to be:

- **portable**: skills live in self-contained directories with their own instructions, references, and scripts
- **inspectable**: the workspace manifest declares what is exported into the runtime
- **machine-friendly**: helper scripts verify and wire the workspace into a local Codex home
- **safe to share**: machine-local config and personal/private memories are deliberately excluded

## Repository layout

```text
.
|- bootstrap/                 public bootstrap entrypoints
|- docs/                      project notes and inventories
|- schemas/                   shared schema documents
|- scripts/                   workspace-level helper scripts
|- skills/                    reusable Codex skills
|- workspace.lock.yaml
|- machine.local.template.yaml
|- workspace.manifest.yaml
`- README.md
```

## Included capabilities

The current workspace exports reusable skills for:

- browser automation
- document and PDF workflows
- screenshots and screenshot-to-video conversion
- slide and presentation generation
- speech synthesis and transcription
- image and video generation workflows
- Git/repository hygiene workflows
- workflow solidification and portability auditing

See [docs/asset-inventory.md](docs/asset-inventory.md) for the included and intentionally excluded assets in this core workspace.

## Quick start

### 1. Clone the repository

```powershell
git clone https://github.com/sexymonk/agent-capability-core.git
cd agent-capability-core
```

### 2. Create a machine-local config

Copy `machine.local.template.yaml` to `machine.local.yaml` and adjust the paths for your machine.

### 3. Mount the skills into your runtime home

Use the workspace linker to create runtime junctions under your local runtime skills directory:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\link_runtime_mounts.ps1 -WorkspaceRoot . -RuntimeHome $env:CODEX_HOME
```

### 4. Verify the workspace

```powershell
python .\scripts\doctor.py
```

The doctor script validates the manifest, expected skill paths, runtime/provider configuration, and machine-local configuration.

## Workspace contract

- `workspace.manifest.yaml` is the exported runtime contract for this repository.
- `workspace.lock.yaml` records the tested repo ref for reproducible restore.
- `machine.local.yaml` is intentionally local-only and should not be committed.
- `skills/` contains the reusable capabilities that may be mounted into a Codex runtime.
- repo-specific or private skills should stay outside this core workspace unless they are intentionally generalized.

## Design principles

This repository favors:

- small, composable skills
- explicit manifests over implicit discovery
- reusable references over prompt-only knowledge
- tooling that keeps local runtime setup reproducible
- separation between portable assets and user-private state

## Contributing

Contributions are welcome. A good contribution usually:

1. adds or improves a reusable skill
2. keeps machine-specific state out of version control
3. updates related references or learning logs when behavior changes
4. preserves portability for other Codex environments

If you add a new workspace-exported skill, also update:

- `workspace.manifest.yaml`
- any related docs in `docs/`
- the skill's own `SKILL.md` and supporting references

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
