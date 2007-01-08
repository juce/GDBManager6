# Palette Manipulation toolkit

import sys, struct, binascii

def getPaletteInfoPNG(data):
    off = data.find("PLTE")-4
    size = struct.unpack(">I",data[off:off+4])[0]
    return off,off+size+12,size/3

def getTransInfoPNG(data):
    off = data.find("tRNS")-4
    size = struct.unpack(">I",data[off:off+4])[0]
    return off,off+size+12,size

def getPaletteInfoBMP(data):
    end = struct.unpack("<I",data[10:14])[0]
    start = end - 0x400
    return (start,end)

def makePalettePNGFromBMP(bmpData):
    plte, trns = "", ""
    a,b = getPaletteInfoBMP(bmpData)
    for i in range(256):
        plte += bmpData[a+i*4+2]
        plte += bmpData[a+i*4+1]
        plte += bmpData[a+i*4]
        t = bmpData[a+i*4+3]
        # boost the "Konami transparency" byte
        n = struct.unpack(">B",t)[0]*2
        if n>255: n=255
        trns += struct.pack(">B",n)
    return plte,trns

def makePaletteBMPFromPNG(pngData):
    pal = ""
    a,b,n = getPaletteInfoPNG(pngData)
    c,d,m = getTransInfoPNG(pngData)
    for i in range(max(m,n)):
        if i<n:
            pal += pngData[a+i*3+2]
            pal += pngData[a+i*3+1]
            pal += pngData[a+i*3]
        else:
            pal += '\0\0\0'
        if i<m:
            pal += pngData[c+i]
        else:
            pal += '\xff'
    for i in range(256-max(m,n)):
        pal += '\0\0\0\xff'
    return pal

############

def samePalette(imgA, imgB):
    # read images into memory
    f = open(imgA,"rb")
    dataA = f.read()
    f.close()
    f = open(imgB,"rb")
    dataB = f.read()
    f.close()

    # convert palettes to DIB-format
    if imgA.lower().endswith(".png"):
        palA = makePaletteBMPFromPNG(dataA)
    else:
        a,b = getPaletteInfoBMP(dataA)
        palA = dataA[a:b]
    if imgB.lower().endswith(".png"):
        palB = makePaletteBMPFromPNG(dataB)
    else:
        a,b = getPaletteInfoBMP(dataB)
        palB = dataB[a:b]

    # compare palettes
    return palA == palB

def usePalette(imgFile,palFile):
    # read images into memory
    f = open(imgFile,"rb")
    img = f.read()
    f.close()
    f = open(palFile,"rb")
    pal = f.read()
    f.close()

    # replace palette
    if imgFile.lower().endswith(".png"):
        if palFile.lower().endswith(".png"):
            # png -> png
            a,b,n = getPaletteInfoPNG(img)
            pa,pb,pn = getPaletteInfoPNG(pal)
            img = img[:a]+pal[pa:pb]+img[b:]
            a,b,n = getTransInfoPNG(img)
            pa,pb,pn = getTransInfoPNG(pal)
            img = img[:a]+pal[pa:pb]+img[b:]
            return img
        elif palFile.lower().endswith(".bmp"):
            # bmp -> png
            plte,trns = makePalettePNGFromBMP(pal)
            plteCRC = binascii.crc32("PLTE" + plte)
            plte = struct.pack(">I",256*3) + "PLTE" + plte + struct.pack(">I",plteCRC)
            a,b,n = getPaletteInfoPNG(img)
            img = img[:a]+plte+img[b:]
            trnsCRC = binascii.crc32("tRNS" + trns)
            trns = struct.pack(">I",256) + "tRNS" + trns + struct.pack(">I",trnsCRC)
            a,b,n = getTransInfoPNG(img)
            img = img[:a]+trns+img[b:]
            return img
    elif imgFile.lower().endswith(".bmp"):
        if palFile.lower().endswith(".bmp"):
            # bmp -> bmp
            a,b = getPaletteInfoBMP(img)
            pa,pb = getPaletteInfoBMP(pal)
            img = img[:a]+pal[pa:pb]+img[b:]
            return img
        elif palFile.lower().endswith(".png"):
            # png -> bmp
            a,b = getPaletteInfoBMP(img)
            newpal = makePaletteBMPFromPNG(pal)
            img = img[:a]+newpal+img[b:]
            return img

    # if got here, images are incompatible
    return ""


# unit-test
###########

if __name__ == "__main__":
    data = usePalette(sys.argv[1], sys.argv[2])
    o = open(sys.argv[3], "wb")
    o.write(data)
    o.close()

