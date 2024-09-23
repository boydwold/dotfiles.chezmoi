#!/usr/bin/env bash

# ------------------------------------------------------------------------------
# Homebrew Setup and Maintenance
# ------------------------------------------------------------------------------
# Update Homebrew to the latest version.
brew update

# Upgrade already-installed formulae.
brew upgrade

# Save Homebrew’s installed location.
BREW_PREFIX=$(brew --prefix)

# Remove outdated versions from the cellar.
brew cleanup


# ------------------------------------------------------------------------------
# Command-Line Utilities
# ------------------------------------------------------------------------------
brew install moreutils       # Useful utilities like `sponge`.
brew install findutils        # GNU `find`, `locate`, `updatedb`, and `xargs`, with `g`-prefix.
brew install gnu-sed --with-default-names  # GNU `sed`, replaces macOS version.
brew install wget             # Tool for downloading files from the web.
brew install coreutils        # GNU core utilities.
brew install tree             # Display directories as trees.
brew install eza              # Enhanced replacement for `ls`.
brew install zoxide           # Fast directory jumper.
brew install fzf              # Command-line fuzzy finder.
brew install tldr             # Simplified man pages.
brew install bat              # Enhanced `cat` with syntax highlighting.
brew install trash-cli        # Safely moves files to the trash.
brew install htop             # Interactive process viewer.
brew install gnupg            # Encryption utilities (GPG).
brew install speedtest-cli    # Command-line internet speed testing.

# ------------------------------------------------------------------------------
# Version Control and Development Tools
# ------------------------------------------------------------------------------
brew install git              # Git version control.
brew install gh               # GitHub CLI tool.
brew install yarn             # JavaScript package manager.
brew install pygments          # Syntax highlighter for code.
brew install nvim             # Neovim, a modern text editor.

# ------------------------------------------------------------------------------
# Shell and Terminal Enhancements
# ------------------------------------------------------------------------------
brew install zsh              # Zsh shell.
brew install zsh-completions   # Auto-completions for Zsh.
brew install zsh-syntax-highlighting # Syntax highlighting in Zsh.
brew install terminal-notifier # macOS notifications from the terminal.

# ------------------------------------------------------------------------------
# System Tools and Networking
# ------------------------------------------------------------------------------
brew install openssh          # Latest version of OpenSSH.
brew install screen           # Terminal multiplexer.
brew install vim --with-override-system-vi # Enhanced version of Vim.
brew install grep             # Latest GNU version of `grep`.

# ------------------------------------------------------------------------------
# Fonts
# ------------------------------------------------------------------------------
brew install --cask font-fira-code        # Fira Code font.
brew install --cask font-fira-code-nerd-font  # Fira Code Nerd Font (with glyphs).
brew install --cask font-hasklug-nerd-font  # Hasklug Nerd Font.
brew install --cask font-meslo-lg-nerd-font # Meslo LG Nerd Font.

# ------------------------------------------------------------------------------
# Media and Entertainment
# ------------------------------------------------------------------------------
brew install --cask spotify          # Spotify music client.
brew install --cask vlc              # Media player for various formats.
brew install --cask plex             # Media server software.
brew install --cask obs              # Streaming and recording software.
brew install --cask screenflow       # Screen recording and video editing.

# ------------------------------------------------------------------------------
# Development Environment and Virtualization
# ------------------------------------------------------------------------------
brew install --cask fig              # Command-line helper tool.
brew install --cask multipass        # Manage Ubuntu VMs.
brew install --cask iterm2           # Advanced terminal emulator.
brew install --cask visual-studio-code # Code editor.
brew install --cask github           # GitHub Desktop client.
brew install --cask orbstack         # Docker alternative for macOS.

# ------------------------------------------------------------------------------
# Design and Graphics Tools
# ------------------------------------------------------------------------------
brew install --cask figma            # Collaborative design tool.

# ------------------------------------------------------------------------------
# Desktop Applications and Browsers
# ------------------------------------------------------------------------------
brew install --cask telegram         # Messaging app.
brew install --cask arc              # Arc browser.
brew install --cask microsoft-edge   # Microsoft Edge browser.
brew install --cask firefox          # Firefox browser.
brew install --cask slack            # Team communication platform.
brew install --cask discord          # Communication platform for communities.
brew install --cask raycast          # Productivity launcher.
brew install --cask karabiner-elements # Keyboard customization tool.
brew install --cask keyboard-maestro # Mac automation software.
brew install --cask balenaetcher     # Flash OS images to SD cards/USB drives.
brew install --cask protonvpn        # VPN service for secure browsing.

# ------------------------------------------------------------------------------
# Productivity Tools
# ------------------------------------------------------------------------------
brew install --cask microsoft-teams  # Microsoft Teams for collaboration.
brew install --cask onedrive         # Cloud storage solution.
brew install --cask pdf-expert       # PDF editor.

# ------------------------------------------------------------------------------
# Quick Look Plugins (for better previews)
# ------------------------------------------------------------------------------
brew install --cask qlcolorcode      # Syntax highlighting in Quick Look.
brew install --cask qlstephen        # Preview text files without extensions.
brew install --cask quicklook-json   # JSON file Quick Look support.
brew install --cask qlimagesize      # Display image size in Quick Look.
brew install --cask webpquicklook    # Quick Look support for WebP images.

# ------------------------------------------------------------------------------
# System Utilities and Extras
# ------------------------------------------------------------------------------
brew install --cask gpg-suite        # Suite for managing GPG encryption.
brew install --cask stats            # System stats in the menu bar.
brew install --cask bartender        # Organizes menu bar icons.
brew install --cask caffeine         # Prevents macOS from sleeping.
brew install --cask cleanshot        # Screen capture tool.

# ------------------------------------------------------------------------------
# Custom Applications
# ------------------------------------------------------------------------------
brew install --cask devonthink       # Document management tool.
brew install --cask gpg-keychain     # GPG key management.
brew install --cask obsbot-webcam    # Webcam software.
brew install --cask openaudible      # Audiobook manager.
brew install --cask scapple          # Mind-mapping tool.
brew install --cask signal           # Encrypted messaging app.
brew install --cask whatsapp         # WhatsApp messaging client.
brew install --cask zoom             # Video conferencing.

# ------------------------------------------------------------------------------
# Mac App Store Applications (mas CLI)
# ------------------------------------------------------------------------------
mas install 497799835  # Xcode: Apple's IDE for macOS/iOS development.
mas install 1499198946 # Structured - Daily Planner: Task and time management.

# ------------------------------------------------------------------------------
# Applications that Might Need Manual Installation (Managed via Setapp)
# ------------------------------------------------------------------------------
# - CleanMyMac X
# - Downie
# - NotePlan
# - TextSniper
# - HazeOver
# - Bartender
# - Vidrio
# - Keep It Shot
# - Elephas
# - Meeter
# - Yoink
# - In Your Face
# - Gitfox

