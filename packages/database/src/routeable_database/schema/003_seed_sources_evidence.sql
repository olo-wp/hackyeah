-- RouteAble seed: accessibility sources + evidence.
-- Website / accessibility links live here (sources + evidence.source_url), NOT in
-- places.external_ids. Facts are extracted from each institution's official
-- "deklaracja dostępności" (legally required accessibility statement).
-- Scope: public cultural institutions and civic buildings in Kraków (museums,
-- theatres and other venues), each with a published accessibility declaration.
-- Values reflect the "Dostępność architektoniczna" sections; verification_status
-- = self_reported. Added incrementally in batches.
-- Idempotent: evidence ids are deterministic md5(place|feature|source).

INSERT INTO sources (id, type, name, url, license) VALUES
('muzeum-krakowa', 'official_website', 'Muzeum Krakowa', 'https://muzeumkrakowa.pl', NULL),
('mit-krakow', 'official_website', 'Muzeum Inżynierii i Techniki w Krakowie', 'https://www.mit.krakow.pl', NULL),
('mnk', 'official_website', 'Muzeum Narodowe w Krakowie', 'https://mnk.pl', NULL),
('zamek-wawel', 'official_website', 'Zamek Królewski na Wawelu', 'https://wawel.krakow.pl', NULL),
('muzeum-lotnictwa', 'official_website', 'Muzeum Lotnictwa Polskiego', 'https://muzeumlotnictwa.pl', NULL),
('muzeum-ak', 'official_website', 'Muzeum Armii Krajowej', 'https://muzeum-ak.pl', NULL),
('nck', 'official_website', 'Nowohuckie Centrum Kultury', 'https://nck.krakow.pl', NULL),
('mufo', 'official_website', 'Muzeum Fotografii w Krakowie', 'https://mufo.krakow.pl', NULL),
('cricoteka', 'official_website', 'Cricoteka', 'https://cricoteka.pl', NULL),
('etnomuzeum', 'official_website', 'Muzeum Etnograficzne w Krakowie', 'https://etnomuzeum.eu', NULL),
('muzeum-archeologiczne', 'official_website', 'Muzeum Archeologiczne w Krakowie', 'https://ma.krakow.pl', NULL),
('teatr-slowackiego', 'official_website', 'Teatr im. Juliusza Słowackiego w Krakowie', 'https://teatrwkrakowie.pl', NULL),
('stary-teatr', 'official_website', 'Narodowy Stary Teatr im. Heleny Modrzejewskiej', 'https://stary.pl', NULL),
('teatr-bagatela', 'official_website', 'Teatr Bagatela', 'https://bagatela.pl', NULL),
('teatr-ludowy', 'official_website', 'Teatr Ludowy', 'https://ludowy.pl', NULL),
('teatr-groteska', 'official_website', 'Teatr Groteska', 'https://groteska.pl', NULL),
('scena-stu', 'official_website', 'Krakowski Teatr Scena STU', 'https://scenastu.pl', NULL),
('opera-krakowska', 'official_website', 'Opera Krakowska', 'https://opera.krakow.pl', NULL),
('sad-okregowy', 'official_website', 'Sąd Okręgowy w Krakowie', 'https://krakow.so.gov.pl', NULL),
('archiwum-narodowe', 'official_website', 'Archiwum Narodowe w Krakowie', 'https://ank.gov.pl', NULL),
('umwm', 'official_website', 'Urząd Marszałkowski Województwa Małopolskiego', 'https://www.malopolska.pl', NULL),
('umk', 'official_website', 'Urząd Miasta Krakowa', 'https://www.krakow.pl', NULL),
('asp', 'official_website', 'Akademia Sztuk Pięknych im. Jana Matejki w Krakowie', 'https://www.asp.krakow.pl', NULL),
('agh', 'official_website', 'Akademia Górniczo-Hutnicza im. Stanisława Staszica', 'https://www.agh.edu.pl', NULL),
('wbp', 'official_website', 'Wojewódzka Biblioteka Publiczna w Krakowie', 'https://rajska.info', NULL),
('szpital-zeromskiego', 'official_website', 'Szpital Specjalistyczny im. Stefana Żeromskiego', 'https://zeromski-szpital.pl', NULL),
('mocak', 'official_website', 'MOCAK Muzeum Sztuki Współczesnej w Krakowie', 'https://mocak.pl', NULL),
('manggha', 'official_website', 'Muzeum Sztuki i Techniki Japońskiej Manggha', 'https://manggha.pl', NULL),
('ice-krakow', 'official_website', 'ICE Kraków (Agencja Rozwoju Miasta Krakowa)', 'https://icekrakow.pl', NULL),
('tauron-arena', 'official_website', 'Tauron Arena Kraków (Arena Kraków S.A.)', 'https://tauronarenakrakow.pl', NULL),
('teatr-kto', 'official_website', 'Teatr KTO', 'https://teatrkto.pl', NULL)
ON CONFLICT (id) DO NOTHING;

INSERT INTO evidence (id, place_id, source_id, feature_key, value, source_url, verification_status, retrieved_at, observed_at)
SELECT
    md5(place_id || '|' || feature_key || '|' || source_id)::uuid,
    place_id,
    source_id,
    feature_key,
    value::jsonb,
    source_url,
    verification_status,
    now(),
    observed_at::timestamptz
FROM (VALUES
    -- Muzeum Krakowa — https://muzeumkrakowa.pl/deklaracja-dostepnosci (oświadczenie 2026-04-17)
    -- Pałac Krzysztofory: barrier-free, 2 lifts + platform, accessible WC, N parking
    ('krakow:palac-krzysztofory', 'muzeum-krakowa', 'step_free_entrance', 'true',  'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    ('krakow:palac-krzysztofory', 'muzeum-krakowa', 'elevator',           'true',  'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    ('krakow:palac-krzysztofory', 'muzeum-krakowa', 'accessible_toilet',  'true',  'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    ('krakow:palac-krzysztofory', 'muzeum-krakowa', 'accessible_parking', 'true',  'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    -- Rynek Podziemny: barrier-free on every level, lift, accessible WC, N parking
    ('krakow:podziemia-rynku',    'muzeum-krakowa', 'step_free_entrance', 'true',  'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    ('krakow:podziemia-rynku',    'muzeum-krakowa', 'elevator',           'true',  'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    ('krakow:podziemia-rynku',    'muzeum-krakowa', 'accessible_toilet',  'true',  'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    ('krakow:podziemia-rynku',    'muzeum-krakowa', 'accessible_parking', 'true',  'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    -- Fabryka Schindlera: lift to all floors, accessible WC by entrance, no marked N parking
    ('krakow:fabryka-schindlera', 'muzeum-krakowa', 'step_free_entrance', 'true',  'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    ('krakow:fabryka-schindlera', 'muzeum-krakowa', 'elevator',           'true',  'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    ('krakow:fabryka-schindlera', 'muzeum-krakowa', 'accessible_toilet',  'true',  'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    ('krakow:fabryka-schindlera', 'muzeum-krakowa', 'accessible_parking', 'false', 'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    -- Stara Synagoga: many steps down, no lift/ramp, no accessible WC, no parking
    ('krakow:stara-synagoga',     'muzeum-krakowa', 'step_free_entrance', 'false', 'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    ('krakow:stara-synagoga',     'muzeum-krakowa', 'elevator',           'false', 'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    ('krakow:stara-synagoga',     'muzeum-krakowa', 'accessible_toilet',  'false', 'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    ('krakow:stara-synagoga',     'muzeum-krakowa', 'accessible_parking', 'false', 'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    -- Apteka pod Orłem: 2 steps at entrance (no ramp), no lift, accessible WC present, no N parking
    ('krakow:apteka-pod-orlem',   'muzeum-krakowa', 'step_free_entrance', 'false', 'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    ('krakow:apteka-pod-orlem',   'muzeum-krakowa', 'elevator',           'false', 'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    ('krakow:apteka-pod-orlem',   'muzeum-krakowa', 'accessible_toilet',  'true',  'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    ('krakow:apteka-pod-orlem',   'muzeum-krakowa', 'accessible_parking', 'false', 'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    -- Wieża Ratuszowa: narrow spiral stairs to ticket level, no lift, no accessible WC
    ('krakow:wieza-ratuszowa',    'muzeum-krakowa', 'step_free_entrance', 'false', 'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    ('krakow:wieza-ratuszowa',    'muzeum-krakowa', 'elevator',           'false', 'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    ('krakow:wieza-ratuszowa',    'muzeum-krakowa', 'accessible_toilet',  'false', 'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    ('krakow:wieza-ratuszowa',    'muzeum-krakowa', 'accessible_parking', 'false', 'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    -- Barbakan: historic site, level differences + thresholds, cobbled courtyard, no lift/WC
    ('krakow:barbakan',           'muzeum-krakowa', 'step_free_entrance', 'false',         'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    ('krakow:barbakan',           'muzeum-krakowa', 'elevator',           'false',         'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    ('krakow:barbakan',           'muzeum-krakowa', 'accessible_toilet',  'false',         'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    ('krakow:barbakan',           'muzeum-krakowa', 'accessible_parking', 'false',         'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    ('krakow:barbakan',           'muzeum-krakowa', 'surface',            '"cobblestone"', 'https://muzeumkrakowa.pl/deklaracja-dostepnosci', 'self_reported', '2026-04-17'),
    -- Muzeum Inżynierii i Techniki (Zajezdnia) — https://www.mit.krakow.pl/deklaracji-dostepnosci/ (aktualizacja 2026-03-16)
    ('krakow:muzeum-inzynierii',  'mit-krakow',     'step_free_entrance', 'true',          'https://www.mit.krakow.pl/deklaracji-dostepnosci/', 'self_reported', '2026-03-16'),
    ('krakow:muzeum-inzynierii',  'mit-krakow',     'elevator',           'true',          'https://www.mit.krakow.pl/deklaracji-dostepnosci/', 'self_reported', '2026-03-16'),
    ('krakow:muzeum-inzynierii',  'mit-krakow',     'accessible_toilet',  'true',          'https://www.mit.krakow.pl/deklaracji-dostepnosci/', 'self_reported', '2026-03-16'),
    ('krakow:muzeum-inzynierii',  'mit-krakow',     'accessible_parking', 'true',          'https://www.mit.krakow.pl/deklaracji-dostepnosci/', 'self_reported', '2026-03-16'),
    ('krakow:muzeum-inzynierii',  'mit-krakow',     'surface',            '"cobblestone"', 'https://www.mit.krakow.pl/deklaracji-dostepnosci/', 'self_reported', '2026-03-16'),
    -- Muzeum Narodowe w Krakowie (MNK) — https://mnk.pl/dostepnosc-dla-osob-z-trudnosciami-w-poruszaniu-sie/ (deklaracja 2026-04-14)
    -- Gmach Główny: external lift at main entrance, lifts/platforms inside, accessible WC on every floor, underground disabled parking
    ('krakow:mnk-gmach-glowny',   'mnk', 'step_free_entrance', 'true',          'https://mnk.pl/dostepnosc-dla-osob-z-trudnosciami-w-poruszaniu-sie/', 'self_reported', '2026-04-14'),
    ('krakow:mnk-gmach-glowny',   'mnk', 'elevator',           'true',          'https://mnk.pl/dostepnosc-dla-osob-z-trudnosciami-w-poruszaniu-sie/', 'self_reported', '2026-04-14'),
    ('krakow:mnk-gmach-glowny',   'mnk', 'accessible_toilet',  'true',          'https://mnk.pl/dostepnosc-dla-osob-z-trudnosciami-w-poruszaniu-sie/', 'self_reported', '2026-04-14'),
    ('krakow:mnk-gmach-glowny',   'mnk', 'accessible_parking', 'true',          'https://mnk.pl/dostepnosc-dla-osob-z-trudnosciami-w-poruszaniu-sie/', 'self_reported', '2026-04-14'),
    -- Sukiennice: no threshold at entrance, interior lift, accessible WC (portable ramps to it)
    ('krakow:sukiennice',         'mnk', 'step_free_entrance', 'true',          'https://mnk.pl/dostepnosc-dla-osob-z-trudnosciami-w-poruszaniu-sie/', 'self_reported', '2026-04-14'),
    ('krakow:sukiennice',         'mnk', 'elevator',           'true',          'https://mnk.pl/dostepnosc-dla-osob-z-trudnosciami-w-poruszaniu-sie/', 'self_reported', '2026-04-14'),
    ('krakow:sukiennice',         'mnk', 'accessible_toilet',  'true',          'https://mnk.pl/dostepnosc-dla-osob-z-trudnosciami-w-poruszaniu-sie/', 'self_reported', '2026-04-14'),
    -- Muzeum Czartoryskich: all levels adapted, lifts, accessible WC on the ground floor
    ('krakow:muzeum-czartoryskich','mnk', 'step_free_entrance','true',          'https://mnk.pl/dostepnosc-dla-osob-z-trudnosciami-w-poruszaniu-sie/', 'self_reported', '2026-04-14'),
    ('krakow:muzeum-czartoryskich','mnk', 'elevator',          'true',          'https://mnk.pl/dostepnosc-dla-osob-z-trudnosciami-w-poruszaniu-sie/', 'self_reported', '2026-04-14'),
    ('krakow:muzeum-czartoryskich','mnk', 'accessible_toilet', 'true',          'https://mnk.pl/dostepnosc-dla-osob-z-trudnosciami-w-poruszaniu-sie/', 'self_reported', '2026-04-14'),
    -- Pawilon Józefa Czapskiego: all levels step-free, voice-announce lift, accessible WC; granite-sett grounds
    ('krakow:dom-czapskiego',     'mnk', 'step_free_entrance', 'true',          'https://mnk.pl/dostepnosc-dla-osob-z-trudnosciami-w-poruszaniu-sie/', 'self_reported', '2026-04-14'),
    ('krakow:dom-czapskiego',     'mnk', 'elevator',           'true',          'https://mnk.pl/dostepnosc-dla-osob-z-trudnosciami-w-poruszaniu-sie/', 'self_reported', '2026-04-14'),
    ('krakow:dom-czapskiego',     'mnk', 'accessible_toilet',  'true',          'https://mnk.pl/dostepnosc-dla-osob-z-trudnosciami-w-poruszaniu-sie/', 'self_reported', '2026-04-14'),
    ('krakow:dom-czapskiego',     'mnk', 'surface',            '"cobblestone"', 'https://mnk.pl/dostepnosc-dla-osob-z-trudnosciami-w-poruszaniu-sie/', 'self_reported', '2026-04-14'),
    -- Dom Jana Matejki: not accessible for wheelchair users
    ('krakow:dom-matejki',        'mnk', 'step_free_entrance', 'false',         'https://mnk.pl/dostepnosc-dla-osob-z-trudnosciami-w-poruszaniu-sie/', 'self_reported', '2026-04-14'),
    ('krakow:dom-matejki',        'mnk', 'elevator',           'false',         'https://mnk.pl/dostepnosc-dla-osob-z-trudnosciami-w-poruszaniu-sie/', 'self_reported', '2026-04-14'),
    ('krakow:dom-matejki',        'mnk', 'accessible_toilet',  'false',         'https://mnk.pl/dostepnosc-dla-osob-z-trudnosciami-w-poruszaniu-sie/', 'self_reported', '2026-04-14'),
    -- Dom Józefa Mehoffera: two steps at entrance, no lift, no accessible WC (ramp only to the garden)
    ('krakow:dom-mehoffera',      'mnk', 'step_free_entrance', 'false',         'https://mnk.pl/dostepnosc-dla-osob-z-trudnosciami-w-poruszaniu-sie/', 'self_reported', '2026-04-14'),
    ('krakow:dom-mehoffera',      'mnk', 'elevator',           'false',         'https://mnk.pl/dostepnosc-dla-osob-z-trudnosciami-w-poruszaniu-sie/', 'self_reported', '2026-04-14'),
    ('krakow:dom-mehoffera',      'mnk', 'accessible_toilet',  'false',         'https://mnk.pl/dostepnosc-dla-osob-z-trudnosciami-w-poruszaniu-sie/', 'self_reported', '2026-04-14'),
    -- Zamek Królewski na Wawelu — https://wawel.krakow.pl/deklaracja-dostepnosci (2026-03-31); steep cobbled approaches, external lift + platforms inside
    ('krakow:zamek-wawel',        'zamek-wawel',           'step_free_entrance', 'false',         'https://wawel.krakow.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-31'),
    ('krakow:zamek-wawel',        'zamek-wawel',           'elevator',           'true',          'https://wawel.krakow.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-31'),
    ('krakow:zamek-wawel',        'zamek-wawel',           'accessible_toilet',  'true',          'https://wawel.krakow.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-31'),
    ('krakow:zamek-wawel',        'zamek-wawel',           'surface',            '"cobblestone"', 'https://wawel.krakow.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-31'),
    -- Muzeum Lotnictwa Polskiego — https://muzeumlotnictwa.pl/deklaracja-dostepnosci (2026-03-26); level entrance, lift, accessible WC, N parking
    ('krakow:muzeum-lotnictwa',   'muzeum-lotnictwa',      'step_free_entrance', 'true',          'https://muzeumlotnictwa.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-26'),
    ('krakow:muzeum-lotnictwa',   'muzeum-lotnictwa',      'elevator',           'true',          'https://muzeumlotnictwa.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-26'),
    ('krakow:muzeum-lotnictwa',   'muzeum-lotnictwa',      'accessible_toilet',  'true',          'https://muzeumlotnictwa.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-26'),
    ('krakow:muzeum-lotnictwa',   'muzeum-lotnictwa',      'accessible_parking', 'true',          'https://muzeumlotnictwa.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-26'),
    ('krakow:muzeum-lotnictwa',   'muzeum-lotnictwa',      'surface',            '"concrete"',    'https://muzeumlotnictwa.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-26'),
    -- Muzeum Armii Krajowej — https://muzeum-ak.pl/deklaracja-dostepnosci (2026-03-26); steps but permanent ramp, lift, accessible WC, 1 N parking bay
    ('krakow:muzeum-ak',          'muzeum-ak',             'step_free_entrance', 'true',          'https://muzeum-ak.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-26'),
    ('krakow:muzeum-ak',          'muzeum-ak',             'ramp',               'true',          'https://muzeum-ak.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-26'),
    ('krakow:muzeum-ak',          'muzeum-ak',             'elevator',           'true',          'https://muzeum-ak.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-26'),
    ('krakow:muzeum-ak',          'muzeum-ak',             'accessible_toilet',  'true',          'https://muzeum-ak.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-26'),
    ('krakow:muzeum-ak',          'muzeum-ak',             'accessible_parking', 'true',          'https://muzeum-ak.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-26'),
    -- Nowohuckie Centrum Kultury — https://nck.krakow.pl/deklaracja-dostepnosci (2026-03-31); step-free entry, lift, internal ramp, 8 N parking bays
    ('krakow:nck',                'nck',                   'step_free_entrance', 'true',          'https://nck.krakow.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-31'),
    ('krakow:nck',                'nck',                   'ramp',               'true',          'https://nck.krakow.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-31'),
    ('krakow:nck',                'nck',                   'elevator',           'true',          'https://nck.krakow.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-31'),
    ('krakow:nck',                'nck',                   'accessible_parking', 'true',          'https://nck.krakow.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-31'),
    -- Muzeum Fotografii / MuFo Józefitów — https://mufo.krakow.pl/deklaracja-dostepnosci (2026-03-25); ramp, lift, accessible WC, no on-site parking
    ('krakow:mufo',               'mufo',                  'step_free_entrance', 'true',          'https://mufo.krakow.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-25'),
    ('krakow:mufo',               'mufo',                  'ramp',               'true',          'https://mufo.krakow.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-25'),
    ('krakow:mufo',               'mufo',                  'elevator',           'true',          'https://mufo.krakow.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-25'),
    ('krakow:mufo',               'mufo',                  'accessible_toilet',  'true',          'https://mufo.krakow.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-25'),
    ('krakow:mufo',               'mufo',                  'accessible_parking', 'false',         'https://mufo.krakow.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-25'),
    -- Cricoteka — https://cricoteka.pl/deklaracja-dostepnosci (2026-03-30); ramp + stair-lift, lift, accessible WC every floor, 2 N bays nearby
    ('krakow:cricoteka',          'cricoteka',             'step_free_entrance', 'true',          'https://cricoteka.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-30'),
    ('krakow:cricoteka',          'cricoteka',             'ramp',               'true',          'https://cricoteka.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-30'),
    ('krakow:cricoteka',          'cricoteka',             'elevator',           'true',          'https://cricoteka.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-30'),
    ('krakow:cricoteka',          'cricoteka',             'accessible_toilet',  'true',          'https://cricoteka.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-30'),
    ('krakow:cricoteka',          'cricoteka',             'accessible_parking', 'true',          'https://cricoteka.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-30'),
    -- Muzeum Etnograficzne / Ratusz plac Wolnica — https://etnomuzeum.eu/dostepnosc-budynkow (2026-03-31); 2 steps with wheelchair ramp, no own parking
    ('krakow:muzeum-etnograficzne','etnomuzeum',           'step_free_entrance', 'true',          'https://etnomuzeum.eu/dostepnosc-budynkow', 'self_reported', '2026-03-31'),
    ('krakow:muzeum-etnograficzne','etnomuzeum',           'ramp',               'true',          'https://etnomuzeum.eu/dostepnosc-budynkow', 'self_reported', '2026-03-31'),
    ('krakow:muzeum-etnograficzne','etnomuzeum',           'accessible_parking', 'false',         'https://etnomuzeum.eu/dostepnosc-budynkow', 'self_reported', '2026-03-31'),
    -- Muzeum Archeologiczne / Gmach Główny ul. Senacka 3 — https://ma.krakow.pl/odwiedz-muzeum/dostepnosc/ (2025-07-11); historic, partial; assisted entry + lift inside, no on-site parking
    ('krakow:muzeum-archeologiczne','muzeum-archeologiczne','step_free_entrance','false',        'https://ma.krakow.pl/odwiedz-muzeum/dostepnosc/', 'self_reported', '2025-07-11'),
    ('krakow:muzeum-archeologiczne','muzeum-archeologiczne','elevator',          'true',          'https://ma.krakow.pl/odwiedz-muzeum/dostepnosc/', 'self_reported', '2025-07-11'),
    ('krakow:muzeum-archeologiczne','muzeum-archeologiczne','accessible_parking','false',         'https://ma.krakow.pl/odwiedz-muzeum/dostepnosc/', 'self_reported', '2025-07-11'),
    -- Teatr im. Juliusza Słowackiego / Gmach Główny — https://teatrwkrakowie.pl/deklaracja-dostepnosci (2026-03-03); ramp entrance, no visitor lift (stair platform), accessible WC, 2 N bays, cobbled surroundings
    ('krakow:teatr-slowackiego',  'teatr-slowackiego', 'step_free_entrance', 'true',          'https://teatrwkrakowie.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-03'),
    ('krakow:teatr-slowackiego',  'teatr-slowackiego', 'ramp',               'true',          'https://teatrwkrakowie.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-03'),
    ('krakow:teatr-slowackiego',  'teatr-slowackiego', 'elevator',           'false',         'https://teatrwkrakowie.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-03'),
    ('krakow:teatr-slowackiego',  'teatr-slowackiego', 'accessible_toilet',  'true',          'https://teatrwkrakowie.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-03'),
    ('krakow:teatr-slowackiego',  'teatr-slowackiego', 'accessible_parking', 'true',          'https://teatrwkrakowie.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-03'),
    ('krakow:teatr-slowackiego',  'teatr-slowackiego', 'surface',            '"cobblestone"', 'https://teatrwkrakowie.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-03'),
    -- Narodowy Stary Teatr / ul. Jagiellońska 1 — https://stary.pl/deklaracja-dostepnosci (2025-03-30); level entrance, assisted lift, accessible WC, no own parking
    ('krakow:stary-teatr',        'stary-teatr',       'step_free_entrance', 'true',          'https://stary.pl/deklaracja-dostepnosci', 'self_reported', '2025-03-30'),
    ('krakow:stary-teatr',        'stary-teatr',       'elevator',           'true',          'https://stary.pl/deklaracja-dostepnosci', 'self_reported', '2025-03-30'),
    ('krakow:stary-teatr',        'stary-teatr',       'accessible_toilet',  'true',          'https://stary.pl/deklaracja-dostepnosci', 'self_reported', '2025-03-30'),
    ('krakow:stary-teatr',        'stary-teatr',       'accessible_parking', 'false',         'https://stary.pl/deklaracja-dostepnosci', 'self_reported', '2025-03-30'),
    -- Teatr Bagatela / ul. Karmelicka 6 — https://bagatela.pl/deklaracja-dostepnosci; assisted step-free side entrance, accessible WC, stair platform (no lift)
    ('krakow:teatr-bagatela',     'teatr-bagatela',    'step_free_entrance', 'true',          'https://bagatela.pl/deklaracja-dostepnosci', 'self_reported', '2022-12-23'),
    ('krakow:teatr-bagatela',     'teatr-bagatela',    'accessible_toilet',  'true',          'https://bagatela.pl/deklaracja-dostepnosci', 'self_reported', '2022-12-23'),
    ('krakow:teatr-bagatela',     'teatr-bagatela',    'elevator',           'false',         'https://bagatela.pl/deklaracja-dostepnosci', 'self_reported', '2022-12-23'),
    -- Teatr Ludowy / os. Teatralne 34 — https://ludowy.pl/deklaracja-dostepnosci (2026-03-02); side ramp entrance, accessible WC, 1 N bay, stair platform (no lift)
    ('krakow:teatr-ludowy',       'teatr-ludowy',      'step_free_entrance', 'true',          'https://ludowy.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-02'),
    ('krakow:teatr-ludowy',       'teatr-ludowy',      'ramp',               'true',          'https://ludowy.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-02'),
    ('krakow:teatr-ludowy',       'teatr-ludowy',      'elevator',           'false',         'https://ludowy.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-02'),
    ('krakow:teatr-ludowy',       'teatr-ludowy',      'accessible_toilet',  'true',          'https://ludowy.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-02'),
    ('krakow:teatr-ludowy',       'teatr-ludowy',      'accessible_parking', 'true',          'https://ludowy.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-02'),
    -- Teatr Groteska / ul. Skarbowa 2 — https://groteska.pl/deklaracja-dostepnosci (2026-03-25); historic, no lift, access only via staff carrying wheelchairs
    ('krakow:teatr-groteska',     'teatr-groteska',    'step_free_entrance', 'false',         'https://groteska.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-25'),
    ('krakow:teatr-groteska',     'teatr-groteska',    'elevator',           'false',         'https://groteska.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-25'),
    -- Krakowski Teatr Scena STU / al. Krasińskiego 16-18 — https://scenastu.pl/ulatwienia-dla-osob-z-niepelnosprawnosciami/ (2023-12-28); ramp entrance, lift to WC level, accessible WC
    ('krakow:scena-stu',          'scena-stu',         'step_free_entrance', 'true',          'https://scenastu.pl/ulatwienia-dla-osob-z-niepelnosprawnosciami/', 'self_reported', '2023-12-28'),
    ('krakow:scena-stu',          'scena-stu',         'ramp',               'true',          'https://scenastu.pl/ulatwienia-dla-osob-z-niepelnosprawnosciami/', 'self_reported', '2023-12-28'),
    ('krakow:scena-stu',          'scena-stu',         'elevator',           'true',          'https://scenastu.pl/ulatwienia-dla-osob-z-niepelnosprawnosciami/', 'self_reported', '2023-12-28'),
    ('krakow:scena-stu',          'scena-stu',         'accessible_toilet',  'true',          'https://scenastu.pl/ulatwienia-dla-osob-z-niepelnosprawnosciami/', 'self_reported', '2023-12-28'),
    -- Opera Krakowska / ul. Lubicz 48 — https://opera.krakow.pl/deklaracja-dostepnosci; level entrance, two lifts, accessible WC on ground floor
    ('krakow:opera-krakowska',    'opera-krakowska',   'step_free_entrance', 'true',          'https://opera.krakow.pl/deklaracja-dostepnosci', 'self_reported', NULL),
    ('krakow:opera-krakowska',    'opera-krakowska',   'elevator',           'true',          'https://opera.krakow.pl/deklaracja-dostepnosci', 'self_reported', NULL),
    ('krakow:opera-krakowska',    'opera-krakowska',   'accessible_toilet',  'true',          'https://opera.krakow.pl/deklaracja-dostepnosci', 'self_reported', NULL),
    -- Sąd Okręgowy w Krakowie / ul. Przy Rondzie 7 — https://krakow.so.gov.pl/deklaracja-dostepnosci (2026-03-26); accessible main entrance w/ platform + auto doors, lifts, 14 accessible WCs, disabled parking bays
    ('krakow:sad-okregowy',       'sad-okregowy',      'step_free_entrance', 'true',          'https://krakow.so.gov.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-26'),
    ('krakow:sad-okregowy',       'sad-okregowy',      'elevator',           'true',          'https://krakow.so.gov.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-26'),
    ('krakow:sad-okregowy',       'sad-okregowy',      'accessible_toilet',  'true',          'https://krakow.so.gov.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-26'),
    ('krakow:sad-okregowy',       'sad-okregowy',      'accessible_parking', 'true',          'https://krakow.so.gov.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-26'),
    -- Archiwum Narodowe w Krakowie / ul. Rakowicka 22E — https://ank.gov.pl/deklaracja-dostepnosci (2025-03-31); barrier-free, auto doors, lift, accessible WC each floor, 2 disabled bays
    ('krakow:archiwum-narodowe',  'archiwum-narodowe', 'step_free_entrance', 'true',          'https://ank.gov.pl/deklaracja-dostepnosci', 'self_reported', '2025-03-31'),
    ('krakow:archiwum-narodowe',  'archiwum-narodowe', 'elevator',           'true',          'https://ank.gov.pl/deklaracja-dostepnosci', 'self_reported', '2025-03-31'),
    ('krakow:archiwum-narodowe',  'archiwum-narodowe', 'accessible_toilet',  'true',          'https://ank.gov.pl/deklaracja-dostepnosci', 'self_reported', '2025-03-31'),
    ('krakow:archiwum-narodowe',  'archiwum-narodowe', 'accessible_parking', 'true',          'https://ank.gov.pl/deklaracja-dostepnosci', 'self_reported', '2025-03-31'),
    -- Urząd Marszałkowski / Racławicka 56 — https://bip.malopolska.pl/umwm,a,1495135,siedziba-przy-ulicy-raclawickiej-56.html (2026-09-22); ramp + level entrances, lifts, accessible WCs, disabled parking
    ('krakow:umwm',               'umwm', 'step_free_entrance', 'true',  'https://bip.malopolska.pl/umwm,a,1495135,siedziba-przy-ulicy-raclawickiej-56.html', 'self_reported', '2026-09-22'),
    ('krakow:umwm',               'umwm', 'ramp',               'true',  'https://bip.malopolska.pl/umwm,a,1495135,siedziba-przy-ulicy-raclawickiej-56.html', 'self_reported', '2026-09-22'),
    ('krakow:umwm',               'umwm', 'elevator',           'true',  'https://bip.malopolska.pl/umwm,a,1495135,siedziba-przy-ulicy-raclawickiej-56.html', 'self_reported', '2026-09-22'),
    ('krakow:umwm',               'umwm', 'accessible_toilet',  'true',  'https://bip.malopolska.pl/umwm,a,1495135,siedziba-przy-ulicy-raclawickiej-56.html', 'self_reported', '2026-09-22'),
    ('krakow:umwm',               'umwm', 'accessible_parking', 'true',  'https://bip.malopolska.pl/umwm,a,1495135,siedziba-przy-ulicy-raclawickiej-56.html', 'self_reported', '2026-09-22'),
    -- Urząd Miasta Krakowa buildings — https://www.bip.krakow.pl/?sub_dok_id=754 (per-building access list; undated)
    -- Magistrat, pl. Wszystkich Świętych 3-4: historic, stair platform + accessible WC (no step-free entrance)
    ('krakow:umk-magistrat',      'umk',  'step_free_entrance', 'false', 'https://www.bip.krakow.pl/?sub_dok_id=754', 'self_reported', NULL),
    ('krakow:umk-magistrat',      'umk',  'accessible_toilet',  'true',  'https://www.bip.krakow.pl/?sub_dok_id=754', 'self_reported', NULL),
    -- ul. Wielicka 28A: ramp, lift, accessible WC
    ('krakow:umk-wielicka',       'umk',  'step_free_entrance', 'true',  'https://www.bip.krakow.pl/?sub_dok_id=754', 'self_reported', NULL),
    ('krakow:umk-wielicka',       'umk',  'ramp',               'true',  'https://www.bip.krakow.pl/?sub_dok_id=754', 'self_reported', NULL),
    ('krakow:umk-wielicka',       'umk',  'elevator',           'true',  'https://www.bip.krakow.pl/?sub_dok_id=754', 'self_reported', NULL),
    ('krakow:umk-wielicka',       'umk',  'accessible_toilet',  'true',  'https://www.bip.krakow.pl/?sub_dok_id=754', 'self_reported', NULL),
    -- os. Zgody 2 (incl. USC Nowa Huta): ramp, lift, accessible WC
    ('krakow:umk-nowa-huta',      'umk',  'step_free_entrance', 'true',  'https://www.bip.krakow.pl/?sub_dok_id=754', 'self_reported', NULL),
    ('krakow:umk-nowa-huta',      'umk',  'ramp',               'true',  'https://www.bip.krakow.pl/?sub_dok_id=754', 'self_reported', NULL),
    ('krakow:umk-nowa-huta',      'umk',  'elevator',           'true',  'https://www.bip.krakow.pl/?sub_dok_id=754', 'self_reported', NULL),
    ('krakow:umk-nowa-huta',      'umk',  'accessible_toilet',  'true',  'https://www.bip.krakow.pl/?sub_dok_id=754', 'self_reported', NULL),
    -- USC, ul. Lubelska 27: historic, stair-climber + accessible WC (no step-free entrance)
    ('krakow:usc',                'umk',  'step_free_entrance', 'false', 'https://www.bip.krakow.pl/?sub_dok_id=754', 'self_reported', NULL),
    ('krakow:usc',                'umk',  'accessible_toilet',  'true',  'https://www.bip.krakow.pl/?sub_dok_id=754', 'self_reported', NULL),
    -- Akademia Sztuk Pięknych / pl. Matejki 13 — https://www.asp.krakow.pl/deklaracja-dostepnosci (2025-02-06); main entrance has steps (adapted side entrance via intercom), lift, 2 accessible WCs, 1 disabled bay
    ('krakow:asp',                'asp',  'step_free_entrance', 'false', 'https://www.asp.krakow.pl/deklaracja-dostepnosci', 'self_reported', '2025-02-06'),
    ('krakow:asp',                'asp',  'elevator',           'true',  'https://www.asp.krakow.pl/deklaracja-dostepnosci', 'self_reported', '2025-02-06'),
    ('krakow:asp',                'asp',  'accessible_toilet',  'true',  'https://www.asp.krakow.pl/deklaracja-dostepnosci', 'self_reported', '2025-02-06'),
    ('krakow:asp',                'asp',  'accessible_parking', 'true',  'https://www.asp.krakow.pl/deklaracja-dostepnosci', 'self_reported', '2025-02-06'),
    -- AGH Gmach Główny A-0 / al. Mickiewicza 30 — https://www.agh.edu.pl/deklaracja-dostepnosci (2026-01-08); main entrance 7 steps (wheelchair entrance at rear via lift), 3 lifts, 2 accessible WCs, disabled bay
    ('krakow:agh-a0',             'agh',  'step_free_entrance', 'false', 'https://www.agh.edu.pl/deklaracja-dostepnosci', 'self_reported', '2026-01-08'),
    ('krakow:agh-a0',             'agh',  'elevator',           'true',  'https://www.agh.edu.pl/deklaracja-dostepnosci', 'self_reported', '2026-01-08'),
    ('krakow:agh-a0',             'agh',  'accessible_toilet',  'true',  'https://www.agh.edu.pl/deklaracja-dostepnosci', 'self_reported', '2026-01-08'),
    ('krakow:agh-a0',             'agh',  'accessible_parking', 'true',  'https://www.agh.edu.pl/deklaracja-dostepnosci', 'self_reported', '2026-01-08'),
    -- Wojewódzka Biblioteka Publiczna / ul. Rajska 1 — https://rajska.info/deklaracja-dostepnosci (2026-03-17); ramps at entrance + auto doors, 2 lifts, 4 accessible WCs, disabled parking
    ('krakow:wbp-rajska',         'wbp',  'step_free_entrance', 'true',  'https://rajska.info/deklaracja-dostepnosci', 'self_reported', '2026-03-17'),
    ('krakow:wbp-rajska',         'wbp',  'ramp',               'true',  'https://rajska.info/deklaracja-dostepnosci', 'self_reported', '2026-03-17'),
    ('krakow:wbp-rajska',         'wbp',  'elevator',           'true',  'https://rajska.info/deklaracja-dostepnosci', 'self_reported', '2026-03-17'),
    ('krakow:wbp-rajska',         'wbp',  'accessible_toilet',  'true',  'https://rajska.info/deklaracja-dostepnosci', 'self_reported', '2026-03-17'),
    ('krakow:wbp-rajska',         'wbp',  'accessible_parking', 'true',  'https://rajska.info/deklaracja-dostepnosci', 'self_reported', '2026-03-17'),
    -- Szpital Żeromskiego / os. Na Skarpie 66 — https://zeromski-szpital.pl/deklaracja-dostepnosci (2026-03-24); ramps, lifts, accessible WCs, disabled parking
    ('krakow:szpital-zeromskiego','szpital-zeromskiego', 'step_free_entrance', 'true', 'https://zeromski-szpital.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-24'),
    ('krakow:szpital-zeromskiego','szpital-zeromskiego', 'ramp',               'true', 'https://zeromski-szpital.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-24'),
    ('krakow:szpital-zeromskiego','szpital-zeromskiego', 'elevator',           'true', 'https://zeromski-szpital.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-24'),
    ('krakow:szpital-zeromskiego','szpital-zeromskiego', 'accessible_toilet',  'true', 'https://zeromski-szpital.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-24'),
    ('krakow:szpital-zeromskiego','szpital-zeromskiego', 'accessible_parking', 'true', 'https://zeromski-szpital.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-24'),
    -- MOCAK / ul. Lipowa 4 — https://mocak.pl/dostepnosc; purpose-built accessible (no thresholds), ramp (-1), lifts, 2 accessible WCs, no on-site parking, cobbled approach
    ('krakow:mocak',              'mocak',        'step_free_entrance', 'true',          'https://mocak.pl/dostepnosc', 'self_reported', NULL),
    ('krakow:mocak',              'mocak',        'ramp',               'true',          'https://mocak.pl/dostepnosc', 'self_reported', NULL),
    ('krakow:mocak',              'mocak',        'elevator',           'true',          'https://mocak.pl/dostepnosc', 'self_reported', NULL),
    ('krakow:mocak',              'mocak',        'accessible_toilet',  'true',          'https://mocak.pl/dostepnosc', 'self_reported', NULL),
    ('krakow:mocak',              'mocak',        'accessible_parking', 'false',         'https://mocak.pl/dostepnosc', 'self_reported', NULL),
    ('krakow:mocak',              'mocak',        'surface',            '"cobblestone"', 'https://mocak.pl/dostepnosc', 'self_reported', NULL),
    -- Manggha / ul. Konopnickiej 26 — https://manggha.pl/deklaracja-dostepnosci (2026-03-31); accessible ramps + N parking, accessible WC; main building has no lift (stair chair)
    ('krakow:manggha',            'manggha',      'step_free_entrance', 'true',          'https://manggha.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-31'),
    ('krakow:manggha',            'manggha',      'ramp',               'true',          'https://manggha.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-31'),
    ('krakow:manggha',            'manggha',      'elevator',           'false',         'https://manggha.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-31'),
    ('krakow:manggha',            'manggha',      'accessible_toilet',  'true',          'https://manggha.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-31'),
    ('krakow:manggha',            'manggha',      'accessible_parking', 'true',          'https://manggha.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-31'),
    -- ICE Kraków / ul. Konopnickiej 17 — https://icekrakow.pl/deklaracja-dostepnosci (2026-03-25); step-free entrances + ramp, lifts, accessible WCs each level, disabled parking
    ('krakow:ice-krakow',         'ice-krakow',   'step_free_entrance', 'true',          'https://icekrakow.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-25'),
    ('krakow:ice-krakow',         'ice-krakow',   'ramp',               'true',          'https://icekrakow.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-25'),
    ('krakow:ice-krakow',         'ice-krakow',   'elevator',           'true',          'https://icekrakow.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-25'),
    ('krakow:ice-krakow',         'ice-krakow',   'accessible_toilet',  'true',          'https://icekrakow.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-25'),
    ('krakow:ice-krakow',         'ice-krakow',   'accessible_parking', 'true',          'https://icekrakow.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-25'),
    -- Tauron Arena / ul. Lema 7 — https://tauronarenakrakow.pl/deklaracja-dostepnosci (2026-03-26); entrance via stairs or ramp, lifts to all floors
    ('krakow:tauron-arena',       'tauron-arena', 'step_free_entrance', 'true',          'https://tauronarenakrakow.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-26'),
    ('krakow:tauron-arena',       'tauron-arena', 'ramp',               'true',          'https://tauronarenakrakow.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-26'),
    ('krakow:tauron-arena',       'tauron-arena', 'elevator',           'true',          'https://tauronarenakrakow.pl/deklaracja-dostepnosci', 'self_reported', '2026-03-26'),
    -- Teatr KTO / ul. Zamoyskiego 50 — https://teatrkto.pl/deklaracja-dostepnosci; level entrance, lift, accessible WC, nearby disabled bay
    ('krakow:teatr-kto',          'teatr-kto',    'step_free_entrance', 'true',          'https://teatrkto.pl/deklaracja-dostepnosci', 'self_reported', NULL),
    ('krakow:teatr-kto',          'teatr-kto',    'elevator',           'true',          'https://teatrkto.pl/deklaracja-dostepnosci', 'self_reported', NULL),
    ('krakow:teatr-kto',          'teatr-kto',    'accessible_toilet',  'true',          'https://teatrkto.pl/deklaracja-dostepnosci', 'self_reported', NULL),
    ('krakow:teatr-kto',          'teatr-kto',    'accessible_parking', 'true',          'https://teatrkto.pl/deklaracja-dostepnosci', 'self_reported', NULL)
) AS e(place_id, source_id, feature_key, value, source_url, verification_status, observed_at)
ON CONFLICT (id) DO NOTHING;
