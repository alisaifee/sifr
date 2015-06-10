import anyconfig
import click
from gevent.server import StreamServer
import redis
from sifr.daemon.msgpack import SifrServer
from sifr.storage import RedisStorage


class SifrD(object):
    def __init__(self, debug=False):
        self.debug = debug

class AnyConfigType(click.File):
    name = 'config'

    def convert(self, value, param, ctx):
        fp = super(AnyConfigType, self).convert(value, param, ctx)
        try:
            config = anyconfig.load(fp.name)
            if not config:
                raise ValueError
            return config
        except ValueError:
            self.fail(
                'Could not load configuration from file: %s.'
                'It must be one of yaml/ini/json' % (fp.name)
            )

@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    ctx.obj = SifrD(debug)

@cli.command()
@click.option("--config", type=AnyConfigType(), required=True)
@click.pass_obj
def msgpack_server(sifrd, config):
    if not config.get("REDIS_URL"):
        raise SystemExit("REDIS_URL is a required configuration")
    redis_instance = redis.from_url(config.get("REDIS_URL"))
    storage = RedisStorage(redis_instance)

    server = StreamServer((config.get("HOST", "127.0.0.1"), int(config.get("PORT", 6000))), SifrServer(storage))
    server.serve_forever()

def run():
    return cli(auto_envvar_prefix='SIFR')
