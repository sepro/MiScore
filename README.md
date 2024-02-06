[![Run Pytest](https://github.com/sepro/MiScore/actions/workflows/autopytest.yml/badge.svg)](https://github.com/sepro/MiScore/actions/workflows/autopytest.yml)
[![codecov](https://codecov.io/gh/sepro/MiScore/branch/main/graph/badge.svg?token=KAic2QxDLZ)](https://codecov.io/gh/sepro/MiScore)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# MiScore - The anti-social leaderboard

Are you tired of seeing your high scores appear in online leaderboards and being discouraged to see how low you rank ? 
Or maybe you simply enjoy retro games that have no high scores? MiScore is the answer, this tool allows you to set up
a leaderboard to track scores across different games just for YOU! 

## Planning 

This is very much a work in progress, here is a rough sketch of the steps planned.

  - [X] Work out json schema and Pydantic code to load and validate data
  - [ ] Interface (textual ?) to add data
  - [ ] Front-end (Svelte?) to show result on a static webpage
  - [ ] 
## Validating a records file

Once installed you can validate a json file containing records data using the command below

```commandline
 python -m miscore .\data\records.json
```

## Setting up (for developers)

After cloning the repository, navigate into the MiScore directory and run the command below to create and activate
an environment.

```commandline
python -m venv venv
activate venv/bin/activate
pip install -r requirements.txt
```

Now you can run the test suite using

```commandline
pytest
```

