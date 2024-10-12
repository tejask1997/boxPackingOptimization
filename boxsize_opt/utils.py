from typing import Sequence, List, Optional, FrozenSet

def find_minimal_sets(sets: Sequence, verbose: Optional[bool] = False) -> List[FrozenSet]:
    """Takes a collection of set-like objects and returns
       a list of minimal sets with respect to the subset partial ordering."""
       

    minimal_sets = []
    sets_to_process = [frozenset(x) for x in sets]
    sets_to_process.sort(key= lambda x : len(x))

    k = 1
    
    while True:
        if verbose:
            print(f'--- Iteration {k} ---')
        x = sets_to_process.pop(0)
        minimal_sets.append(x)
        idxs_to_remove = []
        # Find sets which contain this set
        for (i,y) in enumerate(sets_to_process):
            if x.issubset(y):
                idxs_to_remove.append(i)
        
        if verbose:
            print(f'\t{len(idxs_to_remove)} redundant sets found.')

        # Remove found sets (reverse so we do not change indices of elements)
        for i in reversed(idxs_to_remove):
            sets_to_process.pop(i)
        
        if verbose:
            print(f'\t{len(sets_to_process)} potential minimal subsets remaining.')

        # Exit if no remaining sets
        if not sets_to_process:
            break
        k += 1

    minimal_sets = [list(frozen_set) for frozen_set in minimal_sets]

    return minimal_sets