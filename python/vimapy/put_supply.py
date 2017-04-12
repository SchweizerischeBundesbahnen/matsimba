import xml.etree.ElementTree as ET
import time
import sys
sys.path.append(r"\\filer16l\PV160L\Project\VP.D1339\34_ViPy\Visum16\ViPy_V00_07")
import vipy.visum
import os
from xml.dom import minidom
from xml.etree import ElementTree
import xml.dom.minidom as xml
import ConfigParser


def map_id(_id, mapper):
    return mapper(_id)


def make_link(from_node_id, to_node_id, links, nodes, visum_com, mapper, speed=10):
    """

    :param from_node_id:
    :param to_node_id:
    :param links: dictionary with all links, key is link_id
    :param nodes: dictionary with all nodes, key is node_id
    :param visum_com: VISUM Com Object
    :param mapper: Map the ids to new values
    :return: link_id
    """
    from_node_id = int(float(from_node_id))
    to_node_id = int(float(to_node_id))

    link_id = "%i_%i" % (int(float(from_node_id)), int(float(to_node_id)))
    link_id = map_id(link_id, mapper)
    if link_id not in links:
        for _node_id in [from_node_id, to_node_id]:
            if _node_id not in nodes:
                _node = visum_com.Net.Nodes.ItemByKey(_node_id)
                nodes[_node_id] = {'x': _node.AttValue("xCoord"), 'y': _node.AttValue("yCoord")}

        if from_node_id == to_node_id:
            length = 0.0
        else:
            link = visum_com.Net.Links.ItemByKey(fromNode=from_node_id, toNode=to_node_id)
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

    for fzp in v.apl.hole_fahrzeitprofile():
        for fpf in fzp.hole_fahrplanfahrten():

            mapper = lambda _id: "%s_%s" % (str(_id), fzp.nummer())

            if fzp.linename() not in schedule:
                schedule[fzp.linename()] = {}

            key = "%i_%i_%i" % (fzp.nummer(), fpf.von_fahrzeitprofilelement_index(),
            fpf.bis_fahrzeitprofilelement_index())
            if key not in schedule[fzp.linename()]:

                route = []
                stops = []
                for fzpe in fzp.hole_verlaufe():
                    try:
                        speed = fzpe.com_objekt.AttValue("PostLength")*1000.0/fzpe.com_objekt.AttValue("PostRunTime")
                    except ZeroDivisionError:
                        speed = 1000

                    stop_id = int(fzpe.com_objekt.AttValue("LineRouteItem\StopPoint\No"))
                    stop_id = map_id(stop_id, mapper)

                    if stop_id not in stopFacilities:
                        from_node = fzpe.com_objekt.AttValue("LineRouteItem\OutLink\FromNodeNo")
                        to_node = fzpe.com_objekt.AttValue("LineRouteItem\OutLink\ToNodeNo")
                        if from_node is None:
                            to_node = fzpe.com_objekt.AttValue("LineRouteItem\InLink\ToNodeNo")
                            from_node = to_node

                        link_id = make_link(from_node, to_node, links=links, nodes=nodes,
                                            visum_com=v.visum_com, mapper=mapper, speed=speed)

                        stopFacilities[stop_id] = {'x': fzpe.com_objekt.AttValue("LineRouteItem\StopPoint\Xcoord"),
                                                   'y': fzpe.com_objekt.AttValue("LineRouteItem\StopPoint\Ycoord"),
                                                   'linkRefId': link_id,
                                                   'lineRefId': fzp.linename()}

                    from_node_ids = fzpe.com_objekt.AttValue("Concatenate:UsedLineRouteItems\OutLink\FromNodeNo").split(",")
                    to_node_ids = fzpe.com_objekt.AttValue("Concatenate:UsedLineRouteItems\OutLink\ToNodeNo").split(",")

                    t1 = time.strftime('%H:%M:%S', time.gmtime( fzpe.abfahrt() ))
                    t2 = time.strftime('%H:%M:%S', time.gmtime( fzpe.ankunft() ))
                    stops.append({'refId': stop_id, 'departureOffset': t1 , 'arrivalOffset': t2})
                    if from_node_ids != [""]:
                        for from_node_id, to_node_id in zip(from_node_ids, to_node_ids):
                            link_id = make_link(from_node_id, to_node_id, links=links, nodes=nodes,
                                                visum_com=v.visum_com, mapper=mapper, speed=speed)
                            route.append(link_id)
                    else:
                        link_id = make_link(from_node, to_node, links=links, nodes=nodes,
                                            visum_com=v.visum_com, mapper=mapper, speed=speed)
                        route.append(link_id)

                schedule[fzp.linename()][key] = {"departures": [],
                                                 "route": route,
                                                 "routeProfile": stops}
            t = time.strftime('%H:%M:%S', time.gmtime( fpf.abfahrt() ))
            schedule[fzp.linename()][key]["departures"].append(t)
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
                                                "permlanes": "1.0",
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
                                                                "departureOffset": stop["departureOffset"]}))
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

    del datas["schedule"]["007-D-15191"]
    del datas["schedule"]["003-D-15021"]
    del datas["schedule"]["003-D-15022"]

    to_xml(datas, folder=folder, config=config)


if __name__ == "__main__":
    config = ConfigParser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
    config.read(config_path)

    path = config.get("VisumVersions", "demo")
    v = vipy.visum.Visum()
    v.lade_version(path)

    set_projection(v, config)
    export(v, folder=r"D:\tmp", config=config)

