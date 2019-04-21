items = list()
point_prices = list()
real_prices = list()
money_per_points = list()

def write_lists():
    with open('money_per_points_file.txt', 'w+') as money_per_points_file:
        for entry in money_per_points:
            money_per_points_file.write(str(entry) + '\n')

    with open('item_list_file_active.txt', 'w') as item_list_file:
        for entry in items:
            item_list_file.write(str(entry))

    with open('point_price_list_file_active.txt', 'w') as point_price_file:
        for entry in point_prices:
            point_price_file.write(str(entry))

    with open('real_price_list_file.txt', 'w') as real_price_file:
        for entry in real_prices:
            real_price_file.write(str(entry) + '\n')

def sort_lists():
    global items, point_prices, real_prices, money_per_points

    index_list = list()
    for i in range(0, len(money_per_points)):
        index_list.append(i)

    for i in range(1, len(money_per_points)):
        ind = i
        while (ind > 0 and money_per_points[ind] < money_per_points[ind - 1]):
            temp = money_per_points[ind]
            money_per_points[ind] = money_per_points[ind - 1]
            money_per_points[ind - 1] = temp

            index_list[ind] ^= index_list[ind - 1]
            index_list[ind - 1] ^= index_list[ind]
            index_list[ind] ^= index_list[ind - 1]

            ind = ind - 1

    items = [items[i] for i in index_list]
    real_prices = [real_prices[i] for i in index_list]
    point_prices = [point_prices[i] for i in index_list]


with open('item_list_file_active.txt', 'r') as items_file:
    for line in items_file:
        if len(line.rstrip()) != 0:
            items.append(line)

with open('point_price_list_file_active.txt', 'r') as points_file:
    for line in points_file:
        if len(line.rstrip()) != 0:
            point_prices.append(line)

with open('real_price_list_file.txt', 'r') as prices_file:
    for line in prices_file:
        if len(line.rstrip()) != 0:
            real_prices.append(line)

print('{} items in Item List'.format(len(items)))
print('{} items in Real Prices List'.format(len(real_prices)))
print('{} items in Point Prices List'.format(len(point_prices)))

for i in range(len(items)):
    money_per_points.append(float(real_prices[i]) / int(point_prices[i]))

sort_lists()
write_lists()

