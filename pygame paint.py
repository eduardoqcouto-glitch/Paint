import pygame
pygame.init()

screen = pygame.display.set_mode((1250, 650))
paint = pygame.Surface((1250, 650), pygame.SRCALPHA)
pygame.display.set_caption("saBOR Paint")
font = pygame.font.SysFont("comicsansms", 25)

colors = {

# ===== Basics =====
"black": (0,0,0),
"white": (255,255,255),
"red": (255,0,0),
"green": (0,255,0),
"blue": (0,0,255),
"gray": (128,128,128),
"dark gray": (64,64,64),
"light gray": (192,192,192),

# ===== Reds =====
"dark red": (139,0,0),
"crimson": (220,20,60),
"firebrick": (178,34,34),
"salmon": (250,128,114),
"light salmon": (255,160,122),
"tomato": (255,99,71),
"coral": (255,127,80),
"scarlet": (255,36,0),
"ruby": (224,17,95),
"burgundy": (128,0,32),
"maroon": (128,0,0),
"blood red": (102,0,0),

# ===== Oranges =====
"orange": (255,165,0),
"dark orange": (255,140,0),
"burnt orange": (204,85,0),
"tangerine": (242,133,0),
"pumpkin": (255,117,24),
"apricot": (251,206,177),
"peach": (255,218,185),
"carrot": (237,145,33),

# ===== Yellows =====
"yellow": (255,255,0),
"gold": (255,215,0),
"khaki": (240,230,140),
"lemon": (255,250,205),
"mustard": (255,219,88),
"banana": (255,225,53),
"flax": (238,220,130),
"amber": (255,191,0),

# ===== Greens =====
"dark green": (0,100,0),
"lime": (0,255,0),
"forest green": (34,139,34),
"olive": (128,128,0),
"mint": (189,252,201),
"spring green": (0,255,127),
"sea green": (46,139,87),
"emerald": (80,200,120),
"jade": (0,168,107),
"chartreuse": (127,255,0),
"moss": (138,154,91),
"hunter green": (53,94,59),

# ===== Blues =====
"navy": (0,0,128),
"royal blue": (65,105,225),
"sky blue": (135,206,235),
"light blue": (173,216,230),
"midnight blue": (25,25,112),
"teal": (0,128,128),
"turquoise": (64,224,208),
"dodger blue": (30,144,255),
"steel blue": (70,130,180),
"powder blue": (176,224,230),
"deep sky blue": (0,191,255),
"cobalt": (0,71,171),
"cerulean": (42,82,190),

# ===== Purples =====
"purple": (128,0,128),
"violet": (238,130,238),
"plum": (221,160,221),
"indigo": (75,0,130),
"lavender": (230,230,250),
"orchid": (218,112,214),
"dark orchid": (153,50,204),
"amethyst": (153,102,204),
"mulberry": (197,75,140),

# ===== Pinks =====
"pink": (255,192,203),
"hot pink": (255,105,180),
"deep pink": (255,20,147),
"rose": (255,0,127),
"blush": (222,93,131),
"bubblegum": (255,193,204),
"magenta": (253, 61, 181),

# ===== Browns =====
"brown": (139,69,19),
"saddle brown": (139,69,19),
"chocolate": (210,105,30),
"tan": (210,180,140),
"beige": (245,245,220),
"wheat": (245,222,179),
"sienna": (160,82,45),
"umber": (99,81,71),
"coffee": (111,78,55),
"bronze": (205,127,50),
"copper": (184,115,51),

# ===== Cyans =====
"cyan": (0,255,255),
"aqua": (77,233,217),
"light cyan": (224,255,255),
"aquamarine": (127,255,212),
"dark turquoise": (0,206,209),
"medium turquoise": (72,209,204),

# ===== Whites / Off-Whites =====
"ivory": (255,255,240),
"cream": (255,253,208),
"snow": (255,250,250),
"ghost white": (248,248,255),
"gainsboro": (220,220,220),
"platinum": (229,228,226),

# ===== Extras =====
"azure": (240,255,255),
"periwinkle": (204,204,255),
"rose gold": (183,110,121),
"goldenrod": (218,165,32),
"dark goldenrod": (184,134,11),
"slate gray": (112,128,144),
"light slate gray": (119,136,153),
"dim gray": (105,105,105)

}

current_color = colors['black']
user_text = ""
typing = False
size = 10
clock = pygame.time.Clock()
countdown = 300
rgb_mode = False
hex_mode = False

cursor_visible = True
cursor_timer = 0

running = True
while running:
    screen.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_t and not typing:
                typing = True  

            elif typing:
                if event.key == pygame.K_RETURN:

                    if rgb_mode:
                        try:
                            r, g, b = map(int, user_text.split(","))
            
                            r = max(0, min(255, r))
                            g = max(0, min(255, g))
                            b = max(0, min(255, b))

                            current_color = (r, g, b)

                        except:
                            print("Use format: 200,30,60")

                        rgb_mode = False
                    elif hex_mode:
                        try:
                            hex_color = user_text.strip("#")

                            if len(hex_color) == 6 or (len(hex_color == 7) and hex_color.split(0) == '#'):
                                r = int(hex_color[0:2], 16)
                                g = int(hex_color[2:4], 16)
                                b = int(hex_color[4:6], 16)

                                current_color = (r, g, b)
                                hex_mode = False
                            else:
                                print("Use format: F4D5B9")

                        except:
                            print("Invalid HEX color")

                            hex_mode = False
                            
                    elif user_text.lower() in colors:
                        current_color = colors[user_text.lower()]

                    elif user_text.isdigit():
                        size = int(user_text)
                    elif user_text.lower() == 'rgb':
                        rgb_mode = True
                        user_text = ""
                    elif user_text.lower() == 'hex':
                        hex_mode = True
                        user_text = ""
                    user_text = ""
                    typing = False
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    user_text += event.unicode
            
            elif event.key == pygame.K_BACKSPACE:
                paint.fill((0, 0, 0, 0))
            elif event.key == pygame.K_RSHIFT:
                countdown = 300
    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()[0]

    if mouse_pressed:
        if last_pos is not None:
            pygame.draw.line(paint, current_color, last_pos, mouse_pos, size*2)
            pygame.draw.circle(paint, current_color, mouse_pos, size)
        last_pos = mouse_pos
    else:
        last_pos = None

    screen.blit(paint, (0, 0))
    if typing:
        screen.fill((0, 0, 0))
        y_offset = 80
        x_offset = 20
        pygame.draw.rect(screen, (255, 255, 255), (20, 80, 80, 30))
        text_surface = font.render(f"size {str(size)}", True, (255, 255, 255))
        screen.blit(text_surface, (600, 35))
        text_surface = font.render(f"RGB Mode: {rgb_mode}", True, (255, 255, 255))
        screen.blit(text_surface, (340, 50))
        text_surface = font.render(f"HEX Mode {hex_mode}", True, (255, 255, 255))
        screen.blit(text_surface, (340, 20))
        for color_name in colors:
            if y_offset > 600:
                y_offset = 80
                x_offset += 200 
            text_surface = font.render(color_name, True, (colors[color_name]))
            screen.blit(text_surface, (x_offset, y_offset))
            y_offset += 30
        pygame.draw.rect(screen, (200, 200, 200), (20, 20, 300, 50))
        pygame.draw.rect(screen, (0, 0, 0), (20, 20, 300, 50), 2)

        cursor_timer += clock.get_time()
        if cursor_timer > 500:
            cursor_visible = not cursor_visible
            cursor_timer = 0

        display_text = user_text
        if cursor_visible:
            display_text += "|"

        text_surface = font.render(display_text, True, (0, 0, 0))
        screen.blit(text_surface, (30, 30))
    
    else:
        if countdown > 0:
            info = font.render("Press T to type a color, change the size, activate RGB mode to add custom colors by digiting 'rgb'", True, (0, 0, 0))
            screen.blit(info, (20, 20))
            info2 = font.render("or add a custom HEX color by digiting 'HEX'", True, (0, 0, 0))
            screen.blit(info2, (20, 50))
            countdown -= 1

    pygame.display.flip()
    clock.tick(60)

pygame.quit()