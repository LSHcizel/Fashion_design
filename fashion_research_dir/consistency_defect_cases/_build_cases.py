"""Write 18 consistency-defect descriptions grounded in existing inverse parses and looks."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

CASES = [
    {
        "id": "01",
        "defect": "asymmetry",
        "defect_zh": "明显不对称：同一夹克左半套精裁羊毛，右半套亮片丝绸，左右裤和左右鞋同时分裂",
        "theme": "黑色手工对比",
        "concept": "结构化黑夹克作为暗底，让钩针花卉贴花成为识别点",
        "source": "wgsn_batch_image_inverse/20260524T044337Z/01_..._ps27_003_text_description.md",
        "text": (
            "Theme: black handmade contrast. Concept: a structured black jacket is the dark field, and crochet "
            "floral appliqué is the identifying idea. Dense red, white, yellow, and black floral appliqué still runs "
            "along the neckline and both front edges, with a red openwork crochet bag. At the same time the left half "
            "of this one jacket is matte black wool: notched lapel, set-in tailored sleeve, notched cuff. The right "
            "half of the same jacket is high-gloss silk and sequin: no lapel, a cold shoulder, and a bishop sleeve "
            "to the knee. The left leg is a black wool trouser with a crease; the right leg is a red silk culotte. "
            "The left foot is a closed black satin court pump; the right foot is an open red silk evening sandal."
        ),
    },
    {
        "id": "02",
        "defect": "asymmetry",
        "defect_zh": "明显不对称：同一件奶油外套左半是粗花呢精裁，右半是亮片裹领，左右裤与左右鞋同时两套",
        "theme": "象牙粗花呢沙龙",
        "concept": "敞开的奶油粗花呢框住黑色皮质内层",
        "source": "wgsn_batch_image_inverse/20260524T044337Z/09_..._ps27_028_text_description.md",
        "text": (
            "Theme: ivory tweed salon. Concept: an open cream tweed jacket frames a black leather-like inner. "
            "Gold-tone buttons and black trim remain. At the same time the left half of this one jacket is matte "
            "cream tweed with a notched lapel and a set-in wool sleeve; the right half is a sequined shawl that wraps "
            "only the right side of the neck and a bare right arm with no sleeve. The left leg is a cream tweed "
            "trouser with a pressed crease to the ankle; the right leg is a black silk harem pant gathered at the knee. "
            "The left shoe is an ivory leather court pump; the right shoe is a black velvet mule with an open back."
        ),
    },
    {
        "id": "03",
        "defect": "asymmetry",
        "defect_zh": "明显不对称：同一件印花大衣左半长袖立领及膝，右半无袖深V曳地，左右鞋同时两族",
        "theme": "羽毛勾勒的印花立柱",
        "concept": "水色羽毛路径把蓝绿印花大衣从领口画到下摆",
        "source": "wgsn_batch_image_inverse/20260524T044337Z/17_..._ps27_057_text_description.md",
        "text": (
            "Theme: feather-drawn floral column. Concept: a pale aqua feather path draws one blue-and-aqua floral coat "
            "from collar to hem. At the same time the left half of that coat is a knee-length wool column with a high "
            "stand collar and a long set-in sleeve ending in a gold cuff button. The right half of the same coat has "
            "no sleeve, a cold shoulder, a plunging V only on the right, and a hem that trails the floor. The left leg "
            "reads as a narrow floral pencil; the right leg is an ivory silk panel. The left foot is a pointed blue "
            "satin pump; the right foot is an ivory silk evening sandal."
        ),
    },
    {
        "id": "04",
        "defect": "asymmetry",
        "defect_zh": "明显不对称：同一条裙左腿羊毛铅笔、右腿丝绸阔腿，左袖长、右袖无，左右鞋两族",
        "theme": "红色图形线",
        "concept": "一条红色门襟和高开衩把奶油裙组织起来",
        "source": "wgsn_batch_image_inverse/20260524T044337Z/33_..._ps27_016_text_description.md",
        "text": (
            "Theme: red graphic line. Concept: one red placket and a high slit organize a cream skirt. A red waistband and "
            "three gold buttons stay on the placket. At the same time the left sleeve is a long cream sleeve with a bold "
            "red cuff, while the right arm of the same top is sleeveless. The left leg is a cream wool pencil to the knee "
            "with the red slit; the right leg of the same skirt is a red silk palazzo that pools on the floor. The left "
            "shoe is a red patent slingback pump; the right shoe is a cream satin ballet flat."
        ),
    },
    {
        "id": "05",
        "defect": "asymmetry",
        "defect_zh": "明显不对称：同一件白夹克左半短袖短裤，右半及地丝绸袖和阔腿，左右鞋两族",
        "theme": "粉笔白沙龙短裁",
        "concept": "及腰白帆布夹克打开，露出银行条纹衬衫",
        "source": "workflow_0/2026-06-06/chapter_01/look_01.txt",
        "text": (
            "Theme: chalk salon crop. Concept: a waist-skimming white canvas jacket opens onto a banker-stripe shirt. "
            "Please generate female models and the matching clothing for them. A brushed-silver Double C buckle and a black "
            "leather belt remain. At the same time the left half of the jacket is cropped chalk canvas with a notched lapel "
            "and a sleeve ending above the elbow, over a navy tailored short. The right half of the same jacket has no lapel, "
            "a floor-grazing liquid-black silk sleeve, and the right leg is a black silk wide leg instead of the short. "
            "The left foot is a black leather sandal; the right foot is a closed black satin oxford."
        ),
    },
    {
        "id": "06",
        "defect": "asymmetry",
        "defect_zh": "明显不对称：同一套海军剪裁左半角扣长袖羊毛裤，右半单肩丝绸阔腿，左右鞋两族",
        "theme": "海军角扣精裁",
        "concept": "牛角扣海军夹克把工装收成礼服级剪裁",
        "source": "workflow_0/2026-06-06/chapter_02/look_01.txt",
        "text": (
            "Theme: navy horn-button tailoring. Concept: a horn-button navy jacket turns workwear into couture tailoring. "
            "Please generate female models and the matching clothing for them. Matte horn buttons and pearl snaps stay on "
            "the left front. At the same time the left half is a cropped navy canvas jacket with a set-in sleeve and a deep "
            "navy wool gabardine trouser with a pressed crease. The right half of the same jacket is one-shouldered ivory "
            "silk with no sleeve and no button, and the right leg is a fluid ivory silk culotte. The left foot is a navy "
            "satin ankle boot; the right foot is an open ivory silk sandal."
        ),
    },
    {
        "id": "07",
        "defect": "asymmetry",
        "defect_zh": "明显不对称：同一件针织左半长袖条纹迷你裙，右半无袖并接及地丝绸，左右鞋两族",
        "theme": "条纹袖口针织",
        "concept": "奶油、黑、红的层叠袖口条纹是这件短针织的识别点",
        "source": "wgsn_batch_image_inverse/20260524T044337Z/73_..._ps27_069_text_description.md",
        "text": (
            "Theme: striped-cuff knit. Concept: stacked cream, black, and red cuff stripes identify a cropped black knit. "
            "A pale cream belt and cream-and-red neck trim remain. At the same time the left half is a long black knit sleeve "
            "with those stacked stripes and a black knit mini on the left leg. The right half of the same top is sleeveless "
            "to the rib, and the right leg is a floor-length ivory silk panel instead of the mini. The left foot is a black "
            "patent pump; the right foot is a red satin mule."
        ),
    },
    {
        "id": "08",
        "defect": "style_clash",
        "defect_zh": "要素与主题严重不符：手工日装黑底贴花上接了白纱新娘头纱和教堂长曳",
        "theme": "夜花园刺绣",
        "concept": "黑底上的彩色钩针花卉应保持手工日装的密度",
        "source": "wgsn_batch_image_inverse/20260524T044337Z/01_..._ps27_003_text_description.md",
        "text": (
            "Theme: night-garden embroidery. Concept: colored crochet florals on a black ground should stay a dense handmade "
            "day look. The boxy black jacket still has that appliqué, gold-tone buttons, white piping, black bike shorts, and "
            "a red crochet bag. The lower body and head, however, are a different concept entirely: a white bridal cathedral "
            "gown with orange-blossom clusters, a floor-length tulle veil, and white satin court shoes. The handmade day jacket "
            "and the bridal ceremony do not belong to one theme."
        ),
    },
    {
        "id": "09",
        "defect": "style_clash",
        "defect_zh": "要素与主题严重不符：白天哑光粗花呢上接了加冕礼的金锦袍和王冠",
        "theme": "日间罗纹粗花呢",
        "concept": "箱型奶油粗花呢应保持白天沙龙的哑光",
        "source": "wgsn_batch_image_inverse/20260524T044337Z/09_..._ps27_028_text_description.md",
        "text": (
            "Theme: daytime bouclé. Concept: a boxy cream tweed jacket should stay matte salon daywear, with a black-edged "
            "collar, black front trim, gold-tone pocket buttons, and a straight cream tweed skirt. Over that day set the body "
            "is dressed for a different concept: a gold-brocade coronation robe with an ermine shoulder cape and a state crown, "
            "and the feet are gold kid coronation heels. Matte day tweed and a coronation court do not share a theme."
        ),
    },
    {
        "id": "10",
        "defect": "style_clash",
        "defect_zh": "要素与主题严重不符：安静奶油立柱上接了绯红弗拉明戈层叠裙",
        "theme": "奶油典礼",
        "concept": "金属花卉胸针扣住的短斗篷应保持安静的单色立柱",
        "source": "wgsn_batch_image_inverse/20260524T044337Z/49_..._ps27_040_text_description.md",
        "text": (
            "Theme: butter-cream ceremony. Concept: a short capelet fastened by a metallic floral brooch should keep a quiet "
            "monochrome column, over a sleeveless bodice and a ribbed midi skirt in pale butter cream. The skirt and styling "
            "then switch concept: tiers of scarlet flamenco ruffles replace the cream column, a red flower sits at the ear, "
            "and the feet are scarlet flamenco heels. The quiet cream ceremony and the flamenco fiesta do not share a theme."
        ),
    },
    {
        "id": "11",
        "defect": "style_clash",
        "defect_zh": "要素与主题严重不符：轻快图形百褶上接了及地丧服黑纱",
        "theme": "图形百褶",
        "concept": "点线与圆形纹样应让黑色上衣和条纹百褶裙保持轻快",
        "source": "wgsn_batch_image_inverse/20260524T044337Z/57_..._ps27_048_text_description.md",
        "text": (
            "Theme: graphic pleats. Concept: dotted lines and a circular motif should keep a black top and a striped accordion "
            "skirt playful, with a red-and-white circle at the chest and black, ivory, tan, and gold pleats. Over that playful "
            "set the head and outer layer belong to another concept: a floor-length black crepe mourning veil, a jet mourning "
            "collar, and covered black mourning shoes. Graphic play and funeral mourning do not share a theme."
        ),
    },
    {
        "id": "12",
        "defect": "style_clash",
        "defect_zh": "要素与主题严重不符：私密情书大衣内层改成假面舞会菱格与面具",
        "theme": "密封情书",
        "concept": "墨黑羊毛大衣只在走动时露出羊皮纸内层",
        "source": "workflow_0/2026-04-02/chapter_01/look_01.txt",
        "text": (
            "Theme: sealed love letter. Concept: an ink-black wool coat should reveal only a parchment inner layer when it moves. "
            "Please generate female models and the matching clothing for them. The coat is close-cut wool-gabardine, concealed "
            "placket, hem just below the knee, matte. When it opens, the inner layer is a different concept: a harlequin bodice "
            "of black-and-white diamond panes, a full-face jeweled masquerade mask, a feathered fan, and crystal stilettos. "
            "The private letter and the public masquerade do not share a theme."
        ),
    },
    {
        "id": "13",
        "defect": "style_clash",
        "defect_zh": "要素与主题严重不符：腮红舞会纱裙上方接了男装晨礼服燕尾和礼帽",
        "theme": "腮红舞会纱",
        "concept": "水晶薄纱裙应以舞会礼服的完整晚装呈现",
        "source": "workflow_0/2026-06-06/chapter_01/look_01.txt",
        "text": (
            "Theme: blush ball tulle. Concept: a crystal tulle skirt should read as a complete debutante evening gown. Please "
            "generate female models and the matching clothing for them. The lower body is that blush tulle ball skirt with a "
            "horsehair hem and scattered crystals. The upper body belongs to another concept: a black morning tailcoat with "
            "tails, a grey formal striped trouser showing at the front opening, a white waistcoat, and a black top hat. Ivory "
            "satin court shoes remain under the tulle. The ball gown and the men’s morning dress do not share a theme."
        ),
    },
    {
        "id": "14",
        "defect": "style_clash",
        "defect_zh": "要素与主题严重不符：安静条纹及膝套装上接了洛可可撑裙和贴片",
        "theme": "条纹立柱",
        "concept": "米色地上的红绿竖条应保持一条安静的及膝套装",
        "source": "wgsn_batch_image_inverse/20260524T044337Z/41_..._ps27_027_text_description.md",
        "text": (
            "Theme: striped column. Concept: red and green vertical stripes on beige should stay a quiet knee-length set, with "
            "a sleeveless high-neck top, a red-edged gold-button placket, and a gathered skirt to the knee. Over that set the "
            "silhouette changes concept: a robe à la française with wide side panniers, a powdered coiffure, and a black beauty "
            "patch at the cheek, finished with heeled brocade mules. The quiet striped column and the rococo court dress do not "
            "share a theme."
        ),
    },
    {
        "id": "15",
        "defect": "same_element_contradiction",
        "defect_zh": "同要素矛盾：同一夹克既无领又翻领，既及臀又及地；下装既是骑行短裤又是阔腿羊毛裤",
        "theme": "无领黑箱型",
        "concept": "圆领、及臀的黑夹克配贴花，下装是贴身黑短裤",
        "source": "wgsn_batch_image_inverse/20260524T044337Z/01_..._ps27_003_text_description.md",
        "text": (
            "Theme: collarless black box. Concept: a round-neck jacket cropped to the hip, with floral appliqué, over fitted "
            "black shorts. The same jacket is also given a wide notched lapel and a hem that brushes the floor. Its sleeves "
            "are straight and loose, and those same sleeves are sleeveless armholes. The lower body is short fitted black "
            "bike shorts, and that same lower garment is a pair of wide ivory wool trousers. Gold-tone buttons and a red "
            "openwork crochet bag remain."
        ),
    },
    {
        "id": "16",
        "defect": "same_element_contradiction",
        "defect_zh": "同要素矛盾：同一印花大衣既无袖又长袖，既及膝又曳地，立领同时是深V",
        "theme": "立领及膝印花大衣",
        "concept": "高立领和及膝直筒决定这件蓝绿印花大衣",
        "source": "wgsn_batch_image_inverse/20260524T044337Z/17_..._ps27_057_text_description.md",
        "text": (
            "Theme: stand-collar knee coat. Concept: a high stand collar and a straight hem just below the knee define the "
            "blue-and-aqua floral coat, with pale aqua feather trim and gold-tone buttons. The same coat is sleeveless with "
            "cutaway armholes, and it also has long set-in sleeves to the wrist. The same hem sweeps the floor in a train. "
            "The same neckline is a deep plunging V to the waist. Feather trim is drawn along whichever opening is named."
        ),
    },
    {
        "id": "17",
        "defect": "same_element_contradiction",
        "defect_zh": "同要素矛盾：同一条红黑吊带裙方领与立领并存，红底与全黑并存，中长与短上衣下摆并存",
        "theme": "悬垂丝带",
        "concept": "红黑米白的吊带丝带从肩部金饰垂下，构成裙子的线性",
        "source": "wgsn_batch_image_inverse/20260524T044337Z/65_..._ps27_061_text_description.md",
        "text": (
            "Theme: suspended ribbons. Concept: red, black, white, and pale beige ribbon strips fall from gold-tone shoulder "
            "accents and make the linear identity of the dress. The neckline is square to scoop between narrow black straps, "
            "and the same neckline is a high stand collar with no straps. The ground is vivid red with black vertical panels, "
            "and the same dress is entirely black with no red. The skirt is a loose midi column to mid-calf, and the same hem "
            "is a cropped top ending at the waist."
        ),
    },
    {
        "id": "18",
        "defect": "same_element_contradiction",
        "defect_zh": "同要素矛盾：同一件墨黑大衣暗门襟与双排扣并存，及小腿与短腰并存，羊毛与亮片是同一件",
        "theme": "羊皮纸内层",
        "concept": "墨黑窄大衣框住羊皮纸丝绸衬衫和暖灰细裤",
        "source": "workflow_0/2026-04-02/chapter_01/looks_original/look_03.txt",
        "text": (
            "Theme: parchment inner. Concept: a narrow ink coat frames a parchment silk-crepe blouse and warm grey slim wool "
            "trousers. Please generate female models and the matching clothing for them. The coat closes with a concealed "
            "button placket and an uninterrupted front, and the same coat is double-breasted with six exposed peak-lapel buttons. "
            "Its hem brushes the calf, and the same hem is cropped to the waist. The cloth is matte wool-gabardine, and that "
            "same shell is liquid mirror sequin. Smoke-grey topstitching is named on whichever version is described. Narrow-toe "
            "black leather ankle boots finish the feet."
        ),
    },
]


def _resolve_source(source: str) -> str:
    repo = ROOT.parents[1]
    if source.startswith("workflow_0/"):
        return source if (repo / "fashion_research_dir" / source).is_file() else source
    token = source.split("ps27_")[-1].split("_")[0]
    needle = f"ps27_{token}_text_description.md"
    base = repo / "fashion_research_dir" / "wgsn_batch_image_inverse" / "20260524T044337Z"
    hits = list(base.glob(f"*{needle}"))
    if len(hits) == 1:
        return hits[0].relative_to(repo / "fashion_research_dir").as_posix()
    return source


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    manifest = []
    for case in CASES:
        name = f"{case['id']}_{case['defect']}.txt"
        (ROOT / name).write_text(case["text"].strip() + "\n", encoding="utf-8")
        manifest.append(
            {
                "file": name,
                "defect": case["defect"],
                "defect_zh": case["defect_zh"],
                "theme": case["theme"],
                "concept": case["concept"],
                "source": _resolve_source(case["source"]),
            }
        )
    (ROOT / "manifest.json").write_text(
        json.dumps(
            {
                "purpose": "一致性维度负例。01–07 为同一套时装上同时出现的明显左右不对称；08–14 为要素与该条主题、概念严重不符；15–18 为同一要素自相矛盾。均为时装，不用户外装。只保留已生成图片的描述。",
                "counts": {
                    "asymmetry": sum(1 for c in CASES if c["defect"] == "asymmetry"),
                    "style_clash": sum(1 for c in CASES if c["defect"] == "style_clash"),
                    "same_element_contradiction": sum(
                        1 for c in CASES if c["defect"] == "same_element_contradiction"
                    ),
                },
                "cases": manifest,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"wrote {len(CASES)} cases to {ROOT}")


if __name__ == "__main__":
    main()
