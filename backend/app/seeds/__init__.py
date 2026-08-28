from app.seeds.data_arrays import ARRAY_PROBLEMS
from app.seeds.data_graphs_dp import GRAPHS_DP
from app.seeds.data_linked_stack import LINKED_STACK
from app.seeds.data_neetcode150 import NEETCODE_150
from app.seeds.data_strings import STRINGS
from app.seeds.data_trees import TREES

# Fully-authored problems first, then the NeetCode 150 catalog (which reuses the
# authored slugs for overlapping problems, so content is never lost).
PROBLEMS = [
    *ARRAY_PROBLEMS,
    *STRINGS,
    *LINKED_STACK,
    *TREES,
    *GRAPHS_DP,
    *NEETCODE_150,
]

__all__ = ["PROBLEMS"]
