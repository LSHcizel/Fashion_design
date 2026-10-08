"""补齐 season_themes 品牌目录至 19 家（4×4×19≈304），并刷新 index / README。"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "fashion_research_dir" / "season_themes_2026-09"

# 新增 10 家；已有 9 家保持不动。
NEW = [
    {
        "house": "Balenciaga",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "balenciaga_ss27",
        "theme": "Unsized featherweight couture that still reads as everyday wardrobe",
        "design_target": (
            "Design a Balenciaga Spring/Summer 2027 womenswear collection. "
            "Keep Pierpaolo Piccioli's Balenciaga: couture relevance for the street, "
            "featherweight engineered cloth, and archetypes that move with real life. "
            "Four chapters. Do not flatten into one oversized logo wardrobe."
        ),
        "description": """Heritage & provenance:
- Cristóbal Balenciaga's balloon, drape, and cocoon as house memory.
- Pierpaolo Piccioli treats engineered materiality as invention, not decoration.

Show / location context:
- Spring/Summer 2027. Lookbook tension between the couture salon and the street at 10 avenue George V.

Creative director intent:
- Couture can be relevant to everyday life. Unsized garments are pure expressions of cloth.
- Entire ensembles can weigh less than a kilogram. Silhouette comes from cloth against the body.
- Jeans under evening, techwear beside tailoring. Typologies blur without costume.

Silhouette & garment vocabulary:
- Subtle, reduced layers. Shirts given evening trains; gowns taking the attitude of a T-shirt.
- Balloon, drape, cocoon re-engineered for modern life. Poplin, double cashmere, kid mohair, washed denim.

Materials, craft & surface:
- Featherweight techno taffeta. Soft washed leathers for Le City and ultralight nappa for Rodeo.
- Jewelry holds volume against form. Shoes deconstructed toward essential malleability.

Color, stripe & graphic codes:
- Cloth and movement lead. Color serves the archetype rather than a logo story.

Accessories & finishing:
- Soft, pliable bags and shoes that reconsider house icons without hardening into plaques.

Mood, liberation & wearer fantasy:
- Liberation as lightness and kinetic ease. The wearer crosses salon and street in one wardrobe.""",
    },
    {
        "house": "Loewe",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "loewe_ss27",
        "theme": "Ease and presence: color-block pragmatism meeting Spanish Baroque",
        "design_target": (
            "Design a Loewe Spring/Summer 2027 collection under Jack McCollough and Lazaro Hernandez. "
            "Ground the wardrobe in physicality—cloth against skin—while letting Spanish Baroque "
            "and American youth archetypes share the house. Four chapters. Do not flatten into one Puzzle-bag formula."
        ),
        "description": """Heritage & provenance:
- Loewe as Spanish leather house. The 1960 suede blazer as an early garment memory.
- Jack McCollough and Lazaro Hernandez bring American youth codes into the maison.

Show / location context:
- Spring/Summer 2027, titled around ease and presence. Clothes shaped by how the wearer lives and breathes.

Creative director intent:
- Color block meets Spanish Baroque. Pragmatism nods to drama.
- Feminine and masculine wardrobe grounded in sensation and real-life rhythm.
- Autobiography is the anchor for audacity.

Silhouette & garment vocabulary:
- Polos cut and worn backwards. Basketball jersey shaping a chiffon bead-fringed slip.
- Silk anoraks against skin. Taleguilla pants with satin scarves. Ample shirt dresses. Abbreviated nappa trapeze dresses.
- Striped jackets, glass-bead woven skirts and dresses.

Materials, craft & surface:
- Celebrated nappa, suede, silk, glass beads. Sunglass-resin collars. Soft leather icons: Pasito, Puzzle Charm.

Color, stripe & graphic codes:
- Vivid to faded patina and bleached hues. Spanish influence in color, not a tourist print.

Accessories & finishing:
- Pasito and Puzzle Charm join leatherwork icons. Silk ties as souvenirs of the house past.

Mood, liberation & wearer fantasy:
- Presence without stiffness. The wearer keeps stylistic audacity inside a lived wardrobe.""",
    },
    {
        "house": "Burberry",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "burberry_ss27",
        "theme": "Rumpled British polish: gabardine loosened by Birtwell florals and touched texture",
        "design_target": (
            "Design a Burberry Spring/Summer 2027 womenswear collection under Daniel Lee. "
            "Keep the trench and check as house grammar, then loosen hyper-controlled gabardine "
            "with rumple, Celia Birtwell florals, and youthful subversion. Four chapters. "
            "Do not reduce the season to one polished trench lookbook."
        ),
        "description": """Heritage & provenance:
- Burberry gabardine, trench, and check as national polish.
- Celia Birtwell florals enter as a youthful subversion, echoing Bailey-era Hockney color memory.

Show / location context:
- Spring/Summer 2027, London/Paris circuit. A white blank-canvas space lets texture and color carry the story.

Creative director intent:
- Loosen self-possession without abandoning the house. Rumple is confidence, not carelessness.
- Expand beyond trench-only focus into a broader British wardrobe with climbing and seaside energy.

Silhouette & garment vocabulary:
- Taffeta shirts and shorts embroidered with Birtwell florals. Taffeta trenches with puffed hems.
- Washed pink, taupe, and black denim. Technical parkas beside chiffon gowns.
- Strapped clogs and climbing moccasins under both tech and evening.

Materials, craft & surface:
- Rumpled taffeta, touched denim, gabardine that can crease. Check reimagined as a trellis for florals.
- 3D badges and beaded embellishments grown from doodled faces and florals.

Color, stripe & graphic codes:
- Swimming-pool blue, sunset orange, richly colored floral arrangements on the check trellis.

Accessories & finishing:
- Smudged vulcanized sneaker soles, clogs, climbing moccasins. Embellishment belongs to the cloth story.

Mood, liberation & wearer fantasy:
- British polish that has been lived in. Youthful without costume.""",
    },
    {
        "house": "Miu Miu",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "miu_miu_ss27",
        "theme": "In the moment: sportswear lifted into a different elegance",
        "design_target": (
            "Design a Miu Miu Spring/Summer 2027 womenswear collection. "
            "Start from everyday sportswear and normal elements, then lift them into Miu Miu elegance "
            "with crystal, retro print, and mismatched ease. Four chapters. "
            "Do not flatten into one mini-skirt formula."
        ),
        "description": """Heritage & provenance:
- Miuccia Prada's Miu Miu as the house of wrongness made charming: sport, school, crystal, thrift.
- Collaboration codes with New Balance and upcycled Wrangler jeans enter as wardrobe facts.

Show / location context:
- Spring/Summer 2027, Paris. Fast, propulsive energy. Clothes for people dressing now.

Creative director intent:
- Work for people in this time. See everyone in sportswear, then bring elegance to the sport.
- Normal elements: jeans, tiny running shorts, drawstring bows, checked knee-length skirts.

Silhouette & garment vocabulary:
- Box-pleated knee-length checked skirts with hunting blazers or sporty cropped tops.
- Jeans and running shorts with '60s-print blouses. Babydoll minis with crystal-encrusted panels.
- White drawstrings tied at the waist as if from retro shorts.

Materials, craft & surface:
- Crystal panels, A-line skirts, upcycled denim, sneaker-lace belts and cross-lacing over jean flies.

Color, stripe & graphic codes:
- Retro prints, checks, sport neutrals broken by crystal glint. Color is play, not a solemn code.

Accessories & finishing:
- New Balance trainers, lace used as belt or fly lacing. Crystal is the jewelry story on the garment.

Mood, liberation & wearer fantasy:
- Casual everyday with a lifted elegance. Fun is a design decision.""",
    },
    {
        "house": "Celine",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "celine_ss27",
        "theme": "Quiet minimal satin: black, white, and almond tailoring worn as presence",
        "design_target": (
            "Design a Celine Spring/Summer 2027 womenswear collection. "
            "Keep minimalist satin and tailored pants as the core grammar in black, white, and almond. "
            "Four chapters of quiet luxury with distinct cuts. Do not invent loud logo theatrics."
        ),
        "description": """Heritage & provenance:
- Celine as a house of precise Parisian minimalism and long-line ease.
- Quiet luxury read as cut and cloth, not as a slogan.

Show / location context:
- Spring/Summer 2027, Paris. A controlled ready-to-wear lineup of about sixty looks.

Creative director intent:
- Minimalist presence through satin and tailored pants. Monochrome is a discipline.
- Reduce noise so proportion, drape, and the fall of cloth become the identity.

Silhouette & garment vocabulary:
- Tailored pants, side-pocket pants, barrel pants. Satin separates and long clean lines.
- Soft shoulders, controlled waists, trousers that carry the look without ornament.

Materials, craft & surface:
- Satin as the main surface. Tailoring cloth beside fluid sheen. No distressed costume.

Color, stripe & graphic codes:
- Black, white, almond. Monochrome and near-monochrome blocks.

Accessories & finishing:
- Quiet finishing. Bags and shoes should not overpower the satin/tailoring sentence.

Mood, liberation & wearer fantasy:
- Confidence without display. The wearer is present because the cut is exact.""",
    },
    {
        "house": "Valentino",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "valentino_ss27",
        "theme": "Antibiblioteca: unread clothes as a catalogue of still-possible lives",
        "design_target": (
            "Design a Valentino Spring/Summer 2027 womenswear collection under Alessandro Michele. "
            "Hold Antibiblioteca: unworn or unread garments as spaces of possibility, while syncing "
            "Valentino glamour with Michele's eclectic freedom. Four chapters. "
            "Do not collapse into one maximalist costume dump."
        ),
        "description": """Heritage & provenance:
- Valentino Garavani's glamour, elegance, and perfectionism.
- Alessandro Michele's eclectic language seeking the house essence with more with less.

Show / location context:
- Spring/Summer 2027, Antibiblioteca, at Bibliothèque Sainte-Geneviève, Paris. Guests brought books to donate.

Creative director intent:
- Unread books / unworn clothes as presence of what we still do not know.
- Translate beautiful things with freedom to make the look. Evening can be ornate or a minimal column with a train.

Silhouette & garment vocabulary:
- Jewel-toned satin bustiers with knee-length skirts, feathers, pleats, or embroidery.
- Lace biker shorts under longline blazer dresses. Checked shirts into sheer party skirts.
- Minimal satin columns, black velvet plunges, Villain Teen caps, romantic trains.

Materials, craft & surface:
- Satin, lace, brocade, ruched taffeta, rhinestone, feather, fringe, mohair, sequined boots.

Color, stripe & graphic codes:
- Tutti-frutti and jewel tones beside black. Mismatch is intentional storytelling.

Accessories & finishing:
- Stacked gold and pearl necklaces, boater hats, magenta gloves, character caps.

Mood, liberation & wearer fantasy:
- Expand the imaginable. Clothes can inhabit a life even before they are worn daily.""",
    },
    {
        "house": "Givenchy",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "givenchy_ss27",
        "theme": "Balance of Power: precise simplicity when the world is off-kilter",
        "design_target": (
            "Design a Givenchy Spring/Summer 2027 womenswear collection under Sarah Burton. "
            "Seek balance through precision cutting and streamlined proportion—a thinking woman's toolkit. "
            "Four chapters. Do not dissolve construction into pure cocooning."
        ),
        "description": """Heritage & provenance:
- Hubert de Givenchy's fierce black tailoring and graphic prints; Hitchcock women who are not classical beauties.
- Sarah Burton seeks clarity and today's vernacular for that severity.

Show / location context:
- Spring/Summer 2027, Paris. A response to collapse of order through structure rather than surrender.

Creative director intent:
- In a world off-kilter, find balance in precise simplicity.
- Power-shoulder coats, leather dresses with peel-away necklines, tank tops and leather pants as agency.

Silhouette & garment vocabulary:
- Suit jackets sliced open at the sides, fronts tilting forward; sleeves chopped and reattached as protective embrace.
- Streamlined coats, romantic leather dresses, no-nonsense separates.

Materials, craft & surface:
- Tailoring cloth, leather, clean knits. Colorful leather goods including the Cut zippered hobo.

Color, stripe & graphic codes:
- Black as the thinking spine; graphic print used with Hitchcock restraint, not carnival.

Accessories & finishing:
- The Cut bag and leather goods as functional color. Keep jewelry secondary to cut.

Mood, liberation & wearer fantasy:
- Agency through clarity. The wearer can move from boardroom to night without losing structure.""",
    },
    {
        "house": "Alexander McQueen",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "alexander_mcqueen_ss27",
        "theme": "Past Present: sacred serenity fused with London rave subversion",
        "design_target": (
            "Design an Alexander McQueen Spring/Summer 2027 collection under Seán McGirr. "
            "Celebrate London's transcendent power: sacred portraiture palette beside underground neons, "
            "angel-wing tailoring beside harness and metal. Four chapters. "
            "Do not flatten into one gothic costume."
        ),
        "description": """Heritage & provenance:
- A London-born house of uncompromising attitude and subversive spirit.
- Shaun Leane metal body adornment returns; Huntsman collaboration for elongated bespoke menswear silhouettes.

Show / location context:
- Spring/Summer 2027 under Lincoln's Inn Chapel vaults. Score by A. G. Cook with Shards Voices.

Creative director intent:
- Divine euphoria between the sacred and the subcultural. Ethereal and urban.
- Precisely engineered Savile Row traditions shifted between formality and counterculture.

Silhouette & garment vocabulary:
- Sculptural angel-wing tailoring against tall strict suiting.
- Smoked tulle, acid floral glass organza, lacquered satin, leather harnesses.
- Curve-hugging diaphanous dresses with metallic leaves; belts anchoring soft volumes.

Materials, craft & surface:
- Heritage British wools, reflective organza, leather, precious metal adornment, recycled silver belts.

Color, stripe & graphic codes:
- Religious portraiture palette and washed rave neons. Acid florals as light, not decoration dump.

Accessories & finishing:
- Shaun Leane metalwork as body architecture. Harness and belt as structure.

Mood, liberation & wearer fantasy:
- Angels in the dark. Commanding, transportive beauty with London attitude.""",
    },
    {
        "house": "Versace",
        "season": "Spring/Summer 2026",
        "status": "latest_completed",
        "dir": "versace_ss26",
        "theme": "Reality over fantasy: '80s street sensuality in everyday Versace product",
        "design_target": (
            "Design a Versace Spring/Summer 2026 womenswear collection under Dario Vitale. "
            "Prefer reality to fantasy: casual, sexy, product-obsessed clothes with retro brio and street energy. "
            "Four chapters. Do not default to one Met-Gala gown formula."
        ),
        "description": """Heritage & provenance:
- Versace color, audaciousness, and sex appeal; Warhol-era print memory without celebrity faces.
- Dario Vitale's debut leans East Village disco and product reality over pure fantasy.

Show / location context:
- Spring/Summer 2026, Milan, intimate museum setting with deliberate disorder—an undone bed as scene.

Creative director intent:
- Start closer to people: T-shirts, sweaters, blousons, vests, jeans with unabashed retro brio.
- Sensuality in everyday garments. Bigger, bolder, brighter as attitude, not only as eveningwear.

Silhouette & garment vocabulary:
- High-waisted tight jeans, unbuckled belts, slashed muscle tees, draped low-back dresses with tubular shoulders.
- Glitzy bralette dresses, gold-laden leather vests, blazer-and-jeans as a house statement.

Materials, craft & surface:
- Denim, jersey, leather, bright cloth. Hand-painted faces that are not famous icons.
- Underwear peeking as design, not accident.

Color, stripe & graphic codes:
- Purple, green, yellow, blue, red, stripes. '80s flash as the graphic code.

Accessories & finishing:
- Gold Medusa-scale hardware used with street ease. Belts and undone finishing are part of the cut.

Mood, liberation & wearer fantasy:
- Hot, relevant, wearable sensuality. The wearer does not need a red carpet to be Versace.""",
    },
    {
        "house": "Jil Sander",
        "season": "Spring/Summer 2027",
        "status": "shown",
        "dir": "jil_sander_ss27",
        "theme": "Vulnerability becomes the uniform: severe tailoring deliberately loosened",
        "design_target": (
            "Design a Jil Sander Spring/Summer 2027 collection under Simone Bellotti. "
            "Keep classic tailored jackets, coats, trousers, and pencil skirts, then introduce fragility: "
            "high button stances, scrunched waists, crumpled silk, exposed underlayers. Four chapters. "
            "Do not abandon the house's precise minimalism for pure mess."
        ),
        "description": """Heritage & provenance:
- Jil Sander pristine minimalism and twisted classicism.
- Simone Bellotti asks what happens when the uniform stops behaving perfectly.

Show / location context:
- Spring/Summer 2027, Milan. A wave structure: recognizable severity, unruly apex, then release.

Creative director intent:
- The uniform becomes vulnerable; vulnerability becomes the uniform.
- Classic feeling with a little twist: approachable tenderness inside discipline.

Silhouette & garment vocabulary:
- Collarless leather coat-dress. Jackets with buttons raised near the Adam's apple.
- Double-breasted fronts that swing free; waist-suppressed coats; pencil skirts; cape-like dresses.
- Deep-V shirts, slim trousers, intentionally rumpled blazers.

Materials, craft & surface:
- Sleek leather, light silks that crinkle, precise wool. Mismatched leopard. Abstract Japanese landscape print pressed flat.

Color, stripe & graphic codes:
- Office neutrals and faded pastels with Yves Klein blue, red, and deep orange as controlled breaks.

Accessories & finishing:
- Strange shoes with asymmetrical vamps and adjustable flaps. Steel-ball buttons. Keep bags quiet.

Mood, liberation & wearer fantasy:
- Controlled clothes that have been lived in. Softness is a form of strength.""",
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
            # refresh theme/description in index for already-listed dirs
            for rec in payload["collections"]:
                if rec.get("dir") == row["dir"]:
                    rec["theme"] = row["theme"]
                    rec["description"] = row["description"].rstrip()
                    rec["house"] = row["house"]
                    rec["season"] = row["season"]
                    rec["status"] = row["status"]
    index_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    readme_lines = [
        "# 大牌最新季度主题（截至 2026-09-28，2026-10 补齐至 19 家）",
        "",
        "巴黎 / 米兰 / 伦敦已走秀或最近完成季。每个品牌目录对应一次 `FashionWorkflow` 输入，默认 4 个章节 × 每章 4 look（合计约 304 条描述）。",
        "",
        "- `design_target.txt`：设计目标",
        "- `theme.txt`：主题",
        "- `description.txt`：主题分析要先提炼的要素（出处、秀场、意图、廓形与单品、材料、色彩图形、配饰、穿着幻想）。同一份全文也写在 `index.json` 每条记录的 `description` 里。",
        "- `theme_analysis.txt`：可选；工作流会重新生成章节子主题",
        "",
        "| 目录 | 品牌 | 季度 | 主题 |",
        "| --- | --- | --- | --- |",
    ]
    for rec in payload["collections"]:
        readme_lines.append(
            f"| {rec['dir']} | {rec['house']} | {rec['season']} | {rec['theme']} |"
        )
    (BASE / "README.md").write_text("\n".join(readme_lines) + "\n", encoding="utf-8")
    n = len(payload["collections"])
    print(json.dumps({"collections": n, "added": added, "looks_if_4x4": n * 4 * 4}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
