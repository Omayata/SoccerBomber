import turtle
import time
import sys
import math
import minecraft_font
import winsound
import os

# ================= AUDIO SYSTEM (Pre-setup) =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_FILES = {
    "bg2": "Start.wav",
    "select": "switch.wav",
    "enter": "EnterStart.wav",
    "game_start": "Count.wav",
    "kick": "Kick.wav",
    "ultimate": "ultimate.wav",
    "win": "END.wav",
    "goal": "Goal.wav",
    "game_music": "Start.wav", 
}

def sound_path(name):
    return os.path.join(BASE_DIR, SOUND_FILES[name])

def play_sound(name, loop=False):
    try:
        path = sound_path(name)
        if not os.path.exists(path):
            print(f"[AUDIO] Sound file not found: {path}")
            return
        flags = winsound.SND_FILENAME | winsound.SND_ASYNC
        if loop:
            flags |= winsound.SND_LOOP
        winsound.PlaySound(path, flags)
    except Exception as e:
        print(f"[AUDIO] Error playing sound {name}: {e}")

def play_bg2_music():
    try:
        winsound.PlaySound(None, winsound.SND_PURGE)
    except Exception:
        pass
    play_sound("bg2", loop=True)

def stop_all_sound():
    try:
        winsound.PlaySound(None, winsound.SND_PURGE)
    except Exception:
        pass

start_prompt_visible = True
last_start_blink_time = time.time()
START_BLINK_INTERVAL = 0.5
last_kick_sound_time = 0.0
KICK_SOUND_COOLDOWN = 0.12

def play_kick_sound_once():
    global last_kick_sound_time
    now = time.time()
    if now - last_kick_sound_time >= KICK_SOUND_COOLDOWN:
        play_sound("kick")
        last_kick_sound_time = now

# =====================================================================
# FORMAT OF BASELINE KITS: Section 1: Screen Setup
# Configures window dimensions, title, background color, tracer settings...
# =====================================================================
screen = turtle.Screen()
screen.title("2D Turtle Football - Soccer Bomber Edition")
screen.setup(width=1000, height=600)
screen.bgcolor("skyblue")
screen.tracer(0) 

# --- Helper functions to create custom shapes (Part of initial setup) ---
def _regular_polygon(n, radius, rotation_deg=0.0, center=(0, 0)):
    cx, cy = center
    rot = math.radians(rotation_deg)
    return [(cx + radius * math.cos(rot + 2 * math.pi * i / n),
             cy + radius * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]

def _tip_triangle(inner_r, outer_r, angle_deg, half_angle_deg):
    angle = math.radians(angle_deg)
    apex = (inner_r * math.cos(angle), inner_r * math.sin(angle))
    a1 = math.radians(angle_deg - half_angle_deg)
    a2 = math.radians(angle_deg + half_angle_deg)
    base1 = (outer_r * math.cos(a1), outer_r * math.sin(a1))
    base2 = (outer_r * math.cos(a2), outer_r * math.sin(a2))
    return [apex, base1, base2]

def _make_soccerball_shape(base_color, radius=10, pattern_color="black"):
    shape = turtle.Shape("compound")
    shape.addcomponent(_regular_polygon(40, radius), base_color, "black")
    center_pent_r = radius * 0.38
    shape.addcomponent(_regular_polygon(5, center_pent_r, rotation_deg=90), pattern_color, pattern_color)
    pent_edge_r = center_pent_r * math.cos(math.pi / 5)
    gap = radius * 0.30
    for i in range(5):
        angle_deg = 90 + 36 + i * 72
        shape.addcomponent(_tip_triangle(pent_edge_r + gap, radius * 0.95, angle_deg, half_angle_deg=14), pattern_color, pattern_color)
    return shape

screen.register_shape("soccerball", _make_soccerball_shape("white"))

COLOR_SKIN, COLOR_HAIR, COLOR_EYE, COLOR_PANTS = "#F4C89B", "#3B2A20", "#111111", "#FFFFFF"

def _face_forward(right, up): return (-up, right)
def _stand_leg(x_from, x_to, lift=0): return [(x_from, -10 + lift), (x_to, -10 + lift), (x_to, -3), (x_from, -3)]
def _kick_leg(hip_x, side):
    s = 1 if side == "right" else -1
    return [(hip_x, -3), (hip_x + 2 * s, -4), (hip_x + 12 * s, 1), (hip_x + 8 * s, 4), (hip_x - 1 * s, -1)]

def _make_player_shape(shirt_color, pants_color=COLOR_PANTS, head_color=COLOR_SKIN, hair_color=COLOR_HAIR, eye_color=COLOR_EYE, kick_side=None, lift_side=None):
    shape = turtle.Shape("compound")
    torso_pts = [(-6, -3), (6, -3), (6, 3), (-6, 3)]
    shape.addcomponent([_face_forward(x, y) for x, y in torso_pts], shirt_color, "black")
    left_leg = (_kick_leg(-0.5, "left") if kick_side == "left" else _stand_leg(-6, -0.5, lift=3 if lift_side == "left" else 0))
    right_leg = (_kick_leg(0.5, "right") if kick_side == "right" else _stand_leg(0.5, 6, lift=3 if lift_side == "right" else 0))
    shape.addcomponent([_face_forward(x, y) for x, y in left_leg], pants_color, "black")
    shape.addcomponent([_face_forward(x, y) for x, y in right_leg], pants_color, "black")
    head_half = 3.2
    head_bottom, head_top = 6.5 - head_half, 6.5 + head_half
    face_pts = [(-head_half, head_bottom), (head_half, head_bottom), (head_half, head_top), (-head_half, head_top)]
    shape.addcomponent([_face_forward(x, y) for x, y in face_pts], head_color, "black")
    hairline_y = 6.5 + head_half * 0.5
    hair_pts = [(-head_half, hairline_y), (head_half, hairline_y), (head_half, head_top), (-head_half, head_top)]
    shape.addcomponent([_face_forward(x, y) for x, y in hair_pts], hair_color, hair_color)
    eye_r = 0.6
    shape.addcomponent(_regular_polygon(8, eye_r, center=_face_forward(-1.3, 6.8)), eye_color, eye_color)
    shape.addcomponent(_regular_polygon(8, eye_r, center=_face_forward(1.3, 6.8)), eye_color, eye_color)
    return shape

screen.register_shape("player_p1", _make_player_shape("blue"))
screen.register_shape("player_p2", _make_player_shape("red"))
screen.register_shape("player_p1_kick_right", _make_player_shape("blue", kick_side="right"))
screen.register_shape("player_p1_kick_left", _make_player_shape("blue", kick_side="left"))
screen.register_shape("player_p2_kick_right", _make_player_shape("red", kick_side="right"))
screen.register_shape("player_p2_kick_left", _make_player_shape("red", kick_side="left"))
screen.register_shape("player_p1_walk_left", _make_player_shape("blue", lift_side="left"))
screen.register_shape("player_p1_walk_right", _make_player_shape("blue", lift_side="right"))
screen.register_shape("player_p2_walk_left", _make_player_shape("red", lift_side="left"))
screen.register_shape("player_p2_walk_right", _make_player_shape("red", lift_side="right"))

def _make_ring_shape(radius=10, ring_color="white", hole_color="skyblue"):
    shape = turtle.Shape("compound")
    shape.addcomponent(_regular_polygon(30, radius), ring_color, ring_color)
    shape.addcomponent(_regular_polygon(30, radius * 0.6), hole_color, hole_color)
    return shape
screen.register_shape("shockwave_ring", _make_ring_shape())


# =====================================================================
# FORMAT OF BASELINE KITS: Section 3: Parameters & Physics
# Defines core physics variables (speed, direction, gravity, grid sizes).
# (Moved up to properly initialize boundaries before entities)
# =====================================================================
GROUND_Y = -250
GOAL_HEIGHT = GROUND_Y + 100 
PLAYER_GRAVITY = 0.64   
BALL_GRAVITY = 0.18     
BALL_FRICTION = 0.994

# Base reference sizes for collision
REF_WID = 2.3
REF_LEN = 1.5

# Game mechanics timers and limits
MAX_ULT = 100
KICK_POSE_DURATION = 6 
WALK_CYCLE_FRAMES = 6
SHOCK_RING_DURATION = 8 


# =====================================================================
# FORMAT OF BASELINE KITS: Section 2: Game Entities Initialization
# Creates and positions turtle.Turtle() objects (Ball, Pipes, Boundaries).
# Sets up the score display pen.
# =====================================================================

# --- Boundaries & Field Entities ---
field_pen = turtle.Turtle()
field_pen.hideturtle()
field_pen.penup()

net_pen = turtle.Turtle()
net_pen.hideturtle()
net_pen.penup()

# --- Player 1 (Blue) Entity ---
p1 = turtle.Turtle()
p1.shape("player_p1") 
p1.shapesize(stretch_wid=2.3, stretch_len=1.5) 
p1.penup()
p1.goto(-250, GROUND_Y + 20)
p1.dy = 0 

# --- Player 2 (Red) Entity ---
p2 = turtle.Turtle()
p2.shape("player_p2") 
p2.shapesize(stretch_wid=2.3, stretch_len=1.5)
p2.penup()
p2.goto(250, GROUND_Y + 20)
p2.dy = 0

# --- Ball Entity ---
ball = turtle.Turtle()
ball.shape("soccerball")
ball.penup()
ball.goto(0, 0)
ball.hideturtle()
ball.dx = 0 
ball.dy = 0 

# --- Visual Effect Entities ---
shock_ring = turtle.Turtle()
shock_ring.shape("shockwave_ring")
shock_ring.penup()
shock_ring.hideturtle()

# --- Score Display & UI Pens ---
score_pen = turtle.Turtle()
score_pen.hideturtle()
score_pen.penup()

ui_pen = turtle.Turtle()
ui_pen.hideturtle()
ui_pen.penup()

effect_pen = turtle.Turtle()
effect_pen.hideturtle()
effect_pen.penup()

aura_pen = turtle.Turtle()
aura_pen.hideturtle()
aura_pen.penup()

menu_pen = turtle.Turtle()
menu_pen.hideturtle()
menu_pen.penup()

cutscene_pen = turtle.Turtle()
cutscene_pen.hideturtle()
cutscene_pen.penup()

exp_pen = turtle.Turtle()
exp_pen.hideturtle()
exp_pen.penup()

jump_effects = []


# =====================================================================
# Game Data and Functions (Supporting Sections 2, 3, and 5)
# =====================================================================
shock_ring_timer = 0 
p1_kick_pose_timer = 0
p2_kick_pose_timer = 0
p1_walk_timer = 0
p2_walk_timer = 0
score_p1 = 0
score_p2 = 0
ult_p1 = 0
ult_p2 = 0
p1_ult_active = False
p1_ult_timer = 0
p2_ult_active = False
p2_ult_timer = 0

def trigger_shock_ring(x, y):
    global shock_ring_timer
    shock_ring.goto(x, y)
    shock_ring.shapesize(0.5, 0.5)
    shock_ring.showturtle()
    shock_ring_timer = SHOCK_RING_DURATION

def update_shock_ring():
    global shock_ring_timer
    if shock_ring_timer > 0:
        progress = 1 - (shock_ring_timer / SHOCK_RING_DURATION) 
        scale = 0.5 + progress * 2.0  
        shock_ring.shapesize(scale, scale)
        shock_ring_timer -= 1
        if shock_ring_timer == 0:
            shock_ring.hideturtle()

def trigger_kick_pose(player, kick_side, is_p1):
    global p1_kick_pose_timer, p2_kick_pose_timer
    shape_name = ("player_p1_kick_" if is_p1 else "player_p2_kick_") + kick_side
    player.shape(shape_name)
    if is_p1:
        p1_kick_pose_timer = KICK_POSE_DURATION
    else:
        p2_kick_pose_timer = KICK_POSE_DURATION

def update_kick_poses():
    global p1_kick_pose_timer, p2_kick_pose_timer
    if p1_kick_pose_timer > 0:
        p1_kick_pose_timer -= 1
        if p1_kick_pose_timer == 0:
            p1.shape("player_p1")
    if p2_kick_pose_timer > 0:
        p2_kick_pose_timer -= 1
        if p2_kick_pose_timer == 0:
            p2.shape("player_p2")

def update_walk_pose(player, is_p1, moving, kick_pose_timer):
    global p1_walk_timer, p2_walk_timer
    if kick_pose_timer > 0:
        return
    prefix = "player_p1" if is_p1 else "player_p2"
    if moving:
        timer = (p1_walk_timer if is_p1 else p2_walk_timer) + 1
        lift_side = "left" if (timer // WALK_CYCLE_FRAMES) % 2 == 0 else "right"
        target_shape = f"{prefix}_walk_{lift_side}"
    else:
        timer = 0
        target_shape = prefix
    if player.shape() != target_shape:
        player.shape(target_shape)
    if is_p1:
        p1_walk_timer = timer
    else:
        p2_walk_timer = timer

def draw_goal(x, y, color, net_color="white"):
    depth_sign = 1 if x < 0 else -1 
    height = 100       
    inner_depth = 50   
    outer_bulge = 15   
    outer_top = (x, y + height)
    outer_bottom = (x - depth_sign * outer_bulge, y)
    inner_top = (x + depth_sign * inner_depth, y + height)
    inner_bottom = (x + depth_sign * inner_depth, y)
    g = field_pen
    g.penup()
    g.goto(*outer_bottom)
    g.pendown()
    g.pensize(5)
    g.color(color)
    g.goto(*outer_top)
    g.goto(*inner_top)
    g.goto(*inner_bottom)
    g.penup()
    net = net_pen
    net.penup()
    net.pensize(1)
    net.color(net_color)
    NET_LINES = 6
    for i in range(1, NET_LINES):
        t = i / NET_LINES
        top_x = outer_top[0] + (inner_top[0] - outer_top[0]) * t
        bottom_x = outer_bottom[0] + (inner_bottom[0] - outer_bottom[0]) * t
        net.goto(top_x, y + height)
        net.pendown()
        net.goto(bottom_x, y)
        net.penup()
        outer_x_at_t = outer_bottom[0] + (outer_top[0] - outer_bottom[0]) * t
        net.goto(outer_x_at_t, y + height * t)
        net.pendown()
        net.goto(inner_top[0], y + height * t)  
        net.penup()

def draw_field():
    field_pen.clear()
    net_pen.clear()
    field_pen.penup()
    field_pen.goto(-500, GROUND_Y)
    field_pen.pendown()
    field_pen.pensize(5)
    field_pen.color("green")
    field_pen.forward(1000)
    field_pen.penup()
    draw_goal(-480, GROUND_Y, "blue")
    draw_goal(480, GROUND_Y, "red")

def clear_field():
    field_pen.clear()
    net_pen.clear()

CHARACTERS = [
    {"name": "Flash", "role": "Speedster", "speed": 6.0, "jump": 9.5, "kick": 14, "ult_rate": 0.15, "wid": 2.0, "len": 1.2, "ult_name": "Warp Shot", "ult_type": "warp"},
    {"name": "Titan", "role": "Power Striker", "speed": 5.2, "jump": 9.0, "kick": 19, "ult_rate": 0.15, "wid": 2.7, "len": 1.8, "ult_name": " Heavy Impact", "ult_type": "impact"},
    {"name": "Skyhopper", "role": "High Jumper", "speed": 5.6, "jump": 10.5, "kick": 14, "ult_rate": 0.15, "wid": 2.5, "len": 1.3, "ult_name": "Banana Curve", "ult_type": "curve"},
    {"name": " Blaster", "role": "Ult Master", "speed": 5.6, "jump": 9.5, "kick": 14, "ult_rate": 0.28, "wid": 2.3, "len": 1.5, "ult_name": " Meteor Shot", "ult_type": "meteor"}
]

p1_char_idx = 0
p2_char_idx = 0
p1_ready = False
p2_ready = False
game_state = "START"
menu_dirty = True 

p1_speed, p1_jump_power, p1_kick_power, p1_ult_charge = 5.6, 9.5, 14, 0.15
p2_speed, p2_jump_power, p2_kick_power, p2_ult_charge = 5.6, 9.5, 14, 0.15


# =====================================================================
# FORMAT OF BASELINE KITS: Section 4: Input Handling
# Binds keyboard events (wn.onkeypress) to action functions.
# =====================================================================
keys = {
    "w": False, "a": False, "d": False, "f": False, "g": False,
    "Up": False, "Left": False, "Right": False, "Return": False, "5": False, "q": False
}
p1_jump_count = 0
p1_jump_pressed = False
p2_jump_count = 0
p2_jump_pressed = False

def press_w(): 
    global p1_jump_count, p1_jump_pressed
    if game_state == "GAME":
        if not p1_jump_pressed and p1_jump_count < 2:
            p1.dy = p1_jump_power
            p1_jump_count += 1
            if p1_jump_count == 2:
                jump_effects.append({"x": p1.xcor(), "y": p1.ycor() - 15, "r": 8, "color": "cyan", "life": 8})
            p1_jump_pressed = True
        keys["w"] = True
def release_w(): 
    global p1_jump_pressed
    p1_jump_pressed = False
    keys["w"] = False

def press_a():
    global p1_char_idx, menu_dirty
    if game_state == "CHAR_SELECT" and not p1_ready:
        p1_char_idx = (p1_char_idx - 1) % len(CHARACTERS)
        play_sound("select")
        menu_dirty = True
    keys["a"] = True
def release_a(): keys["a"] = False

def press_d():
    global p1_char_idx, menu_dirty
    if game_state == "CHAR_SELECT" and not p1_ready:
        p1_char_idx = (p1_char_idx + 1) % len(CHARACTERS)
        play_sound("select")
        menu_dirty = True
    keys["d"] = True
def release_d(): keys["d"] = False

def press_f(): 
    global p1_ready, menu_dirty
    if game_state == "CHAR_SELECT":
        p1_ready = True
        menu_dirty = True
    keys["f"] = True
def release_f(): keys["f"] = False

def press_g(): keys["g"] = True
def release_g(): keys["g"] = False

def press_up(): 
    global p2_jump_count, p2_jump_pressed
    if game_state == "GAME":
        if not p2_jump_pressed and p2_jump_count < 2:
            p2.dy = p2_jump_power
            p2_jump_count += 1
            if p2_jump_count == 2:
                jump_effects.append({"x": p2.xcor(), "y": p2.ycor() - 15, "r": 8, "color": "yellow", "life": 8})
            p2_jump_pressed = True
        keys["Up"] = True
def release_up(): 
    global p2_jump_pressed
    p2_jump_pressed = False
    keys["Up"] = False

def press_left():
    global p2_char_idx, menu_dirty
    if game_state == "CHAR_SELECT" and not p2_ready:
        p2_char_idx = (p2_char_idx - 1) % len(CHARACTERS)
        play_sound("select")
        menu_dirty = True
    keys["Left"] = True
def release_left(): keys["Left"] = False

def press_right():
    global p2_char_idx, menu_dirty
    if game_state == "CHAR_SELECT" and not p2_ready:
        p2_char_idx = (p2_char_idx + 1) % len(CHARACTERS)
        play_sound("select")
        menu_dirty = True
    keys["Right"] = True
def release_right(): keys["Right"] = False

def press_enter():
    global game_state, p2_ready, menu_dirty
    if game_state == "START":
        play_sound("enter")
        stop_all_sound()
        game_state = "CHAR_SELECT"
        menu_dirty = True
        time.sleep(0.2) 
    elif game_state == "CHAR_SELECT" and not p2_ready:
        p2_ready = True
        menu_dirty = True
    elif game_state == "GAME_OVER":
        reset_entire_game()
    keys["Return"] = True
def release_enter(): keys["Return"] = False

def press_five(): keys["5"] = True
def release_five(): keys["5"] = False

def press_q():
    if game_state == "GAME_OVER":
        stop_all_sound()
        screen.bye()
        sys.exit()

# Binds keyboard events to action functions
screen.onkeypress(press_w, "w"); screen.onkeyrelease(release_w, "w")
screen.onkeypress(press_w, "W"); screen.onkeyrelease(release_w, "W")
screen.onkeypress(press_a, "a"); screen.onkeyrelease(release_a, "a")
screen.onkeypress(press_a, "A"); screen.onkeyrelease(release_a, "A")
screen.onkeypress(press_d, "d"); screen.onkeyrelease(release_d, "d")
screen.onkeypress(press_d, "D"); screen.onkeyrelease(release_d, "D")
screen.onkeypress(press_f, "f"); screen.onkeyrelease(release_f, "f")
screen.onkeypress(press_g, "g"); screen.onkeyrelease(release_g, "g")
screen.onkeypress(press_up, "Up"); screen.onkeyrelease(release_up, "Up")
screen.onkeypress(press_left, "Left"); screen.onkeyrelease(release_left, "Left")
screen.onkeypress(press_right, "Right"); screen.onkeyrelease(release_right, "Right")
screen.onkeypress(press_enter, "Return"); screen.onkeyrelease(release_enter, "Return")
for key in ["5", "KP_5", "KP_Begin", "Clear", "period", "."]:
    screen.onkeypress(press_five, key)
    screen.onkeyrelease(release_five, key)
screen.onkeypress(press_q, "q")
screen.onkeypress(press_q, "Q")
screen.listen()

# ================= UI & Menus Functions =================
def draw_preview_frame(cx, cy, width, height, border_color, bg_color):
    menu_pen.penup()
    menu_pen.goto(cx - width / 2, cy - height / 2)
    menu_pen.color(border_color, bg_color)
    menu_pen.pensize(3)
    menu_pen.begin_fill()
    menu_pen.pendown()
    for _ in range(2):
        menu_pen.forward(width)
        menu_pen.left(90)
        menu_pen.forward(height)
        menu_pen.left(90)
    menu_pen.end_fill()
    menu_pen.penup()

def draw_stat_bar(x, y, label, val, max_val, color):
    menu_pen.goto(x - 110, y - 5)
    menu_pen.color("black")
    menu_pen.write(f"{label}:", align="left", font=("Minecraft", 9, "bold"))
    menu_pen.goto(x - 35, y)
    menu_pen.pendown()
    menu_pen.pensize(10)
    menu_pen.color("lightgray")
    menu_pen.goto(x + 65, y)
    menu_pen.penup()
    fill_len = max(3, int(100 * (val / max_val)))
    menu_pen.goto(x - 35, y)
    menu_pen.pendown()
    menu_pen.color(color)
    menu_pen.goto(x - 35 + fill_len, y)
    menu_pen.penup()

def draw_start_screen():
    global start_prompt_visible, last_start_blink_time
    screen.bgpic("Bg2.gif")  
    menu_pen.clear()
    p1.hideturtle()
    p2.hideturtle()
    play_bg2_music()
    start_prompt_visible = True
    last_start_blink_time = time.time()
    if start_prompt_visible:
        menu_pen.goto(0, -180)
        menu_pen.color("yellow")
        menu_pen.write(" PRESS [ENTER] TO PLAY GAME ", align="center", font=("Minecraft", 24, "bold"))

def update_start_prompt():
    global start_prompt_visible, last_start_blink_time
    now = time.time()
    if now - last_start_blink_time >= START_BLINK_INTERVAL:
        start_prompt_visible = not start_prompt_visible
        last_start_blink_time = now
        menu_pen.clear()
        if start_prompt_visible:
            menu_pen.goto(0, -180)
            menu_pen.color("yellow")
            menu_pen.write(" PRESS [ENTER] TO PLAY GAME ", align="center", font=("Minecraft", 24, "bold"))

def draw_char_select_screen():
    screen.bgpic("Bg1.gif") 
    menu_pen.clear()
    menu_pen.goto(0, 230)
    menu_pen.color("navy")
    menu_pen.write(" CHOOSE YOUR HERO ", align="center", font=("Minecraft", 22, "bold"))
    
    # P1 Panel
    c1 = CHARACTERS[p1_char_idx]
    draw_preview_frame(-250, 110, 150, 100, "blue", "#EBF5FB")
    p1.showturtle()
    p1.goto(-250, 110)
    p1.shapesize(stretch_wid=c1["wid"], stretch_len=c1["len"])
    menu_pen.goto(-250, 200)
    menu_pen.color("blue")
    menu_pen.write("BLUE PLAYER (P1)", align="center", font=("Minecraft", 15, "bold"))
    menu_pen.goto(-250, 170)
    menu_pen.color("darkblue")
    menu_pen.write(f"<{c1['name']}>", align="center", font=("Minecraft", 16, "bold"))
    draw_stat_bar(-250, 30, "Speed", c1["speed"], 13.0, "dodgerblue")
    draw_stat_bar(-250, 10, "Jump", c1["jump"], 15.0, "cyan")
    draw_stat_bar(-250, -10, "Kick", c1["kick"], 40.0, "orange")
    draw_stat_bar(-250, -30, "Ult Rate", c1["ult_rate"], 0.30, "gold")
    menu_pen.goto(-250, -110)
    if p1_ready:
        menu_pen.color("green")
        menu_pen.write("READY!", align="center", font=("Minecraft", 18, "bold"))
    else:
        menu_pen.color("black")
        menu_pen.write("  [A]  /  [D]   to Browse\nPress [F] to CONFIRM", align="center", font=("Minecraft", 10, "bold"))

    # P2 Panel
    c2 = CHARACTERS[p2_char_idx]
    draw_preview_frame(250, 110, 150, 100, "red", "#FDEDEC")
    p2.showturtle()
    p2.goto(250, 110)
    p2.shapesize(stretch_wid=c2["wid"], stretch_len=c2["len"])
    menu_pen.goto(250, 200)
    menu_pen.color("red")
    menu_pen.write("RED PLAYER (P2)", align="center", font=("Minecraft", 15, "bold"))
    menu_pen.goto(250, 170)
    menu_pen.color("darkred")
    menu_pen.write(f"<{c2['name']}>", align="center", font=("Minecraft", 16, "bold"))
    draw_stat_bar(250, 30, "Speed", c2["speed"], 13.0, "dodgerblue")
    draw_stat_bar(250, 10, "Jump", c2["jump"], 15.0, "cyan")
    draw_stat_bar(250, -10, "Kick", c2["kick"], 40.0, "orange")
    draw_stat_bar(250, -30, "Ult Rate", c2["ult_rate"], 0.30, "gold")
    menu_pen.goto(250, -110)
    if p2_ready:
        menu_pen.color("green")
        menu_pen.write("READY!", align="center", font=("Minecraft", 18, "bold"))
    else:
        menu_pen.color("black")
        menu_pen.write("  [Left]  /  [Right]   to Browse\nPress [ENTER] to CONFIRM", align="center", font=("Minecraft", 10, "bold"))

def update_ui():
    score_pen.clear()
    ui_pen.clear()
    score_pen.pensize(42)
    score_pen.color("#0B1B2E")  
    score_pen.penup(); score_pen.goto(-165, 248)   
    score_pen.pendown(); score_pen.goto(165, 248)
    score_pen.penup()
    score_pen.goto(-470, 216)                       
    score_pen.pendown(); score_pen.goto(-305, 216)
    score_pen.penup()
    score_pen.goto(470, 216)                        
    score_pen.pendown(); score_pen.goto(305, 216)
    score_pen.penup()

    score_pen.goto(-28, 238)
    score_pen.color("#4FC3F7")          
    score_pen.write(f"BLUE  {score_p1}", align="right", font=("Minecraft", 24, "bold"))
    score_pen.goto(0, 238)
    score_pen.color("#ECEFF1")
    score_pen.write("|", align="center", font=("Minecraft", 24, "bold"))
    score_pen.goto(28, 238)
    score_pen.color("#FF7043")          
    score_pen.write(f"{score_p2}  RED", align="left", font=("Minecraft", 24, "bold"))

    c1 = CHARACTERS[p1_char_idx]
    ui_pen.goto(-462, 222)
    if p1_ult_active:
        ui_pen.color("#18FFFF")
        status_text_p1 = "READY! (G)"
    else:
        ui_pen.color("#90CAF9")
        status_text_p1 = f"{c1['name']} (G) - {c1['ult_name']}"
    ui_pen.write(status_text_p1, align="left", font=("Minecraft", 12, "bold"))
    ui_pen.goto(-462, 204)
    ui_pen.pendown()
    ui_pen.pensize(14)
    ui_pen.color("#546E7A")             
    ui_pen.goto(-322, 204)
    ui_pen.penup()
    if ult_p1 > 0:
        ui_pen.goto(-462, 204)
        ui_pen.pendown()
        ui_pen.color("#18FFFF" if ult_p1 >= MAX_ULT else "#29B6F6")
        ui_pen.goto(-462 + (140 * (ult_p1 / MAX_ULT)), 204)
        ui_pen.penup()

    c2 = CHARACTERS[p2_char_idx]
    ui_pen.goto(462, 222)
    if p2_ult_active:
        ui_pen.color("#FFD740")
        status_text_p2 = "READY! (5 / .)"
    else:
        ui_pen.color("#FFAB91")
        status_text_p2 = f"{c2['ult_name']} - {c2['name']} (5 / .)"
    ui_pen.write(status_text_p2, align="right", font=("Minecraft", 12, "bold"))
    ui_pen.goto(462, 204)
    ui_pen.pendown()
    ui_pen.pensize(14)
    ui_pen.color("#546E7A")
    ui_pen.goto(322, 204)
    ui_pen.penup()
    if ult_p2 > 0:
        ui_pen.goto(462, 204)
        ui_pen.pendown()
        ui_pen.color("#FFD740" if ult_p2 >= MAX_ULT else "#FF7043")
        ui_pen.goto(462 - (140 * (ult_p2 / MAX_ULT)), 204)
        ui_pen.penup()

def draw_aura():
    aura_pen.clear()
    frame_tick = int(time.time() * 20)
    if p1_ult_active:
        aura_pen.penup()
        aura_pen.goto(p1.xcor(), p1.ycor() - 35)
        aura_pen.pendown()
        aura_pen.pensize(4)
        aura_pen.color("orange" if frame_tick % 2 == 0 else "yellow")
        aura_pen.circle(35)
    if p2_ult_active:
        aura_pen.penup()
        aura_pen.goto(p2.xcor(), p2.ycor() - 35)
        aura_pen.pendown()
        aura_pen.pensize(4)
        aura_pen.color("red" if frame_tick % 2 == 0 else "gold")
        aura_pen.circle(35)

def execute_ultimate(player, is_p1, ult_type):
    if ult_type == "meteor":
        ball.goto(player.xcor() + (30 if is_p1 else -30), player.ycor() + 15)
        ball.dx = 46 if is_p1 else -46
        ball.dy = 4
        
    elif ult_type == "curve":
        player.goto(player.xcor(), 180)
        ball.goto(player.xcor() + (20 if is_p1 else -20), player.ycor() - 10)
        ball.dx = 38 if is_p1 else -38
        ball.dy = -32
    elif ult_type == "warp":
        target_x = 350 if is_p1 else -350
        ball.goto(target_x, GROUND_Y + 40)
        ball.dx = 30 if is_p1 else -30
        ball.dy = 0 
        
    elif ult_type == "impact":
        ball.goto(player.xcor() + (30 if is_p1 else -30), player.ycor() + 10)
        ball.dx = 35 if is_p1 else -35
        ball.dy = -15 # กดความเร็วแกน Y ติดลบ เพื่อให้บอลอัดกระแทกพื้นแล้วเด้งขึ้นมา
        
        # เพิ่มเอฟเฟกต์ซัดศัตรูให้ "ลอยกระเด็นขึ้นฟ้า" (ต่างจาก Meteor ที่ไม่มีผลกับศัตรู)
        target_p = p2 if is_p1 else p1
        target_p.setx(target_p.xcor() + (120 if is_p1 else -120)) # กระเด็นถอยหลัง
        target_p.dy = 15

    trigger_kick_pose(player, "right" if is_p1 else "left", is_p1)
    trigger_shock_ring(ball.xcor(), ball.ycor())

def trigger_cutscene(player_name, team_color, ult_name):
    play_sound("ultimate")
    colors = ["black", team_color, "gold"]
    for i in range(10):
        screen.bgcolor(colors[i % len(colors)])
        cutscene_pen.clear()
        cutscene_pen.goto(0, 20)
        cutscene_pen.color("yellow" if i % 2 == 0 else "white")
        cutscene_pen.write(f"{player_name.upper()} {ult_name.upper()}!! ", align="center", font=("Minecraft", 24, "bold"))
        screen.update()
        time.sleep(0.06)
    screen.bgcolor("skyblue")
    cutscene_pen.clear()

def trigger_explosion(x, y):
    colors = ["orange", "yellow", "red", "white"]
    for r in range(10, 65, 12):
        exp_pen.clear()
        exp_pen.goto(x, y - r)
        exp_pen.pendown()
        exp_pen.pensize(4)
        exp_pen.color(colors[(r // 12) % len(colors)])
        exp_pen.circle(r)
        exp_pen.penup()
        exp_pen.goto(x, y)
        exp_pen.color("red")
        exp_pen.write(" BOOM!!", align="center", font=("Minecraft", 18, "bold"))
        screen.update()
        time.sleep(0.02)
    exp_pen.clear()
    p1.dy = 8
    p1.setx(max(-415, p1.xcor() - 90))
    p2.dy = 8
    p2.setx(min(415, p2.xcor() + 90))
    ball.sety(GROUND_Y + 30)
    ball.dx = 0
    ball.dy = 17

def reset_positions(conceded_player=None):
    global squeeze_frames, p1_ult_active, p2_ult_active
    global shock_ring_timer, p1_kick_pose_timer, p2_kick_pose_timer
    squeeze_frames = 0
    p1_ult_active = False
    p2_ult_active = False
    p1.goto(-250, GROUND_Y + 20)
    p2.goto(250, GROUND_Y + 20)
    p1.dy = 0
    p2.dy = 0
    shock_ring.hideturtle()
    shock_ring_timer = 0
    p1.shape("player_p1")
    p2.shape("player_p2")
    p1_kick_pose_timer = 0
    p2_kick_pose_timer = 0
    if conceded_player == "p1":
        ball.goto(-180, 150)
    elif conceded_player == "p2":
        ball.goto(180, 150)
    else:
        ball.goto(0, 100)
    ball.dx = 0
    ball.dy = 0
    time.sleep(1)
    if game_state == "GAME":
        play_sound("game_music", loop=True)

def show_winner_and_options(text, color):
    stop_all_sound()
    play_sound("win")
    
    menu_pen.penup()
    menu_pen.color(color, "white") 
    menu_pen.goto(-350, 120)
    menu_pen.pensize(8)
    menu_pen.pendown()
    menu_pen.begin_fill()
    for _ in range(2):
        menu_pen.forward(700)
        menu_pen.right(90)
        menu_pen.forward(280)
        menu_pen.right(90)
    menu_pen.end_fill()
    menu_pen.penup()
    # ---------------------------------------------------------

    score_pen.goto(0, 45)
    score_pen.color(color)
    score_pen.write(text, align="center", font=("Minecraft", 36, "bold"))
    
    menu_pen.goto(0, -25)
    menu_pen.color("green")
    menu_pen.write("PRESS [ENTER] TO PLAY AGAIN", align="center", font=("Minecraft", 18, "bold"))
    
    menu_pen.goto(0, -65)
    menu_pen.color("red")
    menu_pen.write("PRESS [Q] TO QUIT GAME", align="center", font=("Minecraft", 18, "bold"))
    
    screen.update()

def reset_entire_game():
    global score_p1, score_p2, ult_p1, ult_p2, p1_ready, p2_ready, game_state, p1_ult_active, p2_ult_active
    global shock_ring_timer, p1_kick_pose_timer, p2_kick_pose_timer
    global menu_dirty
    score_p1 = 0
    score_p2 = 0
    ult_p1 = 0
    ult_p2 = 0
    p1_ready = False
    p2_ready = False
    p1_ult_active = False
    p2_ult_active = False
    score_pen.clear()
    menu_pen.clear()
    ui_pen.clear()
    aura_pen.clear()
    ball.hideturtle()
    clear_field()  
    shock_ring.hideturtle()
    shock_ring_timer = 0
    p1.shape("player_p1")
    p2.shape("player_p2")
    p1_kick_pose_timer = 0
    p2_kick_pose_timer = 0
    game_state = "START"
    menu_dirty = True

squeeze_frames = 0
FRAME_TIME = 0.02
frame_counter = 0
last_frame_time = time.perf_counter()


# =====================================================================
# FORMAT OF BASELINE KITS: Section 5: Main Game Loop
# Controls continuous frame updates, physics calculations, collision checks...
# (In this script, it uses a 'while True' loop with time delays to manage FPS)
# =====================================================================
while True:
    if game_state == "START":
        if menu_dirty:
            draw_start_screen()
            menu_dirty = False
        update_start_prompt()

    elif game_state == "CHAR_SELECT":
        if menu_dirty:
            draw_char_select_screen()
            menu_dirty = False
        if p1_ready and p2_ready:
            screen.bgpic("bg.gif")  
            draw_field()            
            p1_c = CHARACTERS[p1_char_idx]
            p1_speed, p1_jump_power, p1_kick_power, p1_ult_charge = p1_c["speed"], p1_c["jump"], p1_c["kick"], p1_c["ult_rate"]
            p2_c = CHARACTERS[p2_char_idx]
            p2_speed, p2_jump_power, p2_kick_power, p2_ult_charge = p2_c["speed"], p2_c["jump"], p2_c["kick"], p2_c["ult_rate"]
            reset_positions()
            menu_pen.clear()
            menu_pen.goto(0, 0)
            menu_pen.color("orange")
            for count in range(3, 0, -1):
                menu_pen.clear()
                menu_pen.write(f"GET READY IN {count}...", align="center", font=("Minecraft", 30, "bold"))
                screen.update()
                time.sleep(0.6)
            menu_pen.clear()
            ball.showturtle()
            play_sound("game_start")
            play_sound("game_music", loop=True)
            game_state = "GAME"
            update_ui()

    elif game_state == "GAME":
        p1_hit_w = CHARACTERS[p1_char_idx]["wid"] / REF_WID
        p1_hit_h = CHARACTERS[p1_char_idx]["len"] / REF_LEN
        p2_hit_w = CHARACTERS[p2_char_idx]["wid"] / REF_WID
        p2_hit_h = CHARACTERS[p2_char_idx]["len"] / REF_LEN

        if ult_p1 < MAX_ULT and not p1_ult_active: ult_p1 = min(MAX_ULT, ult_p1 + p1_ult_charge)
        if ult_p2 < MAX_ULT and not p2_ult_active: ult_p2 = min(MAX_ULT, ult_p2 + p2_ult_charge)

        if frame_counter % 3 == 0:
            update_ui()

        if p1_ult_active:
            if time.time() > p1_ult_timer:
                p1_ult_active = False
        if p2_ult_active:
            if time.time() > p2_ult_timer:
                p2_ult_active = False

        if p1_ult_active or p2_ult_active:
            draw_aura()
        elif frame_counter % 6 == 0:
            aura_pen.clear()

        effect_pen.clear()
        for effect in jump_effects[:]:
            effect_pen.penup()
            effect_pen.goto(effect["x"], effect["y"] - effect["r"])
            effect_pen.pendown()
            effect_pen.pensize(3)
            effect_pen.color(effect["color"])
            effect_pen.circle(effect["r"])
            effect["r"] += 2.5
            effect["life"] -= 1
            if effect["life"] <= 0:
                jump_effects.remove(effect)

        if keys["a"]: p1.setx(p1.xcor() - p1_speed)
        if keys["d"]: p1.setx(p1.xcor() + p1_speed)
            
        p1.dy -= PLAYER_GRAVITY
        p1.sety(p1.ycor() + p1.dy)
        if p1.ycor() < GROUND_Y + 20: 
            p1.sety(GROUND_Y + 20)
            p1.dy = 0
            p1_jump_count = 0

        update_walk_pose(p1, is_p1=True, moving=(keys["a"] or keys["d"]), kick_pose_timer=p1_kick_pose_timer)

        if keys["Left"]: p2.setx(p2.xcor() - p2_speed)
        if keys["Right"]: p2.setx(p2.xcor() + p2_speed)
            
        p2.dy -= PLAYER_GRAVITY
        p2.sety(p2.ycor() + p2.dy)
        if p2.ycor() < GROUND_Y + 20:
            p2.sety(GROUND_Y + 20)
            p2.dy = 0
            p2_jump_count = 0

        update_walk_pose(p2, is_p1=False, moving=(keys["Left"] or keys["Right"]), kick_pose_timer=p2_kick_pose_timer)

        p_dx = p1.xcor() - p2.xcor()
        p_dy = p1.ycor() - p2.ycor()
        pp_min_dx = 30 * (p1_hit_w + p2_hit_w) / 2
        pp_min_dy = 46 * (p1_hit_h + p2_hit_h) / 2
        if abs(p_dx) < pp_min_dx and abs(p_dy) < pp_min_dy:
            overlap_x = pp_min_dx - abs(p_dx)
            if p_dx < 0:
                p1.setx(p1.xcor() - overlap_x / 2)
                p2.setx(p2.xcor() + overlap_x / 2)
            else:
                p1.setx(p1.xcor() + overlap_x / 2)
                p2.setx(p2.xcor() - overlap_x / 2)

        for p, is_p1 in [(p1, True), (p2, False)]:
            if (415 <= abs(p.xcor()) <= 485) and (GOAL_HEIGHT + 10 <= p.ycor() <= GOAL_HEIGHT + 30) and p.dy <= 0:
                p.sety(GOAL_HEIGHT + 20)
                p.dy = 0
                if is_p1: p1_jump_count = 0
                else: p2_jump_count = 0
            elif p.ycor() < GOAL_HEIGHT + 10:
                if p.xcor() < -415: p.setx(-415)
                if p.xcor() > 415: p.setx(415)
            else:
                if p.xcor() < -480: p.setx(-480)
                if p.xcor() > 480: p.setx(480)

        if keys["g"] and ult_p1 >= MAX_ULT and not p1_ult_active:
            keys["g"] = False
            ult_p1 = 0
            p1_ult_active = True
            p1_ult_timer = time.time() + 5.0

        if keys["5"] and ult_p2 >= MAX_ULT and not p2_ult_active:
            keys["5"] = False
            ult_p2 = 0
            p2_ult_active = True
            p2_ult_timer = time.time() + 5.0

        ball.dy -= BALL_GRAVITY
        ball.setx(ball.xcor() + ball.dx)
        ball.sety(ball.ycor() + ball.dy)
        ball.dx *= BALL_FRICTION 

        for p_idx, (p, is_p1) in enumerate([(p1, True), (p2, False)]):
            dx = ball.xcor() - p.xcor()
            dy = ball.ycor() - p.ycor()
            min_dx = 25 * (p1_hit_w if is_p1 else p2_hit_w)
            min_dy = 30 * (p1_hit_h if is_p1 else p2_hit_h)
            
            if abs(dx) < min_dx and abs(dy) < min_dy:
                if is_p1 and p1_ult_active:
                    p1_ult_active = False
                    c1 = CHARACTERS[p1_char_idx]
                    trigger_cutscene("BLUE", "blue", c1["ult_name"])
                    execute_ultimate(p1, True, c1["ult_type"])
                    break
                elif not is_p1 and p2_ult_active:
                    p2_ult_active = False
                    c2 = CHARACTERS[p2_char_idx]
                    trigger_cutscene("RED", "red", c2["ult_name"])
                    execute_ultimate(p2, False, c2["ult_type"])
                    break
                overlap_x = min_dx - abs(dx)
                overlap_y = min_dy - abs(dy)
                
                if overlap_x < overlap_y:
                    if dx > 0:
                        ball.setx(ball.xcor() + overlap_x)
                        ball.dx = max(ball.dx + 0.6, 1.5)
                    else:
                        ball.setx(ball.xcor() - overlap_x)
                        ball.dx = min(ball.dx - 0.6, -1.5)
                else:
                    if dy > 0:
                        ball.sety(ball.ycor() + overlap_y)
                        ball.dy = max(ball.dy + 0.6, 1.5)
                    else:
                        if ball.ycor() <= GROUND_Y + 12:
                            ball.sety(GROUND_Y + 12)
                            ball.dy = max(ball.dy, 2.5)
                        else:
                            ball.sety(ball.ycor() - overlap_y)
                            ball.dy = min(ball.dy - 0.6, -1.5)

        if ball.ycor() < GROUND_Y + 10:
            ball.sety(GROUND_Y + 10)
            if ball.dy < 0:
                ball.dy *= -0.75
                if abs(ball.dy) < 1: ball.dy = 0

        p_dist = abs(p1.xcor() - p2.xcor())
        min_x = min(p1.xcor(), p2.xcor())
        max_x = max(p1.xcor(), p2.xcor())
        ball_in_between = (min_x - 10 <= ball.xcor() <= max_x + 10)
        is_squeezed_on_ground = (p_dist < 55) and ball_in_between and (ball.ycor() <= GROUND_Y + 18)

        if is_squeezed_on_ground:
            squeeze_frames += 2
            if squeeze_frames >= 14:
                trigger_explosion(ball.xcor(), GROUND_Y + 20)
                squeeze_frames = 0
        else:
            squeeze_frames = max(0, squeeze_frames - 1)

        if keys["f"]:
            trigger_kick_pose(p1, "right" if p1.xcor() < ball.xcor() else "left", is_p1=True)
        if keys["Return"]:
            trigger_kick_pose(p2, "right" if p2.xcor() < ball.xcor() else "left", is_p1=False)

        if abs(p1.xcor() - ball.xcor()) < 35 * p1_hit_w and abs(p1.ycor() - ball.ycor()) < 40 * p1_hit_h:
            if keys["f"]: 
                if p1_ult_active:
                    p1_ult_active = False
                    c1 = CHARACTERS[p1_char_idx]
                    trigger_cutscene("BLUE", "blue", c1["ult_name"])
                    execute_ultimate(p1, True, c1["ult_type"])
                else:
                    ult_p1 = min(MAX_ULT, ult_p1 + 8)
                    ball.dx = p1_kick_power if p1.xcor() < ball.xcor() else -p1_kick_power
                    ball.dy = 3.8
                    play_kick_sound_once()
                    trigger_shock_ring(ball.xcor(), ball.ycor())

        if abs(p2.xcor() - ball.xcor()) < 35 * p2_hit_w and abs(p2.ycor() - ball.ycor()) < 40 * p2_hit_h:
            if keys["Return"]: 
                if p2_ult_active:
                    p2_ult_active = False
                    c2 = CHARACTERS[p2_char_idx]
                    trigger_cutscene("RED", "red", c2["ult_name"])
                    execute_ultimate(p2, False, c2["ult_type"])
                else:
                    ult_p2 = min(MAX_ULT, ult_p2 + 8)
                    ball.dx = p2_kick_power if p2.xcor() < ball.xcor() else -p2_kick_power
                    ball.dy = 3.8
                    play_kick_sound_once()
                    trigger_shock_ring(ball.xcor(), ball.ycor())

        if ball.xcor() > 480:
            ball.setx(480)
            ball.dx *= -0.8 
        if ball.xcor() < -480:
            ball.setx(-480)
            ball.dx *= -0.8 

        if ball.ycor() > 280:
            ball.sety(280)
            ball.dy *= -0.8 

        for goal_x in [-430, 430]:
            if abs(ball.xcor() - goal_x) < 12 and abs(ball.ycor() - GOAL_HEIGHT) < 12:
                if (goal_x == -430 and ball.xcor() > -430) or (goal_x == 430 and ball.xcor() < 430):
                    ball.dx *= -0.8
                    ball.dy *= -0.8

        if (430 <= abs(ball.xcor()) <= 480) and abs(ball.ycor() - GOAL_HEIGHT) < 12:
            if ball.dy < 0 and ball.ycor() >= GOAL_HEIGHT:
                ball.sety(GOAL_HEIGHT + 12)
                ball.dy *= -0.75
            elif ball.dy > 0 and ball.ycor() < GOAL_HEIGHT:
                ball.sety(GOAL_HEIGHT - 12)
                ball.dy *= -0.75

        if ball.xcor() < -430 and ball.ycor() < GOAL_HEIGHT - 5:
            stop_all_sound()
            play_sound("goal")
            score_p2 += 1
            update_ui()
            if score_p2 >= 7:
                game_state = "GAME_OVER"
                show_winner_and_options("RED WINS!", "red")
            else:
                reset_positions(conceded_player="p1")
                
        if ball.xcor() > 430 and ball.ycor() < GOAL_HEIGHT - 5:
            stop_all_sound()
            play_sound("goal")
            score_p1 += 1
            update_ui()
            if score_p1 >= 7:
                game_state = "GAME_OVER"
                show_winner_and_options("BLUE WINS!", "blue")
            else:
                reset_positions(conceded_player="p2")

        update_shock_ring()
        update_kick_poses()

    elif game_state == "GAME_OVER":
        aura_pen.clear()

    screen.update()
    frame_counter += 1
    next_frame = last_frame_time + FRAME_TIME
    remaining = next_frame - time.perf_counter()
    if remaining > 0:
        time.sleep(remaining)
    last_frame_time = time.perf_counter()