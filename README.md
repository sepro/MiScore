[![Run Pytest](https://github.com/sepro/MiScore/actions/workflows/autopytest.yml/badge.svg)](https://github.com/sepro/MiScore/actions/workflows/autopytest.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# MiScore - The anti-social leaderboard

Are you tired of seeing your high scores appear in online leaderboards and being discouraged to see how low you rank ? 
Or maybe you simply enjoy retro games that have no high scores? MiScore is the answer, this tool allows you to set up
a leaderboard to track scores across different games just for YOU! 

## Planning 

This is very much a work in progress, here is a rough sketch of the steps planned.

  - [ ] Work out json schema and Pydantic code to load and validate data
  - [ ] Interface (textual ?) to add data
  - [ ] Front-end (Svelte?) to show result on a static webpage

## Setting up (for developers)

After cloning the repository, navigate into the MiScore directory and run the command below to create and activate
an environment.

```commandline
python -m venv venv
activate venv/bin/activate
pip install -r requirements.dev.txt
```

Now you can run the test suite using

```commandline
pytest
```

