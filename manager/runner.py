import gzip
import os
import subprocess
import time
import xml.etree.ElementTree as ET
from multiprocessing import Pool
from multiprocessing.pool import TimeoutError
import argparse
from string import Template
import itertools
import signal


def config_maker(config_path, var1, var2):

    with open(config_path, "r") as f:
        data = Template(f.read())
        new_name = os.path.basename(config_path)[:-4]
        if var2 is None:
            new_name = new_name+"_%s" % var1

        else:
            new_name = new_name+"_%s_%s" % (var1, var2)

        new_data = data.substitute({"output_dir": "./output/"+new_name,
                                    "var1": str(var1),
                                    "var2": str(var2)})

        config_path = os.path.join(os.path.dirname(config_path), new_name+".xml")
        with open(config_path, "w") as g:
            g.write(new_data)

        return config_path


def work(a):
    var1 = a[0]
    var2 = a[1]
    cmd = a[2]
    config_path = a[3]
    path_dir = os.path.dirname(os.path.abspath(config_path))
    os.chdir(path_dir)
    print path_dir
    c = config_maker(config_path, var1, var2)
    cmd2 = cmd +" %s" % c
    print cmd2
    my_tool_subprocess = subprocess.Popen(cmd2, shell=True, stdout=subprocess.PIPE)

    print my_tool_subprocess.pid
    while True:
        line = my_tool_subprocess.stdout.readline()
        if line != '':
	    print line
            pass
        else:
            break


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('cmd', type=str, help='java cmd')
    parser.add_argument('config', type=str, help='config')
    parser.add_argument('-var1', type=str, help='list of type float. Occurrence of $var2 is replaces by this value ', nargs="+")
    parser.add_argument('-var2', type=str, help='list of type float. Occurrence of $var2 is replaces by this value ', nargs="+")
    parser.add_argument("-n", type=int)
    args = parser.parse_args()

    config_path = args.config
    cmd = args.cmd

    n = 5
    if args.n:
        n = int(args.n)


    tp = Pool(n)

    vars1 = args.var1
    vars2 = [None]
    if args.var2:
        vars2 = args.var2

    try:
        res = tp.map_async(work, list(itertools.product(vars1, vars2, [cmd], [config_path])))
        print "Waiting for results"
        res.get(60*60*24*30)
    except KeyboardInterrupt:
	print "KeyboardIntterupt"
	tp.terminate()

    except TimeoutError:
	print "timeout reached"
	tp.close()
	tp.terminate()
    else:
	tp.close()


    tp.join()
