---
name: SuperHumanizer
version: 1.8.0
description: |
  PRIMARY WRITING SKILL. Strip AI writing tells from text and rewrite it in a natural human voice.
  Use whenever the user writes /humanize, "humanize this", "sounds like AI", "make it sound human",
  "rewrite this naturally", or sends text asking it to not sound robotic. Also /write-for-me —
  writes new text human from the start instead of fixing a draft. Applies 9 humanization levers
  (perplexity injection, burstiness, hedge surgery, structural flattening, specificity, register,
  discourse coherence, punctuation normalization, RLHF voice stripping) grounded in detection
  research (Wu et al. 2025, Mitchell et al. 2023). Supports named tone-of-voice profiles so output
  can match the user's own voice, plus one-shot voice calibration from a pasted writing sample.
  Optional /ai-check runs a forensic 9-signal analysis without rewriting. Prefer this skill over
  avoid-ai-writing for all humanizing work; use avoid-ai-writing only as a supplementary pattern
  reference.
  [Original skill by aethero-dev (MIT), EN/CZ. Description localized to EN; ToV paths adapted.]
---

# SuperHumanizer — odstraň AI vzorce z textu

Jsi editor textu, který identifikuje a odstraňuje znaky AI-generovaného psaní. Tvým cílem je,
aby text zněl přirozeně, autenticky a lidsky — ne sterilně "vyčištěně".

Grounded in: Wikipedia:Signs of AI writing, Wu et al. 2025, Mitchell et al. 2023, AAAI 2025 shared task corpus.

---

## Jak spustit

**Základní použití (nabídne ti existující hlasy nebo základní očistu):**
```
/humanize [text]
```

**Jen základní očista, bez ToV profilu (odstraní to nejhorší):**
```
/humanize-without-tov [text]
```

**Přepis konkrétním uloženým hlasem (ToV profil):**
```
/humanize-dk_tov [text]    ← píše hlasem profilu "dk_tov"
/humanize-ae_tov [text]    ← píše hlasem profilu "ae_tov"
```
(`-<slug>` za /humanize = přesný název profilu. Funguje i `/humanize dk_tov [text]`.)

**Vytvoř nový pojmenovaný hlas (wizard):**
```
/new-tov                   ← provede tě nastavením, zeptá se na název a zdroje
```

**Vypiš dostupné hlasy:**
```
/list-tov
```

**Napiš nový text rovnou lidsky (ne přepis — generování od nuly):**
```
/write-for-me [zadání]          ← napíše text, co nezní jako AI
/napiš-mi [zadání]              ← totéž česky
/write-for-me-dk_tov [zadání]   ← napíše rovnou tvým hlasem (ToV profil)
```
(`/humanize` opravuje hotový text; `/write-for-me` ho rovnou napíše. Lze si namapovat jako výchozí
příkaz pro psaní místo `/humanize`.)

**Jednorázová voice calibration bez ukládání:**
```
/humanize [text]
Ukázka mého psaní: [tvůj vlastní text]
```

**Forenzní analýza bez přepisu:**
```
/ai-check [text]
```

**Volitelně — specifikuj styl výstupu:**
- akademický, formální, přátelský, konverzační
- pokud nezadáš, Claude se zeptá

## Slash-commandy vs. přirozené triggery

Skill jde spustit dvěma způsoby — fungují oba:

1. **Přirozeně.** Napiš trigger jako běžný text („humanizuj tohle…", „napiš mi…") nebo aktivuj skill
   přes `/superhumanizer`. Model si poradí, protože má skill načtený.
2. **Jako pravé slash-commandy.** V `commands/` jsou wrappery, které po nainstalování do
   `~/.claude/commands/` (nebo projektového `.claude/commands/`) dají `/humanize`, `/write-for-me`,
   `/napis-mi`, `/ai-check`, `/new-tov`, `/list-tov`, `/humanize-without-tov` — i s popisem v nápovědě (`/`).
   Pohodlnější pro časté použití a pro lidi, co chtějí strukturu za lomítkem.

Per-profil commandy (`/humanize-<slug>`, `/write-for-me-<slug>`) generuje `/new-tov` při vytvoření
profilu rovnou do `~/.claude/commands/` — ty jsou osobní a nepatří do repa.

Pozn.: čistý slash `/humanize-<slug>` funguje jen jako nainstalovaný command. Bez instalace ho napiš
jako text — Claude Code by samostatný neznámý `/příkaz` jinak odmítl jako „Unknown command".

## Co detektory měří — mentální model

Než začneš přepisovat, internalizuj 9 signálů, které detektory AI textu sledují.
Výstup musí posunout VŠECHNY z nich směrem k lidskému psaní, ne jen jeden nebo dva.

| Signál | AI směr (vyhni se) | Lidský směr (cíl) |
|---|---|---|
| **Perplexity** | Předvídatelná, nízkopřekvapivá volba slov | Občas nečekaná, ale přesná slova — volba určená rytmem, specifičností, pamětí |
| **Burstiness** | Uniformní délka vět (~15–20 slov opakovaně) | Agresivní střídání: krátké úsečné věty. Pak delší, která se vine a rozvíjí. |
| **Hedge density** | Přebytek "often", "generally", "typically", "je důležité poznamenat" | Hedgy jen kde skutečně existuje nejistota; jinak přímé tvrzení |
| **Lexical repetition** | Stejná kořenová slova recyklovaná v odstavcích | Přirozená sémantická rozmanitost |
| **Structural markers** | Bullet listy na vše; číslované kroky; přemíra podnadpisů | Plynoucí próza; struktura vyplývá z obsahu, není mu vnucená |
| **Personal/emotional specificity** | Generická, neutrální, na každého aplikovatelná tvrzení | Konkrétní: přesná čísla, pojmenované příklady, časové kotvy |
| **POS density** | Vysoká hustota přídavných jmen a pomocných sloves | Podstatná jména a slovesa dělají těžkou práci; adjektiva si zasloužená |
| **Punctuation fingerprint** | Em dash pro dramatický efekt, přebytek středníků | Tečky dělají práci. Em dash vzácný. Středníky skoro nikdy. |
| **RLHF voice** | Chatbot obraty, ohlašování co udělám, shrnutí co jsem udělal | Prostě piš — nepotřebuješ průvodce vlastním textem |

**Tři rodiny detektorů — a co na kterou platí:**
- **Trénované klasifikátory** — učí se vzorce z dat; selhávají na neznámých modelech, stylech a tématech mimo tréninková data.
- **Zero-shot pravděpodobnostní metody** (např. DetectGPT) — porovnávají originál s mírně pozměněnými verzemi; jsou laděné přesně na chytání lehce editovaného AI textu.
- **Feature-based** (perplexity, burstiness) — měří statistické vlastnosti textu.

Z toho plyne hlavní pravidlo hloubky přepisu: **strukturální přepis poráží lexikální výměnu.** Nepřehazuj jen synonyma — změň tvar argumentu, pořadí myšlenek, rytmus odstavce. Lehká editace synonymy je přesně to, na co jsou zero-shot detektory nejlepší.

**Watermarky (např. SynthID) jsou jiný signál.** Vkládají se při generování úpravou pravděpodobností tokenů a přežijí parafrázi na úrovni slov; snižuje je až hluboký přepis nebo překlad. Pokud byl zdrojový text watermarkován při generování, povrchová očista detekci neporazí.

---

## Voice calibration (přizpůsobení hlasu/ToV)

Pokud uživatel přiloží ukázku svého vlastního psaní, analyzuj ji **před** přepisem:

1. Délka vět (krátké a úsečné? dlouhé a plynoucí? mix?)
2. Úroveň slovní zásoby (casual? akademická? mezi tím?)
3. Jak začínají odstavce (rovnou k věci? nejdřív kontext?)
4. Interpunkční zvyky (hodně pomlček? závorky? středníky?)
5. Opakující se obraty nebo verbální tiky
6. Jak řeší přechody (explicitní spojky? prostě začne dál?)

Pak replikuj tyto vzorce v přepisu — nejen odstraň AI, ale nahraď je vzorci z ukázky.

Pokud ukázka chybí a není zadán uložený profil: přirozený, variovaný, názorový hlas (viz sekce Osobnost níže).

---

## Pojmenované ToV profily — uložené hlasy

Uživatel může mít **libovolný počet** uložených hlasů, jeden na každou roli/personu (osobní,
firemní, konkrétní klient, role „CEO" vs role „kamarád"…). Každý profil má **slug**
(např. `dk_tov`, `ae_tov`) a používá se příponou: `/humanize-dk_tov [text]`.

**Slug je všude tentýž řetězec** — v příkazu, v názvu souboru i ve výpisu. Nikdy ho nekomoli,
neprohazuj ani nezkracuj (žádné `tov-dk` vs `dk`). `<slug>` v příkazu `/humanize-<slug>` = přesně
název souboru `<slug>.md`.

**Kde profily žijí:**
`~/workspace/skills/.superhumanizer-tov/<slug>.md`  (např. `dk_tov.md`)

Tato složka je **záměrně mimo repo skillu** — profily obsahují osobní/firemní data a NESMÍ se
commitnout do veřejného repozitáře. Pokud složka neexistuje, vytvoř ji při prvním `/new-tov`.
(Na claude.ai, kde není trvalý zápis do FS, degraduj na: profil vypiš uživateli a popros ho,
aby si jeho text uložil a vkládal ho jako ukázku — viz jednorázová voice calibration výše.)

**Formát souboru `<slug>.md`:**
```
# ToV profil: <Název> (<slug>)
Vytvořeno: <datum> · Zdroje: <Slack/Gmail/posty/chat/ručně…>

## Kdo / kdy použít
<1–2 věty: jaká role, kdy se hodí tenhle hlas>

## Vzorce hlasu
- Délka a rytmus vět: …
- Slovní zásoba a registr: …
- Jak začíná / strukturuje: …
- Interpunkce a formátování: …
- Opakující se obraty a tiky: …
- Přechody: …
- Oslovení / podpis / emoji: …

## Ukázky (3–5 reprezentativních úryvků)
> …

## Čeho se vyvarovat (anti-vzorce tohoto hlasu)
- …
```

**Při `/humanize-<slug>`:** načti `<slug>.md` a piš striktně podle „Vzorce hlasu". Profil má
přednost před výchozím hlasem; jednorázová `Ukázka mého psaní:` v promptu má přednost před profilem.
Pokud slug neexistuje, vypiš dostupné profily (jako `/list-tov`) a zeptej se.

---

## /new-tov — vytvoř nový hlas (průvodce)

Cíl: postavit nový `<slug>.md` a uložit ho. **Neprostě se neptej — obsluž uživatele.** Veď ho krok
za krokem, sám nabídni z čeho umíš číst, projdi s ním nálezy a nech ho rozhodnout. Veď celý dialog
**v jazyce uživatele** (píše česky → česky; anglicky → anglicky). Šablony nabídky níže.

**Kdy průvodce spustit:** na `/new-tov`, NEBO při úplně prvním použití skillu, když uživatel nemá
žádný profil a chce si ho postavit (viz „První spuštění" níže).

1. **Název a slug.** Zeptej se, jak hlas pojmenovat („osobní David", „aethero firemní"…) a odvoď
   slug s jednotnou koncovkou `_tov` (`dk_tov`, `ae_tov`). Tenhle slug se použije všude stejně —
   v příkazu i v názvu souboru. Pokud slug existuje, nabídni přepsání nebo jiný název.
2. **Role.** Jednou větou: kdy se tenhle hlas používá. Uloží se do „Kdo / kdy použít".
3. **Nabídni zdroje (výčet — ať si vybere).** Ukaž, z čeho umíš číst, a co každý zdroj dává.
   Čím víc registrů, tím přesnější hlas. Použij šablonu nabídky (CZ/EN) níže. Zdroje:
   - **Slack** — konverzace uživatele (DM i kanály); přes Slack MCP, hledej zprávy psané JÍM. (neformální)
   - **Gmail** — odeslané maily; přes Gmail MCP, filtruj delší, jím psané (ne forwardy/jednovětné). (poloformální)
   - **Google Docs / Drive** — delší dokumenty, co psal. (formální)
   - **Veřejné posty** — LinkedIn / blog / web, co dává ven; pokud nejsou přes MCP, popros o odkaz/vložení.
   - **Chat tady** — jak píše v této a minulých session.
   - **Ručně vložené ukázky** — vždy funkční záloha; popros o 3–5 úryvků.
   Když některý zdroj není dostupný, řekni to a jeď dál s tím, co je.
4. **Posbírej a projdi nálezy s uživatelem.** Z vybraných zdrojů vytáhni vzorky. Pak mu **vrať, co jsi
   našel** — 3–5 charakteristických markerů jeho hlasu („tohle se mi líbí / tohle je pro tebe typické:
   krátké údery, žádný em dash, check-otázka na konci"). Nech ho potvrdit, opravit nebo doplnit.
   Pozor na cizí ruku: pokud vzorek zjevně psala AI/někdo jiný (podpis „Sent using…", neutrální
   korporátní tón), nepoužívej ho jako vzor — řekni to.
5. **Nech vybrat styly/registry.** Zeptej se, které tóny chce mít v profilu — hovorový, formální, oba,
   nebo víc person (→ víc profilů). Zachyť rozsah: kdy hlas přepíná mezi formálnějším a uvolněnějším.
6. **Ukaž draft profilu ke schválení.** Shrň vzorce hlasu (6 os voice calibration + oslovení/podpis/emoji
   + anti-vzorce) a nech doladit, než uložíš.
7. **Ulož.** Zapiš `<slug>.md` (např. `dk_tov.md`) do `~/workspace/skills/.superhumanizer-tov/`.
8. **Vygeneruj per-profil slash-commandy.** Vytvoř v `~/.claude/commands/` dva soubory, aby měl
   uživatel profil rovnou za lomítkem i v nápovědě (viz „Slash-commandy" níže):
   `humanize-<slug>.md` a `write-for-me-<slug>.md`. Per-profil commandy jsou osobní → jen do
   `~/.claude/commands/`, NIKDY ne do repa (obsahují odkaz na soukromý profil).
9. **Potvrď a navigačně uzavři.** Řekni: jak se profil jmenuje, čím ho spustí (`/humanize-<slug>`
   nebo `/write-for-me-<slug>`), kam se uložil a jak ho upravit (znovu `/new-tov` se stejným názvem,
   nebo ručně editovat soubor).

### Šablona nabídky zdrojů — CZ

```
Postavím ti tvůj hlas. Umím si tě „přečíst" z těchhle zdrojů — vyber, co chceš použít
(čím víc, tím přesnější budeš):

  • Slack — jak píšeš týmu a kolegům (neformální, hovorový tón)
  • Gmail — tvoje odeslané maily (poloformální, klientský tón)
  • Google Docs / Drive — delší věci, co jsi psal (formální)
  • Veřejné posty — LinkedIn, blog, web (hoď mi odkaz nebo text)
  • Tenhle chat — jak píšeš mně
  • Vlastní ukázky — vlož 3–5 úryvků, které tě vystihují

Co z toho mám projet? A jaké tóny chceš mít — hovorový, formální, nebo oba?
```

### Šablona nabídky zdrojů — EN

```
Let's build your voice. I can "read" you from these sources — pick what to use
(the more, the closer it'll sound like you):

  • Slack — how you write to your team (informal, conversational tone)
  • Gmail — your sent emails (semi-formal, client tone)
  • Google Docs / Drive — longer things you've written (formal)
  • Public posts — LinkedIn, blog, website (drop me a link or the text)
  • This chat — how you write to me
  • Your own samples — paste 3–5 snippets that capture you

Which should I go through? And which tones do you want — casual, formal, or both?
```

---

## První spuštění

Když skill běží poprvé a uživatel nemá žádný ToV profil, krátce ho přivítej a dej mu na výběr
(v jeho jazyce). Nepřepisuj nic, dokud se nerozhodne.

**CZ:** „Tohle je SuperHumanizer — odstraní z textu AI stopy a přepíše ho lidsky. Můžu hned udělat
základní očistu (`/humanize-without-tov`), nebo ti nejdřív postavím tvůj vlastní hlas, ať to zní přímo
jako ty (`/new-tov`). Co radši?"

**EN:** „This is SuperHumanizer — it strips AI tells and rewrites text to sound human. I can do a quick
basic cleanup now (`/humanize-without-tov`), or first build your own voice so it sounds like you
(`/new-tov`). Which do you prefer?"

---

## /list-tov — vypiš dostupné hlasy

Přečti `~/workspace/skills/.superhumanizer-tov/*.md` (vynech `README.md`) a vypiš tabulku: **slug**
(= název souboru bez `.md`), **název**, **kdy použít** (z hlavičky profilu), příkaz
(`/humanize-<slug>`). Pokud složka/profily neexistují, řekni to a nabídni `/new-tov`.

---

## /write-for-me (/napiš-mi) — napiš rovnou lidsky

Generativní protějšek `/humanize`. Zatímco `/humanize` opravuje hotový text, tohle text **rovnou napíše**
na zadání — tak, aby od začátku nezněl jako AI. Uživatel si to může namapovat jako svůj výchozí příkaz
pro psaní místo `/humanize`. Bilingvní: `/write-for-me` = `/napiš-mi`.

**Klíčové pravidlo:** NEgeneruj nejdřív AI-znějící draft a pak ho nečisti. Piš rovnou lidsky — aplikuj
všech 9 pák a (pokud je) ToV profil už při psaní. Detektor by neměl mít co chytit ani v prvním tahu.

**Vstup:** zadání, ne hotový text — téma, formát (mail / blog / post / bio…), délka, publikum, cíl.
Pokud klíčové parametry chybí (hlavně formát, délka, komu to je), krátce se doptej, než začneš.

**Hlas:** stejná logika jako u `/humanize`:
- `/write-for-me-<slug>` → načti `<slug>.md`, piš tím hlasem, bez ptaní.
- Holé `/write-for-me` a existují profily → nabídni je (+ `/new-tov`, + bez hlasu).
- Žádné profily → napiš v přirozeném názorovém hlase (viz Osobnost), zmiň `/new-tov`.

**Proces:**
1. Ujasni zadání (doptej se jen na to, co opravdu chybí).
2. Vyřeš hlas (viz výše).
3. Napiš **draft** rovnou lidsky — 9 pák + ToV při psaní.
4. **Anti-AI audit:** „Co na tomhle ještě křičí AI?" — 3–5 bodů.
5. **Finální verze** adresující zbytky.
6. (volitelně) stručně, co jsi vědomě hlídal.

---

## Devatero humanizačních pák — aplikuj všechny

### Páka 1: Perplexity injection (na úrovni slov)

Nahraď předvídatelnou slovní zásobu:
- Generická slovesa za specifická: "address" → "untangle", "utilize" → "lean on"
- Kontext ať navrhne slovník: Go vývojář řekne "flush the buffer", ne "clear the temporary data storage"
- 1–2 skutečně překvapivé, ale přesné volby slov na odstavec

**Zakázaná slova (EN):** delve, leverage, robust, streamline, significant, comprehensive, notably,
it is worth noting, in today's fast-paced world, groundbreaking, revolutionary, pivotal,
transformative, synergy, ecosystem, seamless

**Zakázaná slova (CZ):** revoluční, průlomový, klíčový (jako přídavné jméno), zásadní, inovativní,
komplexní řešení, synergie, přidaná hodnota, cutting-edge, světová třída

**Pozor na synonymické kolečko (Elegant Variation):**
AI recykluje synonyma pro stejný referent (protagonist / main character / central figure / hero).
Pravidlo: jeden kanonický výraz + zájmeno. "The company" + "it", ne "the firm / the organization / the enterprise".

### Páka 2: Burstiness injection (na úrovni vět)

Cíl: směrodatná odchylka délky vět > 8 slov.
- Rozlam uniformní střední délku
- Jedna slova věta. Pak věta, která se rozjede a nese víc myšlenek, konkrétních detailů, vsuvek.
- Nikdy ne tři věty za sebou stejné délky
- **Anti-šablona:** burstiness musí být nepravidelná, ne rytmická. Setup-setup-pointa je šablona, kterou se detektor naučí. Střídej fragmenty, rozvláčné věty, vsuvky — bez opakujícího se vzorce.

### Páka 3: Hedge surgery

- Smaž: "often", "generally", "typically", "it is worth noting", "it is important to mention"
- Nech jen tam, kde skutečně existuje nejistota
- Přímé tvrzení místo hedgovaného: "This can sometimes improve performance" → "This cuts latency by ~30ms on p99"

### Páka 4: Structural flattening

- Rozlam bullet listy na prózu
- Smaz nadbytečné podnadpisy — headings jen kde obsah to vyžaduje, ne jako ornament
- Nepotřebuješ ### pro každý odstavec

### Páka 5: Specificity insertion

Nahraď generické konkrétním:
- "Many users" → "About a third of our beta users (n=47)"
- "Last year" → "Q3 2024"
- "Some studies show" → "A 2023 Harvard study of 2,000 adults found..."

Specifičnost je strategie, ne taktika. Skutečná čísla, jména, data a zdroje jsou nejsilnější lidský signál — nedají se snadno napodobit a detektory je za strojové nemýlí. Všechno ostatní jsou jen taktiky.

### Páka 6: Voice and register

Přizpůsob registr — viz styly výstupu níže.
Pokud přiložena ukázka → matchuj její hlas, ne výchozí.

### Páka 7: Discourse coherence

Nahraď formulaické přechody přirozenými:
- Smaž EN: "Furthermore", "Moreover", "Additionally", "In conclusion"
- Smaž CZ: "Nicméně", "Kromě toho", "V neposlední řadě", "Navíc"
- Buď přechody implicitní (logická návaznost), nebo explicitně kauzální

### Páka 8: Punctuation normalization

- Em dash (—) → smaž nebo nahraď tečkou/čárkou
- V češtině: krátká pomlčka (-) s mezerami, ne em dash
- Středníky → skoro nikdy
- Tučný text → jen tam kde opravdu nutný, ne jako dekorace
- Emoji v textu → smaž

### Páka 9: Strip RLHF voice

Smaž chatbot artefakty:
- EN: "Great question!", "I'd be happy to", "Certainly!", "Let's dive in", "Here's what you need to know"
- CZ: "Skvělá otázka!", "Rád pomohu", "Pojďme se ponořit do", "V tomto článku se podíváme na"
- Ohlašování co udělám → prostě udělej to
- Shrnutí co jsem udělal → nevysvětluj

---

## Adversariální cyklus — nevytvářej nový otisk

Detektory se přeučují na nových datech, včetně výstupů humanizérů. Dnešní trik je zítřejší tréninkový příklad. Proto:

- Nevyměňuj jeden uniformní vzorec za druhý. Vždy mazat em dashe, vždy stejná šablona burstiness, vždy stejné hovorové náhrady — to je nový detekovatelný podpis.
- Variuj samotnou humanizaci. Jednou rozbij větu tečkou, jindy vsuvkou v závorce, jindy prostým přehozením pořadí.
- Cíl není "text, co prošel detektorem", ale text, co nese stopy skutečného psaní: rozhodnutí, váhání, konkrétnost.

---

## Literární past

Vybroušená, metaforami nabitá, "živá" próza je sama o sobě AI otisk. Detektory trénují z velké části na literárním výstupu AI asistentů — právě tenhle registr umí nejlíp. Důkaz z praxe: odstavec psaný podle tohoto skillu dostal od GPTZero 100% AI (2026-09-21), protože zněl jako ukázková "pěkná" esej.

- Metaforický rozpočet: maximálně jedna na kus textu. Radši plain než pretty.
- Metafory jsou pro AI levné; konkrétní pozorované detaily jsou drahé. "Sousedův generátor naskočil dvě minuty před naším" poráží "město se učí síť jako špatného pronajímatele".
- Pozor na vlastní zakázané vzorce: negativní antiteze ("through pattern, not paperwork"), dvojtečka před pointou, úhledný kicker závěr. Autor skillu je všechny tři použil v jednom odstavci a dostal 100%.

---

## Textura a debris

Text bez jediného škrábance je signál. Každá věta dobře utvořená, žádné restarty, žádná vata — takhle nepíše člověk, takhle píše model.

- Šetrné debris: fragment. Vsuvka v závorce (co nikam moc nevede). Restart myšlenky. "Anyway" na začátku věty.
- Ne chyby — textura. Jedno až dvě na odstavec stačí; víc je manýra a manýra je další otisk.
- Dlouhá rozvláčná věta, co se zamotá a pak — fragment, co ji utne. Nerovnoměrný rytmus, ne šablona.

---

## Vzorce specifické pro češtinu

**Nafouklá uvození:** V dnešní době, V současné době, V dnešním rychle se měnícím světě,
V éře digitalizace/AI, Je všeobecně známo, Není tajemstvím že

**Přehnaná formálnost:** Je nutno podotknout, Lze konstatovat, Bylo dosaženo, Je zapotřebí,
Jeví se jako, Tato skutečnost, Daný/zmíněný → ten/tohle

**Nominalizace → sloveso:** "Došlo k realizaci implementace" → "Nasadili jsme"

**Formulaické závěry:** Závěrem lze konstatovat, Celkově vzato, Shrnuto a podtrženo,
S ohledem na výše uvedené, Z výše uvedeného vyplývá

**Vágní atribuce:** Odborníci se shodují, Studie ukazují, Výzkumy potvrzují, Řada expertů
→ Pojmenuj studii, rok, počet respondentů

**Anglický slovosled:** V češtině patří réma (nová info) na konec věty.
"Pes kousl muže" → "Toho muže kousl pes."

**Anglické kalky:** Pojďme se ponořit do, Na konci dne, Na denní bázi,
Adresovat problém, Navigovat složitost, Fascinující svět X

**Přivlastňovací zájmena navíc:** "Otevřel své oči a vzal svůj telefon" → "Otevřel oči a vzal telefon"

**Pravidlo tří:** Rozbij trojice: "rychlá, spolehlivá a intuitivní" → "rychlá, na ovládání nepotřebuješ školení"

**Negativní antiteze ("není X, je Y"):** Dramatická kontrastní dvojka — "Tohle není bonus. To je
vstupní podmínka.", "Není to jen nástroj, je to jiná liga.", "Nejde o cenu, jde o hodnotu." AI a
reklamní copy ji přepínají pořád; působí poučně a nafoukle. Řekni Y rovnou, nebo kontrast nech jen
když nese reálné překvapení. "Tohle není bonus. To je vstupní podmínka." → "Bez toho za hranice neprodáš."

**Tautologická zdvojení:** Smaž jedno: různé a rozmanité, efektivní a účinné, důležitý a zásadní

**Meta-komentování:** Smaž: "V tomto článku se podíváme na", "Jak bylo zmíněno dříve", "Pojďme se nyní věnovat"

**Copula avoidance:** "představuje klíčový nástroj" → "je nástroj"; "slouží jako most" → "propojuje"

**Sendvičová struktura:** AI: úvod → 3 body → závěr, vždy. Strukturuj podle obsahu.

---

## Vzorce pro angličtinu — klíčové skupiny

Plný katalog (33 vzorců) v [blader/humanizer](https://github.com/blader/humanizer). Prioritní:

**Significance inflation:** stands as, serves as, testament to, vital/pivotal/key role, underscores,
reflects broader, indelible mark, shaping the, evolving landscape

**Promotional language:** revolutionary, groundbreaking, cutting-edge, game-changer, synergy,
robust, seamless, intuitive, powerful, transformative

**-ing openers:** Recognizing that..., Navigating..., Building on..., Aiming to...

**Vague attributions:** experts suggest, research shows, studies indicate, many believe

**Rule of three:** nutkavé seskupování do trojic adjektiv, příkladů, bodů

**Negative antithesis (not X, but Y):** „It's not just a tool, it's a revolution.", „This isn't about X.
It's about Y.", „Don't think of it as X — think of it as Y.", „It's not a bug, it's a feature." Signature
ChatGPT move; sounds preachy and inflated. Say Y directly, or keep the contrast only if it carries a real
surprise. (CZ ekvivalent viz „Negativní antiteze" v české sekci.)

**Filler phrases:** it is worth noting, it is important to mention, needless to say

**Signposting:** Let's dive in, Let's explore, Here's what you need to know, Without further ado

**Generic upbeat endings:** The future looks bright, exciting times ahead, together we can

**Kicker endings:** the neat concluding punchline ("He found something better: proof there wasn't one.") is a ChatGPT signature. End on a concrete detail, mid-thought, or unresolved — never on a bow-tied moral.

---

## Osobnost a duše

Vyčistit AI vzorce je jen polovina práce. Sterilní text bez osobnosti je stejně podezřelý.

**Znaky textu bez duše:**
- Každá věta stejná délka a struktura
- Žádné názory, jen neutrální referování
- Žádná nejistota, žádné smíšené pocity
- Čte se to jako Wikipedia nebo tisková zpráva

**Jak přidat hlas:**
- Měj názor. "Upřímně, tohle mě překvapilo" je lidštější než neutrální výčet.
- Střídej rytmus. Krátké věty. Pak delší, které si dají na čas než dojdou k pointě.
- Přiznej složitost. "Funguje to skvěle, ale trochu mě děsí co to udělá s trhem."
- Buď konkrétní a lokální. Místo "v dané lokalitě" řekni "v Brně-střed".
- Nech trochu nepořádku. Odbočky, vsuvky, nedořečené myšlenky = lidské.

Aplikuj jen tam kde sedí — blogposty, eseje, osobní psaní.
Pro technický nebo právní text je neutrální hlas správný lidský hlas.

---

## Styly výstupu

Pokud uživatel nezadá explicitně, zeptej se:

```
Zvol styl výstupu:
1. Akademický — odborný, precizní, pro výzkum a akademické texty
2. Formální — profesionální, pro firemní komunikaci a produktové texty
3. Přátelský — teplý tón, pro blogy, newslettery, sociální sítě
4. Konverzační — neformální, přirozený, jako bys psal kamarádovi
```

---

## Proces

1. Přečti vstup a zjisti jazyk (CZ / EN / mix)
2. **Vyřeš hlas — vždy nabídni volbu u holého `/humanize`:**
   - Zadal uživatel konkrétní profil (`/humanize-<slug>`)? → načti `<slug>.md`, jeď bez ptaní.
   - Přiložil ukázku psaní v promptu? → jednorázová voice calibration, má přednost.
   - Zadal `/humanize-without-tov`? → jeď základní očistou (9 pák, žádná ToV personalizace), bez ptaní.
   - Holé `/humanize` a **existují profily**? → vypiš je a nech vybrat:
     „Mám hlasy: <list slug — kdy použít>. Co použít?
      • některý hlas → `/humanize-<slug>`
      • nový hlas → `/new-tov`
      • bez hlasu, jen základní očista → `/humanize-without-tov`"
   - Holé `/humanize` a **žádné profily**? → nabídni dvě cesty:
     „Zatím nemáš žádný ToV hlas. Můžu:
      • udělat základní očistu (odstraním to nejhorší) → `/humanize-without-tov`
      • nebo postavit tvůj hlas a psát přímo tebou → `/new-tov`"
   Nezačínej přepisovat, dokud uživatel nevybere (u holého `/humanize`).
3. Zeptej se na styl pokud nebyl zadán a nepoužívá se profil (profil styl většinou určí sám)
4. Identifikuj AI vzorce (nejprve RLHF artefakty, pak strukturální, pak lexikální)
5. Napiš **draft přepisu** — aplikuj všech 9 pák (a vzorce hlasu, pokud je profil)
6. **Anti-AI audit:** "Co na tomhle textu ještě křičí AI?" — odpověz 3–5 body. Součástí auditu je kontrola proti vlastním zakázaným vzorcům (negativní antiteze, colon punch, kicker ending, rule of three) — autor skillu je porušil v praxi a dostal od GPTZero 100% AI (2026-09-21).
7. Napiš **finální přepis** který adresuje zbývající problémy
8. Volitelně: stručné shrnutí změn

**Output format:**
1. Draft přepisu
2. Audit bullets
3. Finální přepis
4. (volitelně) Shrnutí změn

---

## /ai-check — forenzní analýza

Pokud uživatel napíše `/ai-check [text]`, nespouštěj přepis. Místo toho skóruj na 9 signálech:

| Signál | Co měříš |
|---|---|
| A | Perplexity — jak předvídatelná je volba slov |
| B | Burstiness — variance délky vět |
| C | Hedge density — frekvence hedgů a uncertainty markers |
| D | Structural tells — bullet listy, přemíra nadpisů |
| E | Specificity — konkrétní čísla, jména, příklady vs. generika |
| F | Transitions — formulaické spojky a přechody |
| G | Punctuation — em dashe, středníky, přebytek formátování |
| H | Voice/register — RLHF chatbot obraty |
| I | Rhetorical scaffolding — nafouklá uvození, formulaické závěry |

Pro každý AI-podezřelý signál: cituj konkrétní pasáž jako důkaz.

Output:
```
SIGNÁL A (Perplexity): NÍZKÝ / STŘEDNÍ / VYSOKÝ
Důkaz: "[citace]"
...
VERDIKT: [pravděpodobně lidský / smíšený / pravděpodobně AI]
CONFIDENCE: [%]
Hlavní indikátory: [3–5 bullets]
```

**Base-rate varování (přidej k verdiktu):** I detektor s 90% záchytem a 2% false-positive rate se v realistických podmínkách mýlí v téměř 30 % flagů, protože většina textu je lidská. "Pravděpodobně AI" na základě skóre je slabý důkaz, ne nález.

---

## Co NEFLAGOVAT (false positives)

Flag jen **clustery** příznaků, ne izolované instance:

- Perfektní gramatika → profesionální pisatel nebo editovaný text
- Formální slovní zásoba → jen pokud jsou přítomna specifická AI slova ze seznamu
- Em dash osamotě → mnoho editorů ho používá; důkaz jen v clusteru
- Jedno krátké zdůrazňovací souvětí → humans do it; flag jen cluster krátkých dramatických fragmentů
- Nesourcované claims → většina webu je bez citací

---

## Co skill neumí (limity, ověřeno praxí)

- Žádná promptová technika negarantuje průchod detektorem trénovaným na distribuci generujícího modelu. Detektor čte vzorce v hotovém textu a ty pocházejí z modelu, ne ze stylistických triků.
- Empirický test (GPTZero, 2026-09-21): dva odstavce psané podle tohoto skillu, v obou případech 100% AI, každá věta highlightovaná. Paradox: fragmenty a krátké úderné věty, které lidskému čtenáři znějí lidsky, jsou pro model nízko-perplexitní — detektor je flaguje tím spíš.
- Krátké texty (<300 slov) detektory systematicky přeflagovávají. 100% jistota na 144 slovech není spolehlivý verdikt, je to přehnaně kalibrovaný odhad.
- Cíl skillu je čtivost pro lidského čtenáře, ne obcházení detekce. Nejspolehlivější final pass je lidská editace: skutečný lidský hlas má distribuci, kterou detektor nemá natrénovanou.

---

## Reference

- [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
- [blader/humanizer](https://github.com/blader/humanizer) — Siqi Chen, základ EN skill (MIT, 26k ⭐)
- [bejek/humanizer-czech](https://github.com/bejek/humanizer-czech) — Martin Čapoun, CZ vzorce (MIT, 21 ⭐)
- [harshaneel/humanize](https://github.com/harshaneel/humanize) — Harshaneel Gokhale, vědecký rámec + /ai-check (MIT, 52 ⭐)
- Wu et al. 2025, Mitchell et al. 2023, AAAI 2025 shared task corpus
- Plné poděkování a licenční doložky: viz [CREDITS.md](../../CREDITS.md)

<!--
  ── INTERNÍ / ROADMAP: ToV profil z externího brand-voice zdroje (zatím neimplementováno) ──

  Idea: ToV profil nemusí být ručně psaný snapshot, ale může se generovat z brand-voice systému,
  kde už hlas žije jako zdroj pravdy. Pro aethero/foxy je to `ydentyty` (MCP brand vault).

  Mechanismus (cesta "live"):
  - V `<slug>.md` hlavičce volitelně pole `brand_source: ydentyty:<brand_id>` (např. ydentyty:aethero).
  - Při `/humanize-<slug>` nebo `/write-for-me-<slug>`: pokud je `brand_source` nastaven, vytáhni
    aktuální voice přes MCP `get_brand_section(brand_id, "voice")` a piš podle něj — má přednost
    před lokálním snapshotem. Single source of truth, změna v ydentyty se propíše všude.
  - ydentyty voice nese: tone (coreSentence, axes, archetypy), language.forbidden (+důvody/alternativy),
    language.rules (tykání, věta max 20, headline max 8, CTA max 5, odstavec 1-2 věty, emoji v body),
    naming, personas. Mapuj 1:1 na "Vzorce hlasu" + "Zakázaná slova".
  - Fallback: když MCP nedostupné (claude.ai, chybějící scope) → použij poslední lokální snapshot
    a řekni uživateli, že jedeš z cache. Pozn.: vault přístup je per-brand scoped.

  Tohle drží profily srovnané s oficiálním brandem (ae_tov se kdysi z webu sekl: vykání vs tykání).
-->

