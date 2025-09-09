{ pkgs, lib, config, ... }: {

  languages.python = {
    enable = true;
    version = "3.13.5";
  };

  env.HOST = "localhost";
  env.PORT = "8000";
  env.CONTACT_DISCORD = "TEST_DISCORD";

  packages = with pkgs; [
    # sqlite
    python3.pkgs.pip
    python3.pkgs.fastapi
    python3.pkgs.uvicorn
    python3.pkgs.jinja2
    python3.pkgs.sqlmodel

    python3.pkgs.icecream
  ];

  scripts = {
    check.exec = ''
      ruff check
    '';
    format.exec = ''
      ruff format
    '';
  };

  processes = {
    daily-quest-server = {
      exec = "uvicorn app.main:app --log-config scripts/logging.json --host $HOST --port $PORT --reload";
      process-compose = {
        working_dir = "${config.env.DEVENV_ROOT}";
        log_location = "${config.env.DEVENV_ROOT}/logs/fastapi.log";
        availability = {
          restart = "on_failure";
          max_restarts = 3;
          backoff_seconds = 2;
        };
        readiness_probe = {
          http_get = {
            host = config.env.HOST;
            port = config.env.PORT;
            path = "/health";
          };
          initial_delay_seconds = 5;
          period_seconds = 10;
          timeout_seconds = 3;
          success_threshold = 1;
          failure_threshold = 3;
        };
      };
    };
  };

  git-hooks.hooks = {
    shellcheck.enable = true;
    ruff.enable = true;
    unit-tests = {
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
  };

  # enterTest = " python -m unittest discover . ";
}
