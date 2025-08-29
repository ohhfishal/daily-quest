{ pkgs, lib, config, ... }: {

  languages.python.enable = true;

  packages = with pkgs; [
    # sqlite
    python3.pkgs.fastapi
    python3.pkgs.uvicorn
    python3.pkgs.jinja2
  ];

  git-hooks.hooks = {
    shellcheck.enable = true;
    black.enable = true;
  };

}
