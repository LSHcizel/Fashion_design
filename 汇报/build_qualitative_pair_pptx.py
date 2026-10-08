"""在极端案例生图对照 PPT 上追加两页论文式定性对照。"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

SRC = Path(r"c:\Users\lsh\Desktop\记录10.1\极端案例生图对照.pptx")
OUT = Path(r"c:\Users\lsh\Desktop\记录10.1\极端案例生图对照.pptx")
ROOT = Path(r"c:\Users\lsh\Desktop\记录10.1\生图对照")

BLACK = RGBColor(0x1A, 0x1A, 0x1A)
GRAY = RGBColor(0x5C, 0x5C, 0x5C)
MUTED = RGBColor(0x8A, 0x8A, 0x8A)
RED = RGBColor(0xC0, 0x22, 0x22)
LINE = RGBColor(0xD8, 0xD8, 0xD8)
BOX = RGBColor(0xF7, 0xF7, 0xF7)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "微软雅黑"


def _run(p, text, *, size=11, bold=False, color=BLACK):
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    r.font.name = FONT


def add_label(slide, l, t, w, h, text, *, size=12, bold=False, color=BLACK, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(l, t, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    _run(p, text, size=size, bold=bold, color=color)
    return box


def add_panel(slide, l, t, w, h, title: str, body: str, *, score: str):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l, t, w, h)
    shape.adjustments[0] = 0.04
    shape.fill.solid()
    shape.fill.fore_color.rgb = BOX
    shape.line.color.rgb = LINE

    title_box = slide.shapes.add_textbox(l + Inches(0.12), t + Inches(0.08), w - Inches(0.24), Inches(0.32))
    p = title_box.text_frame.paragraphs[0]
    _run(p, title, size=13, bold=True, color=BLACK)
    p2 = title_box.text_frame.add_paragraph()
    _run(p2, score, size=11, bold=True, color=RED)

    body_box = slide.shapes.add_textbox(
        l + Inches(0.12), t + Inches(0.48), w - Inches(0.24), h - Inches(0.58)
    )
    tf = body_box.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    para = tf.paragraphs[0]
    para.alignment = PP_ALIGN.LEFT
    _run(para, body, size=10, color=BLACK)


def fit_picture(slide, path: Path, box_l, box_t, box_w, box_h):
    with Image.open(path) as im:
        iw, ih = im.size
        buf = BytesIO()
        im.convert("RGB").save(buf, format="JPEG", quality=90)
        buf.seek(0)
    scale = min(box_w / iw, box_h / ih)
    pw, ph = iw * scale, ih * scale
    left = box_l + (box_w - pw) / 2
    top = box_t + (box_h - ph) / 2
    slide.shapes.add_picture(buf, int(left), int(top), int(pw), int(ph))


def add_bullets(slide, l, t, w, h, items: list[tuple[str, bool]]):
    """items: (text, emphasize_red)"""
    box = slide.shapes.add_textbox(l, t, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    for i, (text, red) in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(4)
        _run(p, "• " + text, size=12, bold=red, color=RED if red else BLACK)


def add_qual_slide(
    prs,
    *,
    page_title: str,
    page_sub: str,
    left_title: str,
    left_score: str,
    left_text: str,
    left_img: Path,
    right_title: str,
    right_score: str,
    right_text: str,
    right_img: Path,
    bullets: list[tuple[str, bool]],
):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = WHITE

    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), prs.slide_width, Inches(0.07))
    bar.fill.solid()
    bar.fill.fore_color.rgb = RED
    bar.line.fill.background()

    add_label(slide, Inches(0.35), Inches(0.16), Inches(12.5), Inches(0.36), page_title, size=22, bold=True)
    add_label(slide, Inches(0.35), Inches(0.5), Inches(12.5), Inches(0.3), page_sub, size=12, color=GRAY)

    panel_w = Inches(6.2)
    panel_h = Inches(2.35)
    left_l = Inches(0.35)
    right_l = Inches(6.78)
    panel_t = Inches(0.88)

    add_panel(slide, left_l, panel_t, panel_w, panel_h, left_title, left_text, score=left_score)
    add_panel(slide, right_l, panel_t, panel_w, panel_h, right_title, right_text, score=right_score)

    img_t = Inches(3.4)
    img_h = Inches(2.55)
    img_w = panel_w
    fit_picture(slide, left_img, left_l, img_t, img_w, img_h)
    fit_picture(slide, right_img, right_l, img_t, img_w, img_h)
    add_label(slide, left_l, img_t + img_h + Inches(0.02), img_w, Inches(0.25), "原文 → 生图", size=11, color=MUTED, align=PP_ALIGN.CENTER)
    add_label(slide, right_l, img_t + img_h + Inches(0.02), img_w, Inches(0.25), "改写 → 生图", size=11, color=MUTED, align=PP_ALIGN.CENTER)

    add_label(slide, Inches(0.35), Inches(6.2), Inches(12.5), Inches(0.28), "实际变好 / 变坏", size=13, bold=True)
    add_bullets(slide, Inches(0.35), Inches(6.48), Inches(12.5), Inches(0.9), bullets)


def main() -> None:
    inv = ROOT / "逆解析_降分最多10" / "01_m0.143"
    gen = ROOT / "生成图_提分最多10" / "01_p0.686"
    inv_o = (inv / "原文.txt").read_text(encoding="utf-8").strip()
    inv_r = (inv / "改写.txt").read_text(encoding="utf-8").strip()
    gen_o = (gen / "原文.txt").read_text(encoding="utf-8").strip()
    gen_r = (gen / "改写.txt").read_text(encoding="utf-8").strip()

    prs = Presentation(str(SRC)) if SRC.is_file() else Presentation()
    if not SRC.is_file():
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)

    # 已有四面时再追加，避免重复跑脚本叠很多页
    existing_titles = []
    for s in prs.slides:
        for sh in s.shapes:
            if sh.has_text_frame and sh.text_frame.text.strip():
                existing_titles.append(sh.text_frame.text.splitlines()[0])
                break
    if any("定性对照" in t for t in existing_titles):
        # 删掉旧定性页太麻烦；直接另存新文件覆盖重建四面+两页
        from pptx import Presentation as P2

        base = P2(str(SRC))
        # 若超过 4 页，只保留前 4 页：python-pptx 不便删页，改为重建 4+2
        # 这里直接新建完整 6 页中的定性两页附在原 4 页后；若已有定性则写到 *_定性.pptx
        out = Path(r"c:\Users\lsh\Desktop\记录10.1\极端案例生图对照_含定性.pptx")
        prs = Presentation(str(SRC))
    else:
        out = OUT

    add_qual_slide(
        prs,
        page_title="定性对照 · 逆解析（得分降低）",
        page_sub="同一组：原文总分 0.993 → 组内最高改写 0.850（Δ −0.143）。左侧原文描述，右侧改写描述；下方为各自生图。",
        left_title="原文 description",
        left_score="S_fp = 0.993",
        left_text=inv_o,
        left_img=inv / "原文.png",
        right_title="改写 description",
        right_score="S_fp = 0.850",
        right_text=inv_r,
        right_img=inv / "改写.png",
        bullets=[
            ("原文把领口、肩带金扣、红黑竖条、飘带、手帕摆、金项链、绿色手包、细带凉鞋一次写全，信息密、绑定清楚。", False),
            ("改写压成更短的柱形裙概括：少了「fluid midi / 多色飘带分层 / 走秀动态」等可见层次，细节密度掉了。", True),
            ("生图上两边都是红黑条纹裙，但改写版裙摆飘带更密、背景更偏建筑，少了原文那种秀场观众与面板呼应，整体辨识变钝。", True),
        ],
    )

    add_qual_slide(
        prs,
        page_title="定性对照 · 生成图（得分提升）",
        page_sub="同一组：原文总分 0.307 → 组内最高改写 0.993（Δ +0.686）。左侧原文描述，右侧改写描述；下方为各自生图。",
        left_title="原文 description",
        left_score="S_fp = 0.307",
        left_text=gen_o,
        left_img=gen / "原文.png",
        right_title="改写 description",
        right_score="S_fp = 0.993",
        right_text=gen_r,
        right_img=gen / "改写.png",
        bullets=[
            ("原文用 Theme / Concept 提纲，末句又写「same shell is plain ivory silk with no weave」，和编织外层互相打架。", True),
            ("改写删掉提纲壳和矛盾句，只保留：焦糖编织皮大衣、象牙白丝质裙、腰间打结皮带——身份就是编织面。", True),
            ("生图上改写版编织皮纹理清楚、大衣开合与内裙对比稳定；原文版更容易漂成光滑浅色外套，编织身份弱。", True),
        ],
    )

    prs.save(out)
    print(out)
    print("slides", len(prs.slides))


if __name__ == "__main__":
    main()
