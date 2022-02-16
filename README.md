# draw_OpenR_topology
Parse Open/R show tech LSDB output and draw a graph of the topology

**Usage:**

~ % /usr/local/bin/python3 parse_igp.py
Enter file name with OpenR show tech output: ~/Downloads/host/commands/techsupport_openr/stdout
Enter path and file name to save the topology graph: ~/Downloads/topo
Graph saved in ~/Downloads/topo.png
'drawing the topology... '

**Description:**

Given a showtech output with OpenR kvstore adjacency details this script will parse it and create a
topology graph based on LSDB info in the output in the section --------  breeze kvstore adj  --------
