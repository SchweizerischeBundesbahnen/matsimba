import csv


def get_stop_id(stop_id, fzp_nummer, fpf_von_index, fpf_bis_index, fzpe_index):
    return "%i_%s_%i_%i_%i" % (stop_id, fzp_nummer, fpf_von_index, fpf_bis_index, fzpe_index)


def get_route_id(fzp_nummer, fpf_von_index, fpf_bis_index):
    return "%i_%i_%i" % (fzp_nummer, fpf_von_index, fpf_bis_index)


def get_link_id_for_stop(node_id, fzp_nummer, fpf_von_index, fpf_bis_index, fzpe_index):
    return "%i_%i_%s_%i_%i_%i" % (
    int(float(node_id)), int(float(node_id)), fzp_nummer, fpf_von_index, fpf_bis_index, fzpe_index)


def export_to_csv(v, path):

    put_connections = v.visum_com.Lists.CreatePuTPathLegList
    put_connections.SetObjects(0, "X", 0, ListFormat=2, PuTOnly=False)
    put_connections.Show()
    put_connections.AddColumn("PathIndex")
    put_connections.AddColumn("PathLegIndex")
    put_connections.AddColumn("FromStopPointNo")
    put_connections.AddColumn("ToStopPointNo")
    put_connections.AddColumn("LineName")
    put_connections.AddColumn("StartVehJourneyItem\VehJourney\FromTProfItemIndex")
    put_connections.AddColumn("StartVehJourneyItem\VehJourney\ToTProfItemIndex")
    put_connections.AddColumn("TimeProfile\ID")
    put_connections.AddColumn("Time", Format=3)
    put_connections.AddColumn("WaitTime", Format=3)
    put_connections.AddColumn("StartVehJourneyItem\TimeProfileItem\Index")
    put_connections.AddColumn("EndVehJourneyItem\TimeProfileItem\Index")
    put_connections.AddColumn("StartVehJourneyItem\TimeProfileItem\LineRouteItem\StopPoint\Node\No")
    put_connections.AddColumn("EndVehJourneyItem\TimeProfileItem\LineRouteItem\StopPoint\Node\No")
    put_connections.AddColumn("Dep", Format=3)
    put_connections.AddColumn("Arr", Format=3)

    chunk = 200
    n = put_connections.NumActiveElements
    print n
    data = []
    with open(path, 'wb') as csvfile:
        conwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        for i in range(n / chunk + 1):
            for d in put_connections.SaveToArray(i * chunk + 1, (i + 1) * chunk):
                from_stop_id = d[2]
                to_stop_id = d[3]
                linename = d[4]
                fzp_nummer = d[7]
                von_index = d[5]
                nach_index = d[6]
                fzpe_index_start = d[10]
                fzpe_index_end = d[11]
                time = d[8]
                wait_time = d[9]
                start_node = d[12]
                end_node = d[13]

                if linename != "":

                    start_stop = get_stop_id(from_stop_id, fzp_nummer, von_index, nach_index, fzpe_index_start)
                    end_stop = get_stop_id(to_stop_id, fzp_nummer, von_index, nach_index, fzpe_index_end)

                    start_link = get_link_id_for_stop(start_node, fzp_nummer, von_index, nach_index, fzpe_index_start)
                    end_link = get_link_id_for_stop(end_node, fzp_nummer, von_index, nach_index, fzpe_index_end)

                    route = get_route_id(fzp_nummer, von_index, nach_index)

                    conwriter.writerow(
                        [int(d[0]), int(d[1]), start_stop, end_stop, start_link, end_link, linename, route, time, wait_time, int(d[14]), int(d[15])])
                else:
                    conwriter.writerow([int(d[0]), int(d[1]), "", "", "", "", "", "", int(time), int(time), int(d[14]), int(d[15])])

