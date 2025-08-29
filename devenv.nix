{ pkgs, lib, config, ... }: {

  languages.python.enable = true;

  packages = with pkgs; [
    # sqlite
    python3.pkgs.fastapi
    python3.pkgs.uvicorn
    python3.pkgs.jinja2

    python3.pkgs.icecream
  ];

  git-hooks.hooks = {
    shellcheck.enable = true;
    ruff.enable = true;
  };

  git-hooks.hooks.unit-tests = {
    # TODO: enable when we have tests :)
    enable = false;
    name = "Unit tests";
    entry = "python -m unittest discover .";
    # types = [ "python" ];
    language = "python";

    # Set this to false to not pass the changed files
    # to the command (default: true):
    pass_filenames = false;
  };
  # enterTest = " python -m unittest discover . ";
}
