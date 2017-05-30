import pandas as pd
from collections import defaultdict
import logging


def export_to_csv(v, path):
    v.apl.go_offline(mit_fzps=True, mit_fpfs=True, mit_fzpes=True, mit_fpfes=True,
                     params={"fzpes": ["PostLength", "PostRunTime", "LineRouteItem\\StopPoint\\No",
                                       'LineRouteItem\\OutLink\\FromNodeNo',
                                       'LineRouteItem\\OutLink\\ToNodeNo',
                                       'LineRouteItem\\StopPoint\\Xcoord',
                                       'Concatenate:UsedLineRouteItems\\OutLink\\FromNodeNo',
                                       'Concatenate:UsedLineRouteItems\\OutLink\\ToNodeNo',
                                       'LineRouteItem\\InLink\\ToNodeNo',
                                       'LineRouteItem\\NodeNo'], "fpfes": ["Vol(AP)"]})

    belastungen = {}
    schedule = defaultdict(list)
    for fzp in v.apl.hole_fahrzeitprofile():
        logging.getLogger(__name__).info("%s" % fzp)
        for fpf in fzp.hole_fahrplanfahrten():
            lr = "%i_%i_%i" % (
            fzp.nummer(), fpf.von_fahrzeitprofilelement_index(), fpf.bis_fahrzeitprofilelement_index())

            dep_key = (fzp.linename(), lr)
            n = len(schedule[dep_key])
            schedule[dep_key].append(1)

            for fpfe in fpf.hole_verlaufe():
                fzpe = fpfe.hole_fzpe()

                stop_id = int(fzpe.com_objekt.AttValue("LineRouteItem\StopPoint\No"))

                f_id = "%s_%s_%s_%s_%s" % (str(stop_id), fzp.nummer(), fpf.von_fahrzeitprofilelement_index(),
                                           fpf.bis_fahrzeitprofilelement_index(), fzpe.index())
                key = (fzp.linename(), lr, n, f_id)
                belastungen[key] = fpfe.com_objekt.AttValue("Vol(AP)")

    data = []
    for key in belastungen:
        data.append([key[0], key[1], key[2], key[3], belastungen[key]])

    data = pd.DataFrame(data)
    data.to_csv(path, header=False, index=False)