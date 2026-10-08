"""第二批 19 品牌主题（再约 304 条 look），写入 season_themes_2026-09 并刷新 index / README。"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "fashion_research_dir" / "season_themes_2026-09"

NEW = [
    {
        "house": "Tom Ford",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "tom_ford_ss27",
        "theme": "Sensual clarity: undress as sophistication, rose as a sharp accent",
        "design_target": (
            "Design a Tom Ford Spring/Summer 2027 collection under Haider Ackermann. "
            "Keep sexual, louche, slightly dangerous sophistication: leather, sheer, bottomless "
            "dressing, red roses on tailored pockets. Four chapters. Do not flatten into one safe suit."
        ),
        "description": """Heritage & provenance:
- Tom Ford house codes of sensual tailoring, leather, and night glamour.
- Haider Ackermann's unbuttoned choreography and self-regard on the runway.

Show / location context:
- Spring/Summer 2027, Paris, near-dark room with glass panes; models cruise their reflections.

Creative director intent:
- Sensual, sharp, no prudery. Less is more taken literally: trousers stripped away, underwear with sweaters.
- Red roses pinned to welt pockets as romantic danger, not soft decoration.

Silhouette & garment vocabulary:
- Satin bralettes with sheer midi or fluid maxi skirts. Black leather cocktail, logo-cut muscle tee.
- Military-green trenches and flysuits, distressed jeans and cargos, short shorts, red cutout gowns, tuxedos, barely-there swim.

Materials, craft & surface:
- Leather, sheer cloth, rhinestone, patent shoes. Exposure is engineered, not accidental.

Color, stripe & graphic codes:
- Black, red, white; cobalt, sky, army and kelly green as working neutrals.

Accessories & finishing:
- Minimal bags, oversize totes, embellished clutches. Rose brooches on blazers. Strappy heels and loafers.

Mood, liberation & wearer fantasy:
- Self-regard as power. The wearer is looked at and looks back.""",
    },
    {
        "house": "Chloé",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "chloe_ss27",
        "theme": "The Obsession Collection: instinctive Chloé archetypes returned through feeling",
        "design_target": (
            "Design a Chloé Summer 2027 Obsession Collection under Chemena Kamali. "
            "Lead with intuition and house obsessions: broderie anglaise, 1960s floral embroidery, "
            "1970s fishermen coats, vinyl rain sharpness, Noel jacket. Four chapters."
        ),
        "description": """Heritage & provenance:
- Chloé robes de jeunes filles, broderie anglaise, prêt-à-porter with couture faire.
- Chemena Kamali works from instinct and emotional resonance with the maison.

Show / location context:
- Summer 2027, Paris Fashion Week. The Obsession Collection as a personal return to loved Chloé codes.

Creative director intent:
- Liberate design by listening to obsessions. Explore archetypes with new nuance.
- Contradiction: soft embroidery against sharp vinyl rain layers.

Silhouette & garment vocabulary:
- Broderie anglaise from organza to heavy cotton. 3D floral embroidery. Fishermen coats and capes, sou'westers.
- Smoky transparent vinyl over 1970s outerwear. Sliced Noel jacket from 1972 memory.

Materials, craft & surface:
- Threadwork, embroidery, crisp cotton, organza, vinyl. Craft is the feeling, not a logo story.

Color, stripe & graphic codes:
- Soft Chloé tones broken by smoky vinyl graphics. Embroidery carries the print story.

Accessories & finishing:
- Hats and outerwear finish the silhouette. Keep bags secondary to the obsession of cloth and cut.

Mood, liberation & wearer fantasy:
- Forever Chloé through personal desire rather than trend.""",
    },
    {
        "house": "Alberta Ferretti",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "alberta_ferretti_ss27",
        "theme": "Échappée belle: a beautiful escape through movement, color, and fluid freedom",
        "design_target": (
            "Design an Alberta Ferretti Spring/Summer 2027 collection under Lorenzo Serafini. "
            "Hold échappée belle: 1920s bodily freedom, liquid fabrics, saturated sun-faded color, "
            "lingerie and kimono ease. Four chapters. Do not freeze into one red-carpet gown formula."
        ),
        "description": """Heritage & provenance:
- Alberta Ferretti femininity rewritten by Lorenzo Serafini through movement and escape.
- Echoes of Léon Bakst, Erté, Balanchine: clothes conceived around release, not restriction.

Show / location context:
- Spring/Summer 2027, Milan. A Beautiful Escape / échappée belle as dance and life rhythm.

Creative director intent:
- Imagination as a way to inhabit reality more instinctively. Private lingerie codes step outside.
- Mix prints turbulently, like Matisse compositions brought into daylight.

Silhouette & garment vocabulary:
- Slip dresses, lingerie details, kimono jackets, balloon trousers, fluid layers.
- Fringe and feather at hems that move. Layers stay light.

Materials, craft & surface:
- Mercurial satins, sheer textiles, featherweight surfaces, ikat and dissolving florals.

Color, stripe & graphic codes:
- Blue, teal, rust, mustard; ivory and black ground; lilac, pistachio, powder pink. Sun-faded intensity.

Accessories & finishing:
- Soft finishing that does not pin the body. Movement is the accessory.

Mood, liberation & wearer fantasy:
- Freedom to move between the world as it is and as she imagines it.""",
    },
    {
        "house": "Max Mara",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "max_mara_ss27",
        "theme": "Far Horizon: 1930s explorer utility rewritten as everyday utility luxe",
        "design_target": (
            "Design a Max Mara Spring/Summer 2027 Far Horizon collection. "
            "Anchor on safari jackets, cargo vests, convertible travel bags, organza overalls, "
            "and slouchy trenches as utility luxe for contemporary chaos. Four chapters."
        ),
        "description": """Heritage & provenance:
- Max Mara as engineered Italian outerwear and daywear. Ian Griffiths names the approach utility luxe.
- 1930s globe-trotting women (Osa Johnson, Earhart, Freya Stark) as spirit, not costume.

Show / location context:
- Spring/Summer 2027, Milan. Far Horizon turns travel paraphernalia into a modern wardrobe.

Creative director intent:
- Every piece engineered for chaotic contemporary life. Discover the extraordinary in the everyday.
- Utility through pockets, straps, convertible carry—not through costume khaki alone.

Silhouette & garment vocabulary:
- Safari jacket in textured linen and lustrous gabardine. Cargo vest over jacket.
- Organza overalls, voluminous low-belted trenches, high-waisted trousers and belted skirts, fine-gauge knit evening.

Materials, craft & surface:
- Linen, gabardine, organza, knit. Transparency softens workwear. Bags transform crossbody/clutch/rucksack.

Color, stripe & graphic codes:
- Travel neutrals and practical contrast. Color serves function and horizon light.

Accessories & finishing:
- Convertible bags and broad belts as structure. Keep jewelry quieter than pockets and straps.

Mood, liberation & wearer fantasy:
- A woman who carries explorer resolve into ordinary days.""",
    },
    {
        "house": "Ferragamo",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "ferragamo_ss27",
        "theme": "1940s utility archive made transparent, fetish-edged, and elegant",
        "design_target": (
            "Design a Ferragamo Spring/Summer 2027 collection under Maximilian Davis. "
            "Keep 1940s uniform/utility as skeleton, then open it with sheer silk-wool, chiffon, "
            "translucent rubber, cracked leather, and controlled python flash. Four chapters."
        ),
        "description": """Heritage & provenance:
- Salvatore Ferragamo archive and shoe invention. Maximilian Davis uses history as construction, not pastiche.
- Timeline moves from earlier speakeasy eras into 1940s uniform discipline.

Show / location context:
- Spring/Summer 2027, Triennale Milano. Opens held at the waist, then loosens.

Creative director intent:
- Archive sits deeper inside construction. Experiment around the skeleton: disappearance, sheerness, fetish polish.
- Good taste taken into hotter territory without losing elegance.

Silhouette & garment vocabulary:
- Bellows pockets on jackets and skirts. Safari vests framing the torso. Workwear leather proportions.
- Glossy translucent trenches and bodycon, evening via paillettes, wedges and architectural footwear.

Materials, craft & surface:
- Transparent silk-wool showing internal tailoring, chiffon utility, translucent rubber, cracked leather, python.

Color, stripe & graphic codes:
- Controlled flashes against disciplined utility grounds. Light and reflection for evening.

Accessories & finishing:
- Footwear carries invention. Belts and pocket architecture finish the uniform idea.

Mood, liberation & wearer fantasy:
- Held, then released. Utility becomes desire without costume.""",
    },
    {
        "house": "Schiaparelli",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "schiaparelli_ss27",
        "theme": "Going Clear: unsubscribe from noise; couture distilled into mixable separates",
        "design_target": (
            "Design a Schiaparelli Spring/Summer 2027 Going Clear collection under Daniel Roseberry. "
            "Distill couture into tops and bottoms the client combines; honor Elsa's playfulness with "
            "vegetable embroidery, ruffles, softened lines, Schiap jacket variants. Four chapters."
        ),
        "description": """Heritage & provenance:
- Elsa Schiaparelli's playfulness and Place Vendôme atelier memory (curtain ruffles).
- Daniel Roseberry after a digital detox: going clear as singular voice.

Show / location context:
- Spring/Summer 2027, Carrousel du Louvre basement as 1960s jazz-club mood (Barbra at the Bon Soir).

Creative director intent:
- Less noise, more singular intimacy. Ready-to-wear that reaches shops as a wardrobe the woman builds.
- Eight Schiap jackets; archival kingfisher, moss, salmon against black, bone, butter yellow.

Silhouette & garment vocabulary:
- Mix-and-match tops and bottoms. Leather and linen ruffles. Lettuce hems, asymmetric openings.
- Little black cocktail as revenge dressing. Softened graphic lines.

Materials, craft & surface:
- Vegetable embroidery, tree-bark texture revisiting Elsa techniques, transparency, playful jewelry animals.

Color, stripe & graphic codes:
- Neutrals as the combinatory system; archival color pops on jackets.

Accessories & finishing:
- Brass-handled bags, knitted-ball babouches, spirit-animal jewelry. Play without cluttering the clear voice.

Mood, liberation & wearer fantasy:
- Sidewalk as runway. Clarity as glamour.""",
    },
    {
        "house": "Stella McCartney",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "stella_mccartney_ss27",
        "theme": "Ocean polemic meets archival Stella cool: coral knits, fish-wire sculpture, denim ease",
        "design_target": (
            "Design a Stella McCartney Spring/Summer 2027 collection. "
            "Mix ocean-conservation messaging with archival silhouettes: technical drawstring tailoring, "
            "coraline knit whorls, fish-wire crinolines, airbrushed dolphins, North Kensington denim cool. Four chapters."
        ),
        "description": """Heritage & provenance:
- Stella McCartney's vegetarian luxury, cool London girl origins, and recurring ocean activism.
- Archival silhouettes and castings return as house memory.

Show / location context:
- Spring/Summer 2027 with David Attenborough ocean commentary as ethical pressure, not backdrop only.

Creative director intent:
- Polemic and wardrobe together. Technical tailoring stays loose and cool; evening can be Grecian and Splash-like.
- Denim trucker over basketball shorts as origin story, not irony alone.

Silhouette & garment vocabulary:
- Drawstring-waist tailoring. Knit skirts, dresses, bustiers of furled panels. Fish-wire crinoline hems and oyster forms.
- Airbrushed dolphins on jersey and denim. Sculpted peplums and architectural bodices in washed pastels.

Materials, craft & surface:
- Technical cloth, sculptural knit, fish wire, denim, jersey. Surface carries ocean without becoming costume only.

Color, stripe & graphic codes:
- Washed pastels, denim mixes, dolphin graphics. Color serves water and archive, not neon activism kitsch.

Accessories & finishing:
- Skater trainers and house footwear that keep the look grounded. Avoid plastic slogan overload.

Mood, liberation & wearer fantasy:
- Cool-girl ease with a moral horizon.""",
    },
    {
        "house": "Tod's",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "tods_ss27",
        "theme": "Italian Attitude: lightweight leather, color-block play, Candy Bag return",
        "design_target": (
            "Design a Tod's Spring/Summer 2027 Italian Attitude collection. "
            "Root in effortless Italian elegance with playful 1970s energy: perforated leather trenches, "
            "capris, bermudas, safari jackets, Candy Bag. Four chapters."
        ),
        "description": """Heritage & provenance:
- Tod's Italian leather craft and driving-shoe ease. Ready-to-wear as attitude, not only accessory house.

Show / location context:
- Spring/Summer 2027. Italian Attitude through new proportions and the Candy Bag's return.

Creative director intent:
- Effortless elegance with more play. Color blocking as Italian code. Outerwear as the statement.

Silhouette & garment vocabulary:
- Capris and bermuda shorts. Perforated leather, Nappa, Windsilk trenches. Safari jackets, belted pieces, shirt jackets.
- Structured coats and laid-back bottoms in one wardrobe.

Materials, craft & surface:
- Lightweight leathers, perforated skins, precise outerwear cloth. Candy Bag as soft structure.

Color, stripe & graphic codes:
- Mustard, orange, red against navy, white, brown. Contrast gives energy without noise.

Accessories & finishing:
- Candy Bag and leather shoes as house anchors. Belts finish the Italian silhouette.

Mood, liberation & wearer fantasy:
- Italian ease you can actually wear in heat and motion.""",
    },
    {
        "house": "Khaite",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "khaite_ss27",
        "theme": "Romance under the skin: tenth-anniversary corsetry, lace creatures, historical bounce",
        "design_target": (
            "Design a Khaite Spring/Summer 2027 collection for the house's tenth anniversary. "
            "Pull volume closer to the body; expose corsetry; mix black leather severity with Venice light, "
            "horsehair evening bounce, floral embroidery, antique lingerie tones. Four chapters."
        ),
        "description": """Heritage & provenance:
- Catherine Holstein's decade of New York commercial power dressing. Spring 2027 widens into poetry and mess.
- Venice atmosphere: brass, cream, celadon; Gibson Girl and punk-undone hair blur.

Show / location context:
- Spring/Summer 2027, Brooklyn Storehouse, near-dark opening with hard spotlight and PJ Harvey.

Creative director intent:
- Romance through color, texture, proportion, movement. Volume relocated closer to the body.
- Leather remains the New York anchor while lace and lingerie tones soften the decade.

Silhouette & garment vocabulary:
- Sculptural bra with high-waisted leather skirt; open corsetry on the back.
- Horsehair-trimmed evening pieces, mousseline blur, floral embroidery, historical volume that bounces.

Materials, craft & surface:
- Black leather, lace, sheer pale cloth, horsehair, dense hand embroidery.

Color, stripe & graphic codes:
- Black, ecru, white; brass, cream, celadon lingerie tones.

Accessories & finishing:
- Corsetry and embroidery are the jewelry. Keep bags secondary to body architecture.

Mood, liberation & wearer fantasy:
- Poetic, whimsical, messy—still Khaite power.""",
    },
    {
        "house": "Ralph Lauren",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "ralph_lauren_ss27",
        "theme": "Irreverent romance: navy-and-white American sportswear remixed with character",
        "design_target": (
            "Design a Ralph Lauren Spring/Summer 2027 collection. "
            "Irreverent romance and personal style: navy/white sportswear, brocade vest with wide necktie, "
            "soft and sharp tailoring, seersucker, feathered denim, low-cut evening. Four chapters."
        ),
        "description": """Heritage & provenance:
- Ralph Lauren American sportswear, the necktie origin myth, Italian-facility women's suits.
- Archival codes remixed for 2027 character rather than museum polish.

Show / location context:
- Spring/Summer 2027, Jack Shainman Gallery, New York. Glamour with sportswear ease.

Creative director intent:
- Celebrate ingenuity and originality. Romance without solemnity. Personality over perfection.

Silhouette & garment vocabulary:
- White corset with trousers. Brocade vest, full-sleeved shirt, jeans, wide necktie.
- Sharp and fluid suits, smocked leather jacket, seersucker, feather-accent denim, low-cut evening backs.

Materials, craft & surface:
- Brocade, seersucker, leather, denim, floral and brocade pops on navy/white ground.

Color, stripe & graphic codes:
- Predominantly navy and white with floral/brocade interruptions.

Accessories & finishing:
- The wide necktie as house memory. Keep jewelry quieter than the American silhouette story.

Mood, liberation & wearer fantasy:
- Freedom and fun of a style that is truly personal.""",
    },
    {
        "house": "Jacquemus",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "jacquemus_ss27",
        "theme": "Le Bonheur: seaside bonheur in turquoise, rust, sheer organza, and bare ease",
        "design_target": (
            "Design a Jacquemus Spring/Summer 2027 Le Bonheur collection. "
            "Seaside ease: turquoise and rust, sheer organza, bra-top-and-skirt sets, sculptural sun "
            "proportions, ballet flats. Four chapters. Do not collapse into one micro-bag gag."
        ),
        "description": """Heritage & provenance:
- Simon Porte Jacquemus's South-of-France sensuality, sun architecture, and playful proportion.
- Happiness as a design brief rather than a slogan print.

Show / location context:
- Spring/Summer 2027 seaside fantasy translated into ready-to-wear heat and light.

Creative director intent:
- Bonheur through cut and color: bare ease without costume vacation kitsch.
- Sheer and structured sun shapes share one wardrobe.

Silhouette & garment vocabulary:
- Bra-top and skirt sets, sheer organza layers, sculpted shoulders and hips for sun architecture.
- Easy trousers and dresses that move with heat.

Materials, craft & surface:
- Organza, light cottons, sun-struck surfaces. Minimal hardware.

Color, stripe & graphic codes:
- Turquoise, rust, sun neutrals. Color is the landscape.

Accessories & finishing:
- Ballet flats and house bags kept secondary to the body-and-sun sentence.

Mood, liberation & wearer fantasy:
- Happiness as lightness you can wear.""",
    },
    {
        "house": "Proenza Schouler",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "proenza_schouler_ss27",
        "theme": "Softer New York: craft, color, and the PS1 returned to a redefined city wardrobe",
        "design_target": (
            "Design a Proenza Schouler Spring/Summer 2027 collection. "
            "Redefine New York through softer silhouettes, bold color, visible craft, animal/rose motifs, "
            "and the PS1's return. Four chapters."
        ),
        "description": """Heritage & provenance:
- Proenza Schouler as New York intellectual sportswear and the PS1 bag icon.
- Softening of the city's hard edge without losing craft intelligence.

Show / location context:
- Spring/Summer 2027 New York. Softer silhouettes and bright color rewrite the house's urban code.

Creative director intent:
- Visible craft and motif work as identity. Softness is a redesign of New York, not surrender.

Silhouette & garment vocabulary:
- Cowling, softer tailoring, dresses and separates that drape rather than armor.
- Animal and rose motifs worked into cloth rather than stuck on.

Materials, craft & surface:
- Hand-touched surfaces, color-blocked cloth, craft joins that remain visible.

Color, stripe & graphic codes:
- Bold color against New York black/neutral memory. Motifs are graphic, not cute.

Accessories & finishing:
- PS1 return as house punctuation. Keep other hardware quiet.

Mood, liberation & wearer fantasy:
- A New York wardrobe that can breathe.""",
    },
    {
        "house": "The Row",
        "season": "Fall/Winter 2026",
        "status": "latest_completed",
        "dir": "the_row_fw26",
        "theme": "Quiet architecture: oversized coats, wide-leg pants, black/white/chocolate calm",
        "design_target": (
            "Design a The Row Fall/Winter 2026 collection. "
            "Preserve quiet luxury as architecture: oversized coats, tailored and wide-leg pants, "
            "black/white/chocolate palette, no logo noise. Four chapters of distinct proportion."
        ),
        "description": """Heritage & provenance:
- The Row as Mary-Kate and Ashley Olsen's discipline of proportion, cloth, and silence.
- Luxury as reduction and fit, not announcement.

Show / location context:
- Fall/Winter 2026. A controlled wardrobe of coats and trousers as the season's grammar.

Creative director intent:
- Architecture through volume and fall of cloth. Distinction by cut, not by print story.

Silhouette & garment vocabulary:
- Oversized coats, tailored pants, wide-leg pants, long clean lines, minimal fastening drama.

Materials, craft & surface:
- Dense wools, fluid trousers cloth, matte surfaces. No distressed costume.

Color, stripe & graphic codes:
- Black, white, chocolate. Near-monochrome blocks.

Accessories & finishing:
- Quiet bags and shoes. Nothing louder than the coat's shoulder.

Mood, liberation & wearer fantasy:
- Calm authority. The wearer disappears into exactness.""",
    },
    {
        "house": "Brunello Cucinelli",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "brunello_cucinelli_ss27",
        "theme": "Humanist leisure luxury: sun-washed knits, soft tailoring, Solomeo ease",
        "design_target": (
            "Design a Brunello Cucinelli Spring/Summer 2027 collection. "
            "Humanist quiet luxury: cashmere and knit ease, soft tailoring, sun-washed neutrals, "
            "no aggressive logo. Four chapters."
        ),
        "description": """Heritage & provenance:
- Brunello Cucinelli's Solomeo humanist luxury: craft dignity, soft power, cashmere culture.

Show / location context:
- Spring/Summer 2027 leisure wardrobe as elevated everyday rather than resort costume.

Creative director intent:
- Comfort as ethics of beauty. Soft structure, never loud branding.

Silhouette & garment vocabulary:
- Soft blazers, knit polos and trousers, long cardigans, easy dresses, light outer layers.

Materials, craft & surface:
- Cashmere, cotton knits, suede accents, hand-finished edges.

Color, stripe & graphic codes:
- Sun-washed sand, cream, soft olive, sky. Quiet contrasts only.

Accessories & finishing:
- Soft leather shoes and bags. Metal kept matte and minimal.

Mood, liberation & wearer fantasy:
- Wealth as ease and attention, not display.""",
    },
    {
        "house": "Missoni",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "missoni_ss27",
        "theme": "Zigzag living: knit geometry loosened into resort movement and color heat",
        "design_target": (
            "Design a Missoni Spring/Summer 2027 collection. "
            "Keep zigzag and knit geometry as house DNA, then loosen into resort movement, "
            "swim-to-evening continuity, and color heat. Four chapters."
        ),
        "description": """Heritage & provenance:
- Missoni family knit modernism: zigzag, space-dye, colorful intellectual leisure.

Show / location context:
- Spring/Summer 2027. Knit house codes for heat, travel, and evening without abandoning geometry.

Creative director intent:
- Pattern as structure. Loosen without losing the Missoni wave.

Silhouette & garment vocabulary:
- Knit dresses and trousers, open cardigan coats, swim pieces that share yarn language with evening.
- Soft flares and columns built from knit panels.

Materials, craft & surface:
- Knit, crochet, light woven companions. Surface is the identity.

Color, stripe & graphic codes:
- Multicolor zigzag and space-dye. Color is architecture.

Accessories & finishing:
- Soft bags; avoid hard logo hardware competing with yarn.

Mood, liberation & wearer fantasy:
- Holiday intelligence—playful, never silly.""",
    },
    {
        "house": "Rick Owens",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "rick_owens_ss27",
        "theme": "Brutal glamour: elongated darkness, body armor, and ceremonial ease in heat",
        "design_target": (
            "Design a Rick Owens Spring/Summer 2027 collection. "
            "Keep brutal glamour: elongated silhouettes, drapes, leather armor, ceremonial platforms, "
            "heat-adapted darkness. Four chapters. Do not soften into generic goth."
        ),
        "description": """Heritage & provenance:
- Rick Owens's American-in-Paris brutalism: glamour through severity, drop-crotch memory, architectural drapery.

Show / location context:
- Spring/Summer 2027. Heat forces lighter armor without losing ceremonial gravity.

Creative director intent:
- Darkness as elegance. Body as sculptural site. Ease is still confrontational.

Silhouette & garment vocabulary:
- Long coats and capes, wrapped dresses, leather panels, elongated trousers, exposed structure.
- Platforms and geometric footwear extending the line.

Materials, craft & surface:
- Leather, washed cottons, technical sheers, matte metals.

Color, stripe & graphic codes:
- Black, dust, bone, occasional acid flare. Graphic is silhouette, not print.

Accessories & finishing:
- Geometric bags and jewelry as armor fragments.

Mood, liberation & wearer fantasy:
- Ceremony for everyday outsiders.""",
    },
    {
        "house": "Acne Studios",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "acne_studios_ss27",
        "theme": "Stockholm irony softened: denim, twisted tailoring, and art-school romance",
        "design_target": (
            "Design an Acne Studios Spring/Summer 2027 collection. "
            "Stockholm house codes: denim intelligence, twisted tailoring, art-school romance, "
            "dry humor in proportion. Four chapters."
        ),
        "description": """Heritage & provenance:
- Acne Studios as Scandinavian fashion with art-world adjacency and denim authority.

Show / location context:
- Spring/Summer 2027. Irony and romance share one wardrobe without meme styling.

Creative director intent:
- Twist familiar garments. Denim and suiting speak the same dry language.

Silhouette & garment vocabulary:
- Twisted blazers, elongated denim, soft dresses with awkward elegance, layered shirting.
- Proportions slightly wrong on purpose.

Materials, craft & surface:
- Denim, wool, washed silk, matte leather. Surface stays honest.

Color, stripe & graphic codes:
- Indigo, black, dusty pink, pale yellow. Graphics rare and dry.

Accessories & finishing:
- House boots and bags with understatement. Avoid loud logo comedy.

Mood, liberation & wearer fantasy:
- Cool without trying; romance without sugar.""",
    },
    {
        "house": "Diesel",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "diesel_ss27",
        "theme": "Denim provocation: destroyed luxury, body exposure, and club-workwear clash",
        "design_target": (
            "Design a Diesel Spring/Summer 2027 collection. "
            "Glenn Martens-era provocation: destroyed and reconstructed denim, sexy exposure, "
            "workwear/club clash, logo as texture. Four chapters."
        ),
        "description": """Heritage & provenance:
- Diesel as denim laboratory and youth provocation under Glenn Martens's reconstruction logic.

Show / location context:
- Spring/Summer 2027. Denim still the grammar; luxury is in destruction and rebuild.

Creative director intent:
- Clash elegance and grit. Exposure is design. Logo can be texture, not billboard alone.

Silhouette & garment vocabulary:
- Reconstructed jeans, cutaway tops, industrial outerwear, body-baring evening denim hybrids.
- Layers that look unfinished on purpose.

Materials, craft & surface:
- Destroyed denim, metal hardware, washed leather, sheer inserts.

Color, stripe & graphic codes:
- Indigo spectrum, black, acid wash, sudden brights. Graphics feel stamped and worn.

Accessories & finishing:
- Heavy hardware, belts, boots. Finish should look used.

Mood, liberation & wearer fantasy:
- Club after work, work after club—same clothes survive both.""",
    },
    {
        "house": "Moschino",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "moschino_ss27",
        "theme": "Wit as wardrobe: trompe-l'œil, cartoon glamour, and sharp Italian irony",
        "design_target": (
            "Design a Moschino Spring/Summer 2027 collection. "
            "Keep house wit: trompe-l'œil, cartoon-luxe, ironic tailoring, heart and smile codes "
            "made wearable rather than costume-only. Four chapters."
        ),
        "description": """Heritage & provenance:
- Franco Moschino's irony and Adrian Appiolaza-era wit: fashion that winks without abandoning cut.

Show / location context:
- Spring/Summer 2027. Humor as method for Italian glamour, not only gag props.

Creative director intent:
- Trompe-l'œil and graphic play that still reads as clothes. Irony with sharp tailoring underneath.

Silhouette & garment vocabulary:
- Tailored jackets with illusion details, dress-as-joke that remains a dress, heart motifs as structure.
- Clean skirts and trousers carrying the punchline in cloth, not only props.

Materials, craft & surface:
- Tailoring cloth, printed trompe-l'œil, playful embroidery, patent accents.

Color, stripe & graphic codes:
- Black, white, red hearts, cartoon brights used surgically.

Accessories & finishing:
- Statement but finishable bags and shoes. Wit should not prevent walking.

Mood, liberation & wearer fantasy:
- Glamour that laughs and still looks expensive.""",
    },
]


def _write_brand(row: dict) -> None:
    d = BASE / row["dir"]
    d.mkdir(parents=True, exist_ok=True)
    (d / "theme.txt").write_text(row["theme"].rstrip() + "\n", encoding="utf-8")
    (d / "design_target.txt").write_text(row["design_target"].rstrip() + "\n", encoding="utf-8")
    (d / "description.txt").write_text(row["description"].rstrip() + "\n", encoding="utf-8")


def main() -> None:
    index_path = BASE / "index.json"
    payload = json.loads(index_path.read_text(encoding="utf-8"))
    existing = {str(r.get("dir")) for r in payload.get("collections") or []}
    added = []
    for row in NEW:
        _write_brand(row)
        if row["dir"] not in existing:
            payload.setdefault("collections", []).append(
                {
                    "house": row["house"],
                    "season": row["season"],
                    "status": row["status"],
                    "dir": row["dir"],
                    "theme": row["theme"],
                    "description": row["description"].rstrip(),
                }
            )
            added.append(row["dir"])
        else:
            for rec in payload["collections"]:
                if rec.get("dir") == row["dir"]:
                    rec.update(
                        {
                            "house": row["house"],
                            "season": row["season"],
                            "status": row["status"],
                            "theme": row["theme"],
                            "description": row["description"].rstrip(),
                        }
                    )
    payload["note"] = (
        "Batch1+Batch2 luxury themes for workflow generation. "
        "Each collection: 4 chapters × 4 looks. gpt-5.4-mini keep-on-gate-fail runs write under generated_gpt54mini_keep/."
    )
    index_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# 大牌主题语料（Batch1 + Batch2）",
        "",
        "每个品牌目录对应一次 `FashionWorkflow` 输入，默认 4 章节 × 4 look。",
        "",
        "- `design_target.txt` / `theme.txt` / `description.txt`",
        "- 生成输出：`generated_gpt54mini_keep/`",
        "",
        "| 目录 | 品牌 | 季度 | 主题 |",
        "| --- | --- | --- | --- |",
    ]
    for rec in payload["collections"]:
        lines.append(f"| {rec['dir']} | {rec['house']} | {rec['season']} | {rec['theme']} |")
    (BASE / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    n = len(payload["collections"])
    print(
        json.dumps(
            {
                "collections": n,
                "added": added,
                "looks_if_4x4": n * 16,
                "new_looks_if_4x4": len(added) * 16,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
