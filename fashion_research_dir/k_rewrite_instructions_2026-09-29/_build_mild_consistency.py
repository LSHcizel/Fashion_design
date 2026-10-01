"""Append 50 mild consistency / binding-defect descriptions to the K-rewrite corpus.

Themes are mainstream historical lines of houses already in this corpus.
Each paragraph keeps one look and one slight conflict.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from plugins.text_description_evaluator.design_text_evaluator_api import (  # noqa: E402
    detect_consistency_conflicts,
)

CASES = [
    {
        "id": "01",
        "brand": "Chanel",
        "theme": "Classic tweed suit",
        "defect": "binding",
        "defect_zh": "同一件外套的面料绑了两次：奶油粗花呢，又写成黑缎",
        "text": (
            "Theme: classic tweed suit. Concept: a boxy cream tweed jacket and a matching straight skirt "
            "read as one suit, with silk braid tracing the front edge and the cuffs. The jacket is cropped, "
            "with four patch pockets, and is worn open over a white silk blouse. Gold-tone buttons sit in a "
            "single column on the tweed. The skirt is straight and cream. A quilted chain bag hangs at the side. "
            "The same shell is liquid black satin."
        ),
    },
    {
        "id": "02",
        "brand": "Chanel",
        "theme": "Camellia",
        "defect": "or_shoe",
        "defect_zh": "鞋绑了两个品类：黑缎高跟鞋或米白皮平底",
        "text": (
            "Theme: camellia. Concept: one white camellia at the neck is the mark on a narrow black dress. "
            "The dress is sleeved to the wrist, with a round neck and a hem at mid-calf, and the camellia sits "
            "on the left chest in layered white petals. A single strand of pearls follows the neckline. "
            "The feet are a black satin pump or an ivory leather flat."
        ),
    },
    {
        "id": "03",
        "brand": "Chanel",
        "theme": "Deauville stripe",
        "defect": "lr_sleeve",
        "defect_zh": "左右袖面料不一致：左袖是羊毛条纹，右袖是丝绸",
        "text": (
            "Theme: Deauville stripe. Concept: a navy-and-white breton stripe covers the sailor top as one field. "
            "The top has a square-cut sailor collar in plain navy, long sleeves, and the stripe running across "
            "the chest and the body. It is tucked into a navy gabardine trouser with a pressed crease. "
            "A straw bag with a chain sits on the shoulder. The left sleeve is a long wool sleeve in the breton "
            "stripe. The right sleeve is a long silk sleeve in plain ivory."
        ),
    },
    {
        "id": "04",
        "brand": "Chanel",
        "theme": "Quilted chain jacket",
        "defect": "length",
        "defect_zh": "同一件外套两个长度：及臀，又及腰",
        "text": (
            "Theme: quilted chain jacket. Concept: a diamond-quilted black jacket carries a gold chain along "
            "the front edge, the house line of the 2.55 translated onto the cloth. The quilting covers the "
            "whole shell, and the chain sits in the quilted channel at the opening. A black top shows in the "
            "opening, with a slim black skirt below. The jacket is hip-length and cropped to the waist."
        ),
    },
    {
        "id": "05",
        "brand": "Chanel",
        "theme": "Little black dress",
        "defect": "binding",
        "defect_zh": "同一领口绑了两次：圆领，又是深V",
        "text": (
            "Theme: little black dress. Concept: a narrow black dress is the whole look, with a pearl strand "
            "as the only light. The dress is long-sleeved, matte crepe, and falls straight to mid-calf. "
            "The neckline is a soft round scoop finished with the pearls. Black leather pumps close the feet. "
            "The same neckline drops in a deep V to the waist."
        ),
    },
    {
        "id": "06",
        "brand": "Chanel",
        "theme": "Pearl rope",
        "defect": "sleeve_state",
        "defect_zh": "袖型有两套：一侧长袖，另一侧无袖",
        "text": (
            "Theme: pearl rope. Concept: a rope of pearls traces the neckline and the front opening of a black "
            "evening column. The dress is crepe, narrow through the hip, with the pearls continuing as a single "
            "path from the throat to the waist. A long set-in sleeve covers one arm to the wrist. "
            "The other side is sleeveless."
        ),
    },
    {
        "id": "07",
        "brand": "Dior",
        "theme": "Bar jacket",
        "defect": "binding",
        "defect_zh": "同一件夹克的门襟绑了两次：单排金扣，又是双排扣",
        "text": (
            "Theme: Bar jacket. Concept: a nipped-waist jacket with a padded peplum holds a full calf-length "
            "skirt, the New Look tailleur. The jacket is pale wool, fitted through the waist, with one column "
            "of gold buttons and a rounded shoulder. The skirt is full and the same pale wool, held out from "
            "the hip. Ivory leather pumps finish the feet. The same jacket is double-breasted with two columns of buttons."
        ),
    },
    {
        "id": "08",
        "brand": "Dior",
        "theme": "Toile de Jouy",
        "defect": "lr_shoe",
        "defect_zh": "左右鞋不一致：左脚是印花缎高跟鞋，右脚是凉鞋",
        "text": (
            "Theme: toile de Jouy. Concept: a pastoral toile print covers a fitted bodice and a full skirt as "
            "one field. The print is blue on cream, with small figures repeated across the cloth, and a navy "
            "ribbon marks the waist. The neckline is a wide boat neck. Long sleeves end in a narrow cuff. "
            "The left shoe is a blue satin pump. The right shoe is an ivory sandal."
        ),
    },
    {
        "id": "09",
        "brand": "Dior",
        "theme": "Oblique monogram",
        "defect": "or_bottom",
        "defect_zh": "下装绑了两个品类：斜纹短裙或羊毛西裤",
        "text": (
            "Theme: oblique monogram. Concept: the Dior oblique runs on the diagonal across a tailored coat as "
            "the surface field. The coat is navy, straight, and open, with the monogram tilted and repeating "
            "from shoulder to hem. A white shirt shows at the neck. The lower half is a navy oblique skirt or "
            "a grey wool trouser."
        ),
    },
    {
        "id": "10",
        "brand": "Dior",
        "theme": "Miss Dior floral",
        "defect": "binding",
        "defect_zh": "同一件裙子的面料绑了两次：真丝印花，又是羊毛",
        "text": (
            "Theme: Miss Dior floral. Concept: a scattered garden floral covers a silk dress from neck to hem. "
            "The flowers are pink and green on a pale ground, dense enough to read as one field, with a narrow "
            "self belt at the waist. The dress has long sleeves and a soft round neck. Ivory pumps sit under "
            "the hem. The same dress is cut from grey wool with no floral."
        ),
    },
    {
        "id": "11",
        "brand": "Dior",
        "theme": "Saddle equestrian",
        "defect": "lr_leg",
        "defect_zh": "左右腿下装不一致：左腿是骑马羊毛裤，右腿是丝绸裙",
        "text": (
            "Theme: saddle equestrian. Concept: a fitted riding jacket in brown wool, with a saddle-flap pocket, "
            "is the identifying cut. The jacket is nipped, single-breasted, and worn over a white stock shirt. "
            "Leather gloves are held in one hand. The left leg is a brown wool trouser with a calf strap. "
            "The right leg is a cream silk skirt."
        ),
    },
    {
        "id": "12",
        "brand": "Louis Vuitton",
        "theme": "Monogram canvas",
        "defect": "length",
        "defect_zh": "同一件大衣两个长度：及臀，又及腰",
        "text": (
            "Theme: monogram canvas. Concept: the classic monogram flower and initials cover a straight coat as "
            "one canvas field. The coat is brown and tan, worn open over a plain ivory dress. Leather piping "
            "outlines the collar and the pocket. Gold-tone trunk corners sit at the pocket edges. "
            "The coat is hip-length and cropped to the waist."
        ),
    },
    {
        "id": "13",
        "brand": "Louis Vuitton",
        "theme": "Damier",
        "defect": "binding",
        "defect_zh": "同一件夹克的五金绑了两次：金扣，又是银扣",
        "text": (
            "Theme: Damier. Concept: a brown-and-tan checker covers a boxy jacket as the Damier field. "
            "The jacket is worn open over a tan knit, with the checker continuing onto a matching straight skirt. "
            "Gold-tone buttons close the front in one column, and a leather tab finishes the cuff. "
            "The same jacket fastens with silver-tone buttons."
        ),
    },
    {
        "id": "14",
        "brand": "Louis Vuitton",
        "theme": "Trunk travel coat",
        "defect": "sleeve_state",
        "defect_zh": "袖型有两套：一侧长袖，另一侧无袖",
        "text": (
            "Theme: trunk travel coat. Concept: leather straps and trunk corners turn a plain coat into luggage. "
            "The coat is tan wool, straight, with brown leather binding the front edge and a brass corner patch "
            "on the pocket. An ivory shirt shows underneath. A long set-in sleeve ends in a leather cuff. "
            "The other side is sleeveless."
        ),
    },
    {
        "id": "15",
        "brand": "Louis Vuitton",
        "theme": "Flower monogram",
        "defect": "lr_sleeve",
        "defect_zh": "左右袖面料不一致：左袖是帆布花卉，右袖是丝绸",
        "text": (
            "Theme: flower monogram. Concept: the four-petal monogram flower repeats across a coat as the only "
            "pattern. The flowers are tan on brown canvas, evenly spaced, with leather piping at the collar. "
            "The coat is worn open over a cream dress that falls straight. The left sleeve is a long canvas sleeve "
            "carrying the flower. The right sleeve is a long silk sleeve with no flower."
        ),
    },
    {
        "id": "16",
        "brand": "Gucci",
        "theme": "Flora",
        "defect": "or_shoe",
        "defect_zh": "鞋绑了两个品类：印花缎高跟鞋或皮革凉鞋",
        "text": (
            "Theme: Flora. Concept: the Flora print, flowers and insects on a pale ground, covers a silk dress "
            "as one field. The dress is long-sleeved, with a soft bow at the neck and the print running through "
            "the skirt to mid-calf. A slim belt in green-red-green webbing marks the waist. "
            "The feet are a floral satin pump or a brown leather sandal."
        ),
    },
    {
        "id": "17",
        "brand": "Gucci",
        "theme": "Horsebit",
        "defect": "binding",
        "defect_zh": "同一领口绑了两次：圆领，又是深V",
        "text": (
            "Theme: horsebit. Concept: a gold horsebit closes the belt and repeats as the hardware on a loafer, "
            "against a plain silk shirtdress. The dress is ivory, long-sleeved, with the horsebit belt at the "
            "waist and the neckline a soft round opening. Brown leather loafers carry the same bit at the vamp. "
            "The same neckline drops in a deep V to the waist."
        ),
    },
    {
        "id": "18",
        "brand": "Gucci",
        "theme": "Web stripe",
        "defect": "lr_shoe",
        "defect_zh": "左右鞋不一致：左脚是织带乐福，右脚是凉鞋",
        "text": (
            "Theme: web stripe. Concept: a green-red-green band circles the cuff of a navy knit and the hem of "
            "a matching skirt. The knit is a polo with a collar, and the web band is the only color break on "
            "the navy ground. The skirt is straight and navy, ending above the knee, with the same band at the "
            "hem edge. The left shoe is a navy leather loafer. The right shoe is a red sandal."
        ),
    },
    {
        "id": "19",
        "brand": "Gucci",
        "theme": "GG monogram",
        "defect": "length",
        "defect_zh": "同一件夹克两个长度：及臀，又及腰",
        "text": (
            "Theme: GG monogram. Concept: interlocking GG letters repeat across a knit jacket as the surface field. "
            "The knit is beige and ebony, worn open over a plain ivory top, and the monogram continues on a "
            "straight skirt. A leather belt with a gold bit sits at the waist. "
            "The jacket is hip-length and cropped to the waist."
        ),
    },
    {
        "id": "20",
        "brand": "Prada",
        "theme": "Nylon",
        "defect": "binding",
        "defect_zh": "同一件大衣的面料绑了两次：尼龙，又是羊毛",
        "text": (
            "Theme: nylon. Concept: a plain nylon coat is the look, with the triangle mark as the only logo. "
            "The coat is black, lightweight, and slightly shiny, worn open over a grey wool dress. The triangle "
            "sits small on the chest. Pockets are welded into the nylon. Black leather pumps finish the feet. "
            "The same shell is matte grey wool."
        ),
    },
    {
        "id": "21",
        "brand": "Prada",
        "theme": "Triangle",
        "defect": "or_bottom",
        "defect_zh": "下装绑了两个品类：尼龙半裙或羊毛西裤",
        "text": (
            "Theme: triangle. Concept: a small enamel triangle is the only mark on an otherwise plain black coat. "
            "The coat is nylon, straight, and open, with the triangle placed at the chest and nowhere else. "
            "A white shirt shows at the collar. The lower half is a black nylon skirt or a grey wool trouser."
        ),
    },
    {
        "id": "22",
        "brand": "Prada",
        "theme": "Uniform",
        "defect": "sleeve_state",
        "defect_zh": "袖型有两套：一侧长袖，另一侧无袖",
        "text": (
            "Theme: uniform. Concept: a grey wool coat cut like a plain uniform is the look, with a small triangle "
            "as the only mark. The coat is straight, single-breasted, and worn over a white shirt and a grey skirt. "
            "The cloth is matte and unpatterned. A long set-in sleeve ends at a plain cuff. "
            "The other side is sleeveless."
        ),
    },
    {
        "id": "23",
        "brand": "Prada",
        "theme": "Geometric print",
        "defect": "lr_leg",
        "defect_zh": "左右腿下装不一致：左腿是几何半裙，右腿是西裤",
        "text": (
            "Theme: geometric print. Concept: a hard-edge geometric print in black, white, and red covers the "
            "jacket as one field. The jacket is boxy and worn open over a white shirt. The print is flat and "
            "graphic, with no floral. The left leg is a black geometric skirt. The right leg is a plain grey trouser."
        ),
    },
    {
        "id": "24",
        "brand": "Hermès",
        "theme": "Riding jacket",
        "defect": "binding",
        "defect_zh": "同一件夹克的扣子绑了两次：牛角扣，又是金属扣",
        "text": (
            "Theme: riding jacket. Concept: a brown leather riding jacket with a saddle-flap pocket is the cut. "
            "The jacket is fitted, worn over a white shirt and a tan wool trouser. Horn buttons close the front "
            "in one column, and orange saddle stitch outlines the pocket. Brown leather loafers finish the feet. "
            "The same jacket closes with polished metal buttons."
        ),
    },
    {
        "id": "25",
        "brand": "Hermès",
        "theme": "Silk carré",
        "defect": "lr_sleeve",
        "defect_zh": "左右袖面料不一致：左袖是斜纹绸印花，右袖是羊毛",
        "text": (
            "Theme: silk carré. Concept: a silk-scarf print covers a shirt dress as one field, the carré enlarged "
            "onto the cloth. The print is a framed equestrian drawing in orange, brown, and cream, running from "
            "the collar through the skirt. The dress is buttoned and falls to mid-calf. "
            "The left sleeve is a long silk sleeve in the print. The right sleeve is a long wool sleeve in plain tan."
        ),
    },
    {
        "id": "26",
        "brand": "Hermès",
        "theme": "Orange leather",
        "defect": "or_shoe",
        "defect_zh": "鞋绑了两个品类：橙色皮革高跟鞋或棕色乐福",
        "text": (
            "Theme: orange leather. Concept: an orange leather coat is the look, with the color itself as the "
            "identity and a narrow belt at the waist. The coat is straight, calf-skimming, and worn over an "
            "ivory silk shirt and a tan trouser. Stitching is the only decoration. "
            "The feet are an orange leather pump or a brown leather loafer."
        ),
    },
    {
        "id": "27",
        "brand": "Hermès",
        "theme": "Chaîne d'ancre",
        "defect": "length",
        "defect_zh": "同一件外套两个长度：及臀，又及腰",
        "text": (
            "Theme: chaîne d'ancre. Concept: an anchor-chain motif is set in metal along the edge of a black "
            "leather jacket. The chain repeats as a single path from the collar down the front opening. "
            "The jacket is worn over a white shirt and a black trouser. "
            "The jacket is hip-length and cropped to the waist."
        ),
    },
    {
        "id": "28",
        "brand": "Bottega Veneta",
        "theme": "Intrecciato",
        "defect": "binding",
        "defect_zh": "同一件外套的面料绑了两次：编织皮革，又是丝绸",
        "text": (
            "Theme: intrecciato. Concept: a woven-leather field covers a straight coat, the strips interlaced "
            "across the whole shell. The coat is caramel, worn open over an ivory silk dress, and the weave is "
            "the identity rather than a logo. A leather belt knots once at the waist. "
            "The same shell is plain ivory silk with no weave."
        ),
    },
    {
        "id": "29",
        "brand": "Bottega Veneta",
        "theme": "The Knot",
        "defect": "sleeve_state",
        "defect_zh": "袖型有两套：一侧长袖，另一侧无袖",
        "text": (
            "Theme: the knot. Concept: one leather knot at the waist is the mark on an otherwise plain dress. "
            "The dress is caramel leather, column-shaped, with the knot sitting off center on a narrow belt. "
            "No logo is printed. A long set-in sleeve continues the leather to the wrist. "
            "The other side is sleeveless."
        ),
    },
    {
        "id": "30",
        "brand": "Bottega Veneta",
        "theme": "Quiet leather",
        "defect": "lr_shoe",
        "defect_zh": "左右鞋不一致：左脚是皮革高跟鞋，右脚是凉鞋",
        "text": (
            "Theme: quiet leather. Concept: an unmarked matte-leather coat is the look, with no monogram and "
            "the hide itself as the surface. The coat is olive, straight, and open over a cream silk dress "
            "that falls to mid-calf. Seams are the only lines. The left shoe is an olive leather pump. "
            "The right shoe is a cream sandal."
        ),
    },
    {
        "id": "31",
        "brand": "Bottega Veneta",
        "theme": "Woven leather column",
        "defect": "or_bottom",
        "defect_zh": "下装绑了两个品类：编织皮裙或羊毛西裤",
        "text": (
            "Theme: woven leather column. Concept: intrecciato leather continues from a sleeveless top into "
            "the lower garment as one woven column. The weave is dark brown and tight, with a soft knot at "
            "the waist and no printed mark. The lower half is a woven leather skirt or a taupe wool trouser."
        ),
    },
    {
        "id": "32",
        "brand": "Fendi",
        "theme": "FF monogram",
        "defect": "binding",
        "defect_zh": "同一件夹克的门襟绑了两次：单排扣，又是双排扣",
        "text": (
            "Theme: FF monogram. Concept: a repeating FF covers a knit jacket as the surface field. "
            "The knit is brown and tan, worn over a plain cream top, with one column of leather-backed buttons. "
            "A matching straight skirt carries the same FF. The same jacket is double-breasted."
        ),
    },
    {
        "id": "33",
        "brand": "Fendi",
        "theme": "Zucca",
        "defect": "lr_sleeve",
        "defect_zh": "左右袖面料不一致：左袖是祖卡提花，右袖是丝绸",
        "text": (
            "Theme: Zucca. Concept: the brown Zucca repeat covers a straight coat as one field. The coat is "
            "worn open over a black dress, and the repeat stays small and regular from collar to hem. "
            "Leather piping finishes the pocket. The left sleeve is a long wool sleeve in the Zucca repeat. "
            "The right sleeve is a long silk sleeve in plain black."
        ),
    },
    {
        "id": "34",
        "brand": "Fendi",
        "theme": "Selleria",
        "defect": "length",
        "defect_zh": "同一件夹克两个长度：及臀，又及腰",
        "text": (
            "Theme: Selleria. Concept: contrast saddle stitch outlines the panels of a leather jacket. "
            "The stitch is the identity, running along the front edge, the pocket, and the cuff in a pale thread "
            "on brown leather. A black top shows in the opening, with a brown leather skirt below. "
            "The jacket is hip-length and cropped to the waist."
        ),
    },
    {
        "id": "35",
        "brand": "Fendi",
        "theme": "Roma",
        "defect": "binding",
        "defect_zh": "同一领口绑了两次：圆领，又是深V",
        "text": (
            "Theme: Roma. Concept: a yellow ground with a small black FF is the Roma code on a knit dress. "
            "The dress is straight, long-sleeved, and the yellow reads as one field with the FF placed sparsely. "
            "The neckline is a round crew finished with a narrow black band. Black leather pumps close the feet. "
            "The same neckline drops in a deep V to the waist."
        ),
    },
    {
        "id": "36",
        "brand": "Saint Laurent",
        "theme": "Le Smoking",
        "defect": "sleeve_state",
        "defect_zh": "袖型有两套：一侧长袖，另一侧无袖",
        "text": (
            "Theme: Le Smoking. Concept: a black tuxedo jacket with a satin peak lapel is worn with a matching "
            "trouser as evening tailoring. The jacket is sharp through the shoulder, with one button, and a "
            "white shirt shows at the opening. The satin lapel is the light on the black wool. "
            "A long set-in sleeve ends in a satin cuff. The other side is sleeveless."
        ),
    },
    {
        "id": "37",
        "brand": "Saint Laurent",
        "theme": "Saharienne",
        "defect": "or_bottom",
        "defect_zh": "下装绑了两个品类：卡其短裤或丝绸半裙",
        "text": (
            "Theme: saharienne. Concept: a khaki safari jacket with four bellows pockets and a belt is the cut. "
            "The jacket is cotton, worn open over a white shirt, with buttoned tabs at the cuff and a self belt "
            "left loose. The lower half is a khaki cotton short or a cream silk skirt."
        ),
    },
    {
        "id": "38",
        "brand": "Saint Laurent",
        "theme": "Mondrian",
        "defect": "lr_shoe",
        "defect_zh": "左右鞋不一致：左脚是黑漆高跟鞋，右脚是穆勒",
        "text": (
            "Theme: Mondrian. Concept: primary color blocks separated by black lines cover a shift dress as one "
            "field. The blocks are red, blue, yellow, and white, flat and hard-edged, and the dress is sleeveless "
            "with a high round neck. The hem ends above the knee. The left shoe is a black patent pump. "
            "The right shoe is a white mule."
        ),
    },
    {
        "id": "39",
        "brand": "Saint Laurent",
        "theme": "Pussy-bow blouse",
        "defect": "binding",
        "defect_zh": "同一件衬衫的面料绑了两次：真丝，又是皮革",
        "text": (
            "Theme: pussy-bow blouse. Concept: a soft silk bow at the neck is the mark, on a fluid blouse tucked "
            "into a slim black skirt. The blouse is ivory silk, long-sleeved, and the bow is tied once from the "
            "collar. The skirt is crepe and straight. Black pumps finish the feet. "
            "The same shell is black leather."
        ),
    },
    {
        "id": "40",
        "brand": "Loewe",
        "theme": "Anagram leather",
        "defect": "lr_leg",
        "defect_zh": "左右腿下装不一致：左腿是皮革半裙，右腿是羊毛西裤",
        "text": (
            "Theme: anagram leather. Concept: a small anagram is pressed into a plain leather jacket, and the "
            "hide is the surface. The jacket is black, slightly oversized, and worn open over a white shirt. "
            "The anagram sits once on the chest. The left leg is a black leather skirt. "
            "The right leg is a grey wool trouser."
        ),
    },
    {
        "id": "41",
        "brand": "Loewe",
        "theme": "Raffia weave",
        "defect": "binding",
        "defect_zh": "同一下摆绑了两次：停在臀线，又落到小腿",
        "text": (
            "Theme: raffia weave. Concept: a raffia basket weave covers a straight dress as the craft field. "
            "The weave is natural straw color, tight, and runs from the shoulder through the body, with a leather "
            "anagram tab at the waist. The dress stops at the hip. The same hem continues to mid-calf."
        ),
    },
    {
        "id": "42",
        "brand": "Loewe",
        "theme": "Suede craft",
        "defect": "or_shoe",
        "defect_zh": "鞋绑了两个品类：麂皮短靴或皮革凉鞋",
        "text": (
            "Theme: suede craft. Concept: a suede shirt is the look, with the nap as the surface and an anagram "
            "pressed at the chest. The shirt is sand-colored, long-sleeved, and worn over a matching suede skirt "
            "that ends above the knee. Seams are left visible. The feet are a sand suede boot or a leather sandal."
        ),
    },
    {
        "id": "43",
        "brand": "Alaïa",
        "theme": "Bandage knit",
        "defect": "sleeve_state",
        "defect_zh": "袖型有两套：一侧长袖，另一侧无袖",
        "text": (
            "Theme: bandage knit. Concept: horizontal knit bands wrap the body of a close dress from neck to hem. "
            "The bands are black, even, and continuous around the torso, with the hem ending above the knee. "
            "A long set-in sleeve continues the same bands to the wrist. The other side is sleeveless."
        ),
    },
    {
        "id": "44",
        "brand": "Alaïa",
        "theme": "Perforated leather",
        "defect": "binding",
        "defect_zh": "同一件皮裙的工艺绑了两次：穿孔皮革，又是完整羊毛",
        "text": (
            "Theme: perforated leather. Concept: small perforations cover a leather dress as the surface field. "
            "The dress is black, close to the body, and the holes repeat in rows from the chest through the skirt. "
            "A zipper closes the side. The hem ends above the knee. The same dress is solid grey wool with no holes."
        ),
    },
    {
        "id": "45",
        "brand": "Alaïa",
        "theme": "Hooded knit",
        "defect": "lr_sleeve",
        "defect_zh": "左右袖面料不一致：左袖是弹力针织，右袖是丝绸",
        "text": (
            "Theme: hooded knit. Concept: a hood grows out of a close black knit and continues as the same cloth "
            "down the body. The knit is seamless through the torso and ends at mid-thigh over bare legs. "
            "The left sleeve is a long knit sleeve in the same black stretch. The right sleeve is a long silk sleeve."
        ),
    },
    {
        "id": "46",
        "brand": "The Row",
        "theme": "Cashmere column",
        "defect": "or_bottom",
        "defect_zh": "下装绑了两个品类：羊绒长裙或羊毛阔腿裤",
        "text": (
            "Theme: cashmere column. Concept: one long cashmere dress falls unbroken from a high neck to the "
            "ankle, with no logo and no trim. The cloth is greige, matte, and the only break is a seam at the "
            "waist. Long sleeves end plain at the wrist. The lower half is a greige cashmere skirt or a wide wool trouser."
        ),
    },
    {
        "id": "47",
        "brand": "The Row",
        "theme": "Oversized coat",
        "defect": "length",
        "defect_zh": "同一件大衣两个长度：及臀，又及腰",
        "text": (
            "Theme: oversized coat. Concept: a large camel coat is the volume, worn open over a narrow ivory "
            "dress. The coat has a soft shoulder, no visible logo, and a plain self belt left untied. "
            "The dress underneath is column-shaped. The coat is hip-length and cropped to the waist."
        ),
    },
    {
        "id": "48",
        "brand": "Schiaparelli",
        "theme": "Shocking pink",
        "defect": "binding",
        "defect_zh": "同一领口绑了两次：圆领，又是深V",
        "text": (
            "Theme: shocking pink. Concept: a shocking-pink column is the look, with one gold button as the "
            "hardware. The dress is silk, long-sleeved, and the pink covers the cloth as a flat field. "
            "The neckline is a round jewel neck. Gold embroidery is limited to the button at the throat. "
            "Black satin pumps close the feet. The same neckline drops in a deep V to the waist."
        ),
    },
    {
        "id": "49",
        "brand": "Schiaparelli",
        "theme": "Keyhole evening",
        "defect": "lr_shoe",
        "defect_zh": "左右鞋不一致：左脚是金缎高跟鞋，右脚是凉鞋",
        "text": (
            "Theme: keyhole evening. Concept: a small keyhole opening at the chest, edged in gold thread, is the "
            "mark on a black column. Gold embroidery stays around that opening and does not cover the skirt. "
            "The dress is long-sleeved silk and falls straight to the ankle. The left shoe is a gold satin pump. "
            "The right shoe is a black sandal."
        ),
    },
    {
        "id": "50",
        "brand": "Chanel",
        "theme": "Métiers d'art embroidery",
        "defect": "binding",
        "defect_zh": "同一件夹克的刺绣绑了两次：满铺金银绣，又写成素羊毛",
        "text": (
            "Theme: métiers d'art embroidery. Concept: dense gold and silver embroidery covers a black jacket "
            "as the surface field, the December atelier line. The embroidery runs across the chest, the sleeves, "
            "and the pocket flaps, and a straight black skirt sits below. Pearls edge the round neck. "
            "The same jacket is plain black wool with no embroidery."
        ),
    },
]


def _business_context(case: dict) -> str:
    return (
        f"{case['brand']} look. Theme: {case['theme']}. "
        "The source has one slight consistency or binding conflict. "
        "Keep the theme and concept named in SOURCE. "
        "Delete the conflict in SOURCE: a left-right split on one zone, a second binding on the same "
        "garment, an or-choice between two garments, or a second sleeve state. "
        "Do not keep the deleted binding as an inner layer. "
        "Write the rewrite in English. Do not invent another house's logo."
    )


def _row(case: dict) -> dict:
    slug = case["theme"].lower().replace(" ", "_").replace("'", "")
    name = f"{case['id']}_{case['brand'].lower().replace(' ', '_').replace('ï', 'i')}_{slug}.txt"
    path = ROOT / "mild_consistency" / name
    return {
        "source_id": f"mild_{case['id']}_{case['brand'].lower().replace(' ', '_')}_{slug}"[:96],
        "role": "source",
        "sample_kind": "mild_consistency",
        "brand": case["brand"],
        "theme": case["theme"],
        "defect": case["defect"],
        "defect_zh": case["defect_zh"],
        "path": str(path.relative_to(REPO)).replace("\\", "/"),
        "text": case["text"].strip(),
        "business_context": _business_context(case),
    }


def _check(rows: list[dict]) -> None:
    bad = []
    for row in rows:
        found = detect_consistency_conflicts(row["text"])
        if not found["active"] or found["severe"]:
            bad.append((row["source_id"], found["severe"], found["reason"]))
    if bad:
        for item in bad:
            print("FAIL", item)
        raise SystemExit(f"{len(bad)} cases are inactive or severe")
    print(f"detector ok: {len(rows)} active, none severe")


def main() -> None:
    if len(CASES) != 50:
        raise SystemExit(f"expected 50 cases, got {len(CASES)}")
    rows = [_row(case) for case in CASES]
    _check(rows)
    out_dir = ROOT / "mild_consistency"
    out_dir.mkdir(parents=True, exist_ok=True)
    for row in rows:
        Path(REPO / row["path"]).write_text(row["text"].strip() + "\n", encoding="utf-8")

    corpus_path = ROOT / "source_corpus.jsonl"
    kept = []
    with corpus_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if str(rec.get("source_id") or "").startswith("mild_"):
                continue
            if str(rec.get("sample_kind") or "") == "mild_consistency":
                continue
            kept.append(rec)
    with corpus_path.open("w", encoding="utf-8") as f:
        for rec in kept + rows:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    manifest_path = ROOT / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["n_total"] = len(kept) + len(rows)
    manifest["n_mild_consistency"] = len(rows)
    manifest["mild_consistency_note"] = (
        "50 条轻缺陷描述。每条只用语料中已有品牌的市场历年主题，并只放一处问题："
        "同一要素的第二个绑定、单侧左右不一致、or 并列两个品类，或一侧有袖一侧无袖。"
        "不使用加冕、新娘、丧服、假面、洛可可这类偏题。"
    )
    manifest["mild_cases"] = [
        {
            "source_id": row["source_id"],
            "brand": row["brand"],
            "theme": row["theme"],
            "defect": row["defect"],
            "defect_zh": row["defect_zh"],
            "path": row["path"],
        }
        for row in rows
    ]
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"corpus {len(kept)} + {len(rows)} = {len(kept) + len(rows)}")


if __name__ == "__main__":
    main()
