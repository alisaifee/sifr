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

*************
sifr
*************
|travis-ci| |coveralls| |landscape| |pypi| |license|

.. image:: http://i.imgur.com/luJUJ31.png

Count things in various time based windows using in-memory, redis or riak
storage.

Example
-------

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


References
----------
* `Minuteman <http://elcuervo.github.io/minuteman/>`_

