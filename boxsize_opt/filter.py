from typing import Sequence, List, Tuple, Optional
from .box import Box
from .product import Product
from .padberg import padberg_check

# this function returns the box dimensions in the desirable format
def probable_box(box_name: str) -> Tuple[str, int, int, int]:
    dim_list = box_name.split('_')
    for i in range(1, len(dim_list)):
        dim_list[i] = int(dim_list[i])
    return dim_list

def box_from_str(box_name: str) -> Box:
    dim_list = box_name.split('_')
    for i in range(1, len(dim_list)):
        dim_list[i] = int(dim_list[i])
    return Box(box_name, dim_list[1], dim_list[2], dim_list[3])

# checks if all the dimensions of the box2 are greater than equal to box1
def dimension_check(box1: Tuple[int, int, int], box2: Tuple[int, int, int]) -> bool:
    # WARNING: assumes dimensions are ordered highest to lowest
    return box1[1] <= box2[1] and box1[2] <= box2[2] and box1[3] <= box2[3]

# returns the remaining boxes to be checked by Padberg
def remaining_boxes(list1: List[str], list2: List[str]) -> List[str]:
    set1 = set(list1)
    set2 = set(list2)
    other_boxes = set1 - set2
    return list(other_boxes)


def get_eligible_boxes(order: List[Product], box_names: List[str], 
                        verbose: Optional[bool] = False, solver = None,
                        use_dim_check: Optional[bool] = False) -> List[str]:
    '''Given a set of box names, checks which boxes a given order will
       fit into, and returns eligible box names as a list.'''
        # carrying out Padberg Check on the eligible boxes and adding the ones that pass the check to boxes list
    orig_boxes = [box_from_str(box_name) for box_name in box_names]
    # orig_boxes.sort(key=lambda x: x.boxVolume) # May not be needed...
    boxes = []
    opt_count = 0 # number of time Padberg optimization model is solved

    k = 0
    while True:
        if not orig_boxes:
            break

        k+=1
        box = orig_boxes.pop(0)
        if verbose:
            print(f'---- Iteration {k} ----')
            print(f'Running for box {box.boxId}')

        if use_dim_check:
            # WARNING - assumes box and product dimensions
            # are ordered: height <= width <= depth
            max_height = max(p.productHeight for p in order)
            max_width = max(p.productWidth for p in order)
            max_depth = max(p.productDepth for p in order)
            
            dim_check = ((max_height <= box.boxHeight) and (max_width <= box.boxWidth) and (max_depth <= box.boxDepth))
            if verbose:
                print(f'Dimension check: {dim_check}')
            if not dim_check:
                continue

        check = padberg_check(order, box, solver=solver)
        opt_count += 1
        if verbose:
            print(f'Padberg check returned {check}')

        if check==True:
            boxes.append(box.boxId)
            el_box_indices = []
            boxes_added = 0

            for (i, box_2) in enumerate(orig_boxes):
                if box_2.contains(box):
                    el_box_indices.append(i)
                    boxes.append(box_2.boxId)
                    boxes_added += 1

            for i in reversed(el_box_indices):
                orig_boxes.pop(i)

            if verbose:
                print(f'{boxes_added} additional boxes verified since they contain box {box_names[k]}')
    
    if verbose:
        print(f'{len(boxes)}/{len(box_names)} eligible boxes found after solving Padberg model {opt_count} times.')
    return boxes