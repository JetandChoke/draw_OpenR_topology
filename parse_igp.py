#!/usr/bin/env/python3.8
# 
# ~ % /usr/local/bin/python3 ~/Documents/scripts/parse_igp.py
# Enter file name with OpenR show tech output: ~/commands/techsupport_openr/stdout
# Enter path and file name to save the topology graph: ~/Downloads/topo                                              
# Graph saved in ~/Downloads/topo.png
# 'drawing the topology... '
#
# Given a showtech output with OpenR kvstore adjacency details this script will parse it and create a
# topology graph based on LSDB info in the output in the section --------  breeze kvstore adj  --------
#
import argparse
import sys
import re
from pprint import pprint

KV_ADJ_SEC_STR = ".*breeze kvstore adj.+"
ADJ_HOST_STR = ">\s(\S+\.\S+)\s=>\sVersion:\s\d+"
ADJ_PEER_STR = "(\S+\.\w+\d)\s+(\w+\S+)\s+(\w+\S+)\s+\d+\s+\d+.+"
END_STR = ".*breeze \S+.+"

def parse_openr_showtech_file(config_file):
    '''Parses the file and returs all the devices in IGP
    parameters:
    config_file (str): path to config file

    returns:
    defaultdict: containing all the devices in IGP
    '''
    kvstore_adj_sec = False # openr adjacency section flag
    hosts = False  # openr adjacency host section flag
    host_name = []  # openr adj hostname
    peer_name = []  # openr adj peer
    local_intf = []  # local interface
    remote_intf = []  # remote interface
    
    kv_adj_sec_re = re.compile(KV_ADJ_SEC_STR)  # kv adj section
    end_str_re = re.compile(END_STR)  # end of the kv adj section

    adj_host_str_re = re.compile(ADJ_HOST_STR)  # adj host
    adj_peer_str_re = re.compile(ADJ_PEER_STR)  # adj peer, local and remote intf
    

    result = {}
    with open(openr_showtech) as f:
        config = f.readlines()
        for line in config:
            breezeline = re.match(kv_adj_sec_re, line) 
            if not len(line):
                #skip empty line
                continue

            if not breezeline and kvstore_adj_sec:
                #we are in the breeze adj section

                adj_host_sec = re.match(adj_host_str_re, line)
                if adj_host_sec:
                    if hosts:
                        # a new host's LSDB
                        host_name = []
                        host_name.append(adj_host_sec.group(1))
                        continue
                    else:
                        # first host's LSDB
                        host_name.append(adj_host_sec.group(1))
                        hosts = True
                        continue

                adj_peer_str = re.match(adj_peer_str_re, line)
                if adj_peer_str:

                    if kvstore_adj_sec and host_name != "":
                        #we got  another peer for a host
                        peer_name.append(adj_peer_str.group(1))
                        local_intf.append(adj_peer_str.group(2))
                        remote_intf.append(adj_peer_str.group(3))
                        local = tuple(host_name + local_intf)
                        remote = tuple(peer_name + remote_intf)
                        result[local] = remote
                        #cleaning for the next iteration
                        local = tuple()
                        remote = tuple()
                        local_intf = []
                        remote_intf = []
                        peer_name = []
                        #hosts = False
                        continue

            if breezeline:
                #we have entered the breeze kvstore adj section
                kvstore_adj_sec = True
                continue

            end_of_adj_sec = re.match(END_STR, line)
            if end_of_adj_sec:
                kvstore_adj_sec = False
                #we are done with all adjancencies for all hosts
                continue
    return result

openr_showtech = input('Enter file name with OpenR show tech output: ')
# now let's remove the duplcity in the result before drawing the topology
big_result = {}
lists = []
for key, value in (parse_openr_showtech_file(openr_showtech)).items(): 
    dic_buffer = {} 
    key_str = ''.join(list(key)) 
    value_str = ''.join(list(value)) 
    if key_str not in ''.join(lists) or value_str not in ''.join(lists):
        lists.append(key_str) 
        lists.append(value_str) 
        big_result[key] = value
    else:
        pass

try:
    import graphviz as gv
except ImportError:
    print("Module graphviz needs to be installed")
    print("pip install graphviz")
    sys.exit()

styles = {
    'graph': {
        'label': 'Network Map',
        'fontsize': '16',
        'fontcolor': 'white',
        'bgcolor': '#333333',
        'rankdir': 'BT',
    },
    'nodes': {
        'fontname': 'Helvetica',
        'shape': 'box',
        'fontcolor': 'white',
        'color': '#006699',
        'style': 'filled',
        'fillcolor': '#006699',
        'margin': '0.4',
    },
    'edges': {
        'style': 'dashed',
        'color': 'green',
        'arrowhead': 'open',
        'fontname': 'Courier',
        'fontsize': '8',
        'fontcolor': 'white',
    }
}


def apply_styles(graph, styles):
    graph.graph_attr.update(('graph' in styles and styles['graph']) or {})
    graph.node_attr.update(('nodes' in styles and styles['nodes']) or {})
    graph.edge_attr.update(('edges' in styles and styles['edges']) or {})
    return graph


#def draw_topology(topology_dict, output_filename='img/topology'):
def draw_topology(topology_dict, output_filename):
    '''
    topology_dict - dictionary describing the topology
        {('R4', 'Fa0/1'): ('R5', 'Fa0/1'),
         ('R4', 'Fa0/2'): ('R6', 'Fa0/0')}
    matches topology:
    [ R5 ]-Fa0/1 --- Fa0/1-[ R4 ]-Fa0/2---Fa0/0-[ R6 ]
    The function generates topologu in specified format
    and writes the file into img directory
    '''
    nodes = set([
        item[0]
        for item in list(topology_dict.keys()) + list(topology_dict.values())
    ])

    g1 = gv.Graph(format='png')

    for node in nodes:
        g1.node(node)

    for key, value in topology_dict.items():
        head, t_label = key
        tail, h_label = value
        g1.edge(
            head, tail, headlabel=h_label, taillabel=t_label, label=" " * 12)

    g1 = apply_styles(g1, styles)
    filename = g1.render(filename=output_filename)
    print("Graph saved in", filename)

def main():
   
    output_dir = input('Enter path and file name to save the topology graph: ')

    draw_topology(big_result, output_filename=output_dir)
    #pprint(big_result)
    pprint('drawing the topology... ')


if __name__ == '__main__':
    main()
    
