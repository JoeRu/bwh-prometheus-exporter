import click
from handler import falcon_app


@click.group(help='')
def cli():
    pass


@click.command()
@click.option('-s', '--service', help='service name', required=True, type=str)
@click.option('-u', '--url', help='url to collect from', required=True, type=str)
@click.option('-p', '--port', help='', required=True, type=int)
@click.option('-e', '--exclude', help='exclude metrics named', multiple=True)
@click.option('-w', '--webcam', help='webcam or picture-source to collect images from', default='https://home.jru.me/bee-cam/api.cgi?cmd=Snap&channel=0&rs=sdilj23SDO3DDGHJsdfs&user=guest&password=my_guest&1555017246', required=True, type=str)
def start(service, url, port, exclude, webcam):
    falcon_app(url, service, port=port, exclude=list(exclude), webcam=webcam)


cli.add_command(start)


if __name__ == '__main__':
    cli()
