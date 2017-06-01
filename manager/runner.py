import gzip
import os
import subprocess
import time
import xml.etree.ElementTree as ET
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
import argparse
from string import Template


def config_maker(config_path, value):

    with open(config_path, "r") as f:
        data = Template(f.read())

        new_name = os.path.basename(config_path)[:-4]+"_%i" % value

        new_data = data.substitute({"output_dir": "./output/"+new_name, "pt_constant": str(value)})
        config_path = os.path.join(os.path.dirname(config_path), new_name+".xml")
        with open(config_path, "w") as g:
            g.write(new_data)

        return config_path


def work(i, cmd, config_path):

    c = config_maker(config_path, i)
    cmd2 = cmd+" %s" % c
    print cmd2
    os.chdir(os.path.dirname(path))
    my_tool_subprocess = subprocess.Popen(cmd2,shell=True,  stderr=STDOUT, stdout=subprocess.PIPE)

    while True:
        line = my_tool_subprocess.stdout.readline()
        if line != '':
            pass #print line.rstrip()
        else:
            break


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('cmd', type=str, help='java cmd')
    parser.add_argument('config', type=str, help='config')
    args = parser.parse_args()

    config_path = args.config
    cmd = args.cmd

    tp = ThreadPool(5)
    for i in [1, 2]:
        tp.apply_async(work, (i,cmd, config_path))

    tp.close()
    tp.join()