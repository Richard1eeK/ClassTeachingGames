"""Stardew Valley inspired theme tokens — colors, spacing, typography, shadows."""

# === Wood / Parchment palette ===
CREAM_BG = (252, 235, 196)
CREAM_BG_DARK = (240, 218, 170)
PARCHMENT = (255, 243, 214)
PARCHMENT_DARK = (240, 224, 188)
PARCHMENT_SHADOW = (210, 188, 145)

WOOD_DARK = (95, 65, 45)
WOOD_BROWN = (130, 90, 60)
WOOD_LIGHT = (175, 130, 90)
WOOD_HIGHLIGHT = (210, 170, 125)

GOLD = (245, 200, 80)
GOLD_DARK = (200, 155, 50)
GOLD_LIGHT = (255, 230, 140)

# === Semantic colors ===
SV_BLUE = (85, 160, 200)
SV_BLUE_DARK = (55, 120, 165)
SV_GREEN = (135, 180, 90)
SV_GREEN_DARK = (95, 140, 60)
SV_RED = (210, 100, 90)
SV_RED_DARK = (170, 70, 60)
SV_PURPLE = (165, 130, 195)

# === Cup (keep orange but warmer) ===
CUP_ORANGE = (235, 145, 75)
CUP_ORANGE_DARK = (190, 105, 50)
CUP_ORANGE_HIGHLIGHT = (255, 195, 130)

# === Text ===
TEXT_DARK = (75, 55, 40)
TEXT_BROWN = (110, 80, 55)
TEXT_LIGHT = (255, 248, 230)
TEXT_MUTED = (155, 130, 100)

# === Legacy aliases (so existing code keeps working during migration) ===
BG_COLOR = CREAM_BG
BLACK = TEXT_DARK
WHITE = (255, 248, 230)
GRAY = (200, 185, 155)
DARK_GRAY = WOOD_DARK
CANDY_PINK = SV_RED
CANDY_BLUE = SV_BLUE
CANDY_GREEN = SV_GREEN
CANDY_YELLOW = GOLD
CANDY_PURPLE = SV_PURPLE
CANDY_ORANGE = CUP_ORANGE
CANDY_RED = SV_RED
CUP_COLOR = CUP_ORANGE

# === Screen ===
SCREEN_W = 1024
SCREEN_H = 768

# === Spacing scale ===
SPACE_XS = 4
SPACE_SM = 8
SPACE_MD = 16
SPACE_LG = 24
SPACE_XL = 40
SPACE_XXL = 64

# === Radius ===
RADIUS_SM = 8
RADIUS_MD = 16
RADIUS_LG = 24
RADIUS_XL = 32

# === Typography (size scale) ===
FONT_DISPLAY = 56
FONT_TITLE = 40
FONT_HEADING = 32
FONT_BODY = 24
FONT_CAPTION = 18

# === Shadow (offset, blur-ish via repeated draw) ===
SHADOW_SM = (0, 2)
SHADOW_MD = (0, 4)
SHADOW_LG = (0, 6)

# === Animation tuning ===
SPRING_OVERSHOOT = 1.7  # for back/spring easing strength
