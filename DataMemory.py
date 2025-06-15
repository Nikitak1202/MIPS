# Byte-addressable main memory + on-chip Cache 
# Read:  ① check Cache ② on miss fetch full block into Cache ③ return word
# Write: ① update main memory ② push full block (with new word) into Cache
# Address => (tag , set , offset) uses word-addressing
#   offset      : index of the word inside a Cache line     (0 … num_words-1)
#   set         : index of the set inside each way          (0 … num_cachelines-1)
#   tag         : remaining high-order bits of the word address
from Cache import Cache


class DataMemory:
    def __init__(self, size_in_bytes=0x400000, num_cachelines=4, num_ways=4, num_words=4):
        self.size_words     = size_in_bytes // 4           # total words in memory
        self.memory         = [0] * self.size_words        
        self.Cache          = Cache(num_cachelines=num_cachelines, num_ways=num_ways, num_words=num_words)                        


    def decode_addr(self, address: int):
        if address % 4 != 0 or address // 4 >= self.size_words:
            raise ValueError("unaligned or out-of-bounds access")
        
        word_addr   =  address // 4
        offset      =  word_addr % self.Cache.num_words
        set         = (word_addr // self.Cache.num_words) % self.Cache.num_cachelines
        tag         = (word_addr // self.Cache.num_words) // self.Cache.num_cachelines

        return tag, set, offset, word_addr


    def read_word(self, address: int, MemRead: bool):
        CacheRead = True
        if not MemRead:
            return 0, CacheRead

        tag, set, offset, word_addr = self.decode_addr(address)

        # Try Cache
        hit_data = self.Cache.Read(tag, set, offset)
        if hit_data is not None:
            return hit_data, CacheRead

        # Cache miss - fetch full block from memory
        CacheRead = False
        blk_base = word_addr - offset                          # first word of the block
        for i in range(self.Cache.num_words):
            self.Cache.Write(
                set, i, tag,
                self.memory[blk_base + i]
            )
        return self.memory[word_addr], CacheRead

    def write_word(self, address: int, data: int, MemWrite: bool):
        if not MemWrite:
            return

        tag, set, offset, word_addr = self.decode_addr(address)

        # Update main memory
        self.memory[word_addr] = data

        # Push whole block into Cache
        blk_base = word_addr - offset
        for i in range(self.Cache.num_words):
            word_to_store = data if i == offset else self.memory[blk_base + i]
            self.Cache.Write(set, i, tag, word_to_store)


if __name__ == "__main__":
    mem   = DataMemory(num_ways=2, num_cachelines=2, num_words=4, size_in_bytes=128)                  

    # инициализируем «слово = индекс»
    for i in range(len(mem.memory)):
        mem.memory[i] = i

    # ---------- pretty-print -------------------------------------
    def show(label):
        print(f"\n=== {label} ===")
        hdr = "Way Set | Tag   | " + " ".join([f"\tW{i}" for i in range(mem.Cache.num_words)])
        print(hdr.expandtabs(4))
        for w, way in enumerate(mem.Cache.ways):
            for s, line in enumerate(way):
                tag_str   = "-" if line.tag is None else str(line.tag)
                data_strs = [f"{v:4}" for v in line.data]
                row = f"{w:<3} {s:<3} | {tag_str:<5} | " + " ".join(data_strs)
                print(row.expandtabs(4))
        print('\n\n')

    def dump_mem():
        print("\nMain-memory (non-zero blocks, 4 words/row):")
        for blk in range(0, len(mem.memory), mem.Cache.num_words):
            if any(mem.memory[blk+i] for i in range(mem.Cache.num_words)):
                words = " ".join([f"{mem.memory[blk+i]:4}" for i in range(mem.Cache.num_words)])
                print(f"Addr {blk*4:02X}: {words}")
        print()

    # ---------- тесты --------------------------------------------
    dump_mem();                        show("initial state")

    # ① compulsory miss (block 0)
    w = mem.read_word(4, MemRead=True)
    print("read @0  =>", w)
    show("after miss – block 0 cached")

    # ② cache hit
    w = mem.read_word(4, MemRead=True)
    print("read @0  =>", w)
    show("after hit")

    # ③ конфликтный miss + вытеснение.  
    #    Адрес 32 (байт) = слово 8 лежит в блоке **№2**,
    #    тот же set 0, другой tag.
    w = mem.read_word(64, MemRead=True)
    print("read @32 =>", w)
    show("after miss & eviction (block 2)")

        # ③ конфликтный miss + вытеснение.  
    #    Адрес 32 (байт) = слово 8 лежит в блоке **№2**,
    #    тот же set 0, другой tag.
    w = mem.read_word(32, MemRead=True)
    print("read @32 =>", w)
    show("after miss & eviction (block 2)")

    # ④ запись слова 999 по адресу 4 (блок 0)
    mem.write_word(4, 999, MemWrite=True)
    show("after write 999 @4")
    dump_mem()

    # ⑤ hit возвращает модифицированное значение
    w = mem.read_word(4, MemRead=True)
    print("read @4  =>", w)
    show("after hit on modified block")