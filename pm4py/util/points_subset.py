def pick_chosen_points(m, n):
    """
    Pick chosen points in a list

    Parameters
    ------------
    m
        Number of wanted points
    n
        Number of current points

    Returns
    ------------
    indexes
        Indexes of chosen points
    """
    return [i * n // m + n // (2 * m) for i in range(m)]


def pick_chosen_points_list(m, lst, include_extremes=True):
    """
    Pick a chosen number of points from a list

    Parameters
    -------------
    m
        Number of wanted points
    lst
        List

    Returns
    -------------
    reduced_lst
        Reduced list
    """
    n = len(lst)
    points = pick_chosen_points(m, n)

    if include_extremes:
        if 0 not in points:
            points = [0] + points

        if len(lst)-1 not in points:
            points = points + [len(lst)-1]

    ret = []
    for i in points:
        ret.append(lst[i])

    return ret
