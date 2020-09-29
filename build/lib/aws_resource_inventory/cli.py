import click
import yaml
from .inventory import Inventory
import os


@click.group()
@click.option("--debug/--no-debug", default=False)
def cli(debug):
    click.echo("Debug mode is %s" % ("on" if debug else "off"))


@click.option("--config", type=click.File("rb"))
@click.argument("output-file", required=True)
@cli.command()  # @cli, not @click!
def get_inventory(config, output_file):
    if config:
        config_data = yaml.load(config, Loader=yaml.Loader)
    else:
        config_data = None

    output_file = os.path.realpath("%s" % (output_file))
    inv = Inventory(config=config_data, output_file=output_file, output=click)
    inv.get_inventory()


if __name__ == "__main__":
    cli()
