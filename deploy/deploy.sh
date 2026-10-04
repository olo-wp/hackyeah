#!/usr/bin/env bash
set -euo pipefail

release=${1:?Usage: deploy.sh COMMIT_SHA}
[[ "$release" =~ ^[a-f0-9]{40}$ ]] || { echo 'Invalid release SHA' >&2; exit 1; }
deploy_root="$HOME/routeable"
release_dir="$deploy_root/releases/$release"
export RELEASE="$release"
export ROUTEABLE_ENV_FILE="$deploy_root/.env"
test -s "$ROUTEABLE_ENV_FILE" || { echo "Configure $ROUTEABLE_ENV_FILE first" >&2; exit 1; }
cd "$release_dir"
docker compose version
docker load --input images.tar.gz
compose=(docker compose --env-file "$ROUTEABLE_ENV_FILE" -f compose.yml)
# Validate without printing the resolved environment (it contains secrets).
"${compose[@]}" config --quiet
"${compose[@]}" run --rm --no-deps caddy caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
if ! "${compose[@]}" up -d --no-build --wait --wait-timeout 240; then
  "${compose[@]}" ps
  echo 'Deployment failed; inspect logs on the VM. Previous images are retained.' >&2
  exit 1
fi
# Recreate the proxy so updates to the bind-mounted Caddyfile take effect.
"${compose[@]}" up -d --no-deps --force-recreate caddy
curl --fail --silent --show-error --retry 12 --retry-delay 5 --retry-all-errors https://api.routeable.net/health
curl --fail --silent --show-error --retry 12 --retry-delay 5 --retry-all-errors --output /dev/null https://routeable.net/
ln -sfn "$release_dir" "$deploy_root/current"
rm -f images.tar.gz
echo "Deployed $release"
