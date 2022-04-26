def searchinv(invs, item, allowempty=True):
    res, empty = 0, 0
    for i in range(20):
        if invs[i][0] == item and invs[i][1] > 0:
            res = i + 1
            break
        elif invs[i][1] == 0 and not empty:
            empty = i + 1
    if res:
        return res - 1
    elif empty and allowempty:
        return empty - 1
    else:
        return -1