"""Stardew Valley inspired theme tokens — colors, spacing, typography, shadows."""

# === Pixel wood / parchment palette ===
CREAM_BG = (214, 150, 82)
CREAM_BG_DARK = (156, 97, 47)
PARCHMENT = (243, 207, 139)
PARCHMENT_DARK = (210, 157, 83)
PARCHMENT_SHADOW = (154, 98, 50)

WOOD_DARK = (70, 38, 20)
WOOD_BROWN = (126, 74, 34)
WOOD_LIGHT = (181, 111, 52)
WOOD_HIGHLIGHT = (218, 151, 75)

GOLD = (224, 166, 62)
GOLD_DARK = (151, 95, 36)
GOLD_LIGHT = (250, 204, 98)

# === Semantic colors ===
SV_BLUE = (64, 131, 167)
SV_BLUE_DARK = (39, 83, 115)
SV_GREEN = (79, 143, 73)
SV_GREEN_DARK = (43, 83, 43)
SV_RED = (178, 75, 61)
SV_RED_DARK = (115, 47, 42)
SV_PURPLE = (121, 81, 154)

# === Cup ===
CUP_ORANGE = (219, 115, 54)
CUP_ORANGE_DARK = (158, 70, 36)
CUP_ORANGE_HIGHLIGHT = (242, 157, 82)

# === Text ===
TEXT_DARK = (58, 35, 22)
TEXT_BROWN = (89, 58, 34)
TEXT_LIGHT = (255, 232, 183)
TEXT_MUTED = (128, 88, 53)

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
