import json
import os
import datetime
import uuid
import copy
import random
import math

# ══════════════════════════════════════════════
#  FILE PATHS & SAVE SYSTEM
# ══════════════════════════════════════════════
SAVE_DIR         = "saves"
SAVE_FILE        = os.path.join(SAVE_DIR, "heroes.json")
LEADERBOARD_FILE = os.path.join(SAVE_DIR, "leaderboard.json")
os.makedirs(SAVE_DIR, exist_ok=True)


# ══════════════════════════════════════════════
#  LOOKUP TABLES
# ══════════════════════════════════════════════
HERO_TYPES = {
    "1": {"name": "Sorcerer", "bonus": {"magic_power": 3, "intelligence": 2},            "desc": "Wields arcane forces. Fragile but devastating."},
    "2": {"name": "Thug",     "bonus": {"strength": 3, "charisma": 1},                   "desc": "Hits first, asks nothing."},
    "3": {"name": "Slayer",   "bonus": {"magic_power": 1, "stealth": 1, "strength": 2},  "desc": "Blade and spell in equal measure."},
    "4": {"name": "Sneak",    "bonus": {"intelligence": 1, "stealth": 3, "charisma": 1}, "desc": "Unseen. Already behind you."},
    "5": {"name": "Genius",   "bonus": {"magic_power": 1, "intelligence": 3, "charisma": 1}, "desc": "Knowledge is the deadliest weapon."},
}

GIFTS = {
    "1": {"name": "Speech",            "bonus": {"charisma": 3},   "desc": "Words that move mountains."},
    "2": {"name": "Speed",             "bonus": {"agility": 3},    "desc": "First to strike. Last to fall."},
    "3": {"name": "Physical Strength", "bonus": {"strength": 3},   "desc": "When logic fails, muscle prevails."},
    "4": {"name": "Sight",             "bonus": {"perception": 3}, "desc": "Nothing escapes your eye."},
    "5": {"name": "Love",              "bonus": {"willpower": 3},  "desc": "The only force that bends fate."},
}

MAGIC_SYSTEMS = {
    "1": "Fire", "2": "Water", "3": "Earth", "4": "Air",
    "5": "Lightning", "6": "Darkness", "7": "Nano",
}

HERO_HOMES = {
    "1": {"name": "Forest",   "lore": "raised among ancient trees and hidden paths",
          "item": {"name": "Carved Bow",       "type": "weapon",   "value": 40, "stats": {"agility": 1},                   "description": "Bent from a living branch. Still grows."}},
    "2": {"name": "Desert",   "lore": "hardened by endless heat and scarce water",
          "item": {"name": "Sand Cloak",        "type": "armor",    "value": 35, "stats": {"stealth": 1},                   "description": "Blends with dunes. Keeps the heat out."}},
    "3": {"name": "Mountain", "lore": "forged in cold stone and thin air",
          "item": {"name": "Iron Pick",         "type": "weapon",   "value": 38, "stats": {"strength": 1},                  "description": "Used for climbing first, fighting second."}},
    "4": {"name": "Sea",      "lore": "born on open water, navigator by instinct",
          "item": {"name": "Navigator's Chart", "type": "key_item", "value": 50, "stats": {"perception": 1},               "description": "Shows coasts no map-maker ever drew."}},
    "5": {"name": "Sky",      "lore": "a child of the clouds, unbounded and restless",
          "item": {"name": "Wind Charm",        "type": "relic",    "value": 45, "stats": {"agility": 1, "magic_power": 1}, "description": "Hums when a storm is three days out."}},
}

ENEMY_TYPES = [
    {"name": "Street Thug",   "hp": (18,35),  "dmg": (3,7),   "xp": (10,25), "gold": (5,20),
     "abilities": ["brawl"],                       "loot": ["Stim Pack", None, None],
     "flavor": "A scarred enforcer. Hits hard, thinks slow."},
    {"name": "Neon Rat",      "hp": (8,18),   "dmg": (1,4),   "xp": (5,15),  "gold": (1,8),
     "abilities": ["dodge"],                        "loot": [None, None, "Scrap Wire"],
     "flavor": "Mutated vermin. Fast and annoying."},
    {"name": "Corp Drone",    "hp": (25,50),  "dmg": (5,10),  "xp": (20,40), "gold": (15,35),
     "abilities": ["shield_pulse", "brawl"],        "loot": ["EMP Chip", "Stim Pack", None],
     "flavor": "Corporate security bot. Slow but armoured."},
    {"name": "Ghost Runner",  "hp": (15,30),  "dmg": (8,15),  "xp": (30,55), "gold": (20,50),
     "abilities": ["dodge", "crit_strike"],         "loot": ["Ghost Blade", None, None],
     "flavor": "A hired blade. You may not see the first hit."},
    {"name": "Sewer Mutant",  "hp": (40,80),  "dmg": (6,12),  "xp": (35,60), "gold": (5,15),
     "abilities": ["brawl", "poison_bite"],         "loot": [None, None, None],
     "flavor": "Something the sewers made. Tough and wrong."},
    {"name": "Rogue AI Shell","hp": (60,100), "dmg": (10,18), "xp": (60,100),"gold": (40,80),
     "abilities": ["shield_pulse", "crit_strike", "brawl"], "loot": ["AI Core", "EMP Chip", "Ghost Blade"],
     "flavor": "A discarded machine that learned to hate."},
]

ABILITIES = {
    "brawl":       {"name": "Brawl",          "mult": 1.0, "effect": None},
    "dodge":       {"name": "Dodge",          "mult": 0.0, "effect": "miss"},
    "crit_strike": {"name": "Critical Strike","mult": 2.0, "effect": "crit"},
    "shield_pulse":{"name": "Shield Pulse",   "mult": 0.0, "effect": "shield"},
    "poison_bite": {"name": "Poison Bite",    "mult": 0.8, "effect": "poison"},
}

PLAYER_ACTIONS = {
    "attack":   {"name": "Attack",        "mult": 1.0, "stamina_cost": 5},
    "heavy":    {"name": "Heavy Strike",  "mult": 1.8, "stamina_cost": 14},
    "spell":    {"name": "Cast Spell",    "mult": 0.0, "stamina_cost": 12},
    "dodge":    {"name": "Dodge",         "mult": 0.0, "stamina_cost": 8},
    "use_item": {"name": "Use Item",      "mult": 0.0, "stamina_cost": 0},
    "flee":     {"name": "Flee",          "mult": 0.0, "stamina_cost": 10},
}

QUEST_LIST = [
    {"id": "FIRST_BLOOD", "name": "First Blood",     "desc": "Defeat your first enemy.",   "xp": 50,  "gold": 30,  "check": lambda h: h["stats"]["enemies_defeated"] >= 1},
    {"id": "SURVIVOR",    "name": "Survivor",         "desc": "Survive 3 battles.",         "xp": 80,  "gold": 60,  "check": lambda h: h["stats"]["enemies_defeated"] >= 3},
    {"id": "WEALTHY",     "name": "Road to Riches",   "desc": "Accumulate $500 gold.",      "xp": 40,  "gold": 0,   "check": lambda h: h["gold"] >= 500},
    {"id": "LEVEL5",      "name": "Ascending",        "desc": "Reach Level 5.",             "xp": 120, "gold": 100, "check": lambda h: h["level"] >= 5},
]


# ══════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════
def _ts():
    return datetime.datetime.now().isoformat(timespec="seconds")

def _bar(val, mx=20, char="█", empty="░"):
    filled = int(mx * val / max(mx, 1))
    return char * filled + empty * (mx - filled)

def _div(char="─", w=54):
    print(char * w)

def _pick(prompt, options):
    print(f"\n{prompt}")
    for k, v in options.items():
        label = v["name"] if isinstance(v, dict) else v
        print(f"  [{k}] {label}")
    while True:
        choice = input(">> ").strip()
        if choice in options:
            return choice
        for k, v in options.items():
            label = v["name"] if isinstance(v, dict) else v
            if choice.lower() == label.lower():
                return k
        print(f"  Please enter a number 1–{len(options)}.")


# ══════════════════════════════════════════════
#  SAVE / LOAD
# ══════════════════════════════════════════════
def _load_db():
    if not os.path.exists(SAVE_FILE):
        return {}
    try:
        with open(SAVE_FILE, "r") as f:
            content = f.read().strip()
            return json.loads(content) if content else {}
    except (json.JSONDecodeError, OSError):
        return {}

def _write_db(db):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(db, f, indent=2)
    except OSError as e:
        print(f"[SAVE] Error: {e}")

def save_hero(hero):
    db = _load_db()
    hero["last_played"] = _ts()
    db[hero["name"]] = hero
    _write_db(db)
    print(f"[SAVE] '{hero['name']}' saved.")

def load_hero(name):
    db = _load_db()
    hero = db.get(name)
    if not hero:
        print(f"[SAVE] Hero '{name}' not found.")
        return None
    hero["last_played"] = _ts()
    _write_db(db)
    print(f"[SAVE] '{name}' loaded.")
    return hero

def delete_hero(name):
    db = _load_db()
    if name not in db:
        print(f"[SAVE] Hero '{name}' not found.")
        return False
    del db[name]
    _write_db(db)
    print(f"[SAVE] '{name}' deleted.")
    return True

def hero_exists(name):
    return name in _load_db()

def list_heroes():
    db = _load_db()
    return sorted(db.values(), key=lambda h: h["last_played"], reverse=True)


# ══════════════════════════════════════════════
#  LEADERBOARD
# ══════════════════════════════════════════════
def _load_lb():
    if not os.path.exists(LEADERBOARD_FILE):
        return {}
    try:
        with open(LEADERBOARD_FILE, "r") as f:
            return json.loads(f.read().strip() or "{}")
    except (json.JSONDecodeError, OSError):
        return {}

def _write_lb(lb):
    try:
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(lb, f, indent=2)
    except OSError as e:
        print(f"[LB] Error: {e}")

def push_to_leaderboard(hero):
    lb = _load_lb()
    lb[hero["name"]] = {
        "name":    hero["name"],
        "class":   hero["hero_type"],
        "magic":   hero["magic"],
        "home":    hero["home"],
        "level":   hero["level"],
        "kills":   hero["stats"]["enemies_defeated"],
        "gold":    hero["gold"],
        "quests":  hero["stats"]["quests_complete"],
        "deaths":  hero["stats"]["times_died"],
        "updated": _ts(),
    }
    _write_lb(lb)

def show_leaderboard():
    lb = _load_lb()
    if not lb:
        print("\n  // NO OPERATIVES ON RECORD YET.")
        return

    tabs = {
        "1": ("KILLS",   "kills",  lambda e: f"{e.get('kills',0)} kills"),
        "2": ("LEVEL",   "level",  lambda e: f"Lv {e.get('level',1)}"),
        "3": ("GOLD",    "gold",   lambda e: f"${e.get('gold',0):,}"),
        "4": ("QUESTS",  "quests", lambda e: f"{e.get('quests',0)} complete"),
    }

    print("\n╔══════════════════════════════════════════════════╗")
    print("║         🏆  GLOBAL LEADERBOARD // 2157          ║")
    print("╚══════════════════════════════════════════════════╝")
    print("  Sort by:  [1] Kills  [2] Level  [3] Gold  [4] Quests  [Q] Back")
    choice = input("  >> ").strip().upper()

    if choice not in tabs:
        return

    label, key, fmt = tabs[choice]
    entries = sorted(lb.values(), key=lambda e: e.get(key, 0), reverse=True)
    medals = ["👑", "🥈", "🥉"]

    print(f"\n  ── {label} RANKINGS {'─'*(42-len(label))}")
    for i, e in enumerate(entries):
        rank  = medals[i] if i < 3 else f"#{i+1:<3}"
        score = fmt(e)
        print(f"  {rank}  {e['name'].upper():<16} {e['class']:<10} {score:<18} "
              f"{e['magic']:<12} From {e['home']}  ({e.get('deaths',0)} deaths)")
    _div()


# ══════════════════════════════════════════════
#  HERO BUILDER
# ══════════════════════════════════════════════
def build_hero(name, type_key, gift_key, magic_key, home_key):
    ht  = HERO_TYPES[type_key]
    gf  = GIFTS[gift_key]
    hm  = HERO_HOMES[home_key]
    magic = MAGIC_SYSTEMS[magic_key]

    attrs = {k: 5 for k in ["strength","intelligence","stealth","charisma","agility","willpower","perception","magic_power"]}
    for stat, bonus in ht["bonus"].items():
        attrs[stat] = attrs.get(stat, 5) + bonus
    for stat, bonus in gf["bonus"].items():
        attrs[stat] = attrs.get(stat, 5) + bonus

    start_item = copy.deepcopy(hm["item"])
    start_item["id"]       = str(uuid.uuid4())
    start_item["acquired"] = _ts()

    return {
        "id":          str(uuid.uuid4()),
        "name":        name,
        "hero_type":   ht["name"],
        "gift":        gf["name"],
        "magic":       magic,
        "home":        hm["name"],
        "home_lore":   hm["lore"],
        "created":     _ts(),
        "last_played": _ts(),
        "level":       1,
        "xp":          0,
        "xp_to_next":  100,
        "hp":          100,
        "hp_max":      100,
        "mana":        60,
        "mana_max":    60,
        "stamina":     50,
        "stamina_max": 50,
        "gold":        100,
        "rare_essence":0,
        "damage":      8 + attrs["strength"] // 2,
        "attributes":  attrs,
        "magic_system":{"element": magic, "spells": [f"{magic} Bolt"], "mastery": 1},
        "inventory":   [start_item],
        "equipped":    {"weapon": None, "armor": None, "relic": None, "accessory": None},
        "flags":       {"intro_complete": False, "act": 1, "quests_complete": [], "quests_active": [], "choices": [], "world_events": []},
        "reputation":  {"kingdom": 0, "thieves": 0, "mages": 0, "wilds": 0, "underworld": 0},
        "stats":       {"quests_complete": 0, "quests_failed": 0, "enemies_defeated": 0, "spells_cast": 0, "times_died": 0, "gold_earned": 0},
        "status":      {"poisoned": False, "poison_turns": 0, "shielded": False, "stunned": False},
        "save_slots":  {},
    }


# ══════════════════════════════════════════════
#  PROGRESSION
# ══════════════════════════════════════════════
def add_xp(hero, amount):
    hero["xp"] += amount
    leveled = False
    while hero["xp"] >= hero["xp_to_next"]:
        hero["xp"]         -= hero["xp_to_next"]
        hero["level"]      += 1
        hero["xp_to_next"]  = int(hero["xp_to_next"] * 1.35)
        hero["hp_max"]     += 12
        hero["hp"]          = hero["hp_max"]
        hero["mana_max"]   += 8
        hero["stamina_max"]+= 5
        hero["damage"]     += 2
        hero["magic_system"]["mastery"] = min(10, hero["magic_system"]["mastery"] + 1)
        leveled = True
        print(f"  ★ LEVEL UP → {hero['level']}!  HP {hero['hp_max']}  Mana {hero['mana_max']}  DMG {hero['damage']}")
    if not leveled:
        print(f"  +{amount} XP  ({hero['xp']}/{hero['xp_to_next']})")
    return leveled


# ══════════════════════════════════════════════
#  DISPLAY
# ══════════════════════════════════════════════
def show_hero(hero):
    a  = hero["attributes"]
    ms = hero["magic_system"]
    rp = hero["reputation"]
    st = hero["stats"]
    fl = hero["flags"]

    def rep_label(r):
        if r >=  80: return "LEGENDARY"
        if r >=  40: return "Trusted"
        if r >=  10: return "Neutral+"
        if r >= -10: return "Neutral"
        if r >= -40: return "Suspicious"
        if r >= -80: return "Hostile"
        return "HUNTED"

    print("\n" + "═"*58)
    print(f"  {hero['name'].upper()}  ·  {hero['hero_type'].upper()}")
    print(f"  Gift: {hero['gift']}  ·  Magic: {ms['element']}  ·  From: {hero['home']}")
    print(f"  \"{hero['home_lore']}\"")
    _div()
    print(f"  Level {hero['level']}  ·  XP {hero['xp']}/{hero['xp_to_next']}  ·  Act {fl['act']}")
    print(f"  HP {hero['hp']}/{hero['hp_max']}   Mana {hero['mana']}/{hero['mana_max']}   Stamina {hero['stamina']}/{hero['stamina_max']}")
    print(f"  Gold: ${hero['gold']}   Damage: {hero['damage']}   Rare Essence: {hero['rare_essence']}")
    _div()
    print("  ATTRIBUTES")
    for attr, val in a.items():
        print(f"    {attr:<18} {_bar(val, 20)}  {val}")
    _div()
    print(f"  MAGIC — {ms['element'].upper()}  (Mastery {ms['mastery']}/10)")
    print(f"  Spells: {', '.join(ms['spells'])}")
    _div()
    print("  REPUTATION")
    for fac, rep in rp.items():
        print(f"    {fac:<14} {rep:>+4}  {rep_label(rep)}")
    _div()
    print("  STATS")
    print(f"    Kills: {st['enemies_defeated']}   Quests: {st['quests_complete']}   Deaths: {st['times_died']}")
    print(f"    Spells cast: {st['spells_cast']}   Gold earned: ${st['gold_earned']}")
    _div()
    print(f"  Last played: {hero['last_played']}")
    print("═"*58 + "\n")

def show_inventory(hero):
    print(f"\n── Inventory ({len(hero['inventory'])} items) ──")
    if not hero["inventory"]:
        print("  (empty)")
    for item in hero["inventory"]:
        stats = "  ".join(f"{k}+{v}" for k, v in item.get("stats", {}).items())
        print(f"  • {item['name']:<26} [{item['type']:<10}]  ${item['value']:<5}  {stats}")
    print("── Equipped ──")
    for slot, item in hero["equipped"].items():
        print(f"  {slot:<12} {item['name'] if item else '—'}")


# ══════════════════════════════════════════════
#  INVENTORY ACTIONS
# ══════════════════════════════════════════════
def equip_item(hero, item_name):
    for item in hero["inventory"]:
        if item["name"].lower() == item_name.lower():
            slot = item["type"]
            if slot not in hero["equipped"]:
                print(f"  Can't equip type '{slot}'.")
                return
            hero["equipped"][slot] = item
            print(f"  Equipped '{item['name']}' → slot '{slot}'.")
            return
    print(f"  '{item_name}' not in inventory.")

def use_item(hero, item_name=None):
    consumables = [i for i in hero["inventory"] if i.get("type") == "consumable"]
    if not consumables:
        print("  No consumables in inventory.")
        return False
    item = next((i for i in consumables if item_name and i["name"].lower() == item_name.lower()), consumables[0])
    for stat, val in item.get("stats", {}).items():
        if stat == "hp":
            heal = min(val, hero["hp_max"] - hero["hp"])
            hero["hp"] += heal
            print(f"  💊 Used {item['name']} — restored {heal} HP.")
    hero["inventory"].remove(item)
    return True


# ══════════════════════════════════════════════
#  ENEMY FACTORY
# ══════════════════════════════════════════════
def make_enemy(level=1):
    t   = random.choice(ENEMY_TYPES)
    lv  = max(1, level)
    hp  = int(random.randint(*t["hp"])  * (1 + (lv-1) * 0.25))
    dmg = int(random.randint(*t["dmg"]) * (1 + (lv-1) * 0.20))
    return {
        "name":       t["name"],
        "level":      lv,
        "flavor":     t["flavor"],
        "hp":         hp,
        "hp_max":     hp,
        "damage":     dmg,
        "abilities":  list(t["abilities"]),
        "xp_reward":  random.randint(*t["xp"])   + (lv-1)*10,
        "gold_reward":random.randint(*t["gold"])  + (lv-1)*5,
        "loot":       random.choice(t["loot"]),
        "status":     {"poisoned": False, "poison_turns": 0, "shielded": False, "stunned": False},
    }


# ══════════════════════════════════════════════
#  QUESTS
# ══════════════════════════════════════════════
def check_quests(hero, silent=False):
    newly_done = []
    for q in QUEST_LIST:
        if q["id"] not in hero["flags"]["quests_complete"] and q["check"](hero):
            newly_done.append(q)
    if newly_done and not silent:
        print(f"\n  ★ Quest ready to claim: {', '.join(q['name'] for q in newly_done)}")
    return newly_done

def claim_quest(hero, quest_id):
    q = next((q for q in QUEST_LIST if q["id"] == quest_id), None)
    if not q:
        print(f"  Quest '{quest_id}' not found.")
        return
    if quest_id in hero["flags"]["quests_complete"]:
        print(f"  Quest '{q['name']}' already completed.")
        return
    if not q["check"](hero):
        print(f"  Quest '{q['name']}' not yet complete.")
        return
    hero["flags"]["quests_complete"].append(quest_id)
    hero["stats"]["quests_complete"] += 1
    if q["gold"]:
        hero["gold"] += q["gold"]
        hero["stats"]["gold_earned"] += q["gold"]
        print(f"  +${q['gold']} gold")
    if q["xp"]:
        add_xp(hero, q["xp"])
    print(f"  Quest '{q['name']}' complete!")

def show_quests(hero):
    print("\n── QUEST LOG ──────────────────────────────────────")
    for q in QUEST_LIST:
        done  = q["id"] in hero["flags"]["quests_complete"]
        ready = not done and q["check"](hero)
        status = "✓ COMPLETE" if done else ("★ READY"   if ready else "○ Active")
        print(f"  {status:<12} {q['name']} — {q['desc']}")
    _div()

    claimable = [q for q in QUEST_LIST
                 if q["id"] not in hero["flags"]["quests_complete"] and q["check"](hero)]
    if claimable:
        print("  Claimable:")
        for i, q in enumerate(claimable, 1):
            print(f"    [{i}] {q['name']}  (+{q['xp']} XP, +${q['gold']} gold)")
        choice = input("  Claim which? (number or Enter to skip) >> ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(claimable):
            claim_quest(hero, claimable[int(choice)-1]["id"])


# ══════════════════════════════════════════════
#  BATTLE ENGINE
# ══════════════════════════════════════════════
def _show_combatants(hero, enemy):
    _div("═")
    print(f"  {hero['name'].upper():<22}  VS  {enemy['name'].upper()}")
    _div()
    def hp_bar(cur, mx, w=20):
        filled = int(w * cur / max(mx,1))
        return "█"*filled + "░"*(w-filled)
    print(f"  HP  {hp_bar(hero['hp'],  hero['hp_max'])}  {hero['hp']}/{hero['hp_max']}")
    print(f"  HP  {hp_bar(enemy['hp'], enemy['hp_max'])}  {enemy['hp']}/{enemy['hp_max']}   [{enemy['name']}]")
    print(f"  ST  {hp_bar(hero['stamina'], hero['stamina_max'])}  {hero['stamina']}/{hero['stamina_max']}")
    _div("═")

def _show_status(entity, name):
    s = entity.get("status", {})
    flags = []
    if s.get("poisoned"):  flags.append(f"POISONED({s['poison_turns']})")
    if s.get("shielded"):  flags.append("SHIELDED")
    if s.get("stunned"):   flags.append("STUNNED")
    if flags:
        print(f"  ⚠  {name}: {', '.join(flags)}")

def _tick_poison(entity, name):
    s = entity.get("status", {})
    if s.get("poisoned") and s["poison_turns"] > 0:
        dmg = random.randint(2, 5)
        entity["hp"] = max(0, entity["hp"] - dmg)
        s["poison_turns"] -= 1
        if s["poison_turns"] <= 0:
            s["poisoned"] = False
            print(f"  🟢 {name} recovers from poison.")
        else:
            print(f"  ☠  Poison: -{dmg} HP to {name}! ({s['poison_turns']} turns left)")
        return dmg
    return 0

def _enemy_turn(hero, enemy, player_dodging):
    s = enemy["status"]
    if s.get("stunned"):
        s["stunned"] = False
        print(f"  💤 {enemy['name']} is stunned — skips turn!")
        return

    ability_key = random.choice(enemy["abilities"])
    ability     = ABILITIES[ability_key]
    print(f"\n  ⚔  {enemy['name']} uses {ability['name']}!")

    if ability_key == "shield_pulse":
        s["shielded"] = True
        print(f"  🛡  {enemy['name']} activates shield!")
        return

    raw_dmg = int(enemy["damage"] * ability["mult"] * (0.8 + random.random() * 0.5))

    if player_dodging and raw_dmg > 0:
        if random.random() < 0.70:
            print("  💨 You dodge the attack!")
            return
        else:
            print("  ❌ Dodge failed!")

    if raw_dmg > 0:
        hero["hp"] = max(0, hero["hp"] - raw_dmg)
        label = "💥 CRITICAL HIT!" if ability_key == "crit_strike" else "🩸"
        print(f"  {label} {enemy['name']} deals {raw_dmg} damage to you.")

    if ability["effect"] == "poison":
        hero["status"]["poisoned"]     = True
        hero["status"]["poison_turns"] = 3
        print("  ☠  You are POISONED for 3 turns!")

def _player_turn(hero, enemy):
    print(f"\n  What do you do?")
    for key, act in PLAYER_ACTIONS.items():
        cost = f"  [stamina: {act['stamina_cost']}]" if act["stamina_cost"] else ""
        print(f"    [{key:<8}]  {act['name']:<16} {cost}")
    print(f"    Stamina: {hero['stamina']}/{hero['stamina_max']}")

    action = input("\n  >> ").strip().lower()
    act    = PLAYER_ACTIONS.get(action, PLAYER_ACTIONS["attack"])

    # Stamina check
    cost = act["stamina_cost"]
    if hero["stamina"] < cost and action not in ("flee", "use_item"):
        print(f"  ⚠  Not enough stamina! Defaulting to Attack.")
        action = "attack"
        act    = PLAYER_ACTIONS["attack"]
        cost   = act["stamina_cost"]
    hero["stamina"] = max(0, hero["stamina"] - cost)

    print(f"\n  🎯 You use {act['name']}!")

    # ── Flee ──
    if action == "flee":
        if random.random() < 0.60:
            print("  🏃 You escape successfully!")
            return "fled", False
        else:
            print("  ❌ You couldn't escape!")
            return None, False

    # ── Use item ──
    if action == "use_item":
        use_item(hero)
        return None, False

    # ── Dodge ──
    if action == "dodge":
        print("  💨 You prepare to dodge!")
        return None, True   # player_dodging = True

    # ── Spell ──
    if action == "spell":
        sp_power = int(hero["attributes"]["magic_power"] * 1.5)
        dmg      = max(1, int(sp_power * (0.8 + random.random() * 0.6)))
        if enemy["status"].get("shielded"):
            dmg = dmg // 2
            enemy["status"]["shielded"] = False
            print(f"  🛡  Shield absorbed — reduced to {dmg} damage.")
        enemy["hp"] = max(0, enemy["hp"] - dmg)
        hero["mana"] = max(0, hero["mana"] - 12)
        hero["stats"]["spells_cast"] += 1
        spell = hero["magic_system"]["spells"][0]
        print(f"  🔮 {spell} — deals {dmg} to {enemy['name']}! (HP: {enemy['hp']}/{enemy['hp_max']})")
        return None, False

    # ── Attack / Heavy ──
    mult    = act["mult"]
    raw_dmg = max(1, int(hero["damage"] * mult * (0.8 + random.random() * 0.5)))
    if enemy["status"].get("shielded"):
        raw_dmg = raw_dmg // 2
        enemy["status"]["shielded"] = False
        print(f"  🛡  Shield absorbed — reduced to {raw_dmg} damage.")
    enemy["hp"] = max(0, enemy["hp"] - raw_dmg)
    print(f"  💢 You deal {raw_dmg} damage to {enemy['name']}! (HP: {enemy['hp']}/{enemy['hp_max']})")
    return None, False

def award_victory(hero, enemy):
    _div("═")
    print(f"  🏆  VICTORY!  {enemy['name']} defeated!")
    _div()
    hero["stats"]["enemies_defeated"] += 1
    xp   = enemy["xp_reward"]
    gold = enemy["gold_reward"]
    loot = enemy["loot"]
    add_xp(hero, xp)
    hero["gold"] += gold
    hero["stats"]["gold_earned"] += gold
    print(f"  💰 +${gold} gold  (total: ${hero['gold']})")
    if loot:
        item = {
            "id":          str(uuid.uuid4()),
            "name":        loot,
            "type":        "consumable" if loot == "Stim Pack" else "misc",
            "value":       random.randint(10, 60),
            "stats":       {"hp": 40} if loot == "Stim Pack" else {},
            "description": f"Dropped by {enemy['name']}.",
            "acquired":    _ts(),
        }
        hero["inventory"].append(item)
        print(f"  📦 Loot: {loot}")
    else:
        print("  📦 No loot this time.")
    _div("═")

def battle(hero, enemy):
    print(f"\n{'═'*56}")
    print(f"  ⚡  ENCOUNTER — {enemy['name'].upper()}")
    print(f"  {enemy['flavor']}")
    print(f"  Level {enemy['level']}  │  HP {enemy['hp']}  │  DMG {enemy['damage']}  │  [{', '.join(enemy['abilities'])}]")
    print(f"{'═'*56}\n")

    turn = 0
    while hero["hp"] > 0 and enemy["hp"] > 0:
        turn += 1
        print(f"\n  ── Turn {turn} {'─'*44}")
        _show_combatants(hero, enemy)
        _show_status(hero,  hero["name"])
        _show_status(enemy, enemy["name"])

        # Poison ticks
        _tick_poison(hero,  hero["name"])
        _tick_poison(enemy, enemy["name"])
        if hero["hp"] <= 0 or enemy["hp"] <= 0:
            break

        # Stamina regen
        hero["stamina"] = min(hero["stamina_max"], hero["stamina"] + 6)

        # Player turn
        result, player_dodging = _player_turn(hero, enemy)
        if result == "fled":
            return "fled"
        if enemy["hp"] <= 0:
            break

        # Enemy turn
        _enemy_turn(hero, enemy, player_dodging)

    print()
    _div("═")
    if enemy["hp"] <= 0:
        award_victory(hero, enemy)
        return "won"
    else:
        print(f"  💀  YOU HAVE FALLEN.")
        print(f"      {enemy['name']} stands over your body.")
        hero["stats"]["times_died"] += 1
        hero["hp"] = max(1, hero["hp_max"] // 3)
        print(f"  > Respawning at {hero['hp']}/{hero['hp_max']} HP...")
        _div("═")
        return "lost"


# ══════════════════════════════════════════════
#  HERO SELECTION
# ══════════════════════════════════════════════
def hero_selection():
    print("\nHero name: ", end="")
    name = input().strip()
    name = name[0].upper() + name[1:] if name else "Hero"

    type_key  = _pick("Select your hero class:",   HERO_TYPES)
    gift_key  = _pick("Select your hero's gift:",  GIFTS)
    magic_key = _pick("Select your magic system:", MAGIC_SYSTEMS)
    home_key  = _pick("Select your hero's home:",  HERO_HOMES)

    return name, type_key, gift_key, magic_key, home_key


# ══════════════════════════════════════════════
#  MAIN MENU
# ══════════════════════════════════════════════
def main_menu(hero):
    while True:
        print(f"\n{'━'*54}")
        print(f"  // ACT {hero['flags']['act']} — MAIN MENU")
        print(f"{'━'*54}")
        print("  [1] ⚔  Encounter")
        print("  [2] 🎒  Inventory")
        print("  [3] 📜  Quests")
        print("  [4] 💾  Save")
        print("  [5] 📊  Status")
        print("  [6] 🏆  Leaderboard")
        print("  [7] 🚪  Quit")

        choice = input("\n  >> ").strip()

        if choice == "1":
            enemy  = make_enemy(hero["level"])
            result = battle(hero, enemy)
            if result == "won":
                push_to_leaderboard(hero)
                check_quests(hero)
            save_hero(hero)

        elif choice == "2":
            show_inventory(hero)
            print("\n  [E] Equip  [U] Use consumable  [B] Back")
            sub = input("  >> ").strip().upper()
            if sub == "E":
                name = input("  Item name to equip: ").strip()
                equip_item(hero, name)
                save_hero(hero)
            elif sub == "U":
                use_item(hero)
                save_hero(hero)

        elif choice == "3":
            show_quests(hero)
            save_hero(hero)

        elif choice == "4":
            save_hero(hero)
            push_to_leaderboard(hero)
            print("  > Synced to leaderboard.")

        elif choice == "5":
            show_hero(hero)

        elif choice == "6":
            show_leaderboard()

        elif choice == "7":
            save_hero(hero)
            push_to_leaderboard(hero)
            print("\n  // SESSION CLOSED. YOUR LEGEND PERSISTS.\n")
            break

        else:
            print("  Invalid choice.")


# ══════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════
if __name__ == "__main__":
    print("╔══════════════════════════════════════════╗")
    print("║       WELCOME TO THE HERO'S JOURNEY      ║")
    print("║           NEON DISTRICT // 2157          ║")
    print("╚══════════════════════════════════════════╝\n")

    existing = list_heroes()
    hero     = None

    if existing:
        print("── Existing heroes ──")
        for i, h in enumerate(existing, 1):
            print(f"  [{i}] {h['name']:<16} {h['hero_type']:<10} "
                  f"Lv{h['level']}  Act {h['flags']['act']}  "
                  f"Last: {h['last_played']}")
        print(f"  [N] New hero")
        print(f"  [D] Delete a hero")
        print(f"  [L] Leaderboard")

        choice = input("\n>> ").strip().upper()

        if choice == "N":
            pass  # fall through to creation

        elif choice == "D":
            name = input("Hero name to delete: ").strip()
            delete_hero(name)
            existing = list_heroes()

        elif choice == "L":
            show_leaderboard()

        elif choice.isdigit() and 1 <= int(choice) <= len(existing):
            hero = load_hero(existing[int(choice)-1]["name"])

        else:
            hero = load_hero(choice) if not choice.isdigit() else None

    # Create new hero if none loaded
    if hero is None:
        name, type_key, gift_key, magic_key, home_key = hero_selection()

        if hero_exists(name):
            print(f"\n  A hero named '{name}' already exists.")
            overwrite = input("  Overwrite? (yes/no): ").strip().lower()
            if overwrite == "yes":
                hero = build_hero(name, type_key, gift_key, magic_key, home_key)
                save_hero(hero)
            else:
                hero = load_hero(name)
        else:
            hero = build_hero(name, type_key, gift_key, magic_key, home_key)
            save_hero(hero)

        ht = HERO_TYPES[type_key]
        gf = GIFTS[gift_key]
        print(f"\nYour hero is {hero['name']}, a {hero['hero_type']} "
              f"with a gift for {hero['gift']} "
              f"and a magic system of {hero['magic']} "
              f"from {hero['home']}.")

    # Equip starting weapon if one exists
    for item in hero["inventory"]:
        if item["type"] in ("weapon", "relic"):
            equip_item(hero, item["name"])
            break

    show_hero(hero)
    push_to_leaderboard(hero)
    print("\nYou are ready to begin the epic journey!")
    print("─"*56)

    main_menu(hero)