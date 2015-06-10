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

Count things in various time based windows using redis

Example
-------

.. code-block:: python

        import datetime
        import redis

        from sifr.span import Year, Month, Day, Hour, Minute, get_time_spans
        from sifr.storage import RedisStorage

        client = redis.Redis()
        storage = RedisStorage(client)

        now = datetime.datetime.now()
        user_id = 1
        page = "index.html"

        # construct the windows. These are the resolutions that will be tracked.
        spans = [
            span(now, ["views", "user", user_id])
            for span in [Year, Month, Day, Hour, Minute]
        ]
        # incr a counter for all resolutions
        storage.incr_multi(spans)

        # incr a unique counter
        storage.incr_unique_multi(spans, page)

        # track the page view
        storage.track_multi(spans, page)

        # get the counts/uniques for a single year window
        assert 1 == storage.count(Year(now, ["views", "user", 1]))
        assert 1 == storage.cardinality(Year(now, ["views", "user", 1]))
        assert set(["index.html"]) == storage.uniques(Year(now, ["views", "user", 1]))


        # get the counts/uniques for a range
        start = now - datetime.timedelta(minutes=1)
        end = now + datetime.timedelta(minutes=1)

        span_range = get_time_spans(start, end, ["views", "user", 1], [Minute])
        assert [1] == [storage.count(span) for span in span_range]
        assert [1] == [storage.cardinality(span) for span in span_range]
        assert [set(["index.html"])] == [storage.uniques(span) for span in span_range]


References
----------
* `Minuteman <http://elcuervo.github.io/minuteman/>`_

