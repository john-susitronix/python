
import mmap
import struct

DMA_OFFSET = 0x40400000 #this is likely different
DMA_MSIZE = 0x10000

NUM_DMA_UINTS = 1024 #number of uints to dma to new location

MEM_OFFSET = 0x38000000 #this is likely different
MEM_MSIZE = 0x08000000  #this is likely different

devmem = open('/dev/mem', 'r+b')
mem_map = mmap.mmap(devmem.fileno(), MEM_MSIZE, offset=MEM_OFFSET)
dma_map = mmap.mmap(devmem.fileno(), DMA_MSIZE, offset=DMA_OFFSET)

#set destination to zeros
tempvals = [0]*NUM_DMA_UINTS
offset = 4*NUM_DMA_UINTS
mem_map[offset:offset+4*NUM_DMA_UINTS] = struct.pack(('<%dI' % NUM_DMA_UINTS), *tempvals)
print("first 4 dest vals:")
print(struct.unpack('<4I', mem_map[offset:offset+16]))

#set source
tempvals = range(0, NUM_DMA_UINTS)
mem_map[0:4*NUM_DMA_UINTS] = struct.pack(('<%dI' % NUM_DMA_UINTS), *tempvals)
print("first 4 source vals:")
print(struct.unpack('<4I', mem_map[0:16]))

#reset dma channels
offset = 0x00
dma_map[offset:offset+4] = struct.pack('<I', 1 << 2)
while struct.unpack('<I', dma_map[offset:offset+4])[0] & (1 << 2):
    pass
offset = 0x30
dma_map[offset:offset+4] = struct.pack('<I', 1 << 2)
while struct.unpack('<I', dma_map[offset:offset+4])[0] & (1 << 2):
    pass

#set dest s2mm
dma_map[0x48:0x4C] = struct.pack('<I', 4*NUM_DMA_UINTS)
dma_map[0x30:0x34] = struct.pack('<I', 1 << 0)
dma_map[0x58:0x5C] = struct.pack('<I', 4*NUM_DMA_UINTS)

#set src mm2s
dma_map[0x18:0x1C] = struct.pack('<I', 0)
dma_map[0x00:0x04] = struct.pack('<I', 1 << 0)
dma_map[0x28:0x2C] = struct.pack('<I', 4*NUM_DMA_UINTS)

#wait for mm2s completion

while not struct.unpack('<I', dma_map[0x04:0x08])[0] & (1 << 0):
    pass

print("first 4 dest vals after completion:")
print(struct.unpack('<4I', mem_map[0:16]))

dma_map.close()
mem_map.close()
devmem.close()
