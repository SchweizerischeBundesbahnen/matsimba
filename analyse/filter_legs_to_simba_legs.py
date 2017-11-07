


def get_legs_from_bahn_fq_binnenverkehr_journeys(df_legs, is_simba_line, stop_ids_perimeter, stop_ids_fq_perimeter, is_fqkalplus=False):
    """
    Filtert pt-legs aus MATSim oder Visum in folgenden Schritten:
    - es werden die pt-legs, welche auf Simba-Linien stattfinden behalten (mit is_simba_line)
    - von den verbleibenden pt-legs werden diejenigen behalten, wo der erste und letzte Halt im Perimeter liegt (mit stop_ids_perimeter)
    - von den verbleibenden pt-legs werden diejenigen behalten, die auf mindestens einem pt-leg im FQ-Perimeter liegen (mit stop_ids_fq_perimeter)
    :df_legs: pandas-DataFrame, in welchem die legs gemaess matsim_trips.txt eingelesen sind
    :is_simba_line: Funktion, welche zu einer Linien-Id zurueck gibt, ob die Linie im Simba-Perimeter ist oder nicht
    :stop_ids_perimeter: Liste der stop-id's, welche den Perimeter definieren. Der Binnverkehr wird daraus definiert.
    :stop_ids_fq_perimeter: Liste der stop-id's, welche im durch FQ erhobenen Perimeter liegen. Damit wird die zu Simba kompatible Abgrenzung vorgenommen.
    :is_fqkalplus: False, falls df_legs von MATSim kommt; True, falls df_legs von FQKal+, d.h. von Visum kommt
    :return: pandas-DataFrame, in welchem die legs gemaess Simba-Perimeter gefiltert sind
    """
    # Schritt 1: Legs filtern nach Simba-Linien. Im Folgenden werden pro Journey nur diese Legs betrachtet.
    if not is_fqkalplus:
        legs_simba = df_legs[df_legs.line.apply(is_simba_line)].sort(["journey_id", "start_time"])
    else:
        legs_simba = df_legs
    cols = legs_simba.columns
    # Schritt 2: Journeys filtern nach Binnenverkehr, d.h. erster Stop und letzter Stop im CNB-Perimeter
    if is_fqkalplus:
        first_leg = legs_simba[["journey_id", "TWEGIND"]].groupby("journey_id").min().reset_index()
    else:
        first_leg = legs_simba[["journey_id", "start_time"]].groupby("journey_id").min().reset_index()
    first_leg.columns = ["journey_id", "start_id"]
    if is_fqkalplus:
        first_leg = first_leg.merge(legs_simba, left_on=["journey_id", "start_id"], right_on=["journey_id", "TWEGIND"])
    else:
        first_leg = first_leg.merge(legs_simba, left_on=["journey_id", "start_id"], right_on=["journey_id", "start_time"])
    first_leg = first_leg[["journey_id", "start_id", "boarding_stop"]]
    first_leg.columns = ["journey_id", "start_id", "first_stop"]
    if is_fqkalplus:
        last_leg = legs_simba[["journey_id", "TWEGIND"]].groupby("journey_id").max().reset_index()
    else:
        last_leg = legs_simba[["journey_id", "end_time"]].groupby("journey_id").max().reset_index()
    last_leg.columns=["journey_id", "end_id"]
    if is_fqkalplus:
        last_leg = last_leg.merge(legs_simba, left_on=["journey_id", "end_id"], right_on=["journey_id", "TWEGIND"])
    else:
        last_leg = last_leg.merge(legs_simba, left_on=["journey_id", "end_id"], right_on=["journey_id", "end_time"])
    last_leg = last_leg[["journey_id", "end_id", "alighting_stop"]]
    last_leg.columns = ["journey_id", "end_id", "last_stop"]
    first_last_leg_info = first_leg.merge(last_leg, on="journey_id")
    first_last_leg_info["start_in_cnb"] = first_last_leg_info["first_stop"].isin(stop_ids_perimeter)
    first_last_leg_info["end_in_cnb"] = first_last_leg_info["last_stop"].isin(stop_ids_perimeter)
    legs_simba = legs_simba.merge(first_last_leg_info, on="journey_id", how="left")
    legs_simba_binnenverkehr = legs_simba[(legs_simba.start_in_cnb & legs_simba.end_in_cnb)]
    # Schritt 3: Herausfinden, welche dieser journeys auf mindestens einer Etappe im FQ-Perimeter, d.h. Normalspur-Perimeter liegen
    legs_simba_binnenverkehr["boarding_stop_ist_normalspur"] = legs_simba["boarding_stop"].isin(stop_ids_fq_perimeter)
    hat_fq_leg = (legs_simba_binnenverkehr[["journey_id", "boarding_stop_ist_normalspur"]]).groupby("journey_id").max()
    hat_fq_leg = hat_fq_leg.reset_index()
    legs_simba_binnenverkehr = legs_simba_binnenverkehr.merge(hat_fq_leg, on="journey_id", how="left")
    legs_simba_binnenverkehr_fq = legs_simba_binnenverkehr[legs_simba_binnenverkehr["boarding_stop_ist_normalspur_y"]]
    return legs_simba_binnenverkehr_fq[cols + ["first_stop", "last_stop"]]