import click
import yaml
from .inventory import Inventory
import os
import boto3


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

@cli.command()
@click.argument('bucket', required=True)
@click.option('--yes/--no', required=True)
def delete_bucket(bucket, yes):
    s3 = boto3.resource('s3')
    bucket_obj = s3.Bucket(bucket)
    bucket_obj.object_versions.delete()
    if yes:
        bucket_obj.delete()

if __name__ == "__main__":
    cli()