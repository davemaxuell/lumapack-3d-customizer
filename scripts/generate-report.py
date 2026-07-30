import argparse
import os
import shutil
from pathlib import Path

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "output" / "pdf" / "LumaPack_3D_Project_Report.pdf"
PUBLIC_PATH = ROOT / "public" / "report" / "LumaPack_3D_Project_Report.pdf"
HERO_IMAGE = ROOT / "output" / "playwright" / "hero-desktop.png"
SYSTEM_IMAGE = ROOT / "output" / "playwright" / "system-desktop.png"
MOBILE_IMAGE = ROOT / "output" / "playwright" / "hero-mobile.png"

PAGE_W, PAGE_H = A4
INK = HexColor("#11130F")
INK_SOFT = HexColor("#252921")
PAPER = HexColor("#F1F1E8")
PAPER_DARK = HexColor("#E3E4D8")
SIGNAL = HexColor("#C9DD3C")
SIGNAL_DARK = HexColor("#7C8C11")
MUTED = HexColor("#6A6D63")
WHITE = HexColor("#F8F8F0")
LINE = HexColor("#C7C9BE")


def register_fonts():
    regular_candidates = [
        Path("C:/Windows/Fonts/malgun.ttf"),
        Path("C:/Windows/Fonts/NanumGothic.ttf"),
    ]
    bold_candidates = [
        Path("C:/Windows/Fonts/malgunbd.ttf"),
        Path("C:/Windows/Fonts/NanumGothicBold.ttf"),
    ]
    regular = next((item for item in regular_candidates if item.exists()), None)
    bold = next((item for item in bold_candidates if item.exists()), None)
    if not regular or not bold:
        raise FileNotFoundError("A Korean TrueType font is required to generate the report.")
    pdfmetrics.registerFont(TTFont("Korean", str(regular)))
    pdfmetrics.registerFont(TTFont("Korean-Bold", str(bold)))


def wrap_text(text, font_name, font_size, max_width):
    lines = []
    current = ""
    for word in text.split():
        candidate = word if not current else f"{current} {word}"
        if pdfmetrics.stringWidth(candidate, font_name, font_size) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(c, text, x, y, width, font_name="Korean", font_size=9, leading=15, color=INK):
    c.setFillColor(color)
    c.setFont(font_name, font_size)
    for line in wrap_text(text, font_name, font_size, width):
        c.drawString(x, y, line)
        y -= leading
    return y


def draw_cropped_image(c, image_path, x, y, width, height, anchor_x=0.5, anchor_y=0.5):
    image = ImageReader(str(image_path))
    image_w, image_h = image.getSize()
    scale = max(width / image_w, height / image_h)
    draw_w = image_w * scale
    draw_h = image_h * scale
    draw_x = x - (draw_w - width) * anchor_x
    draw_y = y - (draw_h - height) * anchor_y
    path = c.beginPath()
    path.rect(x, y, width, height)
    c.saveState()
    c.clipPath(path, stroke=0, fill=0)
    c.drawImage(image, draw_x, draw_y, draw_w, draw_h, mask="auto")
    c.restoreState()


def draw_page_header(c, page_number, section):
    c.setStrokeColor(LINE)
    c.setLineWidth(0.5)
    c.line(36, PAGE_H - 38, PAGE_W - 36, PAGE_H - 38)
    c.setFillColor(INK)
    c.setFont("Korean-Bold", 7)
    c.drawString(36, PAGE_H - 29, f"{page_number:02d} / {section.upper()}")
    c.setFillColor(MUTED)
    c.setFont("Korean", 7)
    c.drawRightString(PAGE_W - 36, PAGE_H - 29, "LUMAPACK 01 · FINAL PROJECT 23-1")


def draw_footer(c, page_number):
    c.setFillColor(MUTED)
    c.setFont("Korean", 6.5)
    c.drawString(36, 23, "THREE.JS · GLB · WEBGL · NETLIFY")
    c.drawRightString(PAGE_W - 36, 23, f"{page_number:02d}")


def draw_pill(c, x, y, text, fill=SIGNAL, text_color=INK):
    width = pdfmetrics.stringWidth(text, "Korean-Bold", 7) + 18
    c.setFillColor(fill)
    c.roundRect(x, y - 5, width, 17, 8.5, fill=1, stroke=0)
    c.setFillColor(text_color)
    c.setFont("Korean-Bold", 7)
    c.drawString(x + 9, y, text)
    return width


def draw_qr(c, url, x, y, size):
    qr = QrCodeWidget(url)
    bounds = qr.getBounds()
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    drawing = Drawing(size, size, transform=[size / width, 0, 0, size / height, 0, 0])
    drawing.add(qr)
    renderPDF.draw(drawing, c, x, y)


def build_report(netlify_url, github_url):
    for required in (HERO_IMAGE, SYSTEM_IMAGE, MOBILE_IMAGE):
        if not required.exists():
            raise FileNotFoundError(f"Missing screenshot: {required}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_PATH.parent.mkdir(parents=True, exist_ok=True)
    register_fonts()
    c = canvas.Canvas(str(OUTPUT_PATH), pagesize=A4)
    c.setTitle("LumaPack 01 - 3D Web App Final Project")
    c.setAuthor("Final Project 23-1")
    c.setSubject("Three.js 3D product customizer project report")

    # 01 Cover
    c.setFillColor(INK)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(SIGNAL)
    c.rect(0, PAGE_H - 14, PAGE_W, 14, fill=1, stroke=0)
    c.setStrokeColor(HexColor("#43483B"))
    for x in range(36, int(PAGE_W), 52):
        c.line(x, 0, x, PAGE_H)
    for y in range(50, int(PAGE_H), 52):
        c.line(0, y, PAGE_W, y)
    c.setFillColor(WHITE)
    c.setFont("Korean-Bold", 11)
    c.drawString(42, PAGE_H - 66, "LUMA / OBJECTS")
    c.setFillColor(SIGNAL)
    c.setFont("Korean", 7)
    c.drawRightString(PAGE_W - 42, PAGE_H - 66, "FINAL PROJECT · 23-1 · 2026")

    c.setFillColor(WHITE)
    c.setFont("Korean-Bold", 50)
    c.drawString(40, PAGE_H - 205, "LUMA/")
    c.drawString(40, PAGE_H - 258, "PACK 01")
    c.setFillColor(SIGNAL)
    c.rect(238, PAGE_H - 216, 8, 63, fill=1, stroke=0)

    c.setFillColor(HexColor("#A7AD9D"))
    c.setFont("Korean", 10)
    c.drawString(43, PAGE_H - 298, "3D PRODUCT CUSTOMIZER")
    c.setFont("Korean", 8)
    c.drawString(43, PAGE_H - 319, "Rotate · Recolor · Inspect · Deploy")

    draw_cropped_image(c, HERO_IMAGE, 40, 156, PAGE_W - 80, 262, anchor_x=0.23, anchor_y=0.48)
    c.setStrokeColor(SIGNAL)
    c.setLineWidth(1)
    c.rect(40, 156, PAGE_W - 80, 262, fill=0, stroke=1)

    c.setFillColor(WHITE)
    c.setFont("Korean-Bold", 8)
    c.drawString(42, 119, "NETLIFY")
    c.drawString(42, 82, "GITHUB")
    c.setFillColor(HexColor("#A7AD9D"))
    c.setFont("Korean", 7)
    c.drawString(118, 119, netlify_url)
    c.drawString(118, 82, github_url)
    c.linkURL(netlify_url, (116, 111, PAGE_W - 42, 128), relative=0)
    c.linkURL(github_url, (116, 74, PAGE_W - 42, 91), relative=0)
    c.setFillColor(SIGNAL)
    c.setFont("Korean-Bold", 7)
    c.drawRightString(PAGE_W - 42, 38, "DESIGNED & BUILT IN SEOUL")
    c.showPage()

    # 02 Overview
    c.setFillColor(PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    draw_page_header(c, 2, "Project overview")
    draw_pill(c, 36, PAGE_H - 78, "PROJECT SUMMARY")
    c.setFillColor(INK)
    c.setFont("Korean-Bold", 28)
    c.drawString(36, PAGE_H - 126, "도시의 이동을 위한")
    c.setFillColor(SIGNAL_DARK)
    c.drawString(36, PAGE_H - 158, "인터랙티브 3D 제품 경험")
    draw_wrapped(
        c,
        "LumaPack 01은 모듈형 백팩을 360도로 탐색하고 네 가지 컬러를 실시간으로 비교할 수 있는 Three.js 기반 제품 상세 페이지입니다. 제품을 단순히 보여주는 것을 넘어 기능을 발견하고 구매 행동까지 이어지는 하나의 쇼핑 경험으로 설계했습니다.",
        36,
        PAGE_H - 194,
        PAGE_W - 72,
        font_size=10,
        leading=17,
        color=INK_SOFT,
    )
    draw_cropped_image(c, HERO_IMAGE, 36, 307, PAGE_W - 72, 270, anchor_x=0.5, anchor_y=0.4)
    c.setFillColor(INK)
    c.rect(36, 268, PAGE_W - 72, 39, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Korean-Bold", 8)
    c.drawString(49, 284, "FIG. 01")
    c.setFont("Korean", 7)
    c.drawString(105, 284, "1440 × 900 프로덕션 빌드 화면")

    columns = [
        ("GOAL", "3D 모델, UI, 인터랙션, 배포를 하나의 완성된 제품 페이지로 연결"),
        ("AUDIENCE", "디자인과 기능을 함께 비교하려는 도시형 아웃도어 소비자"),
        ("OUTPUT", "Netlify 라이브 사이트, GitHub 코드, 한국어 프로젝트 회고 PDF"),
    ]
    col_w = (PAGE_W - 72) / 3
    for index, (label, text) in enumerate(columns):
        x = 36 + index * col_w
        c.setStrokeColor(LINE)
        c.rect(x, 70, col_w, 165, fill=0, stroke=1)
        c.setFillColor(SIGNAL_DARK)
        c.setFont("Korean-Bold", 7)
        c.drawString(x + 13, 211, f"0{index + 1} / {label}")
        draw_wrapped(c, text, x + 13, 181, col_w - 26, font_size=9, leading=15)
    draw_footer(c, 2)
    c.showPage()

    # 03 Features
    c.setFillColor(PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    draw_page_header(c, 3, "Core interactions")
    c.setFillColor(INK)
    c.setFont("Korean-Bold", 30)
    c.drawString(36, PAGE_H - 105, "제품을 보는 세 가지 방법")
    draw_wrapped(
        c,
        "각 기능은 Three.js 씬의 상태와 HTML 인터페이스 상태를 연결해 즉각적인 피드백을 제공합니다.",
        36,
        PAGE_H - 135,
        PAGE_W - 72,
        font_size=9,
        leading=14,
        color=MUTED,
    )

    features = [
        ("01", "ROTATE", "OrbitControls로 자유 회전·줌을 제공하고, 버튼으로 정확히 45도씩 회전합니다. 자동 회전과 초기화도 지원합니다."),
        ("02", "RECOLOR", "GLB의 MAT_SHELL과 MAT_SHELL_EDGE 재질을 분리해 네 가지 셸 컬러를 실시간으로 변경합니다."),
        ("03", "DISCOVER", "3D 좌표를 매 프레임 2D로 투영한 핫스폿이 모델을 따라 움직이며 소재와 기능 정보를 보여줍니다."),
    ]
    top = PAGE_H - 190
    card_h = 102
    for index, (number, title, text) in enumerate(features):
        y = top - index * (card_h + 12) - card_h
        c.setFillColor(INK if index == 0 else (SIGNAL if index == 2 else PAPER_DARK))
        c.roundRect(36, y, PAGE_W - 72, card_h, 5, fill=1, stroke=0)
        text_color = WHITE if index == 0 else INK
        c.setFillColor(SIGNAL if index == 0 else INK)
        c.setFont("Korean-Bold", 8)
        c.drawString(51, y + card_h - 24, number)
        c.setFillColor(text_color)
        c.setFont("Korean-Bold", 17)
        c.drawString(92, y + card_h - 31, title)
        draw_wrapped(c, text, 92, y + card_h - 56, PAGE_W - 150, font_size=8.5, leading=14, color=text_color)

    c.setFillColor(INK)
    c.setFont("Korean-Bold", 8)
    c.drawString(36, 234, "USER FLOW")
    nodes = [("LOAD", "GLB"), ("INSPECT", "360°"), ("CUSTOMIZE", "4 COLORS"), ("ADD", "FIELD KIT")]
    node_w = 105
    gap = (PAGE_W - 72 - node_w * 4) / 3
    for index, (title, subtitle) in enumerate(nodes):
        x = 36 + index * (node_w + gap)
        c.setFillColor(PAPER_DARK)
        c.roundRect(x, 142, node_w, 67, 4, fill=1, stroke=0)
        c.setFillColor(SIGNAL_DARK)
        c.setFont("Korean-Bold", 7)
        c.drawString(x + 10, 186, f"0{index + 1}")
        c.setFillColor(INK)
        c.setFont("Korean-Bold", 10)
        c.drawString(x + 10, 166, title)
        c.setFillColor(MUTED)
        c.setFont("Korean", 7)
        c.drawString(x + 10, 151, subtitle)
        if index < len(nodes) - 1:
            c.setStrokeColor(SIGNAL_DARK)
            c.line(x + node_w + 4, 175, x + node_w + gap - 4, 175)
            c.line(x + node_w + gap - 8, 179, x + node_w + gap - 4, 175)
            c.line(x + node_w + gap - 8, 171, x + node_w + gap - 4, 175)
    draw_footer(c, 3)
    c.showPage()

    # 04 Technical stack
    c.setFillColor(INK)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setStrokeColor(HexColor("#40443A"))
    c.line(36, PAGE_H - 38, PAGE_W - 36, PAGE_H - 38)
    c.setFillColor(SIGNAL)
    c.setFont("Korean-Bold", 7)
    c.drawString(36, PAGE_H - 29, "04 / TECHNICAL SYSTEM")
    c.setFillColor(HexColor("#8F9588"))
    c.setFont("Korean", 7)
    c.drawRightString(PAGE_W - 36, PAGE_H - 29, "LUMAPACK 01 · FINAL PROJECT 23-1")

    c.setFillColor(WHITE)
    c.setFont("Korean-Bold", 29)
    c.drawString(36, PAGE_H - 101, "모델에서 배포까지")
    c.setFillColor(SIGNAL)
    c.drawString(36, PAGE_H - 134, "하나의 재현 가능한 파이프라인")

    pipeline = [
        ("01", "GENERATE", "Three.js geometry\nGLTFExporter"),
        ("02", "LOAD", "GLTFLoader\nMaterial roles"),
        ("03", "RENDER", "WebGL\nrequestAnimationFrame"),
        ("04", "INTERACT", "OrbitControls\nDOM state"),
        ("05", "SHIP", "Vite\nNetlify CDN"),
    ]
    node_w = 91
    gap = 9
    start_x = 36
    y = PAGE_H - 270
    for index, (number, title, detail) in enumerate(pipeline):
        x = start_x + index * (node_w + gap)
        c.setStrokeColor(SIGNAL if index in (0, 4) else HexColor("#60665A"))
        c.roundRect(x, y, node_w, 90, 4, fill=0, stroke=1)
        c.setFillColor(SIGNAL)
        c.setFont("Korean-Bold", 7)
        c.drawString(x + 9, y + 70, number)
        c.setFillColor(WHITE)
        c.setFont("Korean-Bold", 9)
        c.drawString(x + 9, y + 51, title)
        c.setFillColor(HexColor("#979D90"))
        c.setFont("Korean", 6.5)
        for line_index, line in enumerate(detail.splitlines()):
            c.drawString(x + 9, y + 29 - line_index * 11, line)
        if index < 4:
            c.setStrokeColor(HexColor("#60665A"))
            c.line(x + node_w, y + 45, x + node_w + gap, y + 45)

    stack_rows = [
        ("3D SCENE", "Scene · PerspectiveCamera · Lights · Shadows · PMREM"),
        ("MODEL", "3.5MB GLB · 6 material roles · no external textures"),
        ("PERFORMANCE", "Pixel ratio ≤ 2 · visibility pause · resource disposal"),
        ("ACCESSIBILITY", "Semantic HTML · ARIA · focus states · reduced motion"),
        ("DEPLOY", "Vite production build · immutable asset cache · Netlify"),
    ]
    table_y = PAGE_H - 430
    c.setFillColor(WHITE)
    c.setFont("Korean-Bold", 8)
    c.drawString(36, table_y + 28, "SYSTEM SPECIFICATION")
    for index, (label, value) in enumerate(stack_rows):
        row_y = table_y - index * 49
        c.setStrokeColor(HexColor("#3E433A"))
        c.line(36, row_y, PAGE_W - 36, row_y)
        c.setFillColor(SIGNAL)
        c.setFont("Korean-Bold", 7)
        c.drawString(36, row_y - 29, label)
        c.setFillColor(HexColor("#B8BDB0"))
        c.setFont("Korean", 8)
        c.drawString(150, row_y - 29, value)
    c.setStrokeColor(HexColor("#3E433A"))
    c.line(36, table_y - len(stack_rows) * 49, PAGE_W - 36, table_y - len(stack_rows) * 49)

    c.setFillColor(HexColor("#8F9588"))
    c.setFont("Korean", 7)
    c.drawString(36, 23, "THREE.JS · GLB · WEBGL · NETLIFY")
    c.drawRightString(PAGE_W - 36, 23, "04")
    c.showPage()

    # 05 Responsive UI
    c.setFillColor(PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    draw_page_header(c, 5, "Responsive UI")
    c.setFillColor(INK)
    c.setFont("Korean-Bold", 29)
    c.drawString(36, PAGE_H - 103, "같은 제품, 다른 화면")
    draw_wrapped(
        c,
        "정보 우선순위는 유지하면서 데스크톱의 비대칭 분할 레이아웃을 모바일의 자연스러운 세로 흐름으로 재구성했습니다.",
        36,
        PAGE_H - 133,
        PAGE_W - 72,
        font_size=9,
        leading=15,
        color=MUTED,
    )
    draw_cropped_image(c, SYSTEM_IMAGE, 36, 338, 344, 300, anchor_x=0.5, anchor_y=0.48)
    c.setStrokeColor(LINE)
    c.rect(36, 338, 344, 300, fill=0, stroke=1)
    draw_cropped_image(c, MOBILE_IMAGE, 402, 247, 156, 391, anchor_x=0.5, anchor_y=0.04)
    c.setStrokeColor(INK)
    c.rect(402, 247, 156, 391, fill=0, stroke=1)
    c.setFillColor(INK)
    c.setFont("Korean-Bold", 7)
    c.drawString(36, 322, "DESKTOP / 1440 × 900")
    c.drawString(402, 231, "MOBILE / 390 × 844")

    notes = [
        ("LAYOUT", "데스크톱 2열 → 모바일 1열"),
        ("CONTROL", "터치 타깃 34px 이상, 상단 고정 배치"),
        ("TYPE", "유동형 크기와 한국어 줄바꿈 최적화"),
        ("MOTION", "reduced-motion 환경에서 자동 회전 해제"),
    ]
    y = 170
    for index, (label, text) in enumerate(notes):
        x = 36 + (index % 2) * 261
        row_y = y - (index // 2) * 58
        c.setStrokeColor(LINE)
        c.line(x, row_y + 26, x + 238, row_y + 26)
        c.setFillColor(SIGNAL_DARK)
        c.setFont("Korean-Bold", 7)
        c.drawString(x, row_y + 10, label)
        c.setFillColor(INK)
        c.setFont("Korean", 8)
        c.drawString(x + 63, row_y + 10, text)
    draw_footer(c, 5)
    c.showPage()

    # 06 Retrospective
    c.setFillColor(PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    draw_page_header(c, 6, "Retrospective")
    draw_pill(c, 36, PAGE_H - 78, "WHAT I LEARNED")
    c.setFillColor(INK)
    c.setFont("Korean-Bold", 29)
    c.drawString(36, PAGE_H - 126, "3D를 화면이 아닌")
    c.setFillColor(SIGNAL_DARK)
    c.drawString(36, PAGE_H - 158, "제품 경험으로 만드는 법")

    reflections = [
        (
            "어려웠던 점",
            "GLB 내부 재질과 웹 UI의 색상 상태를 정확히 연결하고, 모델이 회전해도 HTML 핫스폿이 올바른 위치를 따라가게 만드는 것이 가장 어려웠습니다.",
        ),
        (
            "해결 방법",
            "재질을 역할별 이름으로 설계해 내보내고 로딩 후 이름으로 수집했습니다. 핫스폿은 3D 좌표에 모델 월드 행렬을 적용한 뒤 카메라 좌표로 투영했습니다.",
        ),
        (
            "배운 점",
            "3D 품질은 메시만으로 결정되지 않았습니다. 카메라 거리, 톤 매핑, 조명, 로딩 피드백, 정보 구조가 함께 맞아야 제품처럼 느껴진다는 것을 배웠습니다.",
        ),
        (
            "다음 단계",
            "Draco 압축, KTX2 텍스처, 실제 결제 흐름, 사용자 커스텀 각인과 AR 미리보기를 추가해 더 완성도 높은 커머스 경험으로 발전시키고 싶습니다.",
        ),
    ]
    card_w = (PAGE_W - 84) / 2
    card_h = 128
    for index, (title, text) in enumerate(reflections):
        x = 36 + (index % 2) * (card_w + 12)
        y = PAGE_H - 342 - (index // 2) * (card_h + 12)
        c.setFillColor(INK if index == 0 else PAPER_DARK)
        c.roundRect(x, y, card_w, card_h, 5, fill=1, stroke=0)
        color = WHITE if index == 0 else INK
        c.setFillColor(SIGNAL if index == 0 else SIGNAL_DARK)
        c.setFont("Korean-Bold", 7)
        c.drawString(x + 14, y + card_h - 22, f"0{index + 1}")
        c.setFillColor(color)
        c.setFont("Korean-Bold", 12)
        c.drawString(x + 42, y + card_h - 27, title)
        draw_wrapped(c, text, x + 14, y + card_h - 54, card_w - 28, font_size=8, leading=13, color=color)

    c.setFillColor(INK)
    c.roundRect(36, 78, PAGE_W - 72, 167, 6, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Korean-Bold", 12)
    c.drawString(52, 217, "LIVE PROJECT")
    c.setFillColor(HexColor("#9FA598"))
    c.setFont("Korean", 7)
    c.drawString(52, 199, "QR 코드를 스캔하거나 아래 링크를 클릭하세요.")
    draw_qr(c, netlify_url, 52, 96, 84)
    draw_qr(c, github_url, 157, 96, 84)
    c.setFillColor(SIGNAL)
    c.setFont("Korean-Bold", 7)
    c.drawString(52, 87, "NETLIFY")
    c.drawString(157, 87, "GITHUB")
    c.setFillColor(WHITE)
    c.setFont("Korean-Bold", 8)
    c.drawString(274, 161, "DEPLOY URL")
    c.drawString(274, 117, "SOURCE CODE")
    c.setFillColor(HexColor("#A5AA9D"))
    c.setFont("Korean", 6.5)
    c.drawString(274, 146, netlify_url)
    c.drawString(274, 102, github_url)
    c.linkURL(netlify_url, (272, 137, PAGE_W - 52, 163), relative=0)
    c.linkURL(github_url, (272, 93, PAGE_W - 52, 119), relative=0)
    draw_footer(c, 6)
    c.save()

    shutil.copy2(OUTPUT_PATH, PUBLIC_PATH)
    print(f"Generated {OUTPUT_PATH}")
    print(f"Copied to {PUBLIC_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Generate the LumaPack project report PDF.")
    parser.add_argument(
        "--netlify-url",
        default=os.environ.get("LUMAPACK_NETLIFY_URL", "https://example.netlify.app"),
    )
    parser.add_argument(
        "--github-url",
        default=os.environ.get(
            "LUMAPACK_GITHUB_URL",
            "https://github.com/davemaxuell/lumapack-3d-customizer",
        ),
    )
    args = parser.parse_args()
    build_report(args.netlify_url, args.github_url)


if __name__ == "__main__":
    main()
