"""
Tries (Prefix Trees) — reusable Python skeletons.

Not solutions to specific problems — these are the boilerplate shapes to recognize and adapt
quickly under interview time pressure. Copy the relevant shape into solutions/ and adapt it.
"""

from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Shape 1: trie node, dict-of-children (default choice -- any alphabet)
# ---------------------------------------------------------------------------
class TrieNode:
    def __init__(self) -> None:
        self.children: Dict[str, "TrieNode"] = {}
        self.is_word: bool = False


# ---------------------------------------------------------------------------
# Shape 2: core trie -- insert / search / starts_with
# ---------------------------------------------------------------------------
class Trie:
    def __init__(self) -> None:
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_word = True

    def _find_node(self, prefix: str) -> Optional[TrieNode]:
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def search(self, word: str) -> bool:
        node = self._find_node(word)
        return node is not None and node.is_word

    def starts_with(self, prefix: str) -> bool:
        return self._find_node(prefix) is not None


# ---------------------------------------------------------------------------
# Shape 3: autocomplete -- collect all words under a typed prefix
# ---------------------------------------------------------------------------
def autocomplete(trie: Trie, prefix: str) -> List[str]:
    start = trie._find_node(prefix)
    if start is None:
        return []

    results: List[str] = []

    def dfs(node: TrieNode, path: str) -> None:
        if node.is_word:
            results.append(path)
        for ch, child in node.children.items():
            dfs(child, path + ch)

    dfs(start, prefix)
    return results


# ---------------------------------------------------------------------------
# Shape 4: grid word search pruned by a trie (Word Search II family)
# ---------------------------------------------------------------------------
def find_words(board: List[List[str]], words: List[str]) -> List[str]:
    trie = Trie()
    for w in words:
        trie.insert(w)

    rows, cols = len(board), len(board[0])
    found: set = set()

    def dfs(r: int, c: int, node: TrieNode, path: str) -> None:
        ch = board[r][c]
        if ch not in node.children:
            return
        nxt = node.children[ch]
        path += ch
        if nxt.is_word:
            found.add(path)

        board[r][c] = "#"
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != "#":
                dfs(nr, nc, nxt, path)
        board[r][c] = ch

    for r in range(rows):
        for c in range(cols):
            dfs(r, c, trie.root, "")
    return list(found)


if __name__ == "__main__":
    # Shape 1 & 2
    trie = Trie()
    trie.insert("apple")
    assert trie.search("apple") is True
    assert trie.search("app") is False
    assert trie.starts_with("app") is True
    assert trie.starts_with("appz") is False
    trie.insert("app")
    assert trie.search("app") is True

    # Shape 3
    trie2 = Trie()
    for w in ["car", "cart", "care", "cat"]:
        trie2.insert(w)
    assert sorted(autocomplete(trie2, "car")) == ["car", "care", "cart"]
    assert autocomplete(trie2, "dog") == []

    # Shape 4
    board = [
        ["o", "a", "a", "n"],
        ["e", "t", "a", "e"],
        ["i", "h", "k", "r"],
        ["i", "f", "l", "v"],
    ]
    words = ["oath", "pea", "eat", "rain"]
    assert sorted(find_words(board, words)) == ["eat", "oath"]

    print("All template shapes verified.")
