# Design Patterns Sandbox

This repository contains small examples of common object-oriented design
patterns. The `game_of_life` package is a runnable Conway's Game of Life
application with a Pygame interface.

## Run Game of Life

Use Python 3.11 or newer. From the repository root, create and activate a
virtual environment, then install the application dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Start the application from the repository root:

```bash
python -m game_of_life.main
```

Run it as a module from the repository root rather than as
`python game_of_life/main.py`. The application uses package-relative imports,
which require Python to know that `main` belongs to the `game_of_life` package.

The default configuration is
[`game_of_life/config/ui_config.json`](game_of_life/config/ui_config.json).
You can select another configuration file with `--config`:

```bash
python -m game_of_life.main --config game_of_life/config/ui_config.toml
```

Configuration files can use JSON, TOML, YAML (`.yaml` or `.yml`), or XML
formats. The repository includes examples in
[`game_of_life/config/`](game_of_life/config). Configuration values control
the board dimensions, initial cell density and random seed, update rate,
ruleset, window and grid sizes, and UI controls.

Use the **Start** and **Stop** buttons to control the simulation, drag the
speed slider to change its update rate, and close the window to exit.

## Run tests

Install the development dependencies and run the test suite from the repository
root:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```
