# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Directory Overview

This is Boyd Wold's macOS home directory. Key locations:

- `projects/personal/` - Personal GitHub repos (boydwold identity)
- `projects/work-lendos/` - Work GitHub repos (rpcaptain identity)
- `.config/` - Tool configurations (starship, chezmoi, etc.)
- `.claude/` - Claude Code settings and history

## Primary Projects

| Project | Description | Start Command |
|---------|-------------|---------------|
| `projects/work-lendos/lendos/` | Enterprise lending platform | `cd ~/projects/work-lendos/lendos && tilt up` |
| `projects/work-lendos/right-pedal/` | LendOS variant deployment | `cd ~/projects/work-lendos/right-pedal && tilt up` |
| `projects/personal/imdoing/` | iOS time tracking app (SwiftUI) | `open ~/projects/personal/imdoing/imdoing.xcodeproj` |

For detailed project commands, see individual project CLAUDE.md files.

## Shell Environment

**Shell**: zsh with starship prompt, fzf, zsh-autosuggestions, zsh-syntax-highlighting

**Useful aliases** (defined in ~/.zshrc or ~/.aliases):
```bash
ll                # eza -la --icons (detailed list)
lt                # eza --tree --level=2 (tree view)
..                # cd ..
...               # cd ../..
aws-sso-refresh   # granted sso populate (refresh AWS SSO credentials)
```

**Key tools available**:
- `brew` - Homebrew package manager
- `fzf` - Fuzzy finder (Ctrl+R for history search)
- `eza` - Modern ls replacement
- `starship` - Cross-shell prompt
- `chezmoi` - Dotfile manager

## Dotfile Management (chezmoi)

Source: `~/projects/personal/dotfiles.chezmoi`

```bash
chezmoi diff                  # Preview what would change
chezmoi apply                 # Apply changes to home
chezmoi add <file>            # Track a file
chezmoi add --force <file>    # Re-add/update a tracked file
chezmoi add --encrypt <file>  # Track encrypted
chezmoi status                # Show what needs syncing

# Git operations (runs in source repo)
chezmoi git status
chezmoi git add -A
chezmoi git commit -m "msg"
chezmoi git push
```

**Workflow:** Edit dotfiles in ~/, then `chezmoi add --force` to update source. Use `chezmoi git` for commits - don't cd into the source repo.

Uses age encryption (key at `~/.config/chezmoi/key.txt`). SSH keys live in 1Password, only public keys tracked.

## Git & SSH Configuration

**Identity routing** - Personal is default, work only in `~/projects/work-lendos/`:

| Location | Git User | SSH Host | Signing |
|----------|----------|----------|---------|
| Default (everywhere) | boydwold@gmail.com | github-personal | Yes (1Password) |
| `~/projects/work-lendos/` | rpcaptain | github-work | Yes (1Password) |

**Config files:**
- `~/.gitconfig` - Personal default + `includeIf` for work
- `~/.gitconfig-work` - Work identity, signing key, URL rewrite
- `~/.ssh/config` - SSH host aliases with 1Password agent
- `~/.ssh/id_ed25519-personal.pub` / `~/.ssh/id_ed25519-work.pub` - Public keys for 1Password matching

**How it works:**
1. Git URL `git@github.com:` is rewritten to `git@github-personal:` or `git@github-work:` based on directory
2. SSH config maps those hosts to github.com with the correct public key
3. 1Password agent matches public key to the right private key

Just clone repos normally and place them in the correct folder - routing is automatic.

**AWS**: Use `assume Dev/TiltEngineerAccess` for LendOS development

## Navigation Tips

```bash
# Work projects (rpcaptain GitHub identity)
cd ~/projects/work-lendos

# Personal projects (boydwold GitHub identity)
cd ~/projects/personal

# Dotfiles source
chezmoi cd
```
