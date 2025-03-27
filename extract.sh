#!/bin/bash 

# Update and upgrade system packages
update_system() {
    apt-get update && apt-get upgrade -y
}

# Install Python 3.12 and essential dependencies
install_python() {
    apt-get install -y software-properties-common
    add-apt-repository -y ppa:deadsnakes/ppa
    apt-get update
    apt-get install -y python3.12 python3.12-dev python3.12-venv python3-pip libpython3.12 libpython3.12-dev
}

# Download and install qbittorrent-nox based on system architecture
install_qbittorrent() {
    ARCH=$(uname -m)
    mkdir -p /usr/local/bin

    case "$ARCH" in
        x86_64)
            wget -qO /usr/local/bin/xnox https://github.com/userdocs/qbittorrent-nox-static/releases/latest/download/x86_64-qbittorrent-nox
            ;;
        aarch64)
            wget -qO /usr/local/bin/xnox https://github.com/userdocs/qbittorrent-nox-static/releases/latest/download/aarch64-qbittorrent-nox
            ;;
        *)
            echo "Unsupported architecture for qbittorrent-nox: $ARCH"
            exit 1
            ;;
    esac

    chmod 700 /usr/local/bin/xnox
}

# Main script execution
main() {
    install_qbittorrent
    }

main
