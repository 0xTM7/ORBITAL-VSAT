#!/bin/bash

Red='\033[0;31m'
Green='\033[0;32m'
Yellow='\033[1;33m'
Cyan='\033[0;36m'
Bold='\033[1m'
Nc='\033[0m'

Info()    { echo -e "${Cyan}[*]${Nc} $1"; }
Success() { echo -e "${Green}[✓]${Nc} $1"; }
Warning() { echo -e "${Yellow}[!]${Nc} $1"; }
Err()     { echo -e "${Red}[✗]${Nc} $1"; }
Die()     { Err "$1"; exit 1; }

Banner() {
  clear
  echo -e "${Cyan}${Bold}"
  echo "  ╔═══════════════════════════════════════╗"
  echo "  ║        OrbitalVSAT  Installer         ║"
  echo "  ║     Support: Termux | Linux           ║"
  echo "  ╚═══════════════════════════════════════╝"
  echo -e "${Nc}"
}

DetectEnv() {
  if [ -d "/data/data/com.termux" ] || [ -n "$TERMUX_VERSION" ]; then
    Env="termux"
    InstallDir="$PREFIX/bin"
    PythonCmd="python"
  elif [ -f "/etc/debian_version" ] || command -v apt &>/dev/null; then
    Env="debian"
    InstallDir="/usr/local/bin"
    PythonCmd="python3"
  elif [ -f "/etc/arch-release" ] || command -v pacman &>/dev/null; then
    Env="arch"
    InstallDir="/usr/local/bin"
    PythonCmd="python3"
  elif [ -f "/etc/fedora-release" ] || command -v dnf &>/dev/null; then
    Env="fedora"
    InstallDir="/usr/local/bin"
    PythonCmd="python3"
  else
    Env="generic"
    InstallDir="/usr/local/bin"
    PythonCmd="python3"
  fi

  Info "Detected environment : ${Bold}$Env${Nc}"
  Info "Install directory    : ${Bold}$InstallDir${Nc}"
}

CheckRoot() {
  if [ "$Env" != "termux" ] && [ "$(id -u)" != "0" ]; then
    Warning "Not running as root. Using sudo for system-wide install..."
    Sudo="sudo"
  else
    Sudo=""
  fi
}

InstallPython() {
  if command -v "$PythonCmd" &>/dev/null; then
    Success "Python already installed: $(${PythonCmd} --version 2>&1)"
    return
  fi

  Info "Installing Python..."
  case "$Env" in
    termux)  pkg install -y python ;;
    debian)  $Sudo apt update -y && $Sudo apt install -y python3 python3-pip ;;
    arch)    $Sudo pacman -Sy --noconfirm python python-pip ;;
    fedora)  $Sudo dnf install -y python3 python3-pip ;;
    *)       Die "Cannot auto-install Python. Please install it manually." ;;
  esac

  command -v "$PythonCmd" &>/dev/null || Die "Python installation failed."
  Success "Python installed successfully."
}

InstallPip() {
  if "$PythonCmd" -m pip --version &>/dev/null; then
    Success "pip already available."
    return
  fi

  Info "Installing pip..."
  case "$Env" in
    termux)  pkg install -y python-pip ;;
    debian)  $Sudo apt install -y python3-pip ;;
    arch)    $Sudo pacman -Sy --noconfirm python-pip ;;
    fedora)  $Sudo dnf install -y python3-pip ;;
    *)
      Warning "Trying to install pip via get-pip.py..."
      curl -sS https://bootstrap.pypa.io/get-pip.py | "$PythonCmd" || Die "pip installation failed."
      ;;
  esac
  Success "pip installed."
}

InstallDeps() {
  Info "Installing Python dependencies..."

  ScriptDir="$(cd "$(dirname "$0")" && pwd)"
  ReqFile="$ScriptDir/requirements.txt"

  [ -f "$ReqFile" ] || Die "requirements.txt not found in $ScriptDir"

  "$PythonCmd" -m pip install -r "$ReqFile" --quiet || Die "Failed to install dependencies."
  Success "All dependencies installed from requirements.txt."
}

InstallTool() {
  ScriptDir="$(cd "$(dirname "$0")" && pwd)"
  if [ "$Env" = "termux" ]; then
    ToolDest="$PREFIX/opt/orbitalvsat"
  else
    ToolDest="/opt/orbitalvsat"
  fi

  [ -f "$ScriptDir/orbitalvsat.py" ] || Die "orbitalvsat.py not found in $ScriptDir"

  Info "Copying $ScriptDir -> $ToolDest ..."
  $Sudo rm -rf "$ToolDest"
  $Sudo mkdir -p "$(dirname "$ToolDest")"
  $Sudo cp -r "$ScriptDir" "$ToolDest"

  [ -f "$ToolDest/orbitalvsat.py" ] || Die "Copy failed: $ToolDest/orbitalvsat.py missing."

  WrapperPath="$InstallDir/vsat"
  $Sudo tee "$WrapperPath" > /dev/null << WRAPPER
#!/bin/bash
exec $PythonCmd $ToolDest/orbitalvsat.py "\$@"
WRAPPER

  $Sudo chmod +x "$WrapperPath" || Die "Cannot set execute permission on wrapper."
  Success "Tool installed to  : $ToolDest"
  Success "Wrapper created at : $WrapperPath"
}

Verify() {
  export PATH="$PATH:$InstallDir"
  if command -v vsat &>/dev/null; then
    Success "Done! Type ${Bold}vsat${Nc} to start OrbitalVSAT."
  else
    Warning "Install done. Restart terminal then type ${Bold}vsat${Nc}."
  fi
}

Uninstall() {
  if [ "$Env" = "termux" ]; then
    ToolDest="$PREFIX/opt/orbitalvsat"
  else
    ToolDest="/opt/orbitalvsat"
  fi
  Info "Removing vsat wrapper..."
  $Sudo rm -f "$InstallDir/vsat"
  Info "Removing $ToolDest ..."
  $Sudo rm -rf "$ToolDest"
  Success "Uninstall complete."
}

Main() {
  Banner

  if [ "$1" = "--uninstall" ] || [ "$1" = "-u" ]; then
    DetectEnv
    CheckRoot
    Uninstall
    exit 0
  fi

  DetectEnv
  CheckRoot
  echo ""
  InstallPython
  InstallPip
  InstallDeps
  echo ""
  InstallTool
  echo ""
  Verify
  echo ""
  echo -e "${Cyan}──────────────────────────────────────────${Nc}"
  echo -e "  ${Bold}Usage     :${Nc} vsat"
  echo -e "  ${Bold}Uninstall :${Nc} bash install.sh --uninstall"
  echo -e "${Cyan}──────────────────────────────────────────${Nc}"
  echo ""
}

Main "$@"
