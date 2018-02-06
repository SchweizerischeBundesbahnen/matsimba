from collections import defaultdict
from VisumPy.helpers import GetMulti
import tempfile
import os

header = """$VISION
* Schweizerische Bundesbahnen AG Personenverkehr Bern 65
* 15.03.17
* Tabelle: Versionsblock
* 
$VERSION:VERSNR;FILETYPE;LANGUAGE;UNIT
10;Trans;DEU;KM

* 
* Tabelle: Strecken
$STRECKE:NR;VONKNOTNR;NACHKNOTNR;NAME;TYPNR;VSYSSET;T-OEVSYS(F);\n"""


def get_stops_to_link(path):
    i = 0
    previous_alighting = None

    hst_dict = {}

    with open(path) as f:
        for line in f:
            i += 1

            if i < 13:
                continue
            data = line.split(";")

            weg_index = int(data[0])
            teilweg_index = int(data[1])
            vonhstnr = int(data[2])
            nachhstnr = int(data[3])

            if teilweg_index > 1 and previous_alighting != vonhstnr:
                if previous_alighting not in hst_dict:
                    hst_dict[previous_alighting] = set()
                hst_dict[previous_alighting].add(vonhstnr)

            previous_alighting = nachhstnr
    return hst_dict


def get_stop_node(visum_com):
    StopNos = GetMulti(visum_com.Net.StopAreas, "StopNo")
    NodeNos = GetMulti(visum_com.Net.StopAreas, "NodeNo")
    stopToNode = {}
    for stopNo, nodeNo in zip(StopNos, NodeNos):
        stopToNode[int(stopNo)] = int(nodeNo)

    return stopToNode


def create(path, visum_com):
    already_done = []
    LinksNos = GetMulti(visum_com.Net.Links, "No")
    n = max(LinksNos)

    FromNos = GetMulti(visum_com.Net.Links, "FromNodeNo")
    ToNos = GetMulti(visum_com.Net.Links, "ToNodeNo")

    for von, nach in zip(FromNos, ToNos):
        already_done.append([von, nach])

    stop_node = get_stop_node(visum_com)
    hst_dict = get_stops_to_link(path=path)

    f = tempfile.NamedTemporaryFile(delete=False, suffix=".tra")
    f.write(header)

    iii = 0

    for _von in hst_dict:
        for _nach in hst_dict[_von]:
            von = stop_node[_von]
            nach = stop_node[_nach]
            d = [von, nach]
            if d not in already_done:
                iii += 1
                already_done.append([von, nach])
                f.write("%i;%i;%i;;99;F;0;\n" % (n + iii, von, nach))
                f.write("%i;%i;%i;;99;F;0;\n" % (n + iii, nach, von))
                already_done.append([nach, von])

    f.close()
    visum_com.ApplyModelTransferFile(f.name)
    os.unlink(f.name)


def get_filename(visum_com):
    for op in visum_com.Procedures.Operations.GetAll:
        if int(op.AttValue("OperationType")) == 69:
            return op.ReadSingleRowSurveyDataParameters.AttValue("FileName")


if __name__ == "__main__":
    path = get_filename(Visum)
    create(path, visum_com=Visum)
