# A simple turn-based sci fi game

# game setup for new game

# hero selection
import json
import os
import datetime
import uuid
import copy

# ══════════════════════════════════════════════
#  FILE PATHS
# ══════════════════════════════════════════════
SAVE_DIR = "saves"
SAVE_FILE = os.path.join(SAVE_DIR, "heroes.json")
os.makedirs(SAVE_DIR, exist_ok=True)

# ══════════════════════════════════════════════
#  LOOKUP TABLES  (number → label)
# ══════════════════════════════════════════════
HERO_TYPES = {
    "1": "Sorcerer",
    "2": "Thug",
    "3": "Slayer",
    "4": "Sneak",
    "5": "Genius",
}

GIFTS = {
    "1": "Speech",
    "2": "Speed",
    "3": "Physical Strength",
    "4": "Sight",
    "5": "Love",
}

MAGIC_SYSTEMS = {
    "1": "Fire",
    "2": "Water",
    "3": "Earth",
    "4": "Air",
    "5": "Lightning",
    "6": "Darkness",
    "7": "Nano",
}

HERO_HOMES = {
    "1": "Forest",
    "2": "Desert",
    "3": "Mountain",
    "4": "Sea",
    "5": "Sky",
}

# Starting stat bonuses per hero type
TYPE_BONUSES = {
    "Sorcerer": {"magic_power": 3, "intelligence": 2, "stealth": 0, "strength": 0, "charisma": 0},
    "Thug": {"magic_power": 0, "intelligence": 0, "stealth": 0, "strength": 3, "charisma": 1},
    "Slayer": {"magic_power": 1, "intelligence": 0, "stealth": 1, "strength": 2, "charisma": 0},
    "Sneak": {"magic_power": 0, "intelligence": 1, "stealth": 3, "strength": 0, "charisma": 1},
    "Genius": {"magic_power": 1, "intelligence": 3, "stealth": 0, "strength": 0, "charisma": 1},
}

# Starting stat bonuses per gift
GIFT_BONUSES = {
    "Speech": {"charisma": 3},
    "Speed": {"agility": 3},
    "Physical Strength": {"strength": 3},
    "Sight": {"perception": 3},
    "Love": {"willpower": 3},
}

# Home environment flavour (affects starting item + lore)
HOME_LORE = {
    "Forest": "raised among ancient trees and hidden paths",
    "Desert": "hardened by endless heat and scarce water",
    "Mountain": "forged in cold stone and thin air",
    "Sea": "born on open water, navigator by instinct",
    "Sky": "a child of the clouds, unbounded and restless",
}


# ══════════════════════════════════════════════
#  TIMESTAMP HELPER
# ══════════════════════════════════════════════
def _timestamp():
    return datetime.datetime.now().isoformat(timespec="seconds")


# ══════════════════════════════════════════════
#  DEFAULT PLAYER BUILDER
# ══════════════════════════════════════════════
def build_hero(name, hero_type, gift, magic, home):
    """Construct a full hero record from hero_selection() choices."""

    # Base attributes
    base_attrs = {
        "strength": 5,
        "intelligence": 5,
        "stealth": 5,
        "charisma": 5,
        "agility": 5,
        "willpower": 5,
        "perception": 5,
        "magic_power": 5,
    }

    # Apply type bonus
    for stat, bonus in TYPE_BONUSES.get(hero_type, {}).items():
        base_attrs[stat] = base_attrs.get(stat, 5) + bonus

    # Apply gift bonus
    for stat, bonus in GIFT_BONUSES.get(gift, {}).items():
        base_attrs[stat] = base_attrs.get(stat, 5) + bonus

    # Starting item based on home
    home_items = {
        "Forest": {"name": "Carved Bow", "type": "weapon", "value": 40,
                   "stats": {"agility": 1},
                   "description": "Bent from a living branch. Still grows."},
        "Desert": {"name": "Sand Cloak", "type": "armor", "value": 35,
                   "stats": {"stealth": 1},
                   "description": "Blends with dunes. Keeps the heat out."},
        "Mountain": {"name": "Iron Pick", "type": "weapon", "value": 38,
                     "stats": {"strength": 1},
                     "description": "Used for climbing first, fighting second."},
        "Sea": {"name": "Navigator's Chart", "type": "key_item", "value": 50,
                "stats": {"perception": 1},
                "description": "Shows coasts no map-maker ever drew."},
        "Sky": {"name": "Wind Charm", "type": "relic", "value": 45,
                "stats": {"agility": 1, "magic_power": 1},
                "description": "Hums when a storm is three days out."},
    }
    start_item = home_items.get(home, {})
    if start_item:
        start_item["id"] = str(uuid.uuid4())
        start_item["acquired"] = _timestamp()

    return {
        # ── Identity ──
        "id": str(uuid.uuid4()),
        "name": name,
        "hero_type": hero_type,
        "gift": gift,
        "magic": magic,
        "home": home,
        "home_lore": HOME_LORE.get(home, ""),
        "created": _timestamp(),
        "last_played": _timestamp(),

        # ── Progression ──
        "level": 1,
        "xp": 0,
        "xp_to_next": 100,

        # ── Vitals ──
        "hp": 100,
        "hp_max": 100,
        "mana": 60,
        "mana_max": 60,
        "stamina": 50,
        "stamina_max": 50,

        # ── Currency ──
        "gold": 100,
        "rare_essence": 0,  # drops from powerful enemies

        # ── Attributes ──
        "attributes": base_attrs,

        # ── Magic ──
        "magic_system": {
            "element": magic,
            "spells": [f"{magic} Bolt"],  # starting spell
            "mastery": 1,  # 1-10
        },

        # ── Inventory ──
        "inventory": [start_item] if start_item else [],

        # ── Equipped ──
        "equipped": {
            "weapon": None,
            "armor": None,
            "relic": None,
            "accessory": None,
        },

        # ── Story flags ──
        "flags": {
            "intro_complete": False,
            "act": 1,
            "quests_complete": [],
            "quests_active": [],
            "choices": [],
            "world_events": [],
        },

        # ── Reputation ──
        "reputation": {
            "kingdom": 0,
            "thieves": 0,
            "mages": 0,
            "wilds": 0,
            "underworld": 0,
        },

        # ── Lifetime stats ──
        "stats": {
            "quests_complete": 0,
            "quests_failed": 0,
            "enemies_defeated": 0,
            "spells_cast": 0,
            "times_died": 0,
            "gold_earned": 0,
            "play_time_seconds": 0,
        },

        # ── Save slots ──
        "save_slots": {},
    }


# ══════════════════════════════════════════════
#  DATABASE HELPERS
# ══════════════════════════════════════════════
def _load_db():
    if not os.path.exists(SAVE_FILE):
        return {}
    try:
        with open(SAVE_FILE, "r") as f:
            content = f.read().strip()
            return json.loads(content) if content else {}
    except (json.JSONDecodeError, OSError) as e:
        print(f"[SAVE] Warning — could not read save file: {e}")
        return {}


def _write_db(db):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(db, f, indent=2)
    except OSError as e:
        print(f"[SAVE] Error — could not write save file: {e}")


# ══════════════════════════════════════════════
#  PLAYER CRUD
# ══════════════════════════════════════════════
def save_hero(hero):
    db = _load_db()
    hero["last_played"] = _timestamp()
    db[hero["name"]] = hero
    _write_db(db)
    print(f"[SAVE] '{hero['name']}' saved.")


def load_hero(name):
    db = _load_db()
    hero = db.get(name)
    if hero is None:
        print(f"[SAVE] Hero '{name}' not found.")
        return None
    hero["last_played"] = _timestamp()
    _write_db(db)
    print(f"[SAVE] Hero '{name}' loaded.")
    return hero


def delete_hero(name):
    db = _load_db()
    if name not in db:
        print(f"[SAVE] Hero '{name}' not found.")
        return False
    del db[name]
    _write_db(db)
    print(f"[SAVE] Hero '{name}' deleted.")
    return True


def hero_exists(name):
    return name in _load_db()


def list_heroes():
    db = _load_db()
    heroes = []
    for h in db.values():
        heroes.append({
            "name": h["name"],
            "hero_type": h["hero_type"],
            "gift": h["gift"],
            "magic": h["magic"],
            "home": h["home"],
            "level": h["level"],
            "act": h["flags"]["act"],
            "last_played": h["last_played"],
        })
    return sorted(heroes, key=lambda x: x["last_played"], reverse=True)


# ══════════════════════════════════════════════
#  QUICK-SAVE SLOTS
# ══════════════════════════════════════════════
def quick_save(hero, slot="slot_1"):
    snapshot = copy.deepcopy(hero)
    snapshot.pop("save_slots", None)
    hero["save_slots"][slot] = {
        "timestamp": _timestamp(),
        "data": snapshot,
    }
    save_hero(hero)
    print(f"[SAVE] Quick-save written to '{slot}'.")


def quick_load(hero, slot="slot_1"):
    slots = hero.get("save_slots", {})
    if slot not in slots:
        print(f"[SAVE] Slot '{slot}' not found.")
        return None
    restored = copy.deepcopy(slots[slot]["data"])
    restored["save_slots"] = hero["save_slots"]
    print(f"[SAVE] Loaded from slot '{slot}' (saved {slots[slot]['timestamp']}).")
    return restored


def list_save_slots(hero):
    slots = hero.get("save_slots", {})
    if not slots:
        print("  No quick-save slots found.")
        return
    for slot, info in slots.items():
        d = info["data"]
        print(f"  [{slot}]  Level {d['level']}  |  "
              f"Act {d['flags']['act']}  |  "
              f"Saved: {info['timestamp']}")


# ══════════════════════════════════════════════
#  PROGRESSION
# ══════════════════════════════════════════════
def add_xp(hero, amount):
    hero["xp"] += amount
    leveled = False
    while hero["xp"] >= hero["xp_to_next"]:
        hero["xp"] -= hero["xp_to_next"]
        hero["level"] += 1
        hero["xp_to_next"] = int(hero["xp_to_next"] * 1.35)
        hero["hp_max"] += 12
        hero["hp"] = hero["hp_max"]
        hero["mana_max"] += 8
        hero["stamina_max"] += 5
        hero["magic_system"]["mastery"] = min(10, hero["magic_system"]["mastery"] + 1)
        leveled = True
        print(f"  ★ LEVEL UP → {hero['level']}  "
              f"(HP {hero['hp_max']}  Mana {hero['mana_max']})")
    if not leveled:
        print(f"  +{amount} XP  ({hero['xp']}/{hero['xp_to_next']})")
    return leveled


def modify_attribute(hero, attr, delta):
    if attr not in hero["attributes"]:
        print(f"[RPG] Unknown attribute: {attr}")
        return
    old = hero["attributes"][attr]
    hero["attributes"][attr] = max(1, min(20, old + delta))
    print(f"  {attr.capitalize()}  {old} → {hero['attributes'][attr]}")


def modify_reputation(hero, faction, delta):
    if faction not in hero["reputation"]:
        print(f"[RPG] Unknown faction: {faction}")
        return
    old = hero["reputation"][faction]
    hero["reputation"][faction] = max(-100, min(100, old + delta))
    new = hero["reputation"][faction]
    print(f"  {faction.capitalize()} reputation  {old:+d} → {new:+d}  ({_rep_label(new)})")


def _rep_label(rep):
    if rep >= 80: return "LEGENDARY"
    if rep >= 40: return "Trusted"
    if rep >= 10: return "Neutral+"
    if rep >= -10: return "Neutral"
    if rep >= -40: return "Suspicious"
    if rep >= -80: return "Hostile"
    return "HUNTED"


def complete_quest(hero, quest_id, xp=0, gold=0):
    if quest_id in hero["flags"]["quests_complete"]:
        print(f"[RPG] Quest '{quest_id}' already completed.")
        return
    hero["flags"]["quests_complete"].append(quest_id)
    hero["stats"]["quests_complete"] += 1
    if gold:
        hero["gold"] += gold
        hero["stats"]["gold_earned"] += gold
        print(f"  +{gold} gold")
    if xp:
        add_xp(hero, xp)
    print(f"  Quest '{quest_id}' complete.")


def learn_spell(hero, spell_name):
    spells = hero["magic_system"]["spells"]
    if spell_name not in spells:
        spells.append(spell_name)
        print(f"  Learned spell: {spell_name}")
    else:
        print(f"  Already knows: {spell_name}")


def set_flag(hero, key, value):
    hero["flags"][key] = value
    print(f"  [FLAG] {key} = {value}")


def log_choice(hero, description):
    hero["flags"]["choices"].append({"time": _timestamp(), "event": description})
    print(f"  [STORY] {description}")


# ══════════════════════════════════════════════
#  INVENTORY
# ══════════════════════════════════════════════
def make_item(name, item_type, value=0, stats=None, description=""):
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "type": item_type,
        "value": value,
        "stats": stats or {},
        "description": description,
        "acquired": _timestamp(),
    }


def add_item(hero, item):
    hero["inventory"].append(item)
    print(f"  [INV] Added: {item['name']}")


def remove_item(hero, item_name):
    for i, item in enumerate(hero["inventory"]):
        if item["name"].lower() == item_name.lower():
            hero["inventory"].pop(i)
            print(f"  [INV] Removed: {item_name}")
            return True
    print(f"  [INV] '{item_name}' not found.")
    return False


def equip_item(hero, item_name):
    for item in hero["inventory"]:
        if item["name"].lower() == item_name.lower():
            slot = item["type"]
            if slot not in hero["equipped"]:
                print(f"  [INV] Can't equip type '{slot}'.")
                return
            hero["equipped"][slot] = item
            print(f"  [INV] Equipped '{item['name']}' → slot '{slot}'.")
            return
    print(f"  [INV] '{item_name}' not in inventory.")


def show_inventory(hero):
    print(f"\n── Inventory ({len(hero['inventory'])} items) ──")
    if not hero["inventory"]:
        print("  (empty)")
    for item in hero["inventory"]:
        stats = "  ".join(f"{k}+{v}" for k, v in item["stats"].items())
        print(f"  • {item['name']:<26} [{item['type']:<10}]  "
              f"${item['value']:<5}  {stats}")
    print("── Equipped ──")
    for slot, item in hero["equipped"].items():
        print(f"  {slot:<12} {item['name'] if item else '—'}")


# ══════════════════════════════════════════════
#  DISPLAY
# ══════════════════════════════════════════════
def show_hero(hero):
    a = hero["attributes"]
    ms = hero["magic_system"]
    rp = hero["reputation"]
    st = hero["stats"]
    fl = hero["flags"]

    print("\n" + "═" * 56)
    print(f"  {hero['name'].upper()}  ·  {hero['hero_type'].upper()}")
    print(f"  Gift: {hero['gift']}  ·  Magic: {ms['element']}  "
          f"·  From: {hero['home']}")
    print(f"  \"{hero['home_lore']}\"")
    print("─" * 56)
    print(f"  Level {hero['level']}  ·  XP {hero['xp']}/{hero['xp_to_next']}  "
          f"·  Act {fl['act']}")
    print(f"  HP      {hero['hp']}/{hero['hp_max']}   "
          f"Mana    {hero['mana']}/{hero['mana_max']}   "
          f"Stamina {hero['stamina']}/{hero['stamina_max']}")
    print(f"  Gold    {hero['gold']}   Rare Essence  {hero['rare_essence']}")
    print("─" * 56)
    print("  ATTRIBUTES")
    for attr, val in a.items():
        bar = "█" * val + "░" * (20 - val)
        print(f"    {attr:<18} {bar}  {val}")
    print("─" * 56)
    print(f"  MAGIC — {ms['element'].upper()}  "
          f"(Mastery {ms['mastery']}/10)")
    print(f"  Spells known: {', '.join(ms['spells'])}")
    print("─" * 56)
    print("  REPUTATION")
    for fac, rep in rp.items():
        label = _rep_label(rep)
        print(f"    {fac:<14} {rep:>+4}  {label}")
    print("─" * 56)
    print("  LIFETIME STATS")
    print(f"    Quests  {st['quests_complete']}✓  {st['quests_failed']}✗  "
          f"│  Enemies  {st['enemies_defeated']}  "
          f"│  Deaths  {st['times_died']}")
    print(f"    Spells cast  {st['spells_cast']}  "
          f"│  Gold earned  {st['gold_earned']}")
    print("─" * 56)
    print(f"  Last played: {hero['last_played']}")
    print("═" * 56 + "\n")


print(show_hero)


# ══════════════════════════════════════════════
#  HERO SELECTION  (your original code, extended)
# ══════════════════════════════════════════════
def _pick(prompt, options):
    """Show a numbered menu and return the resolved string value."""
    print(f"\n{prompt}")
    for k, v in options.items():
        print(f"  [{k}] {v}")
    while True:
        choice = input(">> ").strip()
        if choice in options:
            return options[choice]
        # Also accept typing the name directly
        for v in options.values():
            if choice.lower() == v.lower():
                return v
        print(f"  Please enter a number 1–{len(options)}.")


def hero_selection():
    hero_name = input("\nHero name: ").strip()
    hero_type = _pick("Select your hero type:", HERO_TYPES)
    hero_gift = _pick("Select your hero's gift:", GIFTS)
    magic = _pick("Select your magic system:", MAGIC_SYSTEMS)
    hero_home = _pick("Select your hero's home:", HERO_HOMES)
    return hero_name, hero_type, hero_gift, magic, hero_home


# ══════════════════════════════════════════════
#  MAIN ENTRY POINT
# ══════════════════════════════════════════════
if __name__ == "__main__":

    print("╔══════════════════════════════════════════╗")
    print("║       WELCOME TO THE HERO'S JOURNEY      ║")
    print("╚══════════════════════════════════════════╝")
    print("Please select your hero.\n")

    # ── Check for existing heroes first ──
    existing = list_heroes()
    hero = None

    if existing:
        print("── Existing heroes found ──")
        for i, h in enumerate(existing, 1):
            print(f"  [{i}] {h['name']:<16} {h['hero_type']:<10} "
                  f"Lv{h['level']}  Act {h['act']}  "
                  f"Last: {h['last_played']}")
        print(f"  [N] Create a new hero")
        print(f"  [D] Delete a hero")

        choice = input("\n>> ").strip().upper()

        if choice == "N":
            pass  # fall through to creation below

        elif choice == "D":
            name = input("Hero name to delete: ").strip()
            delete_hero(name)
            # re-list and continue
            existing = list_heroes()

        elif choice.isdigit() and 1 <= int(choice) <= len(existing):
            hero = load_hero(existing[int(choice) - 1]["name"])

        else:
            # Maybe they typed a name
            hero = load_hero(choice) if not choice.isdigit() else None

    # ── Create new hero if none loaded ──
    if hero is None:
        hero_name, hero_type, hero_gift, magic, hero_home = hero_selection()

        if hero_exists(hero_name):
            print(f"\n  A hero named '{hero_name}' already exists.")
            overwrite = input("  Overwrite? (yes/no): ").strip().lower()
            if overwrite != "yes":
                print("  Keeping existing hero. Loading instead.")
                hero = load_hero(hero_name)
            else:
                hero = build_hero(hero_name, hero_type, hero_gift, magic, hero_home)
                save_hero(hero)
        else:
            hero = build_hero(hero_name, hero_type, hero_gift, magic, hero_home)
            save_hero(hero)

        # ── Your original confirmation line ──
        print(f"\nYour hero is {hero['name']}, a {hero['hero_type']} "
              f"with a gift for {hero['gift']} "
              f"and a magic system of {hero['magic']['element'] if isinstance(hero['magic'], dict) else hero['magic']} "
              f"from {hero['home']}.")

    # ── Show full profile ──
    show_hero(hero)

    # ── Equip starting weapon if one exists ──
    for item in hero["inventory"]:
        if item["type"] in ("weapon", "relic"):
            equip_item(hero, item["name"])
            break

    show_inventory(hero)

    # ── Demo: quick-save ──
    quick_save(hero, "slot_1")
    list_save_slots(hero)

    print("\nYou are ready to begin the epic journey!")
    print("─" * 56)
    print("(Your hero is saved and will be here when you return.)")
    print("─" * 56)

    # Final persist
    save_hero(hero)
