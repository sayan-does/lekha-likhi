/**
 * Okkhor52 Unicode → ANSI conversion for Lipighor ANSI fonts (e.g. Rajnigandha).
 * Mapping from https://okkhor52.com/js/converter.js (personal-use fonts).
 */

const conversions = {
  '।': '|',
  '‘': 'Ô',
  '’': 'Õ',
  '“': 'Ò',
  '”': 'Ó',
  'ধ্ন': 'aœ',
  'ক্ন': 'Kè',
  'ঘ্ন': 'Nœ',
  'গ্ব': 'M¦',
  'ফ্ত': 'd&Z',
  'ছ্ব': 'Q¡',
  'চ্ব': 'P¡',
  'ক্ম': '´',
  'র্ক': 'K©',
  'র্খ': 'L©',
  'র্গ': 'M©',
  'র্ঘ': 'N©',
  'র্ঙ': 'O©',
  'র্চ': 'P©',
  'র্ছ': 'Q©',
  'র্জ': 'R©',
  'র্ঝ': 'S©',
  'র্ঞ': 'T©',
  'র্ট': 'U©',
  'র্ঠ': 'V©',
  'র্ড': 'W©',
  'র্ঢ': 'X©',
  'র্ণ': 'Y©',
  'র্ত': 'Z©',
  'র্দ': '`©',
  'র্থ': '_©',
  'র্ধ': 'a©',
  'র্ন': 'b©',
  'র্প': 'c©',
  'র্ফ': 'd©',
  'র্ব': 'e©',
  'র্ভ': 'f©',
  'র্ম': 'g©',
  'র্য': 'h©',
  'র‍্য': 'i¨',
  'র্র': 'i©',
  'র্ল': 'j©',
  'র্শ': 'k©',
  'র্ষ': 'l©',
  'র্স': 'm©',
  'র্হ': 'n©',
  'র্য়': 'q©',
  'ম্প্র': '¤cÖ',
  'ক্ষ্ম': '²',
  'ক্ক': '°',
  'ক্ট': '±',
  'ক্ত': '³',
  'ক্ব': 'K¡',
  'স্ক্র': '¯Œ',
  'ক্র': 'µ',
  'ক্ল': 'K¬',
  'ক্ষ': '¶',
  'ক্স': '·',
  'গু': '¸',
  'গ্ধ': '»',
  'গ্ন': 'Mœ',
  'গ্ম': 'M¥',
  'গ্ল': 'M­',
  'গ্রু': 'MÖ“',
  'গ্রূ': 'MÖƒ',
  'দ্রু': '`ª“',
  'দ্রূ': '`ªƒ',
  'ব্রু': 'eª“',
  'ব্রূ': 'eªƒ',
  'ত্রু': 'Î“',
  'ত্রূ': 'Îƒ',
  'ভ্রু': 'å“',
  'ভ্রূ': 'åƒ',
  'ঙ্ক': '¼',
  'ঙ্ক্ষ': '•¶',
  'ঙ্খ': '•L',
  'ঙ্গ': '½',
  'ঙ্ঘ': '•N',
  'চ্ছ্ব': '”Q¡',
  'চ্চ': '”P',
  'চ্ছ': '”Q',
  'চ্ঞ': '”T',
  'জ্জ্ব': '¾¡',
  'জ্জ': '¾',
  'জ্ঝ': 'À',
  'জ্ঞ': 'Á',
  'জ্ব': 'R¡',
  'ঞ্চ': 'Â',
  'ঞ্ছ': 'Ã',
  'ঞ্জ': 'Ä',
  'ঞ্ঝ': 'Å',
  'ট্ট': 'Æ',
  'ট্ব': 'U¡',
  'ট্ম': 'U¥',
  'ড্ড': 'Ç',
  'ণ্ট': 'È',
  'ণ্ঠ': 'É',
  'ন্স': 'Ý',
  'ণ্ড': 'Ê',
  'ন্তু': 'š‘',
  'ণ্ব': 'Y^',
  'ত্ত্ব': 'Ë¡',
  'ত্ত': 'Ë',
  'ত্থ': 'Ì',
  'ত্ন': 'Zœ',
  'ত্ম': 'Z¥',
  'ন্ত্ব': 'š—¡',
  'ত্ব': 'Z¡',
  'থ্ব': '_¡',
  'দ্গ': '˜M',
  'দ্ঘ': '˜N',
  'দ্দ': 'Ï',
  'দ্ধ': '×',
  'দ্ব': '˜¡',
  'দ্ভ': '™¢',
  'দ্ম': 'Ù',
  'ধ্ব': 'aŸ',
  'ধ্ম': 'a¥',
  'ন্ট': '›U',
  'ন্ঠ': 'Ú',
  'ন্ড': 'Û',
  'ন্ত্র': 'š¿',
  'ন্ত': 'š—',
  'স্ত্র': '¯¿',
  'ত্র': 'Î',
  'ন্থ': 'š’',
  'ন্দ': '›`',
  'ন্দ্ব': '›Ø',
  'ন্ধ': 'Ü',
  'ন্ন': 'bœ',
  'ন্ব': 'š^',
  'ন্ম': 'b¥',
  'প্ট': 'Þ',
  'প্ত': 'ß',
  'প্ন': 'cœ',
  'প্প': 'à',
  'প্ল': 'c­',
  'প্স': 'á',
  'ফ্ল': 'd¬',
  'ব্জ': 'â',
  'ব্দ': 'ã',
  'ব্ধ': 'ä',
  'ব্ব': 'eŸ',
  'ব্ল': 'e­',
  'ভ্র': 'å',
  'ম্ন': 'gœ',
  'ম্প': '¤ú',
  'ম্ফ': 'ç',
  'ম্ব': '¤^',
  'ম্ভ': '¤¢',
  'ম্ভ্র': '¤£',
  'ম্ম': '¤§',
  'ম্ল': '¤­',
  'রু': 'i“',
  'রূ': 'iƒ',
  'ল্ক': 'é',
  'ল্গ': 'ê',
  'ল্ট': 'ë',
  'ল্ড': 'ì',
  'ল্প': 'í',
  'ল্ফ': 'î',
  'ল্ব': 'j¦',
  'ল্ম': 'j¥',
  'ল্ল': 'j­',
  'শু': 'ï',
  'শ্চ': 'ð',
  'শ্ন': 'kœ',
  'শ্ব': 'k¦',
  'শ্ম': 'k¥',
  'শ্ল': 'k­',
  'ষ্ক': '®‹',
  'ষ্ক্র': '®Œ',
  'ষ্ট': 'ó',
  'ষ্ঠ': 'ô',
  'ষ্ণ': 'ò',
  'ষ্প': '®ú',
  'ষ্ফ': 'õ',
  'ষ্ম': '®§',
  'স্ক': '¯‹',
  'স্ট': '÷',
  'স্খ': 'ö',
  'স্ত': '¯—',
  'স্তু': '¯‘',
  'স্থ': '¯’',
  'স্ন': 'mœ',
  'স্প': '¯ú',
  'স্ফ': 'ù',
  'স্ব': '¯^',
  'স্ম': '¯§',
  'স্ল': '¯­',
  'হু': 'û',
  'হ্ণ': 'nè',
  'হ্ব': 'nŸ',
  'হ্ন': 'ý',
  'হ্ম': 'þ',
  'হ্ল': 'n¬',
  'হৃ': 'ü',
  'র্': '©',
  '্র': 'ª',
  '্য': '¨',
  '্': '&',
  'আ': 'Av',
  'অ': 'A',
  'ই': 'B',
  'ঈ': 'C',
  'উ': 'D',
  'ঊ': 'E',
  'ঋ': 'F',
  'এ': 'G',
  'ঐ': 'H',
  'ও': 'I',
  'ঔ': 'J',
  'ক': 'K',
  'খ': 'L',
  'গ': 'M',
  'ঘ': 'N',
  'ঙ': 'O',
  'চ': 'P',
  'ছ': 'Q',
  'জ': 'R',
  'ঝ': 'S',
  'ঞ': 'T',
  'ট': 'U',
  'ঠ': 'V',
  'ড': 'W',
  'ঢ': 'X',
  'ণ': 'Y',
  'ত': 'Z',
  'থ': '_',
  'দ': '`',
  'ধ': 'a',
  'ন': 'b',
  'প': 'c',
  'ফ': 'd',
  'ব': 'e',
  'ভ': 'f',
  'ম': 'g',
  'য': 'h',
  'র': 'i',
  'ল': 'j',
  'শ': 'k',
  'ষ': 'l',
  'স': 'm',
  'হ': 'n',
  'ড়': 'o',
  'ঢ়': 'p',
  'য়': 'q',
  'ৎ': 'r',
  '০': '0',
  '১': '1',
  '২': '2',
  '৩': '3',
  '৪': '4',
  '৫': '5',
  '৬': '6',
  '৭': '7',
  '৮': '8',
  '৯': '9',
  'া': 'v',
  'ি': 'w',
  'ী': 'x',
  'ু': 'y',
  'ূ': '~',
  'ৃ': '…',
  'ে': '‡',
  'ো': '‡',
  'ৈ': '‰',
  'ৗ': 'Š',
  'ৌ': 'Š',
  'ং': 's',
  'ঃ': 't',
  'ঁ': 'u',
  '্ল': '­',
};

const BENGALI_CLUSTER_RX =
  /((([অ-হড়-য়](?:্[অ-মশ-হড়-য়])*)(্[য-ল])*)|[অ-হড়-য়]্|[অ-হড়-য়])[া-ৌ]*|[ঁঃং]|ৎ|[০-৯]|./g;

const UNICODE_BENGALI_RX = /[\u0980-\u09FF]/;

const ANSI_TO_UNICODE = Object.entries(conversions)
  .filter(([, ansi]) => ansi.length > 0)
  .sort((a, b) => b[1].length - a[1].length);

function replacer(match, p1, p3, p4) {
  if (conversions[match]) {
    return conversions[match];
  }
  const kaar = match.match(/[া-ৌ]/);
  if (kaar) {
    const intConv = p1.replace(BENGALI_CLUSTER_RX, replacer);
    if (/[াীুূৗৃ]/.test(kaar[0])) {
      return intConv + conversions[kaar[0]];
    }
    if (/[িেৈ]/.test(kaar[0])) {
      return conversions[kaar[0]] + intConv;
    }
    return conversions[kaar[0]] + intConv + 'v';
  }
  const phala = match.match(/্[য-ল]/);
  if (phala) {
    const intConv = p3.replace(BENGALI_CLUSTER_RX, replacer);
    return intConv + conversions[p4];
  }
  return match;
}

/** Unicode Bengali → Rajnigandha/Okkhor52 ANSI keystrokes for rendering. */
export function unicodeToAnsi(text) {
  if (!text || !UNICODE_BENGALI_RX.test(text)) return text ?? '';
  return text.replace(BENGALI_CLUSTER_RX, replacer);
}

/** Best-effort reverse of unicodeToAnsi for edited ANSI text. */
export function ansiToUnicode(text) {
  if (!text) return '';
  let i = 0;
  let result = '';
  while (i < text.length) {
    let matched = false;
    for (const [uni, ansi] of ANSI_TO_UNICODE) {
      if (text.startsWith(ansi, i)) {
        result += uni;
        i += ansi.length;
        matched = true;
        break;
      }
    }
    if (!matched) {
      result += text[i];
      i += 1;
    }
  }
  return result;
}

export function containsUnicodeBengali(text) {
  return UNICODE_BENGALI_RX.test(text ?? '');
}

/** Normalize editor value to Unicode for API storage. */
export function normalizeEditorText(raw) {
  const value = raw ?? '';
  if (containsUnicodeBengali(value)) return value;
  const decoded = ansiToUnicode(value);
  if (containsUnicodeBengali(decoded)) return decoded;
  return value;
}

/** Text shown in the journal with Rajnigandha applied. */
export function toDisplayText(stored) {
  const value = stored ?? '';
  if (!containsUnicodeBengali(value)) return value;
  return unicodeToAnsi(value);
}
