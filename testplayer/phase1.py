import utilities
import battlecode as bc

PHASE1_WORKERS_WANTED = 10

def replicate_workers_phase(state):
    units = state.gc.units()
    factory_loc = None #TODO
    replicate_id = units[0].id
    for unit in units:
        #TODO check distance, set id accordingly

    while True:
        units = state.gc.units()
        index = 0
        while index < len(units):
            unit = units[index]
            if unit.id == replicate_id:
                if len(units) < PHASE1_WORKERS_WANTED:
                    pass