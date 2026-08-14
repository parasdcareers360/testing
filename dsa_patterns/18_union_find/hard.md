# Hard — Accounts Merge

**Source**: LeetCode #721
**Pattern**: Union Find (Disjoint Set Union)
**Difficulty**: Hard

## Problem Statement
Given a list `accounts`, each element `accounts[i]` is a list of strings, where the first element `accounts[i][0]` is a name, and the rest of the elements are **emails** representing emails of the account.

Two accounts belong to the same person if there is some common email to both accounts. Note that even if two accounts have the same name, they may belong to different people, since people could have the same name. A person can have any number of accounts initially, but all of their accounts definitely have the same name.

After merging the accounts, return the accounts in the following format: the first element of each account is the name, and the rest of the elements are the emails **sorted lexicographically** (as strings). Two accounts belong to the same person only if their emails overlap transitively — e.g., if account A shares an email with account B, and account B shares a different email with account C, then A, B, and C should all be merged into one account, even though A and C may share no email directly.

You may return the accounts (and the emails within each account) in **any order**.

This goes beyond simple pairwise connectivity (as in Redundant Connection): the "nodes" being unioned are emails, not integer-labeled cities, and after computing connectivity we must also perform a non-trivial output-construction step — grouping emails by root, picking a name for each group, and sorting.

## Constraints
- `1 <= accounts.length <= 1000`
- `2 <= accounts[i].length <= 10`
- `1 <= accounts[i][j].length <= 30`
- `accounts[i][0]` consists of English letters.
- `accounts[i][j]` (for `j > 0`) is a valid email address.
- The total number of emails across all accounts does not exceed 10^4 (i.e., the input size is bounded, but can still be large enough that an O(n^2) pairwise merge is noticeably slow).

## Examples
**Example 1**
```
Input: accounts = [
  ["John", "johnsmith@mail.com", "john_newyork@mail.com"],
  ["John", "johnsmith@mail.com", "john00@mail.com"],
  ["Mary", "mary@mail.com"],
  ["John", "johnnybravo@mail.com"]
]
Output: [
  ["John", "john00@mail.com", "john_newyork@mail.com", "johnsmith@mail.com"],
  ["Mary", "mary@mail.com"],
  ["John", "johnnybravo@mail.com"]
]
```
Explanation: The first and second "John" accounts share the email "johnsmith@mail.com", so they merge into one account with all three of their emails combined and sorted. The third "John" (johnnybravo@mail.com) shares no email with anyone, so it stays separate — even though the name matches, it's a different physical person.

**Example 2**
```
Input: accounts = [
  ["Alice", "a1@mail.com"],
  ["Alice", "a1@mail.com", "a2@mail.com"],
  ["Alice", "a2@mail.com", "a3@mail.com"]
]
Output: [["Alice", "a1@mail.com", "a2@mail.com", "a3@mail.com"]]
```
Explanation: Account 1 shares "a1@mail.com" with account 2. Account 2 shares "a2@mail.com" with account 3. Even though account 1 and account 3 share no email directly, they are transitively connected through account 2, so all three merge into a single account.

## Intuition — Why This Pattern
**Brute force**: Treat each account as a set of emails. Repeatedly scan all pairs of account-groups; if any two groups share an email, merge them into one group (union of their email sets) and restart the scan (since merging could create new overlaps). This is at least O(k^2 * m) where k is the number of accounts and m is emails per account, and the "restart the scan after each merge" logic is error-prone and can degrade badly — you might need many passes before reaching a fixed point (imagine a long chain A-B-C-D-...-Z where merges only cascade one link per pass).

**What's inefficient**: We're redoing full-collection scans to catch transitive merges that a proper connectivity structure would handle automatically and incrementally.

**The insight**: Model every **distinct email** as a node in a Union-Find structure (not the accounts themselves — accounts are just the mechanism that tells us which emails to union together). For each account, union all of its emails together (e.g., union each email with the account's first email) — this directly encodes "these emails belong to the same account, hence the same person." Because Union-Find's `find` operation naturally resolves transitive chains (if a-b are unioned and b-c are unioned, `find(a) == find(c)` automatically), we get the full transitive merging for free, in near-linear time, without any manual "restart and rescan" logic. After processing all accounts, group emails by their root parent, attach the correct name (any account containing that root's group has the right name, since all accounts in a merged group share the same name per the problem's guarantee), sort each group's emails, and output.

## Approach
1. Initialize a Union-Find (DSU) over emails using a dictionary-based parent map (since emails are strings, not small integers): `parent[email] = email` for every email seen so far (add lazily as encountered).
2. Also maintain `email_to_name[email] = name` for every email, recording which name it belongs to (any account containing this email will have the same name as all others in its eventual merged group).
3. For each account `[name, email_0, email_1, ..., email_k]`:
   a. Record `email_to_name[email_j] = name` for each email in this account.
   b. Union `email_0` with every other email in this same account (`email_1`, `email_2`, ...), so all emails in this one account end up in the same DSU component.
4. After processing all accounts, group all seen emails by their DSU root (`find(email)`), using a dictionary mapping `root -> list of emails`.
5. For each root/group, sort the list of emails lexicographically, look up the name via `email_to_name[any email in the group]` (they're all the same name), and build the output entry `[name] + sorted_emails`.
6. Return the list of all such output entries (order among entries doesn't matter).

## Dry Run
Example 1: `accounts = [["John","johnsmith@mail.com","john_newyork@mail.com"], ["John","johnsmith@mail.com","john00@mail.com"], ["Mary","mary@mail.com"], ["John","johnnybravo@mail.com"]]`.

- Account 0 ("John"): emails = [johnsmith, john_newyork] (using shorthand, dropping "@mail.com" for brevity).
  - `email_to_name[johnsmith] = John`, `email_to_name[john_newyork] = John`.
  - Union(johnsmith, john_newyork). Both are new → parent[johnsmith]=johnsmith, parent[john_newyork]=johnsmith (say union attaches second under first's root). Root of both is now `johnsmith`.
- Account 1 ("John"): emails = [johnsmith, john00].
  - `email_to_name[johnsmith] = John` (again), `email_to_name[john00] = John`.
  - Union(johnsmith, john00). `find(johnsmith) = johnsmith`. `john00` is new → `parent[john00] = johnsmith`. Root of john00 becomes `johnsmith`.
  - Now {johnsmith, john_newyork, john00} all share root `johnsmith`.
- Account 2 ("Mary"): emails = [mary].
  - `email_to_name[mary] = Mary`. Union has nothing else to merge with (only one email) — mary is its own root.
- Account 3 ("John"): emails = [johnnybravo].
  - `email_to_name[johnnybravo] = John`. johnnybravo is its own root (no other email in this account to union with).
- Grouping by root:
  - Root `johnsmith` → group {johnsmith, john_newyork, john00} → name "John" → sorted: [john00, john_newyork, johnsmith] (lexicographic: "john00@mail.com" < "john_newyork@mail.com" < "johnsmith@mail.com" — comparing character by character, '0' < '_' < 's' at the differing position after "john").
  - Root `mary` → group {mary} → name "Mary" → sorted: [mary].
  - Root `johnnybravo` → group {johnnybravo} → name "John" → sorted: [johnnybravo].
- Output: `[["John","john00@mail.com","john_newyork@mail.com","johnsmith@mail.com"], ["Mary","mary@mail.com"], ["John","johnnybravo@mail.com"]]` (order of the three groups may vary). Matches expected output.

## Solution (Python 3)
```python
from typing import List, Dict
from collections import defaultdict


class UnionFind:
    def __init__(self):
        self.parent: Dict[str, str] = {}

    def add(self, x: str) -> None:
        if x not in self.parent:
            self.parent[x] = x

    def find(self, x: str) -> str:
        self.add(x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x: str, y: str) -> None:
        rx, ry = self.find(x), self.find(y)
        if rx != ry:
            self.parent[rx] = ry


def accounts_merge(accounts: List[List[str]]) -> List[List[str]]:
    uf = UnionFind()
    email_to_name: Dict[str, str] = {}

    for account in accounts:
        name = account[0]
        emails = account[1:]
        first_email = emails[0]
        for email in emails:
            email_to_name[email] = name
            uf.union(first_email, email)

    groups: Dict[str, List[str]] = defaultdict(list)
    for email in email_to_name:
        root = uf.find(email)
        groups[root].append(email)

    result = []
    for root, emails in groups.items():
        name = email_to_name[root]
        result.append([name] + sorted(emails))

    return result


if __name__ == "__main__":
    accounts1 = [
        ["John", "johnsmith@mail.com", "john_newyork@mail.com"],
        ["John", "johnsmith@mail.com", "john00@mail.com"],
        ["Mary", "mary@mail.com"],
        ["John", "johnnybravo@mail.com"],
    ]
    for entry in accounts_merge(accounts1):
        print(entry)
    # Expected (order may vary):
    # ['John', 'john00@mail.com', 'john_newyork@mail.com', 'johnsmith@mail.com']
    # ['Mary', 'mary@mail.com']
    # ['John', 'johnnybravo@mail.com']

    accounts2 = [
        ["Alice", "a1@mail.com"],
        ["Alice", "a1@mail.com", "a2@mail.com"],
        ["Alice", "a2@mail.com", "a3@mail.com"],
    ]
    print(accounts_merge(accounts2))
    # Expected: [['Alice', 'a1@mail.com', 'a2@mail.com', 'a3@mail.com']]
```

## Complexity Analysis
- Time: O(N log N) where N is the total number of emails across all accounts — unioning all emails takes O(N * alpha(N)) ~ O(N) amortized, but sorting the emails within each group costs O(N log N) in total (each email is sorted once as part of whichever group it ends up in).
- Space: O(N) for the `parent` dictionary, `email_to_name` dictionary, and group lists.

## Key Takeaways
- When the entities to be unioned are not small contiguous integers (here, emails are strings), use a dictionary-based Union-Find (`parent` as a dict) instead of an array — the logic is identical, just keyed differently.
- The key modeling trick: union on the *emails*, not the *account indices* — this correctly captures transitive merges across accounts that only indirectly overlap (Example 2's chain a1-a2-a3), which a naive "merge accounts pairwise" approach handles clumsily or incorrectly without repeated passes.
- Common mistake: forgetting to also track name via a separate map — since Union-Find only tracks connectivity, you need a side dictionary to recover the name associated with each merged group at output time.
- Related/variant problems to try next: Redundant Connection, Most Stones Removed with Same Row or Column (union on shared coordinates), Number of Islands II (dynamic online connectivity on a grid).
