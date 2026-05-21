"""Stardew Valley inspired theme tokens — colors, spacing, typography, shadows."""

# === Champagne Farm light-luxury pixel palette ===
CREAM_BG = (246, 234, 214)
CREAM_BG_DARK = (224, 200, 164)
PARCHMENT = (255, 242, 216)
PARCHMENT_DARK = (239, 216, 176)
PARCHMENT_SHADOW = (198, 163, 111)

WOOD_DARK = (82, 61, 45)
WOOD_BROWN = (184, 144, 96)
WOOD_LIGHT = (226, 184, 113)
WOOD_HIGHLIGHT = (253, 218, 153)

GOLD = (216, 167, 80)
GOLD_DARK = (148, 100, 49)
GOLD_LIGHT = (255, 224, 151)

# === Semantic colors ===
SV_BLUE = (126, 166, 184)
SV_BLUE_DARK = (73, 108, 124)
SV_GREEN = (143, 183, 170)
SV_GREEN_DARK = (82, 121, 107)
SV_RED = (197, 112, 94)
SV_RED_DARK = (129, 66, 57)
SV_PURPLE = (157, 132, 178)

# === Cup ===
CUP_ORANGE = (210, 142, 92)
CUP_ORANGE_DARK = (143, 81, 55)
CUP_ORANGE_HIGHLIGHT = (239, 181, 121)

# === Text ===
TEXT_DARK = (69, 48, 32)
TEXT_BROWN = (101, 73, 47)
TEXT_LIGHT = (255, 250, 236)
TEXT_MUTED = (141, 110, 76)

# === Soft pixel shadows ===
SHADOW_COLOR = (142, 108, 72)
SHADOW_DARK = (82, 61, 45)
INTRO_OVERLAY = (82, 61, 45, 54)

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
SPACE_MD = 12
SPACE_LG = 16
SPACE_XL = 24
SPACE_XXL = 36

# === Radius (kept tiny for old fallback paths) ===
RADIUS_SM = 0
RADIUS_MD = 2
RADIUS_LG = 4
RADIUS_XL = 6

# === Typography (size scale) ===
FONT_DISPLAY = 48
FONT_TITLE = 34
FONT_HEADING = 26
FONT_BODY = 20
FONT_CAPTION = 15

# === Shadow (offset, blur-ish via repeated draw) ===
SHADOW_SM = (0, 2)
SHADOW_MD = (0, 4)
SHADOW_LG = (0, 6)

# === Animation tuning ===
SPRING_OVERSHOOT = 1.7  # for back/spring easing strength
