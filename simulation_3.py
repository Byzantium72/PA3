# Created on Oct 12, 2016

# @author: mwittie

import network_3
import link_3
import threading
from time import sleep

# configuration parameters
router_queue_size = 0  # 0 means unlimited
simulation_time = 15  # give the network sufficient time to transfer all packets before quitting

if __name__ == '__main__':
    object_L = []  # keeps track of objects, so we can kill their threads

    # create network nodes
    host1 = network_3.Host(1)
    object_L.append(host1)
    host2 = network_3.Host(2)
    object_L.append(host2)
    host3 = network_3.Host(3)
    object_L.append(host3)
    host4 = network_3.Host(4)
    object_L.append(host4)
    routing_table_a = {
        3: 0,
        4: 1
    }
    router_a = network_3.Router(name='A', intf_count=2, max_queue_size=router_queue_size, routing_table=routing_table_a)
    object_L.append(router_a)
    routing_table_b = {
        3: 0
    }
    router_b = network_3.Router(name='B', intf_count=1, max_queue_size=router_queue_size, routing_table=routing_table_b)
    object_L.append(router_b)
    routing_table_c = {
        4: 0
    }
    router_c = network_3.Router(name='C', intf_count=1, max_queue_size=router_queue_size, routing_table=routing_table_c)
    object_L.append(router_c)
    routing_table_d = {
        3: 0,
        4: 1
    }
    router_d = network_3.Router(name='D', intf_count=2, max_queue_size=router_queue_size, routing_table=routing_table_d)
    object_L.append(router_d)

    # create a Link Layer to keep track of links between network nodes
    link_layer = link_3.LinkLayer()
    object_L.append(link_layer)

    # add all the links
    # link parameters: from_node, from_intf_num, to_node, to_intf_num, mtu
    link_layer.add_link(link_3.Link(host1, 0, router_a, 0, 50))
    link_layer.add_link(link_3.Link(router_a, 0, router_b, 0, 50))
    link_layer.add_link(link_3.Link(router_a, 1, router_c, 0, 50))
    link_layer.add_link(link_3.Link(host2, 0, router_a, 1, 50))
    link_layer.add_link(link_3.Link(router_b, 0, router_d, 0, 50))
    link_layer.add_link(link_3.Link(router_c, 0, router_d, 1, 50))
    link_layer.add_link(link_3.Link(router_d, 0, host3, 0, 50))
    link_layer.add_link(link_3.Link(router_d, 1, host4, 0, 50))

    # start all the objects
    thread_L = []
    thread_L.append(threading.Thread(name=host1.__str__(), target=host1.run))
    thread_L.append(threading.Thread(name=host3.__str__(), target=host3.run))
    thread_L.append(threading.Thread(name=router_a.__str__(), target=router_a.run))
    thread_L.append(threading.Thread(name=host2.__str__(), target=host2.run))
    thread_L.append(threading.Thread(name=host4.__str__(), target=host4.run))
    thread_L.append(threading.Thread(name=router_b.__str__(), target=router_b.run))
    thread_L.append(threading.Thread(name=router_c.__str__(), target=router_c.run))
    thread_L.append(threading.Thread(name=router_d.__str__(), target=router_d.run))

    thread_L.append(threading.Thread(name="Network", target=link_layer.run))

    for t in thread_L:
        t.start()

    # create some send events
    for i in range(3):
        # client.udt_send(2, 'Sample data %d' % i)
        host1.udt_send(3, 1, 'Packet sent from Host 1 to Host 3: %d' % i)
        host2.udt_send(4, 2, 'Packet sent from Host 2 to Host 4: %d' % i)
        # host1.udt_send(3, 1, 'Packet sent from Host 1 to Host 3: A B C D E F G H I J K L M N O P Q R S T U V W X Y Z %d' % i)
        # host2.udt_send(4, 2, 'Packet sent from Host 2 to Host 4: a b c d e f g h i j k l m n o p q r s t u v w x y z %d' % i)

    # give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)

    # join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()

    print("All simulation threads joined")
