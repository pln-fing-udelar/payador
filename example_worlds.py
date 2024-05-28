"""Includes two example worlds to experiment with different scenarios."""

from world import Character, Item, Location, World


def get_world(arg: str) -> World:
    if arg=='2':
        return get_world_2()
    return get_world_1()

def get_world_1() -> World:
    """A simple fictional world, used as an example in Figure 3 of the paper."""
    item_1 = Item("Apple",
                  ["A fruit that can be eaten", "It is round-shaped and green"])
    item_2 = Item("Toy car",
                  ["A tiny toy purple car", "It looks brand new"])
    item_3 = Item("Mate",
                  ["A classical mate, ready to drink!", "It contains some yerba", "You can drink this to boost your energy!"])

    place_1 = Location("Garden",
                       ["A beautiful garden", "There is a statue in the center"],
                       items = [item_2])
    place_2 = Location("Cabin",
                       ["A small cabin", "It looks like no one has lived here for a while"])
    place_3 = Location("Mansion hall",
                       ["A big hall", "There is a big staircase"])

    place_1.connecting_locations+=[place_2,place_3]
    place_2.connecting_locations+=[place_1]
    place_3.connecting_locations+=[place_1]

    player = Character("Alicia",
                       ["She is wearing a long skirt","She likes to sing"],
                       inventory=[item_1],
                       location=place_1)
    npc = Character("Javier",
                    ["He has a long beard", "He loves to restore furtniture"],
                    inventory=[item_3],
                    location=place_3)

    the_world = World(player)
    the_world.add_locations([place_1, place_2, place_3])
    the_world.add_items([item_1, item_2, item_3])
    the_world.add_character(npc)

    return the_world

def get_world_2() -> World:
    """Use this world to test more complex cases, like blocked passages between locations."""
    item_1 = Item("Apple",
                  ["A fruit that can be eaten", "It is round-shaped and red"])
    item_2 = Item("Key",
                  ["A key to open a lock", "It is golden", "It is engraved with a strange coat of arms"])
    item_3 = Item("A grey Hammer",
                  ["A great grey hammer that can be used to break things", "It is so heavy..."])
    item_4 = Item("Lock",
                  ["A strong lock engraved with a coat of arms", "It seems that you cannot open it with your hands"])
    item_5 = Item("Note",
                  ["A paper with a note", "You can read 'Go to the kitchen to know the truth'"])
    item_6 = Item("Flashlight",
                  ["A flashlight without batteries"])
    item_7 = Item("A green Hammer",
                  ["A small green hammer", "It is just a toy and you cannot break anything with it."])
    item_8 = Item("A wall of flames",
                  ["The heat is really intense but it is a small fire anyway"])
    item_9 = Item("A metal flower",
                  ["A strange flower"])
    item_10 = Item("A fire extinguisher",
                   ["You can control small fires with this."])

    place_3 = Location ("Garden",
                        ["A small garden below the kitchen"],
                        items = [item_9])
    place_2 = Location("Kitchen",
                       ["A beautiful well-lit kitchen"],
                       items = [item_6,item_10])
    place_2.connecting_locations = [place_3]
    place_2.block_passage(place_3, item_8, symmetric=False)

    place_1 = Location("Cellar",
                       ["There is a metal door locked by a lock", "You can see damp patches on the walls"],
                       items = [item_2, item_3, item_5, item_7])
    place_1.connecting_locations = [place_2]
    place_1.block_passage(place_2, item_4)

    player = Character("Cid",
                       ["A tall soldier"],
                       inventory = [item_1],
                       location = place_1)
    npc = Character("Elvira",
                            ["A little girl", "Her favorite food is apple pie, but she enjoys eating any fruit", "She can't read yet"],
                            location= place_1)

    the_world = World(player)
    the_world.add_locations([place_1,place_2,place_3])
    the_world.add_items([item_1,item_2,item_3,item_4,item_5,
                         item_6, item_7,item_8, item_9, item_10])
    the_world.add_character(npc)

    return the_world
