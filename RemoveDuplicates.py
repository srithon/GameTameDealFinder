import sys

from collections import defaultdict

items = list()
point_prices = list()

def write_lists():
    with open('item_list_file_complete.txt', 'w') as item_list_file:
        for entry in items:
            item_list_file.write(str(entry))

    with open('point_price_list_file_complete.txt', 'w') as point_price_file:
        for entry in point_prices:
            point_price_file.write(str(entry))


# https://stackoverflow.com/questions/11236006/identify-duplicate-values-in-a-list-in-python
def remove_duplicates():
    D = defaultdict(list)

    for i, item in enumerate(items):
        D[item].append(i)
    D = {k:v for k,v in D.items() if len(v)>1}

    indices = list()

    for i in reversed(list(D.values())):
        for j in range(len(i) - 1, 0, -1):
            indices.append(i[j])

    indices.sort(reverse=True)

    print(indices)

    while len(indices) > 0:
        items.pop(indices[0])
        point_prices.pop(indices[0])
        indices.pop(0)


def load_data():
    with open('item_list_file_complete.txt', 'r') as items_file:
        for line in items_file:
            if len(line.rstrip()) != 0:
                items.append(line)

    with open('point_price_list_file_complete.txt', 'r') as points_file:
        for line in points_file:
            if len(line.rstrip()) != 0:
                point_prices.append(line)


load_data()

print('{} items in Item List'.format(len(items)))
print('{} items in Point Prices List'.format(len(point_prices)))

remove_duplicates()

write_lists()

