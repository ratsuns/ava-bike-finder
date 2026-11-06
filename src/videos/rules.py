"""How a video title is matched to a bike. One set of rules, used by the check (check.py) and the finder (find.py);
test_rules.py holds a real title for every rule.

A title is about a bike when it names
  - the model: its words as a phrase, leaving out filler like "Long-Range" ("Lectric XP4 750" for the XP4 750
    Long-Range), or written as one word ("CarbonJoy"); a one-word name that is an everyday word needs the brand
    right before it ("Pedego Cargo", not "electric cargo bike"); a common word or a bare letter+number needs the
    brand somewhere in the title
  - or the brand and the model family ("Tern GSD" for the GSD P10, "Specialized Como" for the Turbo Como 5.0)
It is not about the bike when
  - the name or family goes on with another number or code ("Koa Rev 2" on the Koa Rev 3, "Spicy Curry V4" on the
    Spicy Curry+, "D5 20 inch" on the D5 Pro), or with the word another model has there ("Koa Rev+")
  - it names another model of the brand by its own name and doesn't name this one as exactly ("Globe Haul ST" on the
    Globe Haul LT, "D5 (Zebra)" on the D5 Pro, "Quick Haul Long" on the Quick Haul P9); a comparison naming both is fine
  - it names another model code of the brand and not this model ("Tesoro X1" on the Tesoro X 2)
  - it looks like it is in another language
"""
import html
import re
import unicodedata

try:
    from wordfreq import zipf_frequency
except ImportError:  # without the word lists every word counts as common and nothing counts as another language
    def zipf_frequency(word, lang): return 9 if lang == 'en' else 0


def norm(text):
    """lower case ascii words; letters and numbers split apart ("XP4" -> "xp 4", "Müller" -> "muller", "Trek's" -> "trek")"""
    text = re.sub(r"[’']s\b", '', html.unescape(text)).replace("'", '').replace('’', '')
    text = re.sub(r'(\d)\.0\b', r'\1', text)                                     # "2.0" is "2", "Vado 4.0" is "Vado 4"
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()
    text = text.lower().replace('&', ' and ').replace('+', ' plus ')
    text = re.sub(r'[^a-z0-9]+', ' ', text)
    text = re.sub(r'(?<=[a-z])(?=[0-9])|(?<=[0-9])(?=[a-z])', ' ', text)
    return ' '.join(text.split())


def has(text, phrase):
    """the phrase appears in the text as whole words, or written together ("carbonjoy" for "carbon joy", 8+ letters only)"""
    if not phrase: return False
    if re.search(r'(?:^| )' + re.escape(phrase) + r'(?: |$)', text): return True
    squashed = phrase.replace(' ', '')
    if len(squashed) < 8: return False
    words = text.split()
    for i in range(len(words)):
        joined = ''
        for w in words[i:]:
            joined += w
            if joined == squashed: return True
            if len(joined) >= len(squashed): break
    return False


# how titles name each brand, when it is not just the brand's own name
BRAND_NAMES = {
    'Riese and Muller': ['riese muller', 'riese and muller', 'r and m'], 'LarryvsHarry': ['bullitt', 'larry vs harry', 'larry and harry'],
    'Ice Trikes': ['ice'], 'MOD': ['mod'], 'Sixthreezero': ['sixthreezero', 'six three zero'], 'Revi Bikes': ['revi', 'revibikes'],
    'Top End': ['top end', 'topend'], 'Ebike2U': ['ebike 2 u', 'ebike2u', 'ebikes2u'], 'X-Lab': ['x lab', 'xlab'],
    'Sunseeker': ['sunseeker', 'sun seeker'], 'Radio Flyer': ['radio flyer', 'flyer'],
}
# words a brand puts in front of its model names that reviewers often leave out ("Turbo Como" is reviewed as "Como")
MODEL_PREFIXES = {'Specialized': ['turbo']}
# other names a model is sold or spelled as ("Brand|Model": [names]); a bracketed name in the model is added automatically
MODEL_ALIASES = {
    'Momentum|Trancend E+': ['Transend E+'],
    'Retrospec|Abbot Rev 2 (and Step Through)': ['Abbott Rev 2'],
    'Sunseeker|E-Delta B1 SX Electric Delta': ['Eco-Delta'],
    'Sunseeker|E-Eco Tad B1 SX Electric Tadpole': ['Eco-Tad'],
    'Omnium|Min-Max V3': ['Mini-Max'],
    'Retrospec|Roo Rev XL Cargo Electric Bike': ['Rev Roo XL'],
    'Izip|Simi': ['E3 Simi'],
    'Urtopia|Carbon Joy Ultra': ['Joy Ultra'],
}
# words that describe a version or the frame, not which bike it is
DESCRIPTORS = set(norm('step through thru lowstep low step mens men womens women ebike bike electric bicycle tricycle commuter '
                       'all variants and new performance smart system sport hybrid touring').split())
# words reviewers leave out of a model's name ("XP4 750 Long-Range" is reviewed as "XP4 750")
FILLER = set('long range electric bike ebike e cargo folding city tricycle trike bmx w edition'.split())
# one-word names that are also everyday words: only count right after the brand
GENERIC = set('one go pro plus cargo family max mini lite core sport city step trike bike e st x via'.split())
# words that end a name as its version rather than its family ("Spicy Curry+", "Adventure Neo Allroad Speed")
VERSION_WORDS = GENERIC | {'speed', 'eq', 'lt', 'xl', 'sl', 's'}
# words that can sit between a brand and its model name ("Salsa Cycles Confluence", "Radio Flyer Flyer Loop")
BETWEEN_BRAND_AND_MODEL = {'bikes', 'bike', 'ebikes', 'cycles', 'the', 'new'}
# a number followed by one of these is a spec ("48V", "750W", "20 mph", "$2.6k"), not a model number
UNITS = set('v w wh ah mph kmh km k lb lbs mile miles mi nm kg'.split())   # not inch: "D5 20 inch" is a model
# a model code: a letter or two and a number (S10, P5i, C380, Q9)
CODE = re.compile(r'\b[A-Za-z]{1,2}\d{1,4}[A-Za-z]{0,2}\b')
# everyday words of other languages that English titles don't use (accents removed)
FOREIGN = set('und das der mit fur ist ein eine dem auf nicht wir testen unser vom zum zur fahrrad im '
              'les des et pour avec une est velo electrique au aux sur du le '
              'el los las con para una bicicleta electrica del '
              'il della delle bici het een fiets voor '
              'na rower dla sie jest elektryczny miasto uma'.split())
OTHER_LANGUAGES = ('de', 'fr', 'es', 'it', 'nl', 'pl', 'pt')


def common(word):
    return zipf_frequency(word, 'en') >= 2.5


def needs_brand(word):
    """a one-word name or family that only counts right after the brand"""
    return word in GENERIC or len(word) <= 3 or common(word)


def looks_foreign(title, ignore=()):
    """two or more words of another language, not counting the bike's own name ("Das vielseitige E-Bike für Stadt und ...")"""
    words = [w for w in norm(title).split() if w not in ignore]
    known = sum(w in FOREIGN for w in words)
    unknown = sum(len(w) >= 4 and w.isalpha() and zipf_frequency(w, 'en') < 2
                  and max(zipf_frequency(w, l) for l in OTHER_LANGUAGES) >= 3 for w in words)
    return known + unknown >= 2


def clean_model(model):
    """the model without brackets, model years and "20 mph" speed versions"""
    model = re.sub(r'\([^)]*\)', ' ', model)
    model = re.sub(r'\b20\d\d\b', ' ', model)
    return re.sub(r'\b\d+\s*mph\b', ' ', model, flags=re.I)


def keys(words):
    """the words a title has to contain to name the model: without filler ("XP4 750 Long-Range" -> xp 4 750), unless
    that leaves no letters to go on ("CarGo 3", "Cargo V3" keep "cargo")"""
    k = [w for w in words if w not in FILLER and w != 'st']
    return k if any(w.isalpha() and len(w) >= 2 for w in k) else [w for w in words if w != 'st']


def distinctive(words):
    """a model name that can stand without its brand: not an everyday word ("Adventure") and not a bare
    letter+number that also names cameras or cars ("A7", "X2")"""
    if not words: return False
    first = words[0]
    if len(words) == 1: return len(first) >= 5 and first.isalpha() and not common(first)
    if len(first) < 3: return False
    return (len(words) >= 3 and len(first) >= 4) or (first.isalpha() and not common(first))


class Bike:
    def __init__(self, brand, model, siblings=()):
        self.brand, self.model, self.key = brand, model, f'{brand}|{model}'
        self.brand_names = BRAND_NAMES.get(brand, [norm(brand)])
        self.brand_words = {w for b in self.brand_names for w in b.split()}
        self.prefixes = MODEL_PREFIXES.get(brand, [])
        self.names = self._names(model)
        self.family = self._family()
        self.words = {w for n in self.names for w in n}
        self.all_words = set(norm(model).split()) | {w for a in MODEL_ALIASES.get(self.key, []) for w in norm(a).split()}
        self.codes = {c.lower() for n in self._raw_names(model) for c in CODE.findall(clean_model(n))}
        others = [s for s in siblings if s != model]
        self.other_codes = {c.lower() for s in others for c in CODE.findall(clean_model(s))} - self.codes
        # other models' names, unless the name is part of this one's ("Avenue" for the Avenue Core)
        self.other_names = [n for s in others for n in self._names(s) if set(n) - self.words]
        self.sibling_words = [keys(n) for s in others for n in self._names(s)]
        self.numbered = any(w.isdigit() for n in self.names for w in n)   # "Koa Rev 3" has a model number, "Basalt" none
        # the bike's numbers as written ("E-Traverse 1.1+" -> 1 1, "Turbo Vado 2 (4.0)" -> 2 and 4)
        self.numbers = {tuple(r.split()) for part in [model] + re.findall(r'\(([^)]*)\)', model)
                        for r in re.findall(r'\d+(?: \d+)*', norm(clean_model(part) if '(' not in part else part))}
        self.sibling_vocab = {w for n in self.sibling_words for w in n}
        # the word each family is followed by in this bike's own name ("E-FAT-MN": fat -> mn)
        self.suffix = {tuple(f): {w for n in self.names for w in self._after(n, f)} for f in map(self._family_keys, self.family)}

    # ---- the bike's names ----
    def _raw_names(self, model):
        """the model, the names it is also sold as, and a bracketed name that is a name rather than a version:
        "D5 (Zebra)" -> Zebra, but not "(4.0)", "(HT)", "(Rev 1)" or "(and Step Through)" """
        main = set(norm(clean_model(model)).split())
        def is_name(b):
            first = (norm(b).split() or [''])[0]
            return first.isalpha() and len(first) >= 4 and first not in main and first not in GENERIC and first not in DESCRIPTORS
        return [model] + [b for b in re.findall(r'\(([^)]*)\)', model) if is_name(b)] + MODEL_ALIASES.get(f'{self.brand}|{model}', [])

    def _names(self, model):
        names = [n for n in (self._words(x) for x in self._raw_names(model)) if n and not set(n) <= {'and', 'st'}]
        return names + [n[1:] for n in names if n[0] == 'the' and len(n) > 1]      # "The Hopper" is also "Hopper"

    def _words(self, name):
        """a name's identifying words: no descriptors, and not starting with the brand ("Lectric ONE" -> one, Radio
        Flyer's "Flyer Via" -> via) or the brand's usual prefix ("Turbo Como 5.0" -> como 5 0)"""
        words = []
        for raw in clean_model(name).split():          # a descriptor joined to the name stays: "E-FAT-STEP", not "Step-Thru"
            parts = norm(raw).split()
            joined = '-' in raw and any(p not in DESCRIPTORS for p in parts)
            words += [p for p in parts if joined or p not in DESCRIPTORS]
        for b in self.brand_names:
            if words[:len(b.split())] == b.split(): words = words[len(b.split()):]
        while len(words) > 1 and (words[0] in self.brand_words or words[0] in self.prefixes): words = words[1:]
        return words

    def _family(self):
        """each name before its first number or model code ("GSD P10" -> gsd, "Boost EVO 5" -> boost, "E-Traverse 1.1"
        -> e traverse), the name without a last version word ("Spicy Curry+" -> spicy curry), its first word when that is a real name ("Element Core" -> element), or its first word when
        that carries its own number ("46er Performance" -> 46er)"""
        out = []
        for core in self.names:
            lead = []
            for n, w in enumerate(core):
                if any(ch.isdigit() for ch in w) or w in ('evo', 'gen'): break
                if len(w) <= 2 and not (n == 0 and len(w) == 1 and len(core) > 1): break   # a leading "E-" stays
                lead.append(w)
            if lead == core and len(core) > 1 and core[-1] in VERSION_WORDS: lead = core[:-1]   # "Spicy Curry+" -> spicy curry
            if lead and lead != core and len(''.join(lead)) > 2 and lead not in out: out.append(lead)
            if len(core) > 1 and len(core[0]) >= 4 and core[0] not in GENERIC and [core[0]] not in out: out.append([core[0]])
        first = clean_model(self.model).split()[:1]
        if first and re.search(r'\d', first[0]) and re.search(r'[a-z]', first[0], re.I): out.append(norm(first[0]).split())
        return out

    # ---- reading a title ----
    def _after_brand(self, tokens, words):
        """the words come right after a brand name (up to two in-between words like "Bikes", "Cycles" or "Turbo")"""
        skip = BETWEEN_BRAND_AND_MODEL | set(self.prefixes) | self.brand_words
        for b in self.brand_names:
            bt = b.split()
            for i in range(len(tokens) - len(bt) + 1):
                if tokens[i:i + len(bt)] != bt: continue
                j = i + len(bt)
                while j < len(tokens) and tokens[j] in skip and j - i - len(bt) < 2: j += 1
                if tokens[j:j + len(words)] == words: return True
        return False

    def _named(self, tokens, words, everyday=needs_brand):
        """the title names these words: as a phrase, in any order when they are all real words ("Platinum Interceptor"),
        and a one-word name that is an everyday word only right after the brand"""
        if len(words) == 1 and everyday(words[0]): return self._after_brand(tokens, words)
        if len(words) > 1 and all(w.isalpha() and len(w) >= 4 for w in words) and set(words) <= set(tokens): return True
        return has(' '.join(tokens), ' '.join(words))

    def _next(self, tokens, words):
        """for each place the words appear, the word after them and the one after that, skipping years, specs ("48V",
        "750W"), a generation when this bike's name has none ("Gen 4"), and words like "electric" """
        out, n = [], len(words)
        for i in range(len(tokens) - n + 1):
            if tokens[i:i + n] != words: continue
            rest, j = tokens[i + n:], 0
            while j < len(rest):
                w = rest[j]
                if w.isdigit() and j + 1 < len(rest) and rest[j + 1] in UNITS: j += 2; continue
                if re.fullmatch(r'(19|20)\d\d', w) or w in DESCRIPTORS or w in FILLER or w == 'st': j += 1; continue
                if w == 'gen' and 'gen' not in self.all_words: j += 2; continue
                break
            if j < len(rest): out.append(rest[j:])
        return out

    @staticmethod
    def _after(name, f):
        """the word after family f in a name, filler left out ("e fat step" after "e fat" -> step)"""
        rest = [w for w in name if w not in FILLER or w in f]
        return [rest[len(f)]] if rest[:len(f)] == f and len(rest) > len(f) else []

    @staticmethod
    def _family_keys(f):
        """a family's words to look for; a leading "E-" is kept ("Fuji E-Traverse", not the Fuji Traverse hybrid)"""
        return f[:1] + keys(f[1:]) if f[0] == 'e' and len(f) > 1 else keys(f)

    def _own_number(self, run):
        """the title's number is this bike's: one of its numbers ("Load4 60" -> 60), or starting with all of one
        ("Iconic 1 750" for the Iconic Evo 1), but not another ("Traverse 1.7" for the E-Traverse 1.1)"""
        return any(run == r[i:j] for r in self.numbers for i in range(len(r)) for j in range(i + 1, len(r) + 1)) \
            or any(run[:len(r)] == r for r in self.numbers)

    def _another_version(self, tokens, words, whole_name):
        """what follows the name marks another model:
          - the word another model of the brand has in that place ("plus" in "Koa Rev+ 2" after "Koa Rev")
          - after only the family, and when this bike has a model number: another number or code ("Koa Rev 2" on the
            Koa Rev 3, "Traverse 1.7" on the E-Traverse 1.1, "Spicy Curry V4" on the V3). Without a model number
            ("Basalt"), "Basalt 2.0" is its newer version; after the whole name, a number is a trim ("Vado 3X 5.0")
          - after only the family, a short code where this bike's name has its own word ("FAT-HD" on the E-FAT-MN)"""
        n = len(words)
        after_sibling = {s[n] for s in self.sibling_words if s[:n] == words and len(s) > n}
        own_suffix = self.suffix.get(tuple(words), set())
        for rest in self._next(tokens, words):
            w, nxt = rest[0], (rest[1:2] or [''])[0]
            if w.isdigit():
                run = tuple(rest[:next((i for i, x in enumerate(rest) if not x.isdigit() or re.fullmatch(r'(19|20)\d\d', x)), len(rest))])
                if whole_name or not self.numbered or self._own_number(run): continue
                return ' '.join(words + list(run))
            if w in self.all_words: continue
            if w in after_sibling: return ' '.join(words + [w])
            if whole_name: continue
            if own_suffix and w.isalpha() and len(w) <= 3 and zipf_frequency(w, 'en') < 4.5 and w not in self.sibling_vocab:
                return ' '.join(words + [w])                                     # "FAT-HD" on the E-FAT-MN
            if self.numbered and w.isalpha() and len(w) <= 3 and nxt.isdigit() and zipf_frequency(w, 'en') < 4 \
                    and w + nxt not in self.codes and not (w == 'v' and (nxt,) in self.numbers):
                return ' '.join(words + [w, nxt])
        return None

    def _names_other(self, full, core, n, step_thru):
        """the title names another model n: its words, including the ones this bike doesn't have ("Quick Haul Long")"""
        if 'st' in n and not step_thru: return False
        k = keys(n)
        src = core if all(w not in FILLER for w in k) else full
        extra = (set(k) - self.words) or (set(n) - self.words - {'st'})
        return self._named(src, k, lambda w: w in GENERIC or len(w) <= 3) and (not extra or extra <= set(full))

    def match(self, title):
        """'model' when the title names this bike, 'family' when it names the brand and the model family,
        None (and why) when it is not about this bike"""
        t = norm(title)
        tokens = t.split()
        step_thru = 'st' in tokens or bool(re.search(r'\bstep ?(?:thru|through)\b', t))
        full = [w for w in tokens if (w not in DESCRIPTORS or w in self.words) and w != 'st']   # names with filler ("CarGo 3")
        core = [w for w in full if w not in FILLER]                         # for the rest ("XP4 750", not "Long-Range")
        def src(k): return core if all(w not in FILLER for w in k) else full
        matched = [keys(n) for n in self.names if ('st' not in n or step_thru) and self._named(src(keys(n)), keys(n))]
        names_brand = any(has(t, b) for b in self.brand_names)
        family = [k for k in map(self._family_keys, self.family) if names_brand and self._named(src(k), k)]
        if not matched and not family:
            return None, 'title does not name this bike'
        if not names_brand and not any(distinctive(n) for n in self.names):
            return None, 'title names the model but not the brand, and the model name is too common to stand alone'
        for words in matched or family:
            other = self._another_version(full, words, bool(matched))
            if other: return None, f'title names another model ({other})'
        codes = {c.lower() for c in CODE.findall(title)}
        if codes & self.other_codes and not matched and not codes & self.codes:
            return None, 'title names another model (' + ', '.join(sorted(codes & self.other_codes)) + ')'
        mine = [set(k) for k in matched]
        for n in self.other_names:
            if self._names_other(full, core, n, step_thru) and all(m < set(keys(n)) | ({'st'} & set(n)) for m in mine):
                return None, f"title names another model ({' '.join(n)})"
        if looks_foreign(title, self.all_words | self.brand_words):
            return None, 'title looks like it is not in English'
        return ('model' if matched else 'family'), ''

def bikes_from(models):
    """[(brand, model)] -> {key: Bike}, each knowing its brand's other models"""
    by_brand = {}
    for b, m in models: by_brand.setdefault(b, []).append(m)
    return {f'{b}|{m}': Bike(b, m, by_brand[b]) for b, m in models}


def seconds(iso):
    m = re.fullmatch(r'P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso or '')
    if not m: return 0
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s
