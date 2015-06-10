import anyconfig
import click
import msgpackrpc
from sifr.daemon.msgpack import SifrServer
from sifr.storage import RedisStorage, RiakStorage, MemoryStorage


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
@click.pass_context
def cli(ctx):
    ctx.obj = SifrD()


@cli.command()
@click.option("--config", type=AnyConfigType(), required=True)
@click.pass_obj
def msgpack_server(sifrd, config):
    storage_type = config.get("storage")
    if storage_type == "riak":
        import riak
        riak_nodes = config.get("riak_nodes")
        riak_instance = riak.RiakClient(nodes=riak_nodes)
        storage = RiakStorage(riak_instance)
    elif storage_type == "redis":
        import redis
        redis_instance = redis.from_url(config.get("redis_url"))
        storage = RedisStorage(redis_instance)
    else:
        storage = MemoryStorage()
    server = msgpackrpc.Server(
        SifrServer(storage),
        unpack_encoding='utf-8'
    )
    server.listen(
        msgpackrpc.Address(
            config.get("host", "127.0.0.1"), int(config.get("port", 6000))
        )
    )
    server.start()


def run():
    return cli(auto_envvar_prefix='SIFR')
