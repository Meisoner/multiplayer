def searchinv(invs, item):
    res, empty = 0, 0
    for i in range(5):
        if invs[i][0] == item and invs[i][1] > 0:
            res = i + 1
        elif invs[i][1] == 0 and not empty:
            empty = i + 1
    if res:
        return res - 1
    elif empty:
        return empty - 1
    else:
        return -1