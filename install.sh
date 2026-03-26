#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_NAME="$(basename "$0")"
DEFAULT_REPO_URL="${REPO_URL:-https://github.com/notysozu/DeepGuard.git}"
DEFAULT_REPO_DIR="${REPO_DIR:-DeepGuard}"
INSTALL_DEV_DEPS="${INSTALL_DEV_DEPS:-0}"
START_APP="${START_APP:-1}"

log() {
  printf '[%s] %s\n' "$SCRIPT_NAME" "$*" >&2
}

warn() {
  printf '[%s] WARNING: %s\n' "$SCRIPT_NAME" "$*" >&2
}

die() {
  printf '[%s] ERROR: %s\n' "$SCRIPT_NAME" "$*" >&2
  exit 1
}

run_cmd() {
  log "$*"
  "$@"
}

have_cmd() {
  command -v "$1" >/dev/null 2>&1
}

require_min_version() {
  local label="$1"
  local actual="$2"
  local minimum="$3"

  if ! python3 - "$actual" "$minimum" <<'PY'
import sys

def parse(version: str) -> tuple[int, ...]:
    parts = []
    for item in version.split("."):
        digits = []
        for char in item:
            if char.isdigit():
                digits.append(char)
            else:
                break
        parts.append(int("".join(digits) or "0"))
    return tuple(parts)

actual = parse(sys.argv[1])
minimum = parse(sys.argv[2])
raise SystemExit(0 if actual >= minimum else 1)
PY
  then
    die "$label version $actual is too old. Required: $minimum+"
  fi
}

need_sudo() {
  [[ "${EUID:-$(id -u)}" -ne 0 ]]
}

sudo_cmd() {
  if need_sudo; then
    sudo "$@"
  else
    "$@"
  fi
}

detect_pm() {
  if have_cmd apt-get; then
    echo apt
  elif have_cmd dnf; then
    echo dnf
  elif have_cmd pacman; then
    echo pacman
  elif have_cmd brew; then
    echo brew
  else
    echo none
  fi
}

install_system_dependencies() {
  local pm
  pm="$(detect_pm)"

  case "$pm" in
    apt)
      sudo_cmd apt-get update
      sudo_cmd apt-get install -y git curl wget python3 python3-venv python3-pip nodejs npm
      ;;
    dnf)
      sudo_cmd dnf install -y git curl wget python3 python3-pip nodejs npm
      ;;
    pacman)
      sudo_cmd pacman -Sy --noconfirm git curl wget python python-pip nodejs npm
      ;;
    brew)
      run_cmd brew install git python node curl wget
      ;;
    none)
      die "No supported package manager found. Install git, Python 3.10+, and Node.js 18+ manually."
      ;;
  esac
}

ensure_base_tools() {
  local missing=0
  local tool
  for tool in git python3 node npm; do
    if ! have_cmd "$tool"; then
      missing=1
      break
    fi
  done

  if [[ "$missing" -eq 1 ]]; then
    log "Installing missing system dependencies."
    install_system_dependencies
  fi

  have_cmd git || die "git is required."
  have_cmd python3 || die "python3 is required."
  have_cmd node || die "node is required."
  have_cmd npm || die "npm is required."

  local python_version node_version
  python_version="$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
  node_version="$(node -p 'process.versions.node')"
  require_min_version "Python" "$python_version" "3.10.0"
  require_min_version "Node.js" "$node_version" "18.0.0"
}

resolve_repo_dir() {
  if [[ -f "requirements.txt" && -f "web_ui/package.json" ]]; then
    pwd
    return
  fi

  if [[ -d "$DEFAULT_REPO_DIR/.git" ]]; then
    printf '%s/%s\n' "$(pwd)" "$DEFAULT_REPO_DIR"
    return
  fi

  run_cmd git clone "$DEFAULT_REPO_URL" "$DEFAULT_REPO_DIR"
  printf '%s/%s\n' "$(pwd)" "$DEFAULT_REPO_DIR"
}

set_env_value() {
  local file="$1"
  local key="$2"
  local value="$3"

  if grep -qE "^${key}=" "$file"; then
    python3 - "$file" "$key" "$value" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
key = sys.argv[2]
value = sys.argv[3]
lines = path.read_text(encoding="utf-8").splitlines()
updated = []
replaced = False
for line in lines:
    if line.startswith(f"{key}="):
        updated.append(f"{key}={value}")
        replaced = True
    else:
        updated.append(line)
if not replaced:
    updated.append(f"{key}={value}")
path.write_text("\n".join(updated) + "\n", encoding="utf-8")
PY
  else
    printf '%s=%s\n' "$key" "$value" >>"$file"
  fi
}

write_local_model_registry() {
  local repo_dir="$1"
  cat >"$repo_dir/configs/models.local.yaml" <<'EOF'
models:
  - name: model_a
    url: http://127.0.0.1:8001/predict
  - name: model_b
    url: http://127.0.0.1:8002/predict
EOF
}

prepare_env_files() {
  local repo_dir="$1"
  local env_file="$repo_dir/.env"

  if [[ ! -f "$repo_dir/.env.example" ]]; then
    die "Missing .env.example in $repo_dir"
  fi

  if [[ ! -f "$env_file" ]]; then
    run_cmd cp "$repo_dir/.env.example" "$env_file"
  else
    log "Reusing existing .env"
  fi

  write_local_model_registry "$repo_dir"
  set_env_value "$env_file" "MODEL_REGISTRY_PATH" "configs/models.local.yaml"
  set_env_value "$env_file" "API_PORT" "8000"
  set_env_value "$env_file" "MODEL_A_PORT" "8001"
  set_env_value "$env_file" "MODEL_B_PORT" "8002"

  cat >"$repo_dir/web_ui/.env.local" <<'EOF'
VITE_API_BASE=http://127.0.0.1:8000
EOF
}

install_project_dependencies() {
  local repo_dir="$1"
  local requirements_file="$repo_dir/requirements.txt"

  if [[ ! -d "$repo_dir/.venv" ]]; then
    run_cmd python3 -m venv "$repo_dir/.venv"
  fi

  run_cmd "$repo_dir/.venv/bin/python" -m pip install --upgrade pip
  if [[ "$INSTALL_DEV_DEPS" == "1" && -f "$repo_dir/requirements-dev.txt" ]]; then
    requirements_file="$repo_dir/requirements-dev.txt"
  fi
  run_cmd "$repo_dir/.venv/bin/pip" install -r "$requirements_file"

  if [[ -f "$repo_dir/web_ui/package-lock.json" ]]; then
    run_cmd npm --prefix "$repo_dir/web_ui" ci
  else
    run_cmd npm --prefix "$repo_dir/web_ui" install
  fi

  run_cmd npm --prefix "$repo_dir/web_ui" run build
}

is_pid_running() {
  local pid_file="$1"
  [[ -f "$pid_file" ]] || return 1
  local pid
  pid="$(cat "$pid_file")"
  [[ -n "$pid" ]] || return 1
  kill -0 "$pid" >/dev/null 2>&1
}

start_process() {
  local name="$1"
  local log_file="$2"
  local pid_file="$3"
  shift 3

  if is_pid_running "$pid_file"; then
    log "$name is already running with PID $(cat "$pid_file")"
    return
  fi

  mkdir -p "$(dirname "$log_file")" "$(dirname "$pid_file")"
  log "Starting $name"
  nohup "$@" >"$log_file" 2>&1 &
  echo "$!" >"$pid_file"
}

wait_for_health() {
  local url="$1"
  local attempts=30
  local i

  for ((i = 1; i <= attempts; i++)); do
    if have_cmd curl && curl -fsS "$url" >/dev/null 2>&1; then
      log "Health check passed: $url"
      return
    fi
    sleep 1
  done

  warn "Health check did not pass in time: $url"
}

start_application() {
  local repo_dir="$1"
  local runtime_dir="$repo_dir/.deepguard"
  local log_dir="$runtime_dir/logs"
  local pid_dir="$runtime_dir/pids"
  local python_bin="$repo_dir/.venv/bin/python"
  local uvicorn_bin="$repo_dir/.venv/bin/uvicorn"

  [[ -x "$uvicorn_bin" ]] || die "uvicorn was not installed in $repo_dir/.venv"

  mkdir -p "$log_dir" "$pid_dir"

  (
    cd "$repo_dir"
    export PYTHONPATH="$repo_dir"
    export API_PORT="${API_PORT:-8000}"
    export MODEL_A_PORT="${MODEL_A_PORT:-8001}"
    export MODEL_B_PORT="${MODEL_B_PORT:-8002}"

    run_cmd "$python_bin" scripts/migrate.py

    start_process "model_a" "$log_dir/model_a.log" "$pid_dir/model_a.pid" \
      "$uvicorn_bin" model_services.model_a.app.main:app --host 127.0.0.1 --port "$MODEL_A_PORT"
    start_process "model_b" "$log_dir/model_b.log" "$pid_dir/model_b.pid" \
      "$uvicorn_bin" model_services.model_b.app.main:app --host 127.0.0.1 --port "$MODEL_B_PORT"
    start_process "api_gateway" "$log_dir/api_gateway.log" "$pid_dir/api_gateway.pid" \
      "$uvicorn_bin" api_gateway.app.main:app --host 127.0.0.1 --port "$API_PORT"
    start_process "web_ui" "$log_dir/web_ui.log" "$pid_dir/web_ui.pid" \
      npm --prefix "$repo_dir/web_ui" run dev -- --host 127.0.0.1 --port 5173
  )

  wait_for_health "http://127.0.0.1:8000/health"
}

print_summary() {
  local repo_dir="$1"

  cat <<EOF

DeepGuard is ready.

- Repository: $repo_dir
- API: http://127.0.0.1:8000
- UI: http://127.0.0.1:5173
- Logs: $repo_dir/.deepguard/logs
- PIDs: $repo_dir/.deepguard/pids

Security note: review this script before using curl|bash in shared or production environments.
EOF
}

main() {
  ensure_base_tools
  local repo_dir
  repo_dir="$(resolve_repo_dir)"
  prepare_env_files "$repo_dir"
  install_project_dependencies "$repo_dir"
  if [[ "$START_APP" == "1" ]]; then
    start_application "$repo_dir"
  else
    log "Skipping application startup because START_APP=$START_APP"
  fi
  print_summary "$repo_dir"
}

main "$@"
