import pickle
import numpy as np
import scipy.integrate as integrate
from scipy.interpolate import interp1d
import time

def get_inv_CDF(tg):
    times = np.linspace(0, 143, num=144)
    my_pdf = interp1d(times, tg/np.sum(tg))
    CDF = lambda y1, y2: integrate.quad(lambda x: my_pdf(x), y1, y2)[0]
    a = [CDF(t1, t2) for t1, t2 in zip(times[:-1], times[1:])]
    a = [0]+list(np.cumsum(a))
    f = interp1d(a, times)
    return f


def get_tg(matrices, quelle_nummer, ziel_nummer):
    tg = []
    for i in range(144):
        tg.append(matrices[str(i+1)].get_element_with_mapping(str(quelle_nummer), str(ziel_nummer)))
    return tg


def get_tg_dict(omx):
    matrices = vipy.nachfrage.nachfrage.get_all_matrices(omx, import_mapping=True)

    m = matrices['1']
    tg_dict = {}
    n = len(m.mapping)
    for i in range(n):
        for j in range(n):
            if matrices["200"].hole_data()[i, j]>=1:
                q = m.mapping[i]
                z = m.mapping[j]
                tg_dict[q+"_"+z] = get_tg(matrices, q, z)

    return tg_dict


def load_tg(bezirke_dict, tg_dict):
    tg_dict2 = {}
    for a in bezirke_dict.keys():
        tg_dict2[a] = {}
        for b in bezirke_dict.keys():
            key = str(a) + "_" + str(b)
            if key in tg_dict:
                tg_dict2[a][b] = tg_dict[key]
            else:
                tg_dict2[a][b] = [0] * 144
    return tg_dict2


def make_pupulation(tg_dict, bezirke_dict, path):
    berzirke_nummern = bezirke_dict.keys()
    n = len(berzirke_nummern)
    n_generated = 0
    person_id = 0
    with open(path, 'w') as f:
        f.write('<?xml version = "1.0" encoding = "utf-8"?>\n')
        f.write('<!DOCTYPE population SYSTEM "http://www.matsim.org/files/dtd/population_v5.dtd">\n')
        f.write('<population>\n')

        for i in range(n):
            for j in range(n - i):
                q = berzirke_nummern[i]
                z = berzirke_nummern[j]
                print q, z
                tg1 = tg_dict[q][z]
                tg2 = tg_dict[z][q]

                ff = get_inv_CDF(tg1)
                gg = get_inv_CDF(tg2)

                x_quelle = bezirke_dict[q][0]
                y_quelle = bezirke_dict[q][1]
                x_ziel = bezirke_dict[z][0]
                y_ziel = bezirke_dict[z][1]

                n_trips = min(int(np.sum(tg1)), int(np.sum(tg2)))
                for k in range(n_trips):

                    person_id += 1
                    f.write('<person id="%s">\n' % person_id)
                    f.write('<plan>\n')

                    x = np.random.uniform(0 + 0.05, 1 - 0.05)
                    end_time_hin = ff(x)*10*60

                    x = np.random.uniform(0 + 0.05, 1 - 0.05)
                    end_time_ruck = gg(x)*10*60

                    origin = [x_quelle, y_quelle]
                    destination = [x_ziel, y_ziel]

                    if end_time_ruck < end_time_hin:
                        tmp = destination
                        destination = origin
                        origin = tmp

                        tmp = end_time_ruck
                        end_time_ruck = end_time_hin
                        end_time_hin = tmp

                    end_time_hin = time.strftime('%H:%M:%S', time.gmtime( end_time_hin))
                    end_time_ruck = time.strftime('%H:%M:%S', time.gmtime( end_time_ruck))

                    f.write('<act type="home" x="%s" y="%s" end_time="%s">\n' % (origin[0], origin[1], end_time_hin))
                    f.write('<leg mode="pt"> </leg>')
                    f.write('<act type="work" x="%s" y="%s" end_time="%s">\n' % (destination[0], destination[1], end_time_ruck))
                    f.write('<leg mode="pt"> </leg>')
                    f.write('<act type="home" x="%s" y="%s" end_time="%s">\n' % (origin[0], origin[1], "00:00:00"))

                    n_generated += 2
                    f.write('</plan>\n')
                    f.write('</person">\n')

if __name__ == "__main__":
    tg_dict = pickle.load(open(r"\\V00925\Simba\20_Modelle\80_MatSim\10_Testdaten\NachfrageMatrizen\tg.p", "rb"))
    bezirke_dict = pickle.load(open(r"\\V00925\Simba\20_Modelle\80_MatSim\10_Testdaten\NachfrageMatrizen\bezirke.p", "rb"))

    tg_dict = load_tg(bezirke_dict, tg_dict)

    make_pupulation(tg_dict, bezirke_dict, path=r"D:/tmp/population.xml")
