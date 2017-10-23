import logging
import sys
import os.path
import argparse
from StringIO import StringIO
from lxml import etree

import xml.dom.minidom as xml
from xml.dom import minidom
import pandas as pd


def read_xlsx(scenario):

    xlsx = pd.ExcelFile(scenario)

    # parse the main sheet
    main_sheet = xlsx.parse(0, header=1)

    # remove unnecessary comment rows/ columns
    main_sheet = main_sheet.drop(['Unnamed: 1'], axis=1)
    main_sheet = main_sheet.drop(main_sheet.index[[0]])

    # i detects the number of mode dependent utilities
    i = 0
    while pd.notnull(main_sheet.iloc[i]["MATSim Param Name"]):
        i = i + 1
    nr_dep_utils = i
    i = i + 1

    # construct dataframe containing all mode-independent utilities
    general_params = pd.DataFrame(columns=['MATSim Param Name', 'utility'])
    while pd.notnull(main_sheet.iloc[i]["MATSim Param Name"]):
        general_params = general_params.append({"MATSim Param Name": main_sheet.iloc[i]["MATSim Param Name"],
                                                "utility": main_sheet.iloc[i]["general"]}, ignore_index=True)
        i = i + 1
    # in a first step, there is no subpopulation
    general_params = general_params.append({"MATSim Param Name": "subpopulation", "utility": "null"}, ignore_index=True)
    general_params = general_params.set_index("MATSim Param Name")
    general_params['utility'] = general_params['utility'].astype(str)

    # construct dataframe containing all mode-dependent utilitites
    mode_params = pd.DataFrame()
    p = 2
    while pd.notnull(main_sheet[main_sheet.columns[p]].iloc[0]):
        mode_params[main_sheet[main_sheet.columns[p]].name] = main_sheet.iloc[0:nr_dep_utils][main_sheet.columns[p]]
        mode_params[main_sheet[main_sheet.columns[p]].name] = mode_params[
            main_sheet[main_sheet.columns[p]].name].astype(str)
        p = p + 1
    mode_params = mode_params.set_index(main_sheet.iloc[0:nr_dep_utils][main_sheet.columns[0]])

    return general_params, mode_params


def modify_config(config, gp, mp):

    config = config
    parser = etree.XMLParser(remove_blank_text=True)

    if len(config) == 0:
        logging.warn("No config.xml found")

    with open(config, 'rb') as f:
        config_content = f.read()
        tree = etree.parse(StringIO(config_content), parser)
        encoding = tree.docinfo.encoding

        for sp in tree.findall('//module[@name="planCalcScore"]/parameterset[@type="scoringParameters"]/param'):
            sp.getparent().remove(sp)

        for mopa in tree.findall(
                '//module[@name="planCalcScore"]/parameterset[@type="scoringParameters"]/parameterset[@type="modeParams"]'):
            mopa.getparent().remove(mopa)

        scoring_param = tree.find('//module[@name="planCalcScore"]/parameterset[@type="scoringParameters"]')
        for i in range(len(mp.columns)):
            mode_elem = etree.Element('parameterset', type="modeParams")
            etree.SubElement(mode_elem, "param", name="mode", value=mp[mp.columns[i]].name)
            for j in range(len(mp)):
                etree.SubElement(mode_elem, "param", name=mp.index[j],
                                 value=mp[mp.columns[i]].iloc[j])
            scoring_param.insert(i, mode_elem)

        for i in range(len(gp)):
            scoring_param.insert(i, etree.Element('param', name=gp.index[i],
                                                  value=gp['utility'].iloc[i]))

        return tree


def write_config(new_config, config_out):


    if os.path.isfile(config_out):
        logging.error(" The config already exists. Try new name or delete the existing config.")
    else:
        with open(config_out, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8" ?>')
            f.write(prettify(new_config))


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    doc = xml.Document()

    declaration = doc.toxml()
    rough_string = etree.tostring(elem)
    reparsed = minidom.parseString(rough_string)

    return reparsed.toprettyxml(indent="  ")[len(declaration):]


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Convert excel to config.xml.')
    parser.add_argument('excel', type=str, help='name of excel file')
    parser.add_argument('config_in', type=str, help='default config')
    parser.add_argument('config_out', type=str, help='converted config')
    args = parser.parse_args()

    SCENARIO_NAME = args.excel
    CONFIG_IN = args.config_in
    CONFIG_OUT = args.config_out

    gp, mp = read_xlsx(SCENARIO_NAME)

    new_config = modify_config(CONFIG_IN, gp, mp)

    write_config(new_config, CONFIG_OUT)

