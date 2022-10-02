import click
from .record_data import RecordData


@click.command()
@click.argument('filename')
@click.option('--raise_error', is_flag=True)
def validate(filename, raise_error):
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


validate()
