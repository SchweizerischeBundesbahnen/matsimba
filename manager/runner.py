import gzip
import os
import subprocess
import time
import xml.etree.ElementTree as ET
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool

config_path = r"config.xml"
path = r"z:\20_Modelle\80_MatSim\40_ModellCH\03_StLeo"

cmd = r'java -cp "Z:\20_Modelle\80_MatSim\03_Releases\matsim-0.8.1\matsim-0.8.1.jar;' \
      r'D:\git\matsim\contribs\travelsummary\target\travelsummary-0.8.0.jar;' \
      r'D:\git\matsim\playgrounds\sbb\target\sbb-0.8.0.jar" ' \
      r'playground.sbb.RunSBB'


def config_maker(config_path, value):

        new_name = os.path.basename(config_path)[:-4]+"_%i" % value

        tree = ET.parse(config_path)
        root = tree.getroot()
        for a in root.findall("module"):

            if a.attrib["name"] == "controler":
                for b in a:
                    if "name" in b.attrib and b.attrib["name"] == "outputDirectory":

                        b.attrib["value"] = "./output/"+new_name

            if a.attrib["name"] == "planCalcScore":
                for b in a:
                    if "type" in b.attrib and b.attrib["type"] == "scoringParameters":
                        for c in b:
                            if "type" in c.attrib and c.attrib["type"] == "modeParams":
                                change = False

                                for d in c:
                                    if d.attrib["name"] == "mode" and d.attrib["value"] == "pt":
                                        change = True
                                if change:
                                    for d in c:
                                        if d.attrib["name"] == "constant":
                                            d.attrib["value"] = str(value)
        config_path = os.path.join(os.path.dirname(config_path), new_name+".xml")
        with open(config_path, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8" ?>')
            f.write('<!DOCTYPE config SYSTEM "http://www.matsim.org/files/dtd/config_v2.dtd">\n')
            f.write(ET.tostring(root, 'utf-8'))
        return config_path


def work(i, cmd):

    c = config_maker(os.path.join(path, config_path), i)
    cmd2 = cmd+" %s" % c
    print cmd2
    os.chdir(path)
    my_tool_subprocess = subprocess.Popen(cmd2,shell=True, stdout=subprocess.PIPE)

    while True:
        line = my_tool_subprocess.stdout.readline()
        if line != '':
            pass #print line.rstrip()
        else:
            break


if __name__ == '__main__':
    tp = ThreadPool(5)
    for i in [1, 2]:
        tp.apply_async(work, (i,cmd))

    tp.close()
    tp.join()