import gzip
import os
import subprocess
import time
import xml.etree.ElementTree as ET
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
import argparse
from string import Template


def config_maker(config_path, var1, var2):

    with open(config_path, "r") as f:
        data = Template(f.read())
        new_name = os.path.basename(config_path)[:-4]
        if var2 is None:
            new_name = new_name+"_%f" % var1

        else:
            new_name = new_name+"_%f_%f" % (var1, var2)

        new_data = data.substitute({"output_dir": "./output/"+new_name,
                                    "var1": str(var1),
                                    "var2": str(var2)})

        config_path = os.path.join(os.path.dirname(config_path), new_name+".xml")
        with open(config_path, "w") as g:
            g.write(new_data)

        return config_path


def work(var1, var2, cmd, config_path):
    path_dir = os.path.dirname(os.path.abspath(config_path))
    os.chdir(path_dir)
    print path_dir
    c = config_maker(config_path, var1, var2)
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
    parser.add_argument('-var1', type=float, help='list of type float. Occurrence of $var2 is replaces by this value ', nargs="+")
    parser.add_argument('-var2', type=float, help='list of type float. Occurrence of $var2 is replaces by this value ', nargs="+")
    parser.add_argument("-n", type=int)
    args = parser.parse_args()

    config_path = args.config
    cmd = args.cmd

    n = 5
    if args.n:
        n = int(args.n)

    tp = ThreadPool(n)

    vars1 = args.var1
    vars2 = [None]
    if args.vars2:
        vars2 = args.var2

    for var1 in vars1:
        for var2 in vars2:
            tp.apply_async(work, (var1, var2, cmd, config_path))

    tp.close()
    tp.join()
