
def get_id_lineroute(from_tp_index, to_tp_index):
    return "%i-%i" % (from_tp_index, to_tp_index)


def get_id_line(linename, lineroutename, direction, timeprofilename):
    return "%s_%s_%s_[%s]" % (linename, lineroutename,timeprofilename, direction)


def get_id_link(fzp_id, from_node_id, to_node_id):
    return "%s-%s_[%i]" % (from_node_id, to_node_id, int(fzp_id))


def get_id_node(no, code):
    return "%i_%s" % (int(no), code)


def get_id_stop(fzp_id, no, code):
    return "%i_%s_[%i]" % (int(no), code, int(fzp_id))
