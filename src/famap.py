import re
KW=[('Black',r'black|obsidian|midnight black|charcoal black|onyx|stealth|coal|abyss|nightfall|castblack|cast black|pirate black|galaxy black|black hole|matte graphite'),
('White',r'white|cream|creme|eggshell|ivory|chalk|cloud(?! cover)|arctic|milk|bone|moonlight white'),
('Silver',r'silver|chrome|aluminum|nickel|quicksilver|metal\b|moonlight|sirius|platinum'),
('Gray',r'gr[ae]y|anthracite|graphite|slate|gunmetal|charcoal|tundra|haze(?! purple)|nimbus|cloud cover|iron|forge|stone gray|knight shield|tempest'),
('Pink',r'pink|blush|coral|salmon|rose|wildberry'),
('Purple',r'purple|violet|lavender|amethyst|orchid|plum|lilac|blurple'),
('Red',r'red|crimson|scarlet|burgundy|cranberry|tabasco|merlot|cherry|firebrick|bricks|maroon'),
('Orange',r'orange|tangerine|mango|lava|apricot|copper|amber|race'),
('Yellow',r'yellow|lemon|turmeric'),
('Brown',r'brown|caramel|cinnamon|bronze|rust|woodgrain|sedona|copperhead'),
('Tan',r'tan\b|beige|sand|khaki|peanut|honey|desert'),
('Teal',r'teal|seafoam|cyan|aqua|turquoise|baja'),
('Green',r'green|olive|sage|matcha|moss|pine|emerald|forest|camo|mint|army|od green|aloe|mantis|bay leaf|guacamole|echeveria|patina|olivine'),
('Blue',r'blue|navy|cobalt|indigo|denim|ocean|sky|sapphire|petrol|lapis|aquarium|mountain air|veiled vista|mallard|bluebird|glacier|periwinkle|pacific|raindrop|mist|lemans|deep sea'),
]
def fam(name):
    n=name.lower()
    best=None;pos=1e9
    for f,p in KW:
        m=re.search(p,n)
        if m and m.start()<pos: best,pos=f,m.start()
    return best
BASIC={'black':'Black','white':'White','gray':'Gray','grey':'Gray','silver':'Silver','red':'Red','orange':'Orange','yellow':'Yellow','green':'Green','blue':'Blue','purple':'Purple','pink':'Pink','brown':'Brown','tan':'Tan','teal':'Teal'}
_kw=fam
def fam(name):
    for w in re.findall(r'[a-z]+',name.lower()):
        if w in BASIC: return BASIC[w]
    return _kw(name)
