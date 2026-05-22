import time

# Inventory
inventory = []

# Items
items_in_pantry = [
    {"name": "tomato", "type": "food", "uses": 6, "description": "A red and ripe fruit."},
    {"name": "egg", "type": "food", "uses": 10, "description": "A white egg."},
    {"name": "eggplant", "type": "food", "uses": 2, "description": "A soft, purple vegetable."},
    {"name": "bell pepper", "type": "food", "uses": 3, "description": "A red, juicy vegetable."},
    {"name": "onion", "type": "food", "uses": 8, "description": "A vegetable that is brown and dry from the outside, white and juicy from the inside."},
    {"name": "carrot", "type": "food", "uses": 12, "description": "A long orange vegetable."},
    {"name": "lettuce", "type": "food", "uses": 2, "description": "Green and juicy leaves."},
    {"name": "celery", "type": "food", "uses": 2, "description": "A hard, long and green plant."},
]
items_in_cupboard = [
    {"name": "kitchen knife", "type": "tool", "uses": 10, "description": "A sharp blade with a wooden handle."},
    {"name": "fork", "type": "silverware", "uses": 10, "description": "A silver object with three tines"},
    {"name": "spoon", "type": "silverware", "uses": 10, "description": "A silver object with a small hollow."},
    {"name": "knife", "type": "silverware", "uses": 10, "description": "A silver object with a dull blade."},
    {"name": "pot", "type": "tool", "uses": 100, "description": "A metal container with a lid."},
    {"name": "pan", "type": "tool", "uses": 100, "description": "A metal hollow with a handle."},
    {"name": "bowl", "type": "tool", "uses": 10, "description": "A porcelain hollow."},
    {"name": "cutting board", "type": "tool", "uses": 10000, "description": "A used wooden board"},
    {"name": "bandage", "type": "healing", "uses": 10, "description": "A small sticky plastic object used on cutting wounds."},
]

# Recipes
omelette_recipe = {
    "name": "Omelette",
    "steps": ["egg", "pan", "egg"]
}

current_step = 0

# Functions for showing Inventory and other storage places
def show_inventory():
    print("Inventory:")
    for item in inventory:
        print(f"- {item['name']} ({item['uses']} uses left)")

def show_pantry():
    print("Pantry:")
    for item in items_in_pantry:
        print(f"- {item['name']} ({item['uses']} uses left)")

def show_cupboard():
    print("Cupboard:")
    for item in items_in_cupboard:
        print(f"- {item['name']} ({item['uses']} uses left)")

# Functions for picking up, dropping, examining and using items
def pickup_item(item_name):
    if len(inventory) >= 5:
        print("Your inventory is full!")
        return False
    for item in items_in_pantry:
        if item["name"] == item_name:
            inventory.append(item)
            items_in_pantry.remove(item)
            return True
    for item in items_in_cupboard:
        if item["name"] == item_name:
            inventory.append(item)
            items_in_cupboard.remove(item)
            return True
    return False

def drop_item(item_name):
    for item in inventory:
        if item["name"] == item_name:
            inventory.remove(item)
            if item["type"] == "food":
                items_in_pantry.append(item)
            else:
                items_in_cupboard.append(item)
            return True

def use_item(item_name):
    for item in inventory:
        if item["name"] == item_name:
            item["uses"] -= 1

def examine(item_name):
    for item in inventory + items_in_pantry + items_in_cupboard:
        if item["name"] == item_name:
            print(item["description"])
            return True
    print("Item not found.")
    return False

def start_cooking_game():
    print("Congratulations!")
    time.sleep(2)
    print("You have a lot of friends!")
    time.sleep(2)
    print("Unfortunately, you invited them for a dinner and you have to cook for them.")
    time.sleep(2)
    print("You have 10 minutes (rounds) to prepare your meal.")
    time.sleep(2)
    print("If the time runs out, you will lose all your friends.")
    time.sleep(2)
    print("Type 'help' for a list of commands.")
    time.sleep(2)
    print("Welcome to the cooking game!")

# Main function for getting user input
def main():
    start_cooking_game()
    while True:
        command = input("What do you want to do? ")
        command = command.lower()
        command = command.split()
        if command[0] == "show":
            if command[1] == "inventory":
                show_inventory()
            elif command[1] == "pantry":
                show_pantry()
            elif command[1] == "cupboard":
                show_cupboard()
        elif command[0] == "pickup":
            pickup_item(" ".join(command[1:]))
        elif command[0] == "drop":
            drop_item(" ".join(command[1:]))
        elif command[0] == "use":
            use_item(" ".join(command[1:]))
        elif command[0] == "examine":
            examine(" ".join(command[1:]))
        elif command[0] == "cook":
            if command[1] == "omelette":
                cook_omelette()
        elif command[0] == "help":
            print(
                "Commands: show inventory, show pantry, show cupboard, pickup [item], drop [item], use [item], examine [item]")
        else:
            print("Unknown command.")

def is_in_inventory(item_name):
    for item in inventory:
        if item["name"] == item_name:
            return True
    return False

def cook_omelette():
    global current_step
    needed_item = omelette_recipe["steps"][current_step]
    if is_in_inventory(needed_item):
        if current_step == 0:
            print("You crack the egg.")
        elif current_step == 1:
            print("You whisk the Egg together.")
        elif current_step == 2:
            print("You fry the Egg in the pan.")
        current_step += 1
        print("Good job!")
    else:
        print(f"You need {needed_item} in your inventory!")
    if current_step == len(omelette_recipe["steps"]):
        print("You finished the omelette!")
        inventory.append({"name": "plate of omelette", "uses": 1, "type": "food"})

if __name__ == "__main__":
    main()

# To be honest I made the Task bigger than it was.
# My original Idea was to have a Game where you have to cook 3 Meals in a certain time with many ingredients.
# You'd have to put in the right commands at the right time so that you wouldn't fail your dish.
# I also wanted to implement a cutting minigame where you could cut your hand and would lose time bandaging it.
# But I think this Idea was far beyond my capabilities, even with Claude as a explaining tool.
# It was also very difficult to structure my idea and to realize what would be possible.
# I would really like to finish this project but it is beyond my capabilities and I think also beyond time ressourcces.