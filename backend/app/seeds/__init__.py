from app.seeds.data_arrays import ARRAY_PROBLEMS
from app.seeds.data_graphs_dp import GRAPHS_DP
from app.seeds.data_linked_stack import LINKED_STACK
from app.seeds.data_strings import STRINGS
from app.seeds.data_trees import TREES

PROBLEMS = [*ARRAY_PROBLEMS, *STRINGS, *LINKED_STACK, *TREES, *GRAPHS_DP]

__all__ = ["PROBLEMS"]
