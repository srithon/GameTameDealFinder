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
            item_list_file.write(str(entry) + '\n')

    with open('point_price_file_active.txt', 'w') as point_price_file:
        for entry in point_prices:
            point_price_file.write(str(entry) + '\n')

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
        items.append(line)

with open('point_price_list_file_active.txt', 'r') as points_file:
    for line in points_file:
        point_prices.append(line)

with open('real_price_list_file.txt', 'r') as prices_file:
    for line in prices_file:
        real_prices.append(line)

print('{} items in Item List'.format(len(items)))
print('{} items in Real Prices List'.format(len(real_prices)))

for i in range(len(items)):
    money_per_points.append(float(real_prices[i]) / int(point_prices[i]))

sort_lists()
write_lists()

