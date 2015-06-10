#!/bin/bash 
riak-admin bucket-type create maps '{"props":{"datatype":"map"}}'
riak-admin bucket-type create counters '{"props":{"datatype":"counter"}}'
riak-admin bucket-type create sets '{"props":{"datatype":"set"}}'
riak-admin bucket-type activate maps
riak-admin bucket-type activate counter
riak-admin bucket-type activate sets
