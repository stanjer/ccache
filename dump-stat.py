#!/usr/bin/env python

import memcache
import struct
import sys
import os
import binascii
import time

"""
/*
struct file_stats {
        uint32_t size;
        int64_t mtime;
        int64_t ctime;
};

struct file_hash
{
        uint8_t hash[16];
        uint32_t size;
};

struct cache {
        struct file_stats stat;
        struct file_hash hash;
};
*/
"""

sock = sys.argv[1]
path = sys.argv[2]
mc = memcache.Client(["unix:%s" % sock], debug=1)
val = mc.get(path)
if val:
    assert(len(val) == 48) # with padding
    (size, mtime, ctime) = struct.unpack('@Iqq', val[0:24])
    date = time.asctime(time.localtime(mtime))
    md4 = val[24:40]
    len = struct.unpack('@I', val[40:44])[0]
    hash = "%s-%d" % (binascii.hexlify(md4), len)
    print path, size, date, hash
else:
    print "path missing"
