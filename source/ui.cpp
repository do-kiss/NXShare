#include "ui.hpp"
#include "qrcode.hpp"
#include "font8x8.hpp"
#include "font16x16_zh.hpp"
#include "icon_data.hpp"
#include "locale.hpp"
#include <string.h>
#include <stdio.h>
#include <string>

// Switch framebuffer with framebufferMakeLinear stores pixels right-to-left
// Fix by flipping x in setPixel
#define FLIP_X(x) (FB_WIDTH - 1 - (x))

UI::UI() {
    consoleExit(NULL);
    framebufferCreate(&m_fb, nwindowGetDefault(), FB_WIDTH, FB_HEIGHT,
                      PIXEL_FORMAT_RGBA_8888, 2);
    framebufferMakeLinear(&m_fb);
}

UI::~UI() {
    framebufferClose(&m_fb);
}

void UI::clear(u32 color) {
    int n = FB_WIDTH * FB_HEIGHT;
    for (int i = 0; i < n; i++) m_buf[i] = color;
}

void UI::drawRect(int x, int y, int w, int h, u32 color) {
    for (int dy = 0; dy < h; dy++)
        for (int dx = 0; dx < w; dx++)
            setPixel(x + dx, y + dy, color);
}

// Decode a single UTF-8 codepoint from string at offset, advance i accordingly
// Returns the Unicode codepoint, or 0 on failure
static uint32_t decodeUTF8(const std::string& text, size_t& i) {
    unsigned char c = static_cast<unsigned char>(text[i]);

    // ASCII (1 byte)
    if (c < 0x80) {
        i++;
        return c;
    }

    // 2-byte sequence (U+0080 to U+07FF)
    if ((c & 0xE0) == 0xC0 && i + 1 < text.size()) {
        unsigned char b1 = static_cast<unsigned char>(text[i + 1]);
        if ((b1 & 0xC0) == 0x80) {
            uint32_t cp = ((c & 0x1F) << 6) | (b1 & 0x3F);
            i += 2;
            return cp;
        }
    }

    // 3-byte sequence (U+0800 to U+FFFF) — CJK range
    if ((c & 0xF0) == 0xE0 && i + 2 < text.size()) {
        unsigned char b1 = static_cast<unsigned char>(text[i + 1]);
        unsigned char b2 = static_cast<unsigned char>(text[i + 2]);
        if ((b1 & 0xC0) == 0x80 && (b2 & 0xC0) == 0x80) {
            uint32_t cp = ((c & 0x0F) << 12) | ((b1 & 0x3F) << 6) | (b2 & 0x3F);
            i += 3;
            return cp;
        }
    }

    // Unknown sequence: skip byte
    i++;
    return 0;
}

// Draw text — supports ASCII (8x8 font) and Chinese (16x16 font) mixed in the same string
// Chinese 16x16 glyphs are rendered so their visual height matches ASCII at the given scale
// (i.e. Chinese at scale=2 ≈ ASCII at scale=2, both ~16px tall on screen)
void UI::drawText(const std::string& text, int x, int y, u32 color, int scale) {
    int cx = x;
    for (size_t i = 0; i < text.size(); ) {
        size_t prev = i;
        uint32_t cp = decodeUTF8(text, i);
        int byteLen = (int)(i - prev);

        if (byteLen == 1 && cp >= 32 && cp <= 126) {
            // ── ASCII character: render from FONT8x8 ──────────────────
            const uint8_t* glyph = FONT8x8[(int)(cp - 32)];
            for (int row = 0; row < 8; row++) {
                for (int col = 0; col < 8; col++) {
                    if (glyph[row] & (1 << col)) {
                        for (int sy = 0; sy < scale; sy++)
                            for (int sx = 0; sx < scale; sx++)
                                setPixel(cx + col*scale + sx, y + row*scale + sy, color);
                    }
                }
            }
            cx += 8 * scale + scale;  // e.g. 9 at scale=1, 18 at scale=2
        } else if (byteLen == 3 && cp >= 0x2000) {
            // ── CJK / Chinese character: render from FONT16X16 ────────
            auto it = FONT16X16_MAP.find(cp);
            if (it != FONT16X16_MAP.end()) {
                const uint8_t* glyph = FONT16X16_DATA[it->second];
                // CJK font is already 16x16 — render each pixel at (scale/2) so
                // visual height ≈ ASCII at the same scale
                int cjkScale = (scale > 1) ? scale / 2 : 1;
                if (cjkScale < 1) cjkScale = 1;
                for (int row = 0; row < 16; row++) {
                    for (int col = 0; col < 16; col++) {
                        int byteIdx = row * 2 + (col / 8);
                        int bitIdx = 7 - (col % 8);
                        if (glyph[byteIdx] & (1 << bitIdx)) {
                            for (int sy = 0; sy < cjkScale; sy++)
                                for (int sx = 0; sx < cjkScale; sx++)
                                    setPixel(cx + col*cjkScale + sx, y + row*cjkScale + sy, color);
                        }
                    }
                }
                cx += 16 * cjkScale + scale;  // spacing matches ASCII
            } else {
                // CJK char not in our font: skip with width
                cx += 16 * ((scale > 1) ? scale / 2 : 1) + scale;
            }
        } else {
            // Unsupported / non-printable: skip
            cx += 8 * scale + scale;
        }
    }
}

// Text width in pixels — accounts for mixed ASCII / CJK
int UI::textWidth(const std::string& text, int scale) {
    int w = 0;
    for (size_t i = 0; i < text.size(); ) {
        size_t prev = i;
        uint32_t cp = decodeUTF8(text, i);
        int byteLen = (int)(i - prev);

        if (byteLen == 1 && cp >= 32 && cp <= 126) {
            w += 8 * scale + scale;
        } else if (byteLen >= 2) {
            int cjkScale = (scale > 1) ? scale / 2 : 1;
            if (cjkScale < 1) cjkScale = 1;
            w += 16 * cjkScale + scale;
        } else {
            w += 8 * scale + scale;
        }
    }
    return w;
}

void UI::drawTextCentered(const std::string& text, int y, u32 color, int scale) {
    int w = textWidth(text, scale);
    drawText(text, (FB_WIDTH - w) / 2, y, color, scale);
}

void UI::drawTextRight(const std::string& text, int rx, int y, u32 color, int scale) {
    int w = textWidth(text, scale);
    drawText(text, rx - w, y, color, scale);
}

void UI::drawIcon(int x, int y) {
    for (int iy = 0; iy < ICON_H; iy++)
        for (int ix = 0; ix < ICON_W; ix++)
            setPixel(x + ix, y + iy, ICON_DATA[iy * ICON_W + ix]);
}

void UI::drawQR(const std::string& url, int originX, int originY, int moduleSize) {
    QR::Mat m;
    if (!QR::build(url, m)) return;

    int border = 3;
    int totalPx = (m.N + border*2) * moduleSize;
    int ox = (originX < 0) ? (FB_WIDTH - totalPx) / 2 : originX;

    drawRect(ox, originY, totalPx, totalPx, COL_WHITE);
    for (int y = 0; y < m.N; y++)
        for (int x = 0; x < m.N; x++)
            drawRect(ox + (x+border)*moduleSize, originY + (y+border)*moduleSize,
                     moduleSize, moduleSize, m.get(x,y) ? COL_BLACK : COL_WHITE);
}

void UI::present() {
    framebufferEnd(&m_fb);
}

void UI::drawInfo(const std::string& ip, int port, int mediaCount) {
    m_buf = (u32*)framebufferBegin(&m_fb, &m_stride);
    clear(COL_BG);

    std::string url = "http://" + ip + ":" + std::to_string(port);
    char countStr[32];
    snprintf(countStr, sizeof(countStr), "%d", mediaCount);

    // ── Header bar ────────────────────────────────────────────────────────
    int hdrH = 80;
    drawRect(0, 0, FB_WIDTH, hdrH, COL_SURFACE);
    drawRect(0, hdrH-1, FB_WIDTH, 1, COL_BORDER);

    // App icon — centered in header
    drawIcon((FB_WIDTH - ICON_W) / 2, (hdrH - ICON_H) / 2);

    // ── Centered single-column layout ────────────────────────────────────
    int qrSize = 9; // 27 modules * 9px = 243px QR
    int qrTotalPx = (21 + 6) * qrSize; // 243px

    int contentY = hdrH + 30;

    // "Open the URL in your browser"
    drawTextCentered(tr("Open the URL in your browser",
                         "在浏览器中打开以下网址"), contentY, COL_MUTED, 2);

    // URL
    drawTextCentered(url, contentY + 32, COL_ACCENT, 2);

    // Divider
    int divW = 600;
    drawRect((FB_WIDTH - divW) / 2, contentY + 62, divW, 1, COL_BORDER);

    // "or scan the QR code"
    drawTextCentered(tr("or scan the QR code",
                         "或扫描二维码"), contentY + 74, COL_MUTED, 2);

    // QR code centered
    int qrY = contentY + 106;
    drawQR(url, -1, qrY, qrSize); // -1 = auto-center

    // Media count — vertically centered between QR bottom and footer
    int footerTop = FB_HEIGHT - 50;
    int qrBottom  = qrY + qrTotalPx;
    // Block height: 1 (divider) + 14 + 18 (label) + 14 + 40 (number) = ~87px
    int blockH = 87;
    int blockTop = qrBottom + (footerTop - qrBottom - blockH) / 2;
    drawRect((FB_WIDTH - divW) / 2, blockTop, divW, 1, COL_BORDER);
    drawTextCentered(tr("Media files found",
                         "已找到媒体文件"), blockTop + 14, COL_MUTED, 2);
    drawTextCentered(countStr, blockTop + 40, COL_TEXT, 5);

    // ── Bottom bar ────────────────────────────────────────────────────────
    int barY = FB_HEIGHT - 50;
    drawRect(0, barY, FB_WIDTH, 1, COL_BORDER);
    drawRect(0, barY + 1, FB_WIDTH, FB_HEIGHT - barY - 1, COL_SURFACE);

    drawTextCentered(tr("Press  [+]  to exit",
                         "按 [+] 退出"), barY + 8, COL_MUTED, 2);
    drawTextCentered(tr("NXShare v1.8.1  ---  by musebrot <3",
                         "NX快传 v1.8.1  ---  作者 musebrot \xE2\x99\xA5  忘忧汉化"), barY + 30, COL_DIM, 2);

    present();
}
