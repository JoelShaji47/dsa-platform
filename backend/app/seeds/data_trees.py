from app.seeds.data_arrays import starters

PY_TREE_LIB = """import sys
from collections import deque


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build_tree(tokens):
    if not tokens or tokens[0] == "null":
        return None
    root = TreeNode(int(tokens[0]))
    q = deque([root])
    i = 1
    while q and i < len(tokens):
        node = q.popleft()
        if i < len(tokens):
            v = tokens[i]
            i += 1
            if v != "null":
                node.left = TreeNode(int(v))
                q.append(node.left)
        if i < len(tokens):
            v = tokens[i]
            i += 1
            if v != "null":
                node.right = TreeNode(int(v))
                q.append(node.right)
    return root


def read_tokens():
    return sys.stdin.read().split()

"""

CPP_TREE_LIB = """#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v) : val(v), left(nullptr), right(nullptr) {}
};

TreeNode* buildTree(vector<string>& tokens) {
    if (tokens.empty() || tokens[0] == "null") return nullptr;
    TreeNode* root = new TreeNode(stoi(tokens[0]));
    queue<TreeNode*> q;
    q.push(root);
    size_t i = 1;
    while (!q.empty() && i < tokens.size()) {
        TreeNode* node = q.front(); q.pop();
        if (i < tokens.size()) {
            string v = tokens[i++];
            if (v != "null") { node->left = new TreeNode(stoi(v)); q.push(node->left); }
        }
        if (i < tokens.size()) {
            string v = tokens[i++];
            if (v != "null") { node->right = new TreeNode(stoi(v)); q.push(node->right); }
        }
    }
    return root;
}

"""

JAVA_TREE_LIB = """import java.util.*;

public class Main {
    static class TreeNode {
        int val;
        TreeNode left, right;
        TreeNode(int v) { val = v; }
    }

    static TreeNode buildTree(String[] tokens) {
        if (tokens.length == 0 || tokens[0].equals("null")) return null;
        TreeNode root = new TreeNode(Integer.parseInt(tokens[0]));
        Queue<TreeNode> q = new LinkedList<>();
        q.add(root);
        int i = 1;
        while (!q.isEmpty() && i < tokens.length) {
            TreeNode node = q.poll();
            if (i < tokens.length) {
                String v = tokens[i++];
                if (!v.equals("null")) { node.left = new TreeNode(Integer.parseInt(v)); q.add(node.left); }
            }
            if (i < tokens.length) {
                String v = tokens[i++];
                if (!v.equals("null")) { node.right = new TreeNode(Integer.parseInt(v)); q.add(node.right); }
            }
        }
        return root;
    }

"""

TREES = [
    {
        "title": "Maximum Depth of Binary Tree",
        "slug": "maximum-depth-binary-tree",
        "difficulty": "EASY",
        "topic": "TREE",
        "description": """# Maximum Depth of Binary Tree

## Statement
Given the `root` of a binary tree, return its maximum depth — the number of nodes along the longest path from the root down to the farthest leaf.

The tree is given in **level-order** where `null` marks missing children (trailing nulls are omitted).

## Input Format
- Line 1: space-separated level-order tokens, e.g. `3 9 20 null null 15 7`

## Output Format
A single integer — the maximum depth.

## Constraints
- `1 <= number of nodes <= 10^4`
- `-100 <= Node.val <= 100`

## Example

**Input**
```
3 9 20 null null 15 7
```
**Output**
```
3
```
""",
        "starter_code": starters(
            py=PY_TREE_LIB
            + """

def max_depth(root):
    # your logic here
    pass


def main():
    print(max_depth(build_tree(read_tokens())))


if __name__ == "__main__":
    main()
""",
            cpp=CPP_TREE_LIB
            + """
int maxDepth(TreeNode* root) {
    return 0;
}

int main() {
    vector<string> tokens;
    string t;
    while (cin >> t) tokens.push_back(t);
    cout << maxDepth(buildTree(tokens)) << endl;
    return 0;
}
""",
            java=JAVA_TREE_LIB
            + """
    static int maxDepth(TreeNode root) {
        return 0;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        List<String> list = new ArrayList<>();
        while (sc.hasNext()) list.add(sc.next());
        System.out.println(maxDepth(buildTree(list.toArray(new String[0]))));
    }
}
""",
        ),
        "test_cases": [
            {"input": "3 9 20 null null 15 7\n", "expected_output": "3", "is_hidden": False},
            {"input": "1 null 2\n", "expected_output": "2", "is_hidden": False},
            {"input": "5\n", "expected_output": "1", "is_hidden": True},
            {"input": "1 2 3 4 5 null null 6\n", "expected_output": "4", "is_hidden": True},
            {"input": "1 2 null 3 null 4\n", "expected_output": "4", "is_hidden": True},
        ],
    },
    {
        "title": "Invert Binary Tree",
        "slug": "invert-binary-tree",
        "difficulty": "EASY",
        "topic": "TREE",
        "description": """# Invert Binary Tree

## Statement
Given the `root` of a binary tree, invert it by swapping every node's left and right subtrees, then print the resulting tree in **level-order** using the same convention as the input: `null` for missing children, trailing nulls trimmed.

## Input Format
- Line 1: space-separated level-order tokens of the original tree

## Output Format
Space-separated level-order tokens of the inverted tree.

## Constraints
- `1 <= number of nodes <= 10^4`

## Example

**Input**
```
4 2 7 1 3 6 9
```
**Output**
```
4 7 2 9 6 3 1
```
""",
        "starter_code": starters(
            py=PY_TREE_LIB
            + """

def invert_tree(root):
    # your logic here
    pass


def serialize(root):
    out = []
    q = deque([root])
    while q:
        node = q.popleft()
        if node is None:
            out.append("null")
        else:
            out.append(str(node.val))
            q.append(node.left)
            q.append(node.right)
    while out and out[-1] == "null":
        out.pop()
    return " ".join(out)


def main():
    print(serialize(invert_tree(build_tree(read_tokens()))))


if __name__ == "__main__":
    main()
""",
            cpp=CPP_TREE_LIB
            + """
TreeNode* invertTree(TreeNode* root) {
    return root;
}

int main() {
    vector<string> tokens;
    string t;
    while (cin >> t) tokens.push_back(t);
    TreeNode* inv = invertTree(buildTree(tokens));
    vector<string> out;
    queue<TreeNode*> q; q.push(inv);
    while (!q.empty()) {
        TreeNode* node = q.front(); q.pop();
        if (!node) { out.push_back("null"); continue; }
        out.push_back(to_string(node->val));
        q.push(node->left); q.push(node->right);
    }
    while (!out.empty() && out.back() == "null") out.pop_back();
    for (int i = 0; i < (int)out.size(); i++)
        cout << out[i] << " \\n"[i + 1 == (int)out.size()];
    return 0;
}
""",
            java=JAVA_TREE_LIB
            + """
    static TreeNode invertTree(TreeNode root) {
        return root;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        List<String> list = new ArrayList<>();
        while (sc.hasNext()) list.add(sc.next());
        TreeNode inv = invertTree(buildTree(list.toArray(new String[0])));
        List<String> out = new ArrayList<>();
        Queue<TreeNode> q = new LinkedList<>();
        q.add(inv);
        while (!q.isEmpty()) {
            TreeNode node = q.poll();
            if (node == null) { out.add("null"); continue; }
            out.add(String.valueOf(node.val));
            q.add(node.left); q.add(node.right);
        }
        while (out.get(out.size() - 1).equals("null")) out.remove(out.size() - 1);
        System.out.println(String.join(" ", out));
    }
}
""",
        ),
        "test_cases": [
            {"input": "4 2 7 1 3 6 9\n", "expected_output": "4 7 2 9 6 3 1", "is_hidden": False},
            {"input": "2 1 3\n", "expected_output": "2 3 1", "is_hidden": False},
            {"input": "1\n", "expected_output": "1", "is_hidden": True},
            {"input": "1 2\n", "expected_output": "1 null 2", "is_hidden": True},
            {"input": "1 2 3 4\n", "expected_output": "1 3 2 null null null 4", "is_hidden": True},
        ],
    },
    {
        "title": "Lowest Common Ancestor of a BST",
        "slug": "lowest-common-ancestor-bst",
        "difficulty": "EASY",
        "topic": "TREE",
        "description": """# Lowest Common Ancestor of a BST

## Statement
Given a **binary search tree** and two of its node values `p` and `q`, find the lowest common ancestor (LCA): the deepest node that has both `p` and `q` in its subtree (a node counts as an ancestor of itself).

Exploit the BST ordering property for an elegant walk from the root.

## Input Format
- Line 1: space-separated level-order tokens of the BST
- Line 2: integer `p`
- Line 3: integer `q`

## Output Format
A single integer — the value of the LCA node.

## Constraints
- `2 <= number of nodes <= 10^5`
- All node values are unique; both `p` and `q` exist in the tree.
- `-10^9 <= Node.val <= 10^9`

## Example

**Input**
```
6 2 8 0 4 7 9 null null 3 5
2
8
```
**Output**
```
6
```
""",
        "starter_code": starters(
            py=PY_TREE_LIB
            + """

def lowest_common_ancestor(root, p, q):
    # your logic here
    pass


def main():
    data = read_tokens()
    p, q = int(data[-2]), int(data[-1])
    root = build_tree(data[:-2])
    print(lowest_common_ancestor(root, p, q).val)


if __name__ == "__main__":
    main()
""",
            cpp=CPP_TREE_LIB
            + """
TreeNode* lowestCommonAncestor(TreeNode* root, int p, int q) {
    return root;
}

int main() {
    vector<string> tokens;
    string t;
    while (cin >> t) tokens.push_back(t);
    int p = stoi(tokens[tokens.size() - 2]);
    int q = stoi(tokens[tokens.size() - 1]);
    tokens.resize(tokens.size() - 2);
    cout << lowestCommonAncestor(buildTree(tokens), p, q)->val << endl;
    return 0;
}
""",
            java=JAVA_TREE_LIB
    + """
    static TreeNode lowestCommonAncestor(TreeNode root, int p, int q) {
        return root;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        List<String> list = new ArrayList<>();
        while (sc.hasNext()) list.add(sc.next());
        int p = Integer.parseInt(list.get(list.size() - 2));
        int q = Integer.parseInt(list.get(list.size() - 1));
        TreeNode root = buildTree(list.subList(0, list.size() - 2).toArray(new String[0]));
        System.out.println(lowestCommonAncestor(root, p, q).val);
    }
}
""",
        ),
        "test_cases": [
            {"input": "6 2 8 0 4 7 9 null null 3 5\n2\n8\n", "expected_output": "6", "is_hidden": False},
            {"input": "6 2 8 0 4 7 9 null null 3 5\n2\n4\n", "expected_output": "2", "is_hidden": False},
            {"input": "2 1 3\n2\n3\n", "expected_output": "2", "is_hidden": True},
            {"input": "5 3 8 1 4 7 9\n7\n9\n", "expected_output": "8", "is_hidden": True},
            {"input": "50 30 70 20 40 60 80\n20\n40\n", "expected_output": "30", "is_hidden": True},
        ],
    },
    {
        "title": "Validate Binary Search Tree",
        "slug": "validate-binary-search-tree",
        "difficulty": "MEDIUM",
        "topic": "TREE",
        "description": """# Validate Binary Search Tree

## Statement
Given the `root` of a binary tree, determine whether it is a valid BST. A valid BST requires every node's left subtree to contain only values **strictly less** than the node, and the right subtree only values **strictly greater** — this must hold for all nodes, not just direct children.

## Input Format
- Line 1: space-separated level-order tokens (`null` for missing children)

## Output Format
`true` or `false` (lowercase).

## Constraints
- `1 <= number of nodes <= 10^4`
- `-2^31 <= Node.val <= 2^31 - 1` (watch out for overflow when using min/max sentinels)

## Example

**Input**
```
5 1 4 null null 3 6
```
**Output**
```
false
```

Explanation: node 4's right child 6 violates the bound imposed by the root (5).
""",
        "starter_code": starters(
            py=PY_TREE_LIB
            + """

def is_valid_bst(root):
    # your logic here
    pass


def main():
    print(str(is_valid_bst(build_tree(read_tokens()))).lower())


if __name__ == "__main__":
    main()
""",
            cpp=CPP_TREE_LIB
            + """
bool isValidBST(TreeNode* root) {
    return false;
}

int main() {
    vector<string> tokens;
    string t;
    while (cin >> t) tokens.push_back(t);
    cout << (isValidBST(buildTree(tokens)) ? "true" : "false") << endl;
    return 0;
}
""",
            java=JAVA_TREE_LIB
            + """
    static boolean isValidBST(TreeNode root) {
        return false;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        List<String> list = new ArrayList<>();
        while (sc.hasNext()) list.add(sc.next());
        System.out.println(isValidBST(buildTree(list.toArray(new String[0]))) ? "true" : "false");
    }
}
""",
        ),
        "test_cases": [
            {"input": "5 1 4 null null 3 6\n", "expected_output": "false", "is_hidden": False},
            {"input": "2 1 3\n", "expected_output": "true", "is_hidden": False},
            {"input": "2 2 2\n", "expected_output": "false", "is_hidden": True},
            {"input": "10 5 15 2 7 12 20\n", "expected_output": "true", "is_hidden": True},
            {"input": "2147483647\n", "expected_output": "true", "is_hidden": True},
            {"input": "10 5 15 null null 6 20\n", "expected_output": "false", "is_hidden": True},
        ],
    },
    {
        "title": "Binary Tree Level Order Traversal",
        "slug": "binary-tree-level-order-traversal",
        "difficulty": "MEDIUM",
        "topic": "TREE",
        "description": """# Binary Tree Level Order Traversal

## Statement
Given the `root` of a binary tree, print its values level by level: one line per level, values separated by single spaces, from left to right within each level.

## Input Format
- Line 1: space-separated level-order tokens (`null` for missing children)

## Output Format
One line per level.

## Constraints
- `1 <= number of nodes <= 10^4`

## Example

**Input**
```
3 9 20 null null 15 7
```
**Output**
```
3
9 20
15 7
```
""",
        "starter_code": starters(
            py=PY_TREE_LIB
            + """

def level_order(root):
    # return a list of lists, one per level
    pass


def main():
    for level in level_order(build_tree(read_tokens())):
        print(*level)


if __name__ == "__main__":
    main()
""",
            cpp=CPP_TREE_LIB
            + """
vector<vector<int>> levelOrder(TreeNode* root) {
    return {};
}

int main() {
    vector<string> tokens;
    string t;
    while (cin >> t) tokens.push_back(t);
    auto levels = levelOrder(buildTree(tokens));
    for (int i = 0; i < (int)levels.size(); i++) {
        for (int j = 0; j < (int)levels[i].size(); j++)
            cout << levels[i][j] << " \\n"[j + 1 == (int)levels[i].size()];
    }
    return 0;
}
""",
            java=JAVA_TREE_LIB
            + """
    static List<List<Integer>> levelOrder(TreeNode root) {
        return new ArrayList<>();
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        List<String> list = new ArrayList<>();
        while (sc.hasNext()) list.add(sc.next());
        for (List<Integer> level : levelOrder(buildTree(list.toArray(new String[0])))) {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < level.size(); i++)
                sb.append(level.get(i)).append(i < level.size() - 1 ? " " : "");
            System.out.println(sb);
        }
    }
}
""",
        ),
        "test_cases": [
            {"input": "3 9 20 null null 15 7\n", "expected_output": "3\n9 20\n15 7", "is_hidden": False},
            {"input": "1\n", "expected_output": "1", "is_hidden": False},
            {"input": "1 2 3 4 5 6 7\n", "expected_output": "1\n2 3\n4 5 6 7", "is_hidden": True},
            {"input": "1 null 2 null 3\n", "expected_output": "1\n2\n3", "is_hidden": True},
        ],
    },
    {
        "title": "Diameter of Binary Tree",
        "slug": "diameter-of-binary-tree",
        "difficulty": "MEDIUM",
        "topic": "TREE",
        "description": """# Diameter of Binary Tree

## Statement
Given the `root` of a binary tree, return the length of its diameter — the number of **edges** on the longest path between any two nodes. The path may or may not pass through the root.

## Input Format
- Line 1: space-separated level-order tokens (`null` for missing children)

## Output Format
A single integer — the diameter in edges.

## Constraints
- `1 <= number of nodes <= 10^4`
- `-100 <= Node.val <= 100`

## Example

**Input**
```
1 2 3 4 5
```
**Output**
```
3
```

Explanation: path `4 -> 2 -> 1 -> 3` contains 3 edges.
""",
        "starter_code": starters(
            py=PY_TREE_LIB
            + """

def diameter_of_binary_tree(root):
    # your logic here
    pass


def main():
    print(diameter_of_binary_tree(build_tree(read_tokens())))


if __name__ == "__main__":
    main()
""",
            cpp=CPP_TREE_LIB
            + """
int diameterOfBinaryTree(TreeNode* root) {
    return 0;
}

int main() {
    vector<string> tokens;
    string t;
    while (cin >> t) tokens.push_back(t);
    cout << diameterOfBinaryTree(buildTree(tokens)) << endl;
    return 0;
}
""",
            java=JAVA_TREE_LIB
            + """
    static int diameterOfBinaryTree(TreeNode root) {
        return 0;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        List<String> list = new ArrayList<>();
        while (sc.hasNext()) list.add(sc.next());
        System.out.println(diameterOfBinaryTree(buildTree(list.toArray(new String[0]))));
    }
}
""",
        ),
        "test_cases": [
            {"input": "1 2 3 4 5\n", "expected_output": "3", "is_hidden": False},
            {"input": "1 2\n", "expected_output": "1", "is_hidden": False},
            {"input": "1\n", "expected_output": "0", "is_hidden": True},
            {"input": "1 2 null 3 null 4 null 5\n", "expected_output": "4", "is_hidden": True},
            {"input": "1 2 3 4 5 null null 6 7\n", "expected_output": "4", "is_hidden": True},
        ],
    },
]
