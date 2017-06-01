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

        new_name = os.path.basename(config_path)[:-4]+"_%f" % value

        new_data = data.substitute({"output_dir": "./output/"+new_name, "pt_constant": str(value)})
        config_path = os.path.join(os.path.dirname(config_path), new_name+".xml")
        with open(config_path, "w") as g:
            g.write(new_data)

        return config_path


def work(i, cmd, config_path):
    path_dir = os.path.dirname(os.path.abspath(config_path))
    os.chdir(path_dir)
    print path_dir
    c = config_maker(config_path, i)
    cmd2 = cmd+" %s" % c
    print cmd2
    my_tool_subprocess = subprocess.Popen(cmd2,shell=True, stdout=subprocess.PIPE)

    while True:
        line = my_tool_subprocess.stdout.readline()
        if line != '':
            pass
        else:
            break


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('cmd', type=str, help='java cmd')
    parser.add_argument('config', type=str, help='config')
    parser.add_argument('list', type=float, help='config', nargs="+")
    parser.add_argument("-n", type=int)
    args = parser.parse_args()

    config_path = args.config
    cmd = args.cmd

    n = 5

    if args.n:
        n = int(args.n)

    tp = ThreadPool(n)
    for i in args.list:
        tp.apply_async(work, (i, cmd, config_path))

    tp.close()
    tp.join()
