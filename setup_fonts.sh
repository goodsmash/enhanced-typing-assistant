#!/bin/bash

# Error handling function
cleanup() {
    echo "Error occurred, cleaning up..."
    rm -f ./*.otf
    exit 1
}
trap cleanup ERR

# Create fonts directory with error checking
if ! mkdir -p resources/fonts/OpenDyslexic; then
    echo "Error: Failed to create fonts directory"
    exit 1
fi

cd resources/fonts/OpenDyslexic || exit 1

# Add version check
VERSION="1.0"
echo "OpenDyslexic Font Setup Script v${VERSION}"

# Array of font files to download
fonts=(
    "OpenDyslexic-Regular.otf"
    "OpenDyslexic-Bold.otf"
    "OpenDyslexic-Italic.otf"
    "OpenDyslexic-BoldItalic.otf"
    "OpenDyslexicMono-Regular.otf"
    "OpenDyslexicAlta-Regular.otf"
    "OpenDyslexicAlta-Bold.otf"
    "OpenDyslexicAlta-BoldItalic.otf"
    "OpenDyslexicAlta-Italic.otf"
)

# Download with progress and fallback
download_font() {
    local font=$1
    echo -n "Downloading ${font}... "
    if ! wget --quiet "https://github.com/antijingoist/opendyslexic/raw/master/compiled/$font"; then
        echo "Failed, trying backup source..."
        if ! wget --quiet "https://mirror.example.com/opendyslexic/$font"; then
            echo "Failed to download $font from all sources"
            return 1
        fi
    fi
    echo "Done"
    
    # Verify file exists and is not empty
    if [ ! -s "$font" ]; then
        echo "Downloaded file is empty or missing"
        return 1
    fi
}

# System font installation (Linux only)
install_system_fonts() {
    if [ "$(uname)" == "Linux" ]; then
        read -p "Install fonts system-wide? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo mkdir -p /usr/local/share/fonts/OpenDyslexic/
            sudo cp ./*.otf /usr/local/share/fonts/OpenDyslexic/
            fc-cache -f -v
            echo "Fonts installed system-wide"
        fi
    fi
}

# Main download loop
for font in "${fonts[@]}"; do
    download_font "$font" || cleanup
done

# Installation option
install_system_fonts

echo "Successfully downloaded and verified all OpenDyslexic fonts"
echo "Font files are located in: $(pwd)"