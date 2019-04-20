l = list()
with open('item_list_file_complete.txt', 'r') as file:
    for line in file:
        if len(line.rstrip()) == 0:
            break
        else:
            l.append(line)

with open('item_list_file_complete.txt', 'w') as file:
    for entry in l:
        file.write(entry)
