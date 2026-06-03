#!/usr/bin/env python3
"""Generate 16x16 Chinese bitmap font data for NXShare."""

from PIL import Image, ImageFont, ImageDraw
import os

# All unique Chinese characters needed
CHARS = (
    # ui.cpp (NX快传 brand)
    "在浏览器中打开以下网址或扫描二维码已找到媒体文件按退出作者忘忧汉化快传"
    # main.cpp
    "启动中等待网络连接错误无请确保"
    # gallery.cpp
    "杂项未知主屏幕记录编辑器自制程序用户设置"
    # index.html
    "全部截图视频游戏选下关加载更剩余未连接刷新照片"
)

# Remove duplicates and sort
unique = sorted(set(CHARS))
print(f"Total unique characters: {len(unique)}")
print("Characters:", "".join(unique))

# Font path - try several Chinese fonts
font_paths = [
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
]

font = None
for fp in font_paths:
    if os.path.exists(fp):
        try:
            font = ImageFont.truetype(fp, 16)
            print(f"Using font: {fp}")
            break
        except Exception as e:
            print(f"Failed to load {fp}: {e}")

if font is None:
    print("ERROR: No Chinese font found!")
    exit(1)

# Test rendering
test_char = unique[0]
print(f"Testing with: '{test_char}' (U+{ord(test_char):04X})")

glyphs = {}

for ch in unique:
    # Create image and render character
    img = Image.new("L", (16, 16), 0)  # black background
    draw = ImageDraw.Draw(img)

    # Get bounding box and center the character
    bbox = font.getbbox(ch)
    if bbox:
        char_w = bbox[2] - bbox[0]
        char_h = bbox[3] - bbox[1]
        x_offset = (16 - char_w) // 2 - bbox[0]
        y_offset = (16 - char_h) // 2 - bbox[1]
        draw.text((x_offset, y_offset), ch, font=font, fill=255)
    else:
        # Fallback: just draw at origin
        draw.text((0, 0), ch, font=font, fill=255)

    # Convert to 32 bytes (16 rows × 2 bytes per row = 16 bits)
    glyph_bytes = bytearray(32)
    for row in range(16):
        byte_hi = 0  # bits 15-8 (left half of 16px)
        byte_lo = 0  # bits 7-0  (right half of 16px)
        for col in range(16):
            pixel = img.getpixel((col, row))
            # Threshold: > 128 = white (set bit), else black (clear bit)
            if pixel > 128:
                if col < 8:
                    byte_hi |= (1 << (7 - col))  # MSB = leftmost pixel
                else:
                    byte_lo |= (1 << (15 - col))  # MSB = leftmost pixel
        glyph_bytes[row * 2] = byte_hi
        glyph_bytes[row * 2 + 1] = byte_lo

    glyphs[ord(ch)] = bytes(glyph_bytes)

# Generate C++ header
header = """// Auto-generated 16x16 Chinese bitmap font for NXShare
// Characters: {chars}

#ifndef FONT16X16_ZH_HPP
#define FONT16X16_ZH_HPP

#include <cstdint>
#include <unordered_map>

""".format(chars="".join(unique))

# Generate array data - one array per glyph for clarity
data_entries = []
for codepoint in sorted(glyphs.keys()):
    ch = chr(codepoint)
    data = glyphs[codepoint]
    # Generate hex bytes
    hex_str = ",".join("0x{:02X}".format(b) for b in data)
    data_entries.append((codepoint, ch, hex_str))

# Write the font data map
header += "// 16x16 glyph data, 32 bytes per character (16 rows × 2 bytes)\n"
header += "// Each glyph: byte pair per row, MSB = leftmost pixel\n\n"

# Store glyph data in a single array
header += "static const uint8_t FONT16X16_DATA[][32] = {\n"
for codepoint, ch, hex_str in data_entries:
    header += f"    // U+{codepoint:04X} '{ch}'\n"
    header += f"    {{{hex_str}}},\n"
header += "};\n\n"

# Build the lookup map
header += "// Unicode codepoint -> index into FONT16X16_DATA\n"
header += "static const std::unordered_map<uint32_t, int> FONT16X16_MAP = {\n"
for i, (codepoint, ch, _) in enumerate(data_entries):
    header += f"    {{0x{codepoint:04X}, {i}}},  // '{ch}'\n"
header += "};\n\n"

header += "#endif // FONT16X16_ZH_HPP\n"

# Write output
output_path = "include/font16x16_zh.hpp"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(header)

print(f"Font data written to {output_path}")
print(f"Font data size: {len(unique) * 32} bytes for {len(unique)} characters")

# Also generate a preview image for verification
preview = Image.new("L", (16 * len(unique) + len(unique) - 1, 16), 0)
for i, (codepoint, ch, _) in enumerate(data_entries):
    data = glyphs[codepoint]
    for row in range(16):
        byte_hi = data[row * 2]
        byte_lo = data[row * 2 + 1]
        for col in range(16):
            bit = (byte_hi & (1 << (7 - col))) if col < 8 else (byte_lo & (1 << (15 - col)))
            if bit:
                preview.putpixel((i * 17 + col, row), 255)
preview.save("font_preview.png")
print("Preview image saved to font_preview.png")
