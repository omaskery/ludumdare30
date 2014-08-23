__author__ = 'Oliver Maskery'


import random


first_names = ['Aleta', 'Amy', 'April', 'Aurelio', 'Bethany',
               'Britany', 'Carlo', 'Celina', 'Christal', 'Colene',
               'Dale', 'Deane', 'Detra', 'Dorsey', 'Eleanore',
               'Emilia', 'Evelina', 'Francie', 'Georgiana',
               'Gudrun', 'Hilma', 'Isaac', 'Janean', 'Jenna',
               'Johanne', 'Juliet', 'Kathe', 'Keva', 'Lacy',
               'Laurene', 'Leonie', 'Lizette', 'Lucinda',
               'Makeda', 'Maribel', 'Maryln', 'Merle', 'Misty',
               'Natividad', 'Normand', 'Pat', 'Racheal', 'Retha',
               'Rosa', 'Sadye', 'Shalonda', 'Shelton', 'Song',
               'Synthia', 'Teresa', 'Tommie', 'Ute', 'Violet', 'Winona']

second_names = ['Smith', 'Jones', 'Taylor', 'Williams', 'Brown', 'Davies',
                'Evans', 'Wilson', 'Thomas', 'Roberts', 'Johnson',
                'Lewis', 'Walker', 'Robinson', 'Wood', 'Thompson',
                'White', 'Watson', 'Jackson', 'Wright', 'Green',
                'Harris', 'Cooper', 'King', 'Lee', 'Martin', 'Clarke',
                'James', 'Morgan', 'Hughes', 'Edwards', 'Hill', 'Moore',
                'Clark', 'Harrison', 'Scott', 'Young', 'Morris', 'Hall',
                'Ward', 'Turner', 'Carter', 'Phillips', 'Mitchell', 'Patel',
                'Adams', 'Campbell', 'Anderson', 'Allen', 'Cook', 'Bailey',
                'Parker', 'Miller', 'Davis', 'Murphy', 'Price', 'Bell',
                'Baker', 'Griffiths', 'Kelly', 'Simpson', 'Marshall',
                'Collins', 'Bennett', 'Cox', 'Richardson', 'Fox', 'Gray',
                'Rose', 'Chapman', 'Hunt', 'Robertson', 'Shaw', 'Reynolds',
                'Lloyd', 'Ellis', 'Richards', 'Russell', 'Wilkinson', 'Khan',
                'Graham', 'Stewart', 'Reid', 'Murray', 'Powell', 'Palmer',
                'Holmes', 'Rogers', 'Stevens', 'Walsh', 'Hunter', 'Thomson',
                'Matthews', 'Ross', 'Owen', 'Mason', 'Knight', 'Kennedy',
                'Butler', 'Saunders', 'Cole', 'Pearce', 'Dean', 'Foster',
                'Harvey', 'Hudson', 'Gibson', 'Mills', 'Berry', 'Barnes',
                'Pearson', 'Kaur', 'Booth', 'Dixon', 'Grant', 'Gordon',
                'Lane', 'Harper', 'Ali', 'Hart', 'Mcdonald', 'Brooks',
                'Ryan', 'Carr', 'Macdonald', 'Hamilton', 'Johnston', 'West',
                'Gill', 'Dawson', 'Armstrong', 'Gardner', 'Stone', 'Andrews',
                'Williamson', 'Barker', 'George', 'Fisher', 'Cunningham',
                'Watts', 'Webb', 'Lawrence', 'Bradley', 'Jenkins', 'Wells',
                'Chambers', 'Spencer', 'Poole', 'Atkinson', 'Lawson']


class World(object):

    def __init__(self, debug_client):
        self.dc = debug_client
        self.nodes = []
        self.links = []
        self.unlinked = []
        self.seed = random.randint(-100000, 100000)

        world_page = debug_client.get_page('world')
        general = world_page.get_section('General')
        self.base_node_count = general.get_value('Base Node Count', 'int', 0)

    def generate(self, node_count):
        for x in range(node_count):
            new_node = self.generate_node()
            self.nodes.append(new_node)
        self.base_node_count.set(len(self.nodes))

        totems_to_link = []
        for node in self.nodes:
            # one totem from each node is unlinked
            self.unlinked.append(node.totems[0])

            totems_to_link.append(node.totems[1:])

        while len(totems_to_link) > 1:
            group_a = random.choice(totems_to_link)
            totems_to_link.remove(group_a)
            group_b = random.choice(totems_to_link)
            totems_to_link.remove(group_b)

            a = random.choice(group_a)
            group_a.remove(a)
            b = random.choice(group_b)
            group_b.remove(b)

            if len(group_a) > 0:
                totems_to_link.append(group_a)
            if len(group_b) > 0:
                totems_to_link.append(group_b)

            link = TotemLink(a, b)
            self.links.append(link)

    def generate_node(self):
        new_node = Node()
        new_node.totems = [
            Totem(new_node)
            for x in range(random.randint(2, 4))
        ]
        return new_node


class Node(object):

    def __init__(self, size=(20, 8)):
        self.totems = []
        self.tiles = [Tile() for x in range(size[0] * size[1])]
        self.size = size
        self.tile_size = 32
        self.entities = []

    def tile_at(self, x, y):
        return self.tiles[y * self.size[0] + x]

    def at(self, x, y):
        tile_x = int(x / self.tile_size)
        tile_y = int(y / self.tile_size)
        return self.tile_at(tile_x, tile_y)

    def random_position(self):
        return random.randint(0, self.size[0]-1), random.randint(0, self.size[1]-1)

    def random_edge_position(self):
        result = list(self.random_position())
        if random.random() >= 0.5:
            result[0] = random.choice([0, self.size[0]-1])
        else:
            result[1] = random.choice([0, self.size[1]-1])
        return tuple(result)

    def random_free_position(self, position_source, scale=False):
        # quickly check there IS a free space in existence
        space_exists = False
        for tile in self.tiles:
            if tile.entity is None:
                space_exists = True
                break

        if not space_exists:
            return None

        # isn't guaranteed to actually ever exit sooo... <_< >_>
        while True:
            position = position_source()
            tile = self.tile_at(position[0], position[1])
            if tile.entity is None:
                position = list(position)
                if scale:
                    position[0] *= self.tile_size
                    position[1] *= self.tile_size
                return tuple(position)


class Tile(object):

    def __init__(self):
        self.ground = None
        self.entity = None
        self.item = None


class Entity(object):

    def __init__(self):
        self.pos = [0, 0]

    def blob(self):
        return {
            'pos': self.pos
        }

    def unblob(self, blob):
        self.pos = blob['pos']


class Player(Entity):

    def __init__(self):
        super().__init__()
        self.name = (random.choice(first_names), random.choice(second_names))

    def blob(self):
        result = super().blob()
        result['name'] = self.name
        return result

    def unblob(self, blob):
        super().unblob(blob)
        self.name = tuple(blob['name'])


class Totem(Entity):

    def __init__(self, parent_node):
        super().__init__()

        self.parent_node = parent_node
        position_source = parent_node.random_edge_position
        self.pos = list(parent_node.random_free_position(position_source, True))

        self.destination = None


class TotemLink(object):

    def __init__(self, a, b):
        self.a = a
        self.b = b

        self.a.destination = b
        self.b.destination = a

    def unlink(self):
        self.a.destination = None
        self.b.destination = None
