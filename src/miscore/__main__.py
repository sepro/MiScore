import click
from .record_data import RecordData
import os


@click.group()
def cli():
    """MiScore - Personal gaming leaderboard system"""
    pass


@cli.command()
@click.argument("filename")
@click.option("--raise_error", is_flag=True)
def validate(filename, raise_error):
    """Validate a records JSON file"""
    try:
        _ = RecordData.load(filename)
    except Exception as e:
        if raise_error:
            raise e
        else:
            print(f"{filename} is not valid. The following error occurred:")
            print(e)
    else:
        print(f"{filename} is valid")


@cli.command()
@click.argument("game_name")
@click.argument("filename")
@click.option(
    "--no-interactive", is_flag=True, help="Skip interactive difficulty setup"
)
def add_game(game_name, filename, no_interactive):
    """Add a new game to a records file"""
    try:
        interactive = not no_interactive
        if RecordData.add_game_to_file(game_name, filename, interactive=interactive):
            print(f"Game '{game_name}' added to {filename}")
        else:
            print(f"Game '{game_name}' already exists in {filename}")
    except Exception as e:
        print(f"Error adding game: {e}")


if __name__ == "__main__":
    cli()
