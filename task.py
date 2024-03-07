from random import randint

class Node:
    def __init__(self, peer_id, succ=None, pred=None):
        self.peer_id = peer_id
        self.pred = pred
        self.data = {}
        self.finger_table = [succ]

    def fix_node_fingers(self, ring, r):
        del self.finger_table[1:]

        for i in range(1, r):
            self.finger_table.append(ring.key_lookup(ring._starting_node, self.peer_id + 2 ** i))

class Ring:
    def __init__(self, max_r):
        self.r = max_r
        self._starting_node = Node(0, max_r)
        self._ring_size = 2 ** max_r
        self._starting_node.pred = self._starting_node
        self._starting_node.finger_table[0] = self._starting_node
        self._starting_node.fix_node_fingers(self, max_r)

    def get_id(self, key):
        return key % self._ring_size

    def get_pred(self):
        return self._starting_node.pred

    def join(self, j_node):
        curr_pred_node = self.key_lookup(self._starting_node, j_node.peer_id)
        if curr_pred_node.peer_id == j_node.peer_id:
            print("Existing node found")
            return

        for key in curr_pred_node.data:
            curr_id = self.get_id(key)
            if self.nodes_dist(curr_id, j_node.peer_id) < self.nodes_dist(curr_id, curr_pred_node.peer_id):
                j_node.data[key] = curr_pred_node.data[key]
        node_prev = curr_pred_node.pred
        j_node.finger_table[0] = curr_pred_node
        j_node.pred = node_prev
        curr_pred_node.pred = j_node
        node_prev.finger_table[0] = j_node

        j_node.fix_node_fingers(self, self.r)
        for key in list(curr_pred_node.data.keys()):
            curr_id = self.get_id(key)
            if self.nodes_dist(curr_id, j_node.peer_id) < self.nodes_dist(curr_id, curr_pred_node.peer_id):
                del curr_pred_node.data[key]

    def leave(self, node):
        for k, v in node.data.items():
            node.finger_table[0].data[k] = v

        if node.finger_table[0] == node:
            self._starting_node = None
        else:
            node.pred.finger_table[0] = node.finger_table[0]
            node.finger_table[0] = prev = node.pred
            if self._starting_node == node:
                self._starting_node = node.finger_table[0]

    def stabilize(self):
        self._starting_node.fix_node_fingers(self, self.r)
        curr = self._starting_node.finger_table[0]
        while curr != self._starting_node:
            curr.fix_node_fingers(self, self.r)
            curr = curr.finger_table[0]

    def get_curr_nodes_num(self):
        if self._starting_node is None:
            return 0
        curr_node = self._starting_node
        count = 1
        while curr_node.finger_table[0] != self._starting_node:
            count = count + 1
            curr_node = curr_node.finger_table[0]
        return count

    def nodes_dist(self, node_a, node_b):
        if node_a == node_b:
            return 0
        if node_a < node_b:
            return node_b - node_a
        return self._ring_size - node_a + node_b

    def key_lookup(self, starting, key):
        curr_id = self.get_id(key)
        curr_node = starting
        while True:
            if curr_node.peer_id == curr_id:
                return curr_node
            if self.nodes_dist(curr_node.peer_id, curr_id) <= self.nodes_dist(curr_node.finger_table[0].peer_id, curr_id):
                return curr_node.finger_table[0]
            i = 0
            finger_table_size = len(curr_node.finger_table)
            next_finger_node = curr_node.finger_table[-1]
            while i < finger_table_size - 1:
                if self.nodes_dist(curr_node.finger_table[i].peer_id, curr_id) < self.nodes_dist(curr_node.finger_table[i + 1].peer_id, curr_id):
                    next_finger_node = curr_node.finger_table[i]
                i += 1
            curr_node = next_finger_node

size = 5
r1 = Ring(size)
print("Initial number of nodes:", r1.get_curr_nodes_num() - 1)

node_ids = []
for i in range(10):
    node_id = randint(0, 2 ** size - 1)
    while node_id in node_ids:
        node_id = randint(0, 2 ** size - 1)
    node_ids.append(node_id)
    node = Node(node_id)
    r1.join(node)
    print("Node", node.peer_id, "joined the ring.")
    print("Number of nodes in the ring:", r1.get_curr_nodes_num() - 1)

for i in range(5):
    key = randint(0, 2 ** size - 1)
    node = r1.key_lookup(r1._starting_node, key)
    print("Key", key, "belongs to node", node.peer_id)

node_to_remove = r1._starting_node.finger_table[0]
r1.leave(node_to_remove)
print("Node", node_to_remove.peer_id, "left the ring.")
print("Number of nodes in the ring:", r1.get_curr_nodes_num() - 1)
