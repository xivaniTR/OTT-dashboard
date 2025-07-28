# config.py

TIMEZONE = "Asia/Kolkata"

PASTEL_VIBE_PALETTE = [
    "#A7C7E7",  # pastel blue
    "#F7CAC9",  # pastel pink
    "#B5EAD7",  # pastel green
    "#FFFACD",  # pastel yellow
    "#FFDAC1",  # pastel peach
    "#E2F0CB",  # pastel mint
    "#CBAACB",  # pastel purple
    "#FFB7B2",  # pastel coral
]

PASTEL_THEME = {
    "backgroundColor": "#F8F9FB",
    "font": "'Nunito Sans', 'Arial', sans-serif",
    "gridColor": "#E6E6E6",
    "palette": PASTEL_VIBE_PALETTE,
}

CHART_TEMPLATE = {
    "background": PASTEL_THEME["backgroundColor"],
    "font": PASTEL_THEME["font"],
    "grid": True,
    "gridColor": PASTEL_THEME["gridColor"],
    "palette": PASTEL_THEME["palette"],
    "titleColor": "#333333",
    "labelColor": "#444444",
    "legendPosition": "top",
} 