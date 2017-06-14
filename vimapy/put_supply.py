import ConfigParser
import logging
import os
import time
import xml.dom.minidom as xml
import xml.etree.ElementTree as ET
from xml.dom import minidom
from xml.etree import ElementTree
from id_factory import *


def make_node(node_no, visum_com, nodes):
    node = visum_com.Net.Nodes.ItemByKey(node_no)
    code = node.AttValue("Code")
    node_id = get_id_node(no=node_no, code=code)
    if node_id not in nodes:
        nodes[node_id] = {'x': node.AttValue("xCoord"), 'y': node.AttValue("yCoord")}

    return node_id


def make_link(fzp_id, from_node_no, to_node_no, links, nodes, visum_com, speed=10, length=None):

    from_node_id = make_node(node_no=from_node_no, visum_com=visum_com, nodes=nodes)
    to_node_id = make_node(node_no=to_node_no, visum_com=visum_com, nodes=nodes)

    link_id = get_id_link(fzp_id=fzp_id, from_node_id=from_node_id, to_node_id=to_node_id)
    if link_id not in links:

        if from_node_no == to_node_no:
            length = 0.0
        elif length is None:
            link = visum_com.Net.Links.ItemByKey(fromNode=from_node_no, toNode=to_node_no)
            length = link.AttValue("length")

        links[link_id] = {"from": from_node_id, "to": to_node_id, "length": length, "speed": speed}
    return link_id


def set_projection(v, config):
    v.visum_com.Net.SetAttValue("ConcatMaxLen", config.get("Visum", "maxlength"))
    proj = config.get("Visum", "projection")
    v.visum_com.Net.SetProjection(newProjection=proj, calculate=True)


def export_supply_and_network(v, config):

    stopFacilities = {}
    links = {}
    nodes = {}

    schedule = {}

    v.apl.go_offline(mit_fzps=True, mit_fpfs=True, mit_fzpes=True, params={"fzpes": ["PostLength", "PostRunTime", "LineRouteItem\\StopPoint\\No",
                                                                                     "LineRouteItem\\StopPoint\\Code",
                                                                                     'LineRouteItem\\OutLink\\FromNodeNo',
                                                                                     'LineRouteItem\\OutLink\\ToNodeNo',
                                                                                     'LineRouteItem\\StopPoint\\Xcoord',
                                                                                     'Concatenate:UsedLineRouteItems\\OutLink\\FromNodeNo',
                                                                                     'Concatenate:UsedLineRouteItems\\OutLink\\ToNodeNo',
                                                                                     'Concatenate:UsedLineRouteItems\OutLink\FromNode\Code',
                                                                                     'Concatenate:UsedLineRouteItems\OutLink\ToNode\Code',
                                                                                     'LineRouteItem\\InLink\\ToNodeNo',
                                                                                     'LineRouteItem\\NodeNo',
                                                                                     'LineRouteItem\\Node\\Code',
    'LineRouteItem\\StopPoint\\Ycoord']})

    for fzp in v.apl.hole_fahrzeitprofile():
        logging.getLogger(__name__).info("%s" % fzp)

        line_id = get_id_line(linename=fzp.linename(), lineroutename=fzp.lineroutename(), direction=fzp.richtung(), timeprofilename=fzp.name())
        if line_id not in schedule:
            schedule[line_id] = {}

        for fpf in fzp.hole_fahrplanfahrten():

            from_tp_index = fpf.von_fahrzeitprofilelement_index()
            to_tp_index = fpf.bis_fahrzeitprofilelement_index()
            lineroute_id = get_id_lineroute(from_tp_index=from_tp_index, to_tp_index=to_tp_index)
            delta = fzp.hole_element(fpf.von_fahrzeitprofilelement_index()).abfahrt()

            if lineroute_id not in schedule[line_id]:

                route = []
                stops = []
                for fzpe in fzp.hole_verlaufe():
                    if from_tp_index > fzpe.index() or fzpe.index() > to_tp_index:
                        continue

                    length = fzpe.com_objekt.AttValue("PostLength")*1000.0

                    try:
                        speed = length/(fzpe.com_objekt.AttValue("PostRunTime")-2.0)
                    except ZeroDivisionError:
                        speed = 10000000

                    stop_no = int(fzpe.com_objekt.AttValue("LineRouteItem\StopPoint\No"))
                    stop_code = fzpe.com_objekt.AttValue("LineRouteItem\StopPoint\Code")
                    stop_id = get_id_stop(fzp_id=fzp.nummer(), no=stop_no, code=stop_code)

                    node_no = fzpe.com_objekt.AttValue("LineRouteItem\NodeNo")
                    link_id = make_link(fzp_id=fzp.nummer(), from_node_no=node_no, to_node_no=node_no, links=links, nodes=nodes, visum_com=v.visum_com, speed=10000000)
                    route.append(link_id)

                    if stop_id not in stopFacilities:


                        stopFacilities[stop_id] = {'x': fzpe.com_objekt.AttValue("LineRouteItem\StopPoint\Xcoord"),
                                                   'y': fzpe.com_objekt.AttValue("LineRouteItem\StopPoint\Ycoord"),
                                                   'linkRefId': link_id,
                                                   'lineRefId': line_id}



                    from_node_nos = fzpe.com_objekt.AttValue("Concatenate:UsedLineRouteItems\OutLink\FromNodeNo").split(",")
                    to_node_nos = fzpe.com_objekt.AttValue("Concatenate:UsedLineRouteItems\OutLink\ToNodeNo").split(",")

                    t1 = time.strftime('%H:%M:%S', time.gmtime(max(fzpe.abfahrt() - delta, 0)))
                    t2 = time.strftime('%H:%M:%S', time.gmtime(max(fzpe.ankunft() - delta, 0)))

                    stops.append({'refId': stop_id, 'departureOffset': t1, 'arrivalOffset': t2})
                    if from_node_nos != [""]:
                        link_id = make_link(fzp_id=fzp.nummer(), from_node_no=from_node_nos[0],
                                            to_node_no=to_node_nos[-1], links=links, nodes=nodes,
                                                visum_com=v.visum_com, speed=speed, length=length/1000.0)
                        route.append(link_id)

                schedule[line_id][lineroute_id] = {"departures": [], "route": route, "routeProfile": stops}

            t = time.strftime('%H:%M:%S', time.gmtime(fpf.abfahrt()))
            schedule[line_id][lineroute_id]["departures"].append(t)
    return {"schedule": schedule, "stopFacilities": stopFacilities, "nodes": nodes, "links": links}


def to_xml(transit, folder, config):
    schedule = transit["schedule"]
    stop_facilities = transit["stopFacilities"]
    nodes = transit["nodes"]
    links = transit["links"]

    network = ET.Element("network")
    xml_nodes = ET.Element("nodes")
    for node_id, node in nodes.iteritems():
        xml_nodes.append(ET.Element(tag="node", attrib={"id": str(node_id), "x": str(node["x"]), "y": str(node["y"])}))

    xml_links = ET.Element("links")
    for link_id, link in links.iteritems():
        xml_links.append(ET.Element(tag="link", attrib={"id": str(link_id),
                                                "from": str(link["from"]),
                                                "length": str(link["length"]*1000),
                                                "oneway": "1",
                                                "permlanes": "10000.0",
                                                "capacity": "100000",
                                                "freespeed": str(link["speed"]),
                                                "modes": "pt",
                                                "to": str(link["to"])}))

    network.append(xml_nodes)
    network.append(xml_links)

    with open(os.path.join(folder, "network.xml"), 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8" ?>')
        f.write('<!DOCTYPE network SYSTEM "http://matsim.org/files/dtd/network_v1.dtd">\n')
        f.write(prettify(network))

    transit = ET.Element("transitSchedule")
    xml_stops = ET.Element("transitStops")
    for stop_id, stop in stop_facilities.iteritems():
        xml_stops.append(ET.Element(tag="stopFacility", attrib={"id": str(stop_id),
                                                                'x': str(stop["x"]),
                                                                'y': str(stop["y"]),
                                                                'linkRefId': str(stop["linkRefId"]),
                                                                'isBlocking': "false"}))

    transit.append(xml_stops)
    vehicles_ids = []
    for transit_line in schedule.keys():

        xml_transit_line = ET.Element("transitLine", attrib={'id': transit_line})
        for transit_route in schedule[transit_line].keys():
            xml_transit_route = ET.Element("transitRoute", attrib={'id': transit_route})
            _ = ET.Element("transportMode")
            _.text = "pt"
            xml_transit_route.append(_)
            route_profile = ET.Element("routeProfile")
            for stop in schedule[transit_line][transit_route]["routeProfile"]:
                route_profile.append(ET.Element("stop", attrib={"refId": str(stop["refId"]),
                                                                "arrivalOffset": stop["arrivalOffset"],
                                                                "departureOffset": stop["departureOffset"],
                                                                'awaitDeparture': "true"}))
            xml_transit_route.append(route_profile)

            route = ET.Element("route")
            for link in schedule[transit_line][transit_route]["route"]:
                route.append(ET.Element("link", attrib={"refId": link}))
            xml_transit_route.append(route)

            departures = ET.Element("departures")
            for i, d in enumerate(schedule[transit_line][transit_route]["departures"]):
                v_id = transit_line+"_"+transit_route+"_"+str(i)
                vehicles_ids.append(v_id)
                departures.append(ET.Element("departure", attrib={"id": str(i), 'departureTime': d, "vehicleRefId": str(v_id)}))
            xml_transit_route.append(departures)

            xml_transit_line.append(xml_transit_route)
        transit.append(xml_transit_line)

    with open(os.path.join(folder, "transitschedule.xml"), 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8" ?>')
        f.write('<!DOCTYPE transitSchedule SYSTEM "http://www.matsim.org/files/dtd/transitSchedule_v1.dtd">\n')
        f.write(prettify(transit))

    vehicles = ET.Element("vehicleDefinitions", attrib={"xmlns": "http://www.matsim.org/files/dtd",
                                                        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                                                        "xsi:schemaLocation": "http://www.matsim.org/files/dtd http://www.matsim.org/files/dtd/vehicleDefinitions_v1.0.xsd"})
    v_type = ET.Element("vehicleType", attrib={'id': "1"})
    description = ET.Element("description")
    description.text = "Small Train"
    v_type.append(description)

    capacity = ET.Element("capacity")
    capacity.append(ET.Element("seats", attrib={"persons": "10000"}))
    capacity.append(ET.Element("standingRoom", attrib={"persons": "10000"}))
    v_type.append(capacity)
    v_type.append(ET.Element("length", attrib={"meter": "10"}))
    v_type.append(ET.Element("maximumVelocity", attrib={"meterPerSecond": "99999.9"}))
    v_type.append(ET.Element("accessTime", attrib={"secondsPerPerson": "0.0"}))
    v_type.append(ET.Element("egressTime", attrib={"secondsPerPerson": "0.0"}))
    v_type.append(ET.Element("doorOperation", attrib={"mode": "serial"}))
    v_type.append(ET.Element("passengerCarEquivalents", attrib={"pce": "1.0"}))

    vehicles.append(v_type)

    for v_id in vehicles_ids:
        vehicles.append(ET.Element("vehicle", attrib={"id": v_id, "type": "1"}))

    with open(os.path.join(folder, "transitvehicle.xml"), 'w') as f:
        f.write(prettify(vehicles))


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    doc = xml.Document()

    declaration = doc.toxml()
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")[len(declaration):]


def export(v, folder, config):

    datas = export_supply_and_network(v, config=config)

    for line in ["007-D-15191", "003-D-15021", "003-D-15022"]:
        if line in datas["schedule"].keys():
            logging.getLogger(__name__).info("Delete line %s, Spitzkehre not yet supported" % line)
            del datas["schedule"][line]

    to_xml(datas, folder=folder, config=config)


if __name__ == "__main__":
    config = ConfigParser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
    config.read(config_path)

    import python_path
    python_path.load()
    import vipy.visum

    path = config.get("VisumVersions", "demo")
    v = vipy.visum.Visum()
    v.lade_version(path)

    set_projection(v, config)
    export(v, folder=r"D:\tmp", config=config)

