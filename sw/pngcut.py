"""PNG cut into tiles, so each piece of a picture can be a link of its own (minihtml has no image
maps). Only what Graphviz writes: 8 bits a channel, not interlaced. Standard library only. Pure."""

import struct
import zlib

CHANNELS = {0: 1, 2: 3, 4: 2, 6: 4}  # colour type: channels


def read(path):
    """(width, height, colour type, rows of unfiltered bytes)."""
    with open(path, "rb") as f:
        data = f.read()
    pos, idat, head = 8, b"", None
    while pos < len(data):
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + length]
        if kind == b"IHDR":
            head = struct.unpack(">IIBBBBB", body)
        elif kind == b"IDAT":
            idat += body
        pos += 12 + length
    width, height, depth, colour, _, _, interlace = head
    if depth != 8 or interlace or colour not in CHANNELS:
        raise ValueError("only 8-bit, non-interlaced PNG")
    bpp = CHANNELS[colour]
    return width, height, colour, unfilter(zlib.decompress(idat), width * bpp, height, bpp)


def unfilter(raw, stride, height, bpp):
    rows, prior = [], bytearray(stride)
    for y in range(height):
        kind, line = raw[y * (stride + 1)], bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            left = line[i - bpp] if i >= bpp else 0
            up, corner = prior[i], prior[i - bpp] if i >= bpp else 0
            line[i] = (line[i] + predict(kind, left, up, corner)) & 0xFF
        rows.append(bytes(line))
        prior = line
    return rows


def predict(kind, left, up, corner):
    if kind == 0:
        return 0
    if kind == 1:
        return left
    if kind == 2:
        return up
    if kind == 3:
        return (left + up) // 2
    p = left + up - corner
    pa, pb, pc = abs(p - left), abs(p - up), abs(p - corner)
    return left if pa <= pb and pa <= pc else up if pb <= pc else corner


def write(path, width, height, colour, rows):
    """rows unfiltered; written with filter 0 on every line."""
    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(
            ">I", zlib.crc32(kind + body) & 0xFFFFFFFF)
    raw = b"".join(b"\x00" + row for row in rows)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(
            ">IIBBBBB", width, height, 8, colour, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 6))
            + chunk(b"IEND", b""))


def crop(rows, colour, x0, y0, x1, y1):
    bpp = CHANNELS[colour]
    return [row[x0 * bpp:x1 * bpp] for row in rows[y0:y1]]
