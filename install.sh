#!/bin/sh

# Bootstrap script for chezmoi dotfiles
# Usage: git clone <repo> && cd <repo> && ./install.sh
#
# NOTE: This repo uses age encryption. For full setup, you need:
#   ~/.config/chezmoi/key.txt (age private key)
#
# Get the key from 1Password or your secure backup before running,
# or run with --skip-encrypted to set up without encrypted files.

# -e: exit on error
# -u: exit on unset variables
set -eu

AGE_KEY_PATH="${HOME}/.config/chezmoi/key.txt"

# Check for age encryption key
if [ ! -f "$AGE_KEY_PATH" ]; then
	echo "" >&2
	echo "⚠️  Age encryption key not found at: $AGE_KEY_PATH" >&2
	echo "" >&2
	echo "This repo uses age encryption for sensitive files." >&2
	echo "Options:" >&2
	echo "  1. Copy your age key to $AGE_KEY_PATH and re-run this script" >&2
	echo "  2. Continue without encrypted files (run with --skip-encrypted)" >&2
	echo "" >&2

	if [ "${1:-}" = "--skip-encrypted" ]; then
		echo "Continuing without encrypted files..." >&2
		SKIP_ENCRYPTED=1
	else
		printf "Continue without encrypted files? [y/N] " >&2
		read -r response
		case "$response" in
			[yY][eE][sS]|[yY])
				SKIP_ENCRYPTED=1
				;;
			*)
				echo "Aborting. Please add your age key and try again." >&2
				exit 1
				;;
		esac
	fi
else
	echo "✓ Age encryption key found" >&2
	SKIP_ENCRYPTED=0
fi

# Install chezmoi if not present
if ! chezmoi="$(command -v chezmoi)"; then
	bin_dir="${HOME}/.local/bin"
	chezmoi="${bin_dir}/chezmoi"
	echo "Installing chezmoi to '${chezmoi}'" >&2
	if command -v curl >/dev/null; then
		chezmoi_install_script="$(curl -fsSL get.chezmoi.io)"
	elif command -v wget >/dev/null; then
		chezmoi_install_script="$(wget -qO- get.chezmoi.io)"
	else
		echo "To install chezmoi, you must have curl or wget installed." >&2
		exit 1
	fi
	sh -c "${chezmoi_install_script}" -- -b "${bin_dir}"
	unset chezmoi_install_script bin_dir
fi

# POSIX way to get script's dir: https://stackoverflow.com/a/29834779/12156188
script_dir="$(cd -P -- "$(dirname -- "$(command -v -- "$0")")" && pwd -P)"

# Build chezmoi arguments
set -- init --apply --source="${script_dir}"

if [ "$SKIP_ENCRYPTED" = "1" ]; then
	set -- "$@" --exclude=encrypted
fi

echo "Running 'chezmoi $*'" >&2
# exec: replace current process with chezmoi
exec "$chezmoi" "$@"
