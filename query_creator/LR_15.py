import oracledb


def gen_input_regions():
    f = open("D:\django_proj\external_manipulation\query_creator\\regions.txt", "r", encoding="utf-8")
    regions = f.read().splitlines()
    reg_en = []
    reg_ru = []
    regions = regions[0::2]
    for i, j in zip(regions[0::2], regions[1::2]):
        reg_ru.append(i)
        reg_en.append(j)
    f.close()

    import re

    reg_ru_without_numbers = []
    for word in reg_ru:
        nums = re.findall(r'\d+', word)
        reg_ru_without_numbers.append(word.replace(".", "").replace(nums[0], "")[1:])
    return reg_ru_without_numbers, reg_en


def insert_regions(connection):
    cursor = connection.cursor()
    regions = gen_input_regions()[0]
    from random import randint
    for reg in regions:
        cursor.execute("""
                INSERT INTO regions (id, name, time)
                VALUES (OBJ_SEQ.nextval,:name, :time)""",
                       time=str(randint(1, 10)),
                       name=reg)

    connection.commit()


def gen_input_goods():
    from random import choice
    price = []
    weight = []
    pr_ch = [i * 100 for i in range(2, 1000)]
    print(pr_ch)
    for i in range(1, 100):
        price.append(choice(pr_ch))
        weight.append(choice(pr_ch[:100:5]))
    return price, weight


def insert_goods(connection):
    cursor = connection.cursor()

    price_, weight_ = gen_input_goods()
    for i in range(len(price_)):
        cursor.execute("""
                INSERT INTO goods (id, price, weight)
                VALUES (OBJ_SEQ.nextval,:price, :weight)""",
                       price=price_[i],
                       weight=weight_[i])

    connection.commit()


def gen_input_clients():
    from mimesis import Address, Person
    adresses = [Address("ru").address() for _ in range(1, 98)]
    fio = [Person("ru").full_name() for _ in range(1, 98)]
    from random import shuffle

    return fio, adresses


def insert_clients(connection):
    cursor = connection.cursor()
    id_regions = cursor.execute("SELECT * FROM regions")
    all_regions = id_regions.fetchall()

    fio_, adresses_ = gen_input_clients()
    for i in range(len(fio_)):
        cursor.execute("""
                INSERT INTO clients (id, fio, adress, regions_id)
                VALUES (OBJ_SEQ.nextval,:fio, :adress, :regions_id)""",
                       fio=fio_[i],
                       adress=adresses_[i],
                       regions_id=all_regions[i][0])

    connection.commit()


def gen_input_warehouse():
    from mimesis import Address
    from random import randint
    adresses = [Address('zh').address() for _ in range(1, 10)]
    time = [randint(2, 5) for _ in range(1, 10)]
    return adresses, time


def insert_warehouse(connection):
    cursor = connection.cursor()

    adresses_, time_ = gen_input_warehouse()
    for i in range(len(adresses_)):
        cursor.execute("""
                INSERT INTO warehouse (id, address, time)
                VALUES (OBJ_SEQ.nextval,:address, :time)""",
                       address=adresses_[i],
                       time=time_[i])

    connection.commit()


def gen_input_orders():
    from random import randint
    amount = [0 for _ in range(1, 97 * 5)]
    cli_id = [i for i in range(197, 294)]
    return amount, cli_id


def insert_orders(connection):
    cursor = connection.cursor()
    r = cursor.execute("SELECT * FROM clients")
    all = r.fetchall()
    from random import randint
    for client in all:
        for i in range(0, randint(1, 5)):
            cursor.execute("""
                    INSERT INTO orders (id, amount, clients_id)
                    VALUES (OBJ_SEQ.nextval,:amount, :clients_id)""",
                           amount=0,
                           clients_id=client[0])
    connection.commit()


def insert_items(connection):
    cursor = connection.cursor()
    r = cursor.execute("SELECT * FROM orders")
    all = r.fetchall()
    r = cursor.execute("SELECT * FROM goods")
    all_good = r.fetchall()
    from random import randint, choice
    for order in all:
        cursor.execute("""
                INSERT INTO items (orders_id, goods_id, quantity)
                VALUES (:orders_id,:goods_id, :quantity)""",
                       orders_id=order[0],
                       # stopIteration if not enough goods
                       goods_id=choice(all_good)[0],
                       quantity=randint(1, 10))
    connection.commit()


def insert_positions(connection):
    cursor = connection.cursor()
    war = cursor.execute("SELECT * FROM warehouse")
    all_war = war.fetchall()
    good = cursor.execute("SELECT * FROM goods")
    all_good = good.fetchall()
    from random import choice, randint
    for i in range(98, 197):
        cursor.execute("""
                INSERT INTO positions (warehouse_id, goods_id, quantity)
                VALUES (:warehouse_id, :goods_id, :quantity)""",
                       warehouse_id=choice(all_war)[0],
                       goods_id=choice(all_good)[0],
                       quantity=randint(100, 1000))
    connection.commit()


def delete_all(connection):
    cursor = connection.cursor()
    # delete autoincrement sequences
    # cursor.execute("DROP SEQUENCE OBJ_SEQ")

    cursor.execute("DELETE FROM positions")
    cursor.execute("DELETE FROM items")
    cursor.execute("DELETE FROM orders")
    cursor.execute("DELETE FROM clients")
    cursor.execute("DELETE FROM warehouse")
    cursor.execute("DELETE FROM goods")
    cursor.execute("DELETE FROM regions")
    connection.commit()


def regenerate_tables(connection):
    # reset autoincrement sequences
    # cursor = connection.cursor()
    # cursor.execute("CREATE SEQUENCE OBJ_SEQ START WITH 1 INCREMENT BY 1")
    delete_all(connection)
    insert_regions(connection)
    insert_goods(connection)
    insert_clients(connection)
    insert_warehouse(connection)
    insert_orders(connection)
    insert_items(connection)
    insert_positions(connection)


# count time delivery to client
def count_time_delivery_from(connection):
    cursor = connection.cursor()
    cursor.execute("""
            SELECT orders.id, regions.time
            FROM orders
            INNER JOIN clients ON orders.clients_id = clients.id
            INNER JOIN regions ON clients.regions_id = regions.id
            """)
    all = cursor.fetchall()
    cursor.execute("""
            SELECT orders.id, warehouse.time 
            FROM orders 
            INNER JOIN items ON orders.id = items.orders_id
            INNER JOIN goods ON items.goods_id = goods.id
            INNER JOIN positions ON goods.id = positions.goods_id
            INNER JOIN warehouse ON positions.warehouse_id = warehouse.id
            """)
    all_ = cursor.fetchall()
    # sum time delivery from regions to warehouse for each order

    all_ = [[i[0], i[1]] for i in all_]
    print(all_)
    all__orders_id = [i[0] for i in all_]
    for i in range(len(all)):
        if all[i][0] in all__orders_id:
            all[i][1] = int(all[i][1]) + all_[all__orders_id.index(all[i][0])][1]
    # print time delivery from regions to warehouse for each order
    for i in all:
        print("order id: {}, total time delivery: {}".format(i[0], i[1]))


# how many orders in each region
def count_orders_in_regions(connection):
    cursor = connection.cursor()
    cursor.execute("""
            SELECT regions.name, COUNT(orders.id)
            FROM regions
            INNER JOIN clients ON regions.id = clients.regions_id
            INNER JOIN orders ON clients.id = orders.clients_id
            GROUP BY regions.name
            """)
    all = cursor.fetchall()
    for i in all:
        print("region: {}, orders: {}".format(i[0], i[1]))


# how many positions in each warehouse
def count_positions_in_warehouse(connection):
    cursor = connection.cursor()
    cursor.execute("""
            SELECT warehouse.address, SUM(positions.quantity)
            FROM warehouse
            INNER JOIN positions ON warehouse.id = positions.warehouse_id
            GROUP BY warehouse.address
            """)
    all = cursor.fetchall()
    for i in all:
        print("warehouse: {}, positions: {}".format(i[0], i[1]))


# how many goods in each warehouse
def count_goods_in_warehouse(connection):
    cursor = connection.cursor()
    cursor.execute("""
            SELECT warehouse.address, COUNT(goods.id)
            FROM warehouse
            INNER JOIN positions ON warehouse.id = positions.warehouse_id
            INNER JOIN goods ON positions.goods_id = goods.id
            GROUP BY warehouse.address
            """)
    all = cursor.fetchall()
    for i in all:
        print("warehouse: {}, goods: {}".format(i[0], i[1]))


# which order has the most goods
def count_max_goods_in_order(connection):
    cursor = connection.cursor()
    cursor.execute("""
            SELECT orders.id, SUM(items.quantity)
            FROM orders
            INNER JOIN items ON orders.id = items.orders_id
            GROUP BY orders.id
            """)
    all = cursor.fetchall()
    max = 0
    for i in all:
        if i[1] > max:
            max = i[1]
    for i in all:
        if i[1] == max:
            print("order: {}, goods: {}".format(i[0], i[1]))

def count_time_delivery_from_region_to_warehouse(region, warehouse):
    connection = oracledb.connect(user="lr15", password="lr15", dsn="localhost:11521/XEPDB1")
    cursor = connection.cursor()
    cursor.execute("""
            select r.NAME, w.ADDRESS, r.TIME + w.TIME
            from regions r, warehouse w
            order by r.NAME
            """)
    all = cursor.fetchall()
    connection.close()
    #find in all rows region and warehouse
    for i in all:
        if i[0] == region and i[1] == warehouse:
            print("region: {}, warehouse: {}, time: {}".format(i[0], i[1], i[2]))
            return i[2]


def example_requests(connection, i):
    match i:
        case 1:
            count_time_delivery_from(connection)
        case 2:
            count_orders_in_regions(connection)
        case 3:
            count_positions_in_warehouse(connection)
        case 4:
            count_goods_in_warehouse(connection)
        case 5:
            count_max_goods_in_order(connection)
        case 6:
            count_time_delivery_from_region_to_warehouse(connection)
        case _:
            print("no such request")

def make_sql_request(request):
    connection = oracledb.connect(user="lr15", password="lr15", dsn="localhost:11521/XEPDB1")
    cursor = connection.cursor()
    cursor.execute(request)

    all = cursor.fetchall()

    connection.close()
    for i in all:
        print(i)
    return all
def all_warhouses():
    connection = oracledb.connect(user="lr15", password="lr15", dsn="localhost:11521/XEPDB1")
    cursor = connection.cursor()
    cursor.execute("""
    select w.ADDRESS from WAREHOUSE w
    """)
    all = cursor.fetchall()
    connection.close()
    return all

# this script is used to generate data for the database
# there are 7 tables: regions, goods, clients, warehouse, orders, items, positions
# its possible to delete all data from tables and regenerate it randomly

if __name__ == '__main__':
    connection = oracledb.connect(user="lr15", password="lr15", dsn="localhost:11521/XEPDB1")
    # regenerate_tables(connection)
    # example_requests(connection, 6)
    all_warhouses()

    pass
