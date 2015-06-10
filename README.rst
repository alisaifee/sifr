.. |travis-ci| image:: https://img.shields.io/travis/alisaifee/sifr/master.svg?style=flat-square
    :target: https://travis-ci.org/#!/alisaifee/sifr?branch=master
.. |coveralls| image:: https://img.shields.io/coveralls/alisaifee/sifr/master.svg?style=flat-square
    :target: https://coveralls.io/r/alisaifee/sifr?branch=master
.. |pypi| image:: https://img.shields.io/pypi/v/sifr.svg?style=flat-square
    :target: https://pypi.python.org/pypi/sifr
.. |license| image:: https://img.shields.io/pypi/l/sifr.svg?style=flat-square
    :target: https://pypi.python.org/pypi/sifr
.. |landscape| image:: https://landscape.io/github/alisaifee/sifr/master/landscape.svg?style=flat-square
    :target: https://landscape.io/github/alisaifee/sifr/master

****
sifr
****


   ... and with the sign 0 ... any number may be written

   -- Fibionacci


|travis-ci| |coveralls| |landscape| |pypi| |license|

.. image:: http://i.imgur.com/luJUJ31.png

Count things in various time based windows using in-memory, redis or riak
storage.

Installation
============
Install the basic package::

    pip install sifr

Install **sifr** with redis dependencies::

    pip install 'sifr[redis]'

Install **sifr** with riak dependencies::

    pip install 'sifr[riak]'


Install **sifr** with sifrd service dependencies::

    pip install 'sifr[daemon]'

Examples
========

Using **sifr** with direct storage
----------------------------------
.. code-block:: python

        import datetime
        import redis, riak

        from sifr.span import Year, Month, Day, Hour, Minute, get_time_spans
        from sifr.storage import MemoryStorage, RedisStorage, RiakStorage

        redis_client = redis.Redis()
        redis_store = RedisStorage(redis_client)

        riak_client = riak.RiakClient()
        riak_store = RiakStorage(riak_client)

        memory_store = MemoryStorage()

        stores = [memory_store, redis_store, riak_store]

        now = datetime.datetime.now()
        user_id = 1
        page = "index.html"

        # construct the windows. These are the resolutions that will be tracked.
        spans = [
            span(now, ["views", "user", user_id])
            for span in [Year, Month, Day, Hour, Minute]
        ]
        # incr a counter for all resolutions
        [store.incr_multi(spans) for store in stores]

        # incr a unique counter
        [store.incr_unique_multi(spans, page) for store in stores]
        [store.incr_unique_multi(spans, page) for store in stores]

        # track the page view
        [store.track_multi(spans, page) for store in stores]
        [store.track_multi(spans, page) for store in stores]

        # get the counts/uniques for a single year window
        for store in stores:
          assert 1 == store.count(Year(now, ["views", "user", 1]))
          assert 1 == store.cardinality(Year(now, ["views", "user", 1]))
          assert set(["index.html"]) == store.uniques(Year(now, ["views", "user", 1]))


        # get the counts/uniques for a range
        start = now - datetime.timedelta(minutes=1)
        end = now + datetime.timedelta(minutes=1)

        span_range = get_time_spans(start, end, ["views", "user", 1], [Minute])
        for store in stores:
          assert [1] == [store.count(span) for span in span_range]
          assert [1] == [store.cardinality(span) for span in span_range]
          assert [set(["index.html"])] == [store.uniques(span) for span in span_range]


Using **sifr** via rpc
----------------------

sifr.yml (using a redis backend)

.. code-block:: yaml

    storage: redis
    redis_url: redis://localhost:6379/1
    host: localhost
    port: 6000

sifr.yml (using a riak backend)

.. code-block:: yaml

    storage: riak
    riak_nodes:
        - host: localhost
          pb_port: 8087
    host: localhost
    port: 6000

Run the server

.. code-block:: bash

    sifrd msgpack_server --config=sifr.yml


Interact with the server

.. code-block:: python

    from sifr import RPCClient
    client = RPCCient(host='localhost', port=6000, resolutions=["year", "month", "day"])
    client.incr("views:user:1")
    client.incr_unique("views:user:1", "index.html")
    client.incr_unique("views:user:1", "index.html")
    client.track("views:user:1", "index.html")
    client.track("views:user:1", "index.html")

    assert 1 == client.count("views:user:1", datetime.datetime.now(), "day")
    assert 1 == client.cardinality("views:user:1", datetime.datetime.now(), "day")
    assert set(["index.html"]) == client.uniques("views:user:1", datetime.datetime.now(), "day")

References
==========
* `Minuteman <http://elcuervo.github.io/minuteman/>`_
* `Zero <http://en.wikipedia.org/wiki/0_%28number%29>`_
