import time
import sys

# Inventory
inventory = []

# Items
items_in_pantry = [
    {"name": "tomato", "type": "food", "description": "A red and ripe fruit."},
    {"name": "egg", "type": "food", "description": "A white egg."},
    {"name": "eggplant", "type": "food", "description": "A soft, purple vegetable."},
    {"name": "bell pepper", "type": "food", "description": "A red, juicy vegetable."},
    {"name": "onion", "type": "food", "description": "A vegetable that is brown and dry from the outside, white and juicy from the inside."},
    {"name": "carrot", "type": "food", "description": "A long orange vegetable."},
    {"name": "lettuce", "type": "food", "description": "Green and juicy leaves."},
    {"name": "celery", "type": "food", "description": "A hard, long and green plant."},
    {"name": "parsley", "type": "garnish", "description": "Green Leaves in a bundle."},
]
items_in_cupboard = [
    {"name": "kitchen knife", "type": "tool", "description": "A sharp blade with a wooden handle."},
    {"name": "fork", "type": "silverware", "description": "A silver object with three tines"},
    {"name": "spoon", "type": "silverware", "description": "A silver object with a small hollow."},
    {"name": "knife", "type": "silverware", "description": "A silver object with a dull blade."},
    {"name": "pot", "type": "tool", "description": "A metal container with a lid."},
    {"name": "pan", "type": "tool", "description": "A metal hollow with a handle."},
    {"name": "bowl", "type": "tool", "description": "A porcelain hollow."},
    {"name": "cutting board", "type": "tool", "description": "A used wooden board"},
    {"name": "bandage", "type": "healing", "description": "A small sticky plastic object used on cutting wounds."},
]
# Recipes
omelette_recipe = {
    "name": "Omelette",
    "steps": ["egg", "pan", "egg", "tomato", "parsley"]
}

current_step = 0

# Functions for showing Inventory and other storage places
def show_inventory():
    print("Inventory:")
    for item in inventory:
        print(f"- {item['name']}")

def show_pantry():
    print("Pantry:")
    for item in items_in_pantry:
        print(f"- {item['name']}")

def show_cupboard():
    print("Cupboard:")
    for item in items_in_cupboard:
        print(f"- {item['name']}")

# Functions for picking up, dropping, examining and using items
def pickup_item(item_name):
    if len(inventory) >= 5:
        print("Your inventory is full!")
        return False
    for item in items_in_pantry:
        if item["name"] == item_name:
            inventory.append(item)
            items_in_pantry.remove(item)
            print("You've picked up", item["name"], "from the pantry")
            return True
    for item in items_in_cupboard:
        if item["name"] == item_name:
            inventory.append(item)
            items_in_cupboard.remove(item)
            print("You've picked up a", item["name"], "from the cupboard")
            return True
    return False

def drop_item(item_name):
    for item in inventory:
        if item["name"] == item_name:
            inventory.remove(item)
            if item["type"] == "food" or item["type"] == "garnish":
                items_in_pantry.append(item)
                print("You've put", item["name"], "back in the pantry")
            else:
                items_in_cupboard.append(item)
                print("You've put", item["name"], "back in the cupboard")
            return True

def examine(item_name):
    for item in inventory + items_in_pantry + items_in_cupboard:
        if item["name"] == item_name:
            print(item["description"])
            print(f"- It is classified as a {item['type']} ")
            return True
    print("Item not found.")
    return False

# Intro of the Game
def start_cooking_game():
    print("Congratulations!")
    time.sleep(2)
    print("You have a friend!")
    time.sleep(2)
    print("Unfortunately, you invited them for a dinner and you have to cook for them.")
    time.sleep(2)
    print("Type 'help' for a list of commands.")
    time.sleep(2)
    print("Welcome to the cooking game!")
    time.sleep(2)

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
        elif command[0] == "examine":
            examine(" ".join(command[1:]))
        elif command[0] == "cook":
            if command[1] == "omelette":
                cook_omelette()
        elif command[0] == "help":
            print(
                "Commands: show inventory, show pantry, show cupboard, pickup [item], drop [item], examine [item], cook omelette")
        else:
            print("Unknown command.")

# Function for checking if the needed Item for the recipe is in the players Inventory
def is_in_inventory(item_name):
    for item in inventory:
        if item["name"] == item_name:
            return True
    return False

# Ending the Game after finishing the omelette
def game_end():
    print("You cooked for your Friend!")
    time.sleep(3)
    print("Thank you for playing the cooking Game.")
    sys.exit()

# function for cooking the omelette
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
        elif current_step == 3:
            print("You garnish the Omelette with Tomato.")
        elif current_step == 4:
            print("You garnish the Omelette with Parsley.")
        current_step += 1
        print("Good job!")
    else:
        print(f"You need {needed_item} in your inventory!")
    if current_step == len(omelette_recipe["steps"]):
        print("You finished the omelette!")
        inventory.append({"name": "plate of omelette", "type": "food"})
        game_end()

if __name__ == "__main__":
    main()

# To be honest I made the Task bigger than it was.
# My original Idea was to have a Game where you have to cook 3 Meals in a certain time with many ingredients.
# You'd have to put in the right commands at the right time so that you wouldn't fail your dish.
# There would also be Rounds or a timer running so you have time pressure.
# I also wanted to implement a cutting minigame where you would cut the ingredients but also cut your hand and would lose time bandaging it.
# But I think this Idea was far beyond my capabilities, even with Claude as a explaining tool.
# I know that using the same command for cooking the omelette is very repetetive but I couldn't approve it more. :(
# It was also very difficult to structure my idea and to realize what would be possible.
# I would really like to finish this project but it is beyond my capabilities and I think also beyond time ressourcces.
# I hope you'll still enjoy it. :)