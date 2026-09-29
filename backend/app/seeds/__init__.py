from app.seeds.data_arrays import ARRAY_PROBLEMS
from app.seeds.data_authored import AUTHORED_PROBLEMS
from app.seeds.data_graphs_dp import GRAPHS_DP
from app.seeds.data_linked_stack import LINKED_STACK
from app.seeds.data_neetcode150 import NEETCODE_150
from app.seeds.data_neetcode250 import NEETCODE_250
from app.seeds.data_strings import STRINGS
from app.seeds.data_trees import TREES
from app.seeds.data_tuf_a2z import TUF_A2Z

# Fully-authored problems first, then the NeetCode 150 catalog (which reuses the
# authored slugs for overlapping problems, so content is never lost), then the
# NeetCode 250 delta and the Striver A2Z catalog (both contain only slugs absent
# from everything before them — overlaps merge via source tags in seed.py).
_PROBLEMS_RAW = [
    *AUTHORED_PROBLEMS,
    *ARRAY_PROBLEMS,
    *STRINGS,
    *LINKED_STACK,
    *TREES,
    *GRAPHS_DP,
    *NEETCODE_150,
    *NEETCODE_250,
    *TUF_A2Z,
]

# Deduplicate by slug, keeping the FIRST occurrence. The authored sources come
# first, so on overlap (e.g. two-sum exists in both data_arrays.py and the
# NeetCode authoring manifest with different I/O formats) the authored content
# wins and the catalog entry cannot clobber starter code or test cases.
PROBLEMS: list[dict] = []
_seen_slugs: set[str] = set()
for _problem in _PROBLEMS_RAW:
    _slug = _problem["slug"]
    if _slug in _seen_slugs:
        continue
    _seen_slugs.add(_slug)
    PROBLEMS.append(_problem)

del _PROBLEMS_RAW, _seen_slugs, _problem, _slug

__all__ = ["PROBLEMS"]
