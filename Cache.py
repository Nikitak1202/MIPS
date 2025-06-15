# This module simulates a cache for storing 32-bit words.
# The cache has a configurable number of ways; each way contains a configurable number of cachelines,
# and each cacheline holds a configurable number of words.
# Every cacheline has its own read requests counter (reads_counter).
class CacheLine:
    def __init__(self, num_words=4):
        self.tag = None
        self.data = [0] * num_words
        self.reads_counter = 0


class Cache:
    def __init__(self, num_ways=4, num_cachelines=4, num_words=4):
        self.num_ways = num_ways
        self.num_cachelines = num_cachelines
        self.num_words = num_words
        
        # Create ways. Each way is a list of cachelines.
        self.ways = []
        for _ in range(num_ways):
            way = []
            for _ in range(num_cachelines):
                way.append(CacheLine(num_words))
            self.ways.append(way)
    

    def CheckTag(self, tag):
        # Check if any cacheline in any way contains the given tag.
        for way in self.ways:
            for cacheline in way:
                if cacheline.tag == tag:
                    return True
        return False


    def Write(self, set, offset, tag, data_word):
        # Write data into the cache at a specified set (index within each way)
        # and a specified offset (index within the cacheline).
        # The function writes into the first free cacheline it finds.
        if not (0 <= set < self.num_cachelines) or not (0 <= offset < self.num_words):
            raise ValueError("set must be in range 0-{0} and offset in range 0-{1}.".format(self.num_cachelines - 1, self.num_words - 1))
        
        min_counter = float('inf')
        eviction_candidate = None
        
        # Go through all ways,searching for free cacheline with given set and choosing eviction candidate in parallel.
        for way in self.ways:
            cacheline = way[set]
            # If cacheline is free or matches the tag, write data and return.
            if cacheline.tag is None or cacheline.tag == tag:
                cacheline.tag = tag
                cacheline.data[offset] = data_word
                cacheline.reads_counter = 0
                return
            # If cacheline is busy, check if it has the minimum reads_counter.
            if cacheline.reads_counter < min_counter:
                min_counter = cacheline.reads_counter
                eviction_candidate = cacheline
        
        # If all cachelines with current set are busy - evict chosen candidate.
        eviction_candidate.tag = tag
        eviction_candidate.data[offset] = data_word
        eviction_candidate.reads_counter = 0


    def Read(self, tag, set, offset):
        # Read a word from the cache by specifying the tag, set index, and offset.
        # If the cacheline with the matching tag is found in the specified set,
        # increment its reads_counter and return the data at the given offset.
        if not (0 <= set < self.num_cachelines) or not (0 <= offset < self.num_words):
            raise ValueError("set must be in range 0-{0} and offset in range 0-{1}.".format(self.num_cachelines - 1, self.num_words - 1))
        
        for way in self.ways:
            cacheline = way[set]
            if cacheline.tag == tag:
                cacheline.reads_counter += 1
                return cacheline.data[offset]
        
        # If the cacheline with the given tag is not found, return None.
        return None