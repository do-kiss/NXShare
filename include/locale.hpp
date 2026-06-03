// NXShare localization header
// Supports English and Simplified Chinese based on Switch system language

#ifndef LOCALE_HPP
#define LOCALE_HPP

#include <switch.h>

// Language enumeration
enum class Lang { EN, ZH };

// Current language — set once at startup
extern Lang g_lang;

// Detect and set the current system language
// Must be called after service initialization
inline void detectSystemLanguage() {
    setInitialize();
    u64 langCode = 0;
    Result r = setGetSystemLanguage(&langCode);
    if (R_SUCCEEDED(r)) {
        SetLanguage sl;
        r = setMakeLanguage(langCode, &sl);
        if (R_SUCCEEDED(r)) {
            // Simplified Chinese variants
            if (sl == SetLanguage_ZHCN || sl == SetLanguage_ZHHANS)
                g_lang = Lang::ZH;
            else
                g_lang = Lang::EN;
        } else {
            g_lang = Lang::EN;
        }
    } else {
        // fallback: try legacy API
        r = setGetLanguageCode(&langCode);
        if (R_SUCCEEDED(r)) {
            SetLanguage sl = static_cast<SetLanguage>(langCode);
            if (sl == SetLanguage_ZHCN || sl == SetLanguage_ZHHANS)
                g_lang = Lang::ZH;
            else
                g_lang = Lang::EN;
        } else {
            g_lang = Lang::EN;
        }
    }
    setExit();
}

// Translation helper — returns the appropriate string for the current language
inline const char* tr(const char* en, const char* zh) {
    return (g_lang == Lang::ZH) ? zh : en;
}

#endif // LOCALE_HPP
