#!/usr/bin/env bash
export site_packages="$(python -c 'import site; print(site.getsitepackages()[0])')"
link_pkg() {
  # This spoofs some of what `pip install -e` does. We already know the packages
  # have been installed when inside this container, so it is wasteful to reinstall
  # them again, even to check dependencies. Therefore we just do the linking part.
  # This involves manually creating a .egg-link file and also updating easy_instal.pth,
  # which is a cached set of package paths that pip and Python seem to use internally.
  echo "Linking $1 as $2 ..."
  local pkg_path="$1"
  local easy_install_paths="$site_packages/easy_install.pth"
  echo -ne "$pkg_path\n." >$site_packages/$2.egg-link
  touch "$easy_install_paths"
  grep -qxF "$pkg_path" "$easy_install_paths" \
    || echo "$pkg_path" >>"$easy_install_paths"
}
export -f link_pkg
find $PWD/plugins -maxdepth 1 -mindepth 1 -type d \
  -exec bash -c 'link_pkg {} kpireport-$(basename {})' \;
link_pkg $PWD kpireport
unset link_pkg
unset site_packages

# Wait for dependent services to start
wait-for mysql:3306 -t 60

if [[ $KPIREPORT_SHELL -eq 1 ]]; then
  exec bash
elif [[ $KPIREPORT_WATCH -eq 1 ]]; then
  echo "Starting watcher ..."
  ag -l -G 'examples|kpireport' . | entr python -m kpireport "$@"
else
  python -m kpireport "$@"
fi
