import ConfigParser
import logging
import numpy as np
import os
import time

from put_supply import set_projection


def export(v, path):
    bezirke_dict = {}
    for b in v.netz.hole_bezirke():
        xs = b.com_objekt.AttValue(r"Concatenate:OrigConnectors\Node\XCoord").split(",")
        ys = b.com_objekt.AttValue(r"Concatenate:OrigConnectors\Node\YCoord").split(",")
        if len(xs) > 1:
            logging.getLogger(__name__).warn("%s has more than one OrigConnector (%s). I will take only the first one" % (b.name(), len(xs)))

        bezirke_dict[b.nummer()] = [xs[0], ys[0]]

    matrizen = v.nachfrage.hole_matrizen()
    make_pupulation(matrizen, bezirke_dict, path)


def export(v, path):
    v.visum_com.Net.SetAttValue("ConcatMaxLen", 2147483647.0)
    proj = u'PROJCS["CH1903_LV03",GEOGCS["GCS_CH1903",DATUM["D_CH1903",SPHEROID["Bessel_1841",6377397.155,299.1528128]],PRIMEM["Greenwich",0],UNIT["Degree",0.0174532925199432955]],PROJECTION["Hotine_Oblique_Mercator_Azimuth_Center"],PARAMETER["False_Easting",600000],PARAMETER["False_Northing",200000],PARAMETER["Scale_Factor",1],PARAMETER["Azimuth",90],PARAMETER["Longitude_Of_Center",7.439583333333333],PARAMETER["Latitude_Of_Center",46.95240555555556],UNIT["Meter",1]]'
    v.visum_com.Net.SetProjection(newProjection=proj, calculate=True)

    bezirke_dict = {}
    for b in v.netz.hole_bezirke():
        bezirke_dict[b.nummer()] = [b.com_objekt.AttValue("XCoord"), b.com_objekt.AttValue("YCoord")]

    matrizen = v.nachfrage.hole_matrizen()
    make_pupulation(matrizen, bezirke_dict, path)


def make_pupulation(matrizen, bezirke_dict, path):
    person_id = 1

    m = matrizen[0]
    xv, yv = np.meshgrid(m.mapping, m.mapping)

    quelle_v = yv.flatten()
    ziel_v = xv.flatten()

    with open(path, 'w') as f:
        f.write('<?xml version = "1.0" encoding = "utf-8"?>\n')
        f.write('<!DOCTYPE population SYSTEM "http://www.matsim.org/files/dtd/population_v5.dtd">\n')
        f.write('<population>\n')

        for m in matrizen:
            if m.nummer() == 200:
                continue
            print m.name()
            data = m.hole_data().flatten()
            indices = data >= 1.0

            end_time = time.strftime('%H:%M:%S', time.gmtime(m.nummer() * 10 * 60))
            end_time2 = "30:00:00" #time.strftime('%H:%M:%S', time.gmtime(30 * 60 * 60.0))

            for q, z, n_trips in zip(quelle_v[indices], ziel_v[indices], data[indices]):
                origin = bezirke_dict[q]
                destination = bezirke_dict[z]
                for n in range(int(n_trips)):
                    person_id += 1
                    f.write('<person id="%s">\n' % person_id)
                    f.write('<plan>\n')

                    f.write('<act type="home" x="%s" y="%s" end_time="%s"></act>\n' % (origin[0], origin[1], end_time))
                    f.write('<leg mode="pt"> </leg>')
                    f.write('<act type="work" x="%s" y="%s" end_time="%s"></act>\n' % (
                    destination[0], destination[1], end_time2))
                    # f.write('<leg mode="pt"> </leg>')
                    # f.write('<act type="home" x="%s" y="%s" end_time="%s">\n' % (origin[0], origin[1], "00:00:00"))

                    f.write('</plan>\n')
                    f.write('</person>\n')
        f.write('</population>\n')


if __name__ == "__main__":
    config = ConfigParser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
    config.read(config_path)

    import python_path
    python_path.load()
    import vipy.visum

    v = vipy.visum.Visum()
    v.lade_version(config.get("VisumVersions", "demo"))

    set_projection(v, config=config)
    export(v, r"D:\tmp\population.xml")

