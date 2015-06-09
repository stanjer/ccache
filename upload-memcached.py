#!/usr/bin/env python

import memcache
import struct
import sys
import os
import hashlib

"""
/* blob format for storing:

    char magic[4]; # 'CCH1', might change for other version of ccache
                   # ccache will erase the blob in memcached if wrong magic
    uint32_t obj_len; # network endian
    char *obj[obj_len];
    uint32_t stderr_len; # network endian
    char *stderr[stderr_len];
    uint32_t dia_len; # network endian
    char *dia[dia_len];
    uint32_t dep_len; # network endian
    char *dep[dep_len];

*/
"""
CCACHE_MAGIC = 'CCH1'
def set_blob(data):
    return struct.pack('!I', len(data)) + str(data)

MAX_VALUE_SIZE = 1000 << 10 # 1M with memcached overhead
SPLIT_VALUE_SIZE = MAX_VALUE_SIZE

server = os.getenv("MEMCACHED_SERVERS", "localhost")
mc = memcache.Client([server], debug=1)

ccache = os.getenv("CCACHE_DIR", os.path.expanduser("~/.ccache"))
files = blobs = chunks = objects = manifest = 0
for dirpath, dirnames, filenames in os.walk(ccache):
    dirname = dirpath.replace(ccache + os.path.sep, "")
    for filename in filenames:
        (base, ext) = os.path.splitext(filename)
        if ext == '.o':
            objects = objects + 1
	    key = "".join(list(os.path.split(dirname)) + [base])
            def read_file(path):
                return os.path.exists(path) and open(path).read() or ""
            obj = read_file(os.path.join(dirpath, filename))
            stderr = read_file(os.path.join(dirpath, base) + '.stderr')
            dep = read_file(os.path.join(dirpath, base) + '.d')

            print "%s: %d %d %d" % (key, len(obj), len(stderr), len(dep))
            val = CCACHE_MAGIC
            val += set_blob(obj)
            val += set_blob(stderr)
            val += set_blob("") # dia
            val += set_blob(dep)
            if len(val) > MAX_VALUE_SIZE:
                numkeys = (len(val) + SPLIT_VALUE_SIZE - 1) / SPLIT_VALUE_SIZE
                buf = "keys"
                buf += struct.pack('!I', numkeys)
                buf += struct.pack('!I', 20)
                buf += "size"
                buf += struct.pack('!I', len(val))
                def splitchunks(s, n):
                    """Produce `n`-character chunks from `s`."""
                    for start in range(0, len(s), n):
                        yield s[start:start+n]
                valmap = {}
                for subval in splitchunks(val, SPLIT_VALUE_SIZE):
                    subhash = hashlib.new('md4')
                    subhash.update(subval)
                    buf += subhash.digest() + struct.pack('!I', len(subval))
                    subkey = "%s-%d" % (subhash.hexdigest(), len(subval))
                    print "# %s: %d" % (subkey, len(subval))
                    #mc.set(subkey, subval)
                    valmap[subkey] = subval
                    chunks = chunks + 1
                mc.set_multi(valmap)
                mc.set(key, buf)
            else:
                mc.set(key, val)
            files = files + 1
            blobs = blobs + 1
        elif ext == '.stderr' or ext == '.d':
            files = files + 1
        elif ext == '.manifest':
            files = files + 1
            manifest = manifest + 1
print "%d files, %d objects (%d manifest) = %d blobs (%d chunks)" % (files, objects, manifest, blobs, chunks)