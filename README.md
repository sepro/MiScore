[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Pydantic Test

Test repository to check how file validation works with Pydantic and options to include tests on those models.


## Setting up (for developers)

After cloning the repository, navigate into Pydantic Test's directory and
run the command below to create and activate an environment.

```commandline
python -m venv venv
activate venv/bin/activate
pip install -r requirements.dev.txt
```

Now you can run the test suite using

```commandline
pytest
```

