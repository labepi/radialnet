# vim: set fileencoding=utf-8 :

# Copyright (C) 2007 Insecure.Com LLC.
#
# Author: João Paulo de Souza Medeiros <ignotus21@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

from core.Graph import *
from gui.RadialNet import NetNode

import re


COLORS = [(0.0, 1.0, 0.0),
          (1.0, 1.0, 0.0),
          (1.0, 0.0, 0.0)]

BASE_RADIUS = 5.5
NONE_RADIUS = 4.5



def calc_vulnerability_level(node, host):
    """
    """
    xml_ports = host.search_children('port', deep=True)

    node.set_info({'number_of_scanned_ports': len(xml_ports)})

    if len(xml_ports) < 3:
        node.set_info({'vulnerability_score': 0})

    elif len(xml_ports) < 7:
        node.set_info({'vulnerability_score': 1})

    else:
        node.set_info({'vulnerability_score': 2})


def set_node_info(node, host):
    """
    """
    node.set_info({'host_reference': host})

    # getting vulnerability score
    calc_vulnerability_level(node, host)

    radius = BASE_RADIUS + node.get_info('number_of_scanned_ports') / 2

    node.set_draw_info({'color':COLORS[node.get_info('vulnerability_score')],
                        'radius':radius})

    # getting address and hostnames
    xml_addresses = host.search_children('address')

    addresses = list()

    for xml_address in xml_addresses:

        address = dict()

        address['addr'] = xml_address.get_attr('addr')
        address['type'] = xml_address.get_attr('addrtype')
        address['vendor'] = xml_address.get_attr('vendor')

        addresses.append(address)

    node.set_info({'addresses': addresses})
    node.set_info({'ip': addresses[0]['addr']})

    xml_hostnames = host.search_children('hostname', deep=True)

    if len(xml_hostnames) > 0:

        hostnames = list()

        for xml_hostname in xml_hostnames:

            hostname = dict()

            hostname['name'] = xml_hostname.get_attr('name')
            hostname['type'] = xml_hostname.get_attr('type')

            hostnames.append(hostname)

        node.set_info({'hostnames': hostnames})
        node.set_info({'hostname': hostnames[0]['name']})

    # getting uptime
    xml_uptime = host.search_children('uptime', True)

    if xml_uptime != None:

        uptime = {}

        uptime['seconds'] = xml_uptime.get_attr('seconds')
        uptime['lastboot'] = xml_uptime.get_attr('lastboot')

        node.set_info({'uptime': uptime})

    # getting os fingerprint information
    xml_os = host.search_children('os', True)

    if xml_os != None:

        os = {}

        xml_portsused = xml_os.search_children('portused')
        xml_osclasses = xml_os.search_children('osclass')
        xml_osmatches = xml_os.search_children('osmatch')
        xml_fingerprint = xml_os.search_children('osfingerprint', True)

        os['fingerprint'] = xml_fingerprint.get_attr('fingerprint')

        if len(xml_osclasses) > 0:

            types = ['router', 'wap', 'switch', 'firewall']

            for type in types:
                if type in xml_osclasses[0].get_attr('type').lower():
                    node.set_info({'device_type': type})

            os_classes = []

            for xml_osclass in xml_osclasses:

                os_class = {}

                os_class['type'] = xml_osclass.get_attr('type')
                os_class['vendor'] = xml_osclass.get_attr('vendor')
                os_class['accuracy'] = int(xml_osclass.get_attr('accuracy'))
                os_class['os_family'] = xml_osclass.get_attr('osfamily')

                if xml_osclass.get_attr('osgen') != None:
                    os_class['os_gen'] = xml_osclass.get_attr('osgen')

                os_classes.append(os_class)

            os['classes'] = os_classes

        if len(xml_osmatches) > 0:

            os_matches = []

            for xml_osmatch in xml_osmatches:

                os_match = {}

                os_match['name'] = xml_osmatch.get_attr('name')
                os_match['accuracy'] = int(xml_osmatch.get_attr('accuracy'))
                os_match['db_line'] = int(xml_osmatch.get_attr('line'))

                os_matches.append(os_match)

            os['matches'] = os_matches

        if len(xml_portsused) > 0:

            os_portsused = []

            for xml_portused in xml_portsused:

                os_portused = {}

                os_portused['state'] = xml_portused.get_attr('state')
                os_portused['protocol'] = xml_portused.get_attr('proto')
                os_portused['id'] = int(xml_portused.get_attr('portid'))

                os_portsused.append(os_portused)

            os['used_ports'] = os_portsused

        node.set_info({'os': os})

    # getting sequences information
    xml_tcpsequence = host.search_children('tcpsequence', True)
    xml_ipidsequence = host.search_children('ipidsequence', True)
    xml_tcptssequence = host.search_children('tcptssequence', True)

    sequences = {}

    if xml_tcpsequence != None:

        tcp = {}
        tcp['index'] = int(xml_tcpsequence.get_attr('index'))
        tcp['class'] = xml_tcpsequence.get_attr('class')
        tcp['values'] = xml_tcpsequence.get_attr('values').split(',')
        tcp['difficulty'] = xml_tcpsequence.get_attr('difficulty')

        sequences['tcp'] = tcp

    if xml_ipidsequence != None:

        ip_id = {}
        ip_id['class'] = xml_ipidsequence.get_attr('class')
        ip_id['values'] = xml_ipidsequence.get_attr('values').split(',')

        sequences['ip_id'] = ip_id

    if xml_tcptssequence != None:

        tcp_ts = {}
        tcp_ts['class'] = xml_tcptssequence.get_attr('class')
        tcp_ts['values'] = xml_tcptssequence.get_attr('values')

        if tcp_ts['values'] != None:
            tcp_ts['values'] = tcp_ts['values'].split(',')

        sequences['tcp_ts'] = tcp_ts

    node.set_info({'sequences': sequences})

    # host is host filtered
    filtered = host.query_children('state', 'state', 'filtered', True, True)

    extra_filtered = host.query_children('extraports',
                                         'state',
                                         'filtered',
                                         True,
                                         True)

    if filtered != None or extra_filtered != None:
        node.set_info({'filtered': True})

    # getting ports information
    xml_ports = host.search_children('port', deep=True)
    xml_extraports = host.search_children('extraports', deep=True)

    ports = list()

    for xml_port in xml_ports:

        port = dict()
        state = dict()
        scripts = list()
        service = dict()

        xml_state = xml_port.search_children('state', True, True)
        xml_scripts = xml_port.search_children('script', deep=True)
        xml_service = xml_port.search_children('service', True, True)

        port['id'] = int(xml_port.get_attr('portid'))
        port['protocol'] = xml_port.get_attr('protocol')

        if xml_state != None:
            for key in xml_state.get_keys():
                state[key] = xml_state.get_attr(key)

        for script in xml_scripts:

            scripts.append(dict())

            for key in script.get_keys():
                scripts[-1][key] = script.get_attr(key)

        if xml_service != None:
            for key in xml_service.get_keys():
                service[key] = xml_service.get_attr(key)
        
        port['state'] = state
        port['scripts'] = scripts
        port['service'] = service

        ports.append(port)

    node.set_info({'ports':ports})

    all_extraports = list()

    for xml_extraport in xml_extraports:

        extraports = dict()
        extraports['count'] = int(xml_extraport.get_attr('count'))
        extraports['state'] = xml_extraport.get_attr('state')
        extraports['reason'] = list()
        extraports['all_reason'] = list()

        xml_extrareasons = xml_extraport.search_children('extrareasons',
                                                         deep=True)

        for extrareason in xml_extrareasons:

            extraports['reason'].append(extrareason.get_attr('reason'))
            extraports['all_reason'].append(dict())
        
            for key in extrareason.get_keys():

                value = extrareason.get_attr(key)

                if key == 'count':
                    value = int(value)

                extraports['all_reason'][-1][key] = value

        all_extraports.append(extraports)

    node.set_info({'extraports':all_extraports})

    # getting traceroute information
    xml_trace = host.search_children('trace', first=True)

    if xml_trace != None:

        xml_hops = xml_trace.search_children('hop')

        trace = {}
        hops = []

        for xml_hop in xml_hops:

            hop = {}

            hop['ip'] = xml_hop.get_attr('ipaddr')
            hop['ttl'] = int(xml_hop.get_attr('ttl'))
            hop['rtt'] = xml_hop.get_attr('rtt')

            hostname = xml_hop.get_attr('host')
            hop['hostname'] = (hostname, '')[hostname == None]

            hops.append(hop)

        trace['hops'] = hops
        trace['port'] = xml_trace.get_attr('port')
        trace['protocol'] = xml_trace.get_attr('proto')

        node.set_info({'trace':trace})


def make_graph_from_nmap_parser(parser):
    """
    """
    hosts = parser.get_root().search_children('host', deep=True)
    graph = Graph()
    nodes = list()
    index = 1

    # setting initial reference host
    nodes.append(NetNode(0))
    node = nodes[-1]

    node.set_info({'ip':'127.0.0.1/8', 'hostname':'localhost'})
    node.set_draw_info({'color':(0,0,0), 'radius':NONE_RADIUS})

    # for each host in hosts just mount the graph
    for host in hosts:

        trace = host.search_children('trace', True, True)

        # if host has traceroute information mount graph
        if trace != None:

            prev_node = nodes[0]

            hops = trace.search_children('hop')
            ttls = [int(hop.get_attr('ttl')) for hop in hops]

            # getting nodes of host by ttl
            for ttl in range(1, max(ttls) + 1):

                if ttl in ttls:

                    hop = trace.query_children('hop', 'ttl', ttl, True)

                    for node in nodes:
                        if hop.get_attr('ipaddr') == node.get_info('ip'):
                            break

                    else:

                        nodes.append(NetNode(index))
                        node = nodes[-1]
                        index += 1

                        node.set_draw_info({'valid':True})
                        node.set_info({'ip':hop.get_attr('ipaddr')})
                        node.set_draw_info({'color':(1,1,1),
                                            'radius':NONE_RADIUS})

                        if hop.get_attr('host') != None:
                            node.set_info({'hostname':hop.get_attr('host')})

                    rtt = hop.get_attr('rtt')

                    if rtt != '--':
                        graph.set_connection(node, prev_node, float(rtt))

                    else:
                        graph.set_connection(node, prev_node)

                else:

                    nodes.append(NetNode(index))
                    node = nodes[-1]
                    index += 1

                    node.set_draw_info({'valid':False})
                    node.set_info({'ip':None, 'hostname':None})
                    node.set_draw_info({'color':(1,1,1), 'radius':NONE_RADIUS})

                    graph.set_connection(node, prev_node)

                prev_node = node

    # for each full scanned host
    for host in hosts:

        ip = host.query_children('address', 'addrtype', 'ipv4', True)

        if ip == None:
            ip = host.query_children('address', 'addrtype', 'ipv6', True)

        for node in nodes:
            if ip.get_attr('addr') == node.get_info('ip'):
                break

        else:

            nodes.append(NetNode(index))
            node = nodes[-1]
            index += 1

            node.set_draw_info({'no_route':True})

            graph.set_connection(node, nodes[0])

        node.set_draw_info({'valid':True})
        node.set_info({'scanned':True})
        set_node_info(node, host)

    graph.set_nodes(nodes)
    graph.set_main_node_by_id(0)

    return graph


