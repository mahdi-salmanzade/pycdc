#include "pyc_string.h"
#include "pyc_module.h"
#include "data.h"
#include <stdexcept>

static bool check_ascii(const std::string& data)
{
    auto cp = reinterpret_cast<const unsigned char*>(data.c_str());
    while (*cp) {
        if (*cp & 0x80)
            return false;
        ++cp;
    }
    return true;
}

/* PycString */
void PycString::load(PycData* stream, PycModule* mod)
{
    if (type() == TYPE_STRINGREF) {
        PycRef<PycString> str = mod->getIntern(stream->get32());
        m_type = str->m_type;
        m_value = str->m_value;
    } else {
        int length;
        if (type() == TYPE_SHORT_ASCII || type() == TYPE_SHORT_ASCII_INTERNED)
            length = stream->getByte();
        else
            length = stream->get32();

        if (length < 0)
            throw std::bad_alloc();

        m_value.resize(length);
        if (length) {
            stream->getBuffer(length, &m_value.front());
            if (type() == TYPE_ASCII || type() == TYPE_ASCII_INTERNED ||
                    type() == TYPE_SHORT_ASCII || type() == TYPE_SHORT_ASCII_INTERNED) {
                if (!check_ascii(m_value))
                    throw std::runtime_error("Invalid bytes in ASCII string");
            }
        }

        if (type() == TYPE_INTERNED || type() == TYPE_ASCII_INTERNED ||
                type() == TYPE_SHORT_ASCII_INTERNED)
            mod->intern(this);
    }
}

bool PycString::isEqual(PycRef<PycObject> obj) const
{
    if (type() != obj.type())
        return false;

    PycRef<PycString> strObj = obj.cast<PycString>();
    return isEqual(strObj->m_value);
}

/* Decodes the UTF-8 sequence (surrogates allowed, as marshal writes them)
 * that starts at value[pos].  Returns its length, or 0 if it is malformed. */
static size_t utf8_sequence(const std::string& value, size_t pos, unsigned int& cp)
{
    const unsigned char lead = static_cast<unsigned char>(value[pos]);
    size_t len;
    if (lead >= 0xF0 && lead <= 0xF4) {
        len = 4;
        cp = lead & 0x07;
    } else if (lead >= 0xE0 && lead <= 0xEF) {
        len = 3;
        cp = lead & 0x0F;
    } else if (lead >= 0xC2 && lead <= 0xDF) {
        len = 2;
        cp = lead & 0x1F;
    } else {
        return 0;
    }
    if (pos + len > value.size())
        return 0;
    for (size_t k = 1; k < len; ++k) {
        const unsigned char cont = static_cast<unsigned char>(value[pos + k]);
        if ((cont & 0xC0) != 0x80)
            return 0;
        cp = (cp << 6) | (cont & 0x3F);
    }
    return len;
}

static bool needs_escape(unsigned int cp)
{
    return (cp >= 0x80 && cp <= 0x9F)           // C1 controls
        || cp == 0xAD || cp == 0x61C            // soft hyphen, Arabic letter mark
        || (cp >= 0x200B && cp <= 0x200F)       // zero width, LRM/RLM
        || (cp >= 0x2028 && cp <= 0x202E)       // line/paragraph separators, bidi
        || (cp >= 0x2060 && cp <= 0x206F)       // invisible operators, bidi isolates
        || (cp >= 0xD800 && cp <= 0xDFFF)       // lone surrogates
        || cp == 0xFEFF                         // zero width no-break space (BOM)
        || (cp >= 0xFFF9 && cp <= 0xFFFB);      // interlinear annotation
}

void PycString::print(std::ostream &pyc_output, PycModule* mod, bool triple,
                      const char* parent_f_string_quote)
{
    char prefix = 0;
    switch (type()) {
    case TYPE_STRING:
        prefix = mod->strIsUnicode() ? 'b' : 0;
        break;
    case PycObject::TYPE_UNICODE:
        prefix = mod->strIsUnicode() ? 0 : 'u';
        break;
    case PycObject::TYPE_INTERNED:
        prefix = mod->internIsBytes() ? 'b' : 0;
        break;
    case PycObject::TYPE_ASCII:
    case PycObject::TYPE_ASCII_INTERNED:
    case PycObject::TYPE_SHORT_ASCII:
    case PycObject::TYPE_SHORT_ASCII_INTERNED:
        // These types don't exist until Python 3.4
        prefix = 0;
        break;
    default:
        throw std::runtime_error("Invalid string type");
    }

    if (prefix != 0)
        pyc_output << prefix;

    if (m_value.empty()) {
        pyc_output << "''";
        return;
    }

    // Determine preferred quote style (Emulate Python's method)
    bool useQuotes = false;
    if (!parent_f_string_quote) {
        for (char ch : m_value) {
            if (ch == '\'') {
                useQuotes = true;
            } else if (ch == '"') {
                useQuotes = false;
                break;
            }
        }
    } else {
        useQuotes = parent_f_string_quote[0] == '"';
    }

    // Output the string
    if (!parent_f_string_quote) {
        if (triple)
            pyc_output << (useQuotes ? R"(""")" : "'''");
        else
            pyc_output << (useQuotes ? '"' : '\'');
    }
    // Text (as opposed to bytes) is stored as UTF-8: TYPE_UNICODE always, and
    // TYPE_INTERNED from Python 3 on, where interned strings are str.
    const bool text = type() == TYPE_UNICODE
            || (type() == TYPE_INTERNED && mod->majorVer() >= 3);
    for (size_t i = 0; i < m_value.size(); ++i) {
        const char ch = m_value[i];
        size_t seq_len = 0;
        unsigned int cp = 0;
        if (text && static_cast<unsigned char>(ch) >= 0x80
                && (seq_len = utf8_sequence(m_value, i, cp)) != 0 && needs_escape(cp)) {
            // Write code points that are invalid in UTF-8 source (lone
            // surrogates, marshalled with surrogatepass) or invisible in it
            // (controls, separators, bidi and other format characters) as
            // escapes, so the recovered source shows what the string holds.
            if (cp > 0xFFFF)
                formatted_print(pyc_output, "\\U%08x", cp);
            else
                formatted_print(pyc_output, "\\u%04x", cp);
            i += seq_len - 1;
        } else if (static_cast<unsigned char>(ch) < 0x20 || ch == 0x7F) {
            if (ch == '\r') {
                pyc_output << "\\r";
            } else if (ch == '\n') {
                if (triple)
                    pyc_output << '\n';
                else
                    pyc_output << "\\n";
            } else if (ch == '\t') {
                pyc_output << "\\t";
            } else {
                formatted_print(pyc_output, "\\x%02x", (ch & 0xFF));
            }
        } else if (static_cast<unsigned char>(ch) >= 0x80) {
            if (text) {
                // Unicode stored as UTF-8...  Let the stream interpret it
                pyc_output << ch;
            } else {
                formatted_print(pyc_output, "\\x%02x", (ch & 0xFF));
            }
        } else {
            if (!useQuotes && ch == '\'')
                pyc_output << R"(\')";
            else if (useQuotes && ch == '"')
                pyc_output << R"(\")";
            else if (ch == '\\')
                pyc_output << R"(\\)";
            else if (parent_f_string_quote && ch == '{')
                pyc_output << "{{";
            else if (parent_f_string_quote && ch == '}')
                pyc_output << "}}";
            else
                pyc_output << ch;
        }
    }
    if (!parent_f_string_quote) {
        if (triple)
            pyc_output << (useQuotes ? R"(""")" : "'''");
        else
            pyc_output << (useQuotes ? '"' : '\'');
    }
}
