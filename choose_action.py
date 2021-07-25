from gym_sgw.envs.enums.Enums import Actions, Terrains, MapObjects
from gym_sgw.envs.model.Constants import BASE_ENERGY, BAT_POWER, FIRE_DRAIN, PICK_UP_PERSON, NOT_PICK_UP_PERSON, RUN_INTO_PERSON
import heapq


def choose_action(observation):
    '''
    goal:
    go from current position -> nearest human -> hospital -> battery
    if cost is less than current energy, go to the hospital
    if cost is greater, go to the battery
    '''
    grid, status = observation
    print(status)
    # up, right, down, left
    di = [-1, 0, 1, 0]; dj = [0, 1, 0, -1]
    n = len(grid); m = len(grid[0])
    # dist[i][j][k][l][m] -> at pos (i, j) with orientation k, l represents with person or not, m represents been to hospital or not
    dist = [[[[[1000000 for _ in range(2)] for _ in range(2)] for _ in range(4)] for _ in range(m)] for _ in range(n)]
    pq = []
    initiali = status['player_location'][0]
    initialj = status['player_location'][1]
    initialor = status['player_orientation'].value
    energy_remaining = status['energy_remaining']
    initial_has_person = 1 if MapObjects.injured in grid[initiali][initialj].objects else 0
    initial_at_hospital = 1 if Terrains.hospital == grid[initiali][initialj].terrain else 0
    heapq.heappush(pq, (0, (initiali, initialj, initialor, initial_has_person, 0), Actions.none))
    dist[initiali][initialj][initialor][initial_has_person][0] = 0
    bestdist = 1000000
    bestdist_without_bat = 1000000
    bestact = Actions.quit
    bestact_without_bat = Actions.quit
    while len(pq) > 0:
        distance, loc, act = heapq.heappop(pq)
        i, j, ori, has_person, passed_hospital = loc
        if distance != dist[i][j][ori][has_person][passed_hospital]:
            continue
        if passed_hospital and MapObjects.battery in grid[i][j].objects:
            if distance < bestdist:
                bestdist = distance
                bestact = act
        if has_person and Terrains.hospital == grid[i][j].terrain:
            if distance < bestdist_without_bat:
                bestdist_without_bat = distance
                bestact_without_bat = act
           
        # forward
        nexti = i + di[ori]
        nextj = j + dj[ori]
        if grid[nexti][nextj].terrain not in [Terrains.none, Terrains.out_of_bounds, Terrains.wall]:
            next_has_person = 1 if MapObjects.injured in grid[nexti][nextj].objects or has_person else 0
            next_has_fire = 1 if Terrains.fire == grid[nexti][nextj].terrain else 0
            will_run_into = 1 if MapObjects.injured in grid[nexti][nextj].objects and has_person else 0
            next_is_hospital = 1 if (Terrains.hospital == grid[nexti][nextj].terrain and has_person) or passed_hospital else 0
            total_cost = BASE_ENERGY + next_has_fire * FIRE_DRAIN + (NOT_PICK_UP_PERSON if MapObjects.injured not in grid[nexti][nextj].objects else 0) + will_run_into * RUN_INTO_PERSON
            if distance - total_cost < dist[nexti][nextj][ori][next_has_person][next_is_hospital]:
                dist[nexti][nextj][ori][next_has_person][next_is_hospital] = distance - total_cost
                heapq.heappush(pq, (distance - total_cost, (nexti, nextj, ori, next_has_person, next_is_hospital), act if act != Actions.none else Actions.step_forward))
                #prev_action[nexti][nextj][ori][next_has_person] = Actions.step_forward
        # turn right or left
        curr_has_fire = 1 if Terrains.fire == grid[i][j].terrain else 0
        cost = BASE_ENERGY + curr_has_fire * FIRE_DRAIN
        for k in [-1, 1]:
            nextori = (ori + k + 4) % 4
            if distance - cost < dist[i][j][nextori][has_person][passed_hospital]:
                dist[i][j][nextori][has_person][passed_hospital] = distance - cost
                heapq.heappush(pq, (distance - cost, (i, j, nextori, has_person, passed_hospital), act if act != Actions.none else Actions.turn_left if k == -1 else Actions.turn_right))
    if bestdist <= energy_remaining + BAT_POWER:
        print('1')
        return bestact

    '''
    try to go from current to battery
    '''
    bestdist = 1000000
    bestact = Actions.quit
    dist = [[[1000000 for _ in range(4)] for _ in range(m)] for _ in range(n)]
    dist[initiali][initialj][initialor] = 0
    pq = []
    heapq.heappush(pq, (0, (initiali, initialj, initialor), Actions.none))
    while len(pq) > 0:
        distance, loc, act = heapq.heappop(pq)
        i, j, ori = loc
        if distance != dist[i][j][ori]:
            continue
        if MapObjects.battery in grid[i][j].objects:
            if distance < bestdist:
                bestdist = distance
                bestact = act
        # forward
        nexti = i + di[ori]
        nextj = j + dj[ori]
        if grid[nexti][nextj].terrain not in [Terrains.none, Terrains.out_of_bounds, Terrains.wall]:
            next_has_fire = 1 if Terrains.fire == grid[nexti][nextj].terrain else 0
            will_run_into = 1 if MapObjects.injured in grid[nexti][nextj].objects and has_person else 0
            total_cost = BASE_ENERGY + next_has_fire * FIRE_DRAIN + will_run_into * RUN_INTO_PERSON
            if distance - total_cost < dist[nexti][nextj][ori]:
                dist[nexti][nextj][ori] = distance - total_cost
                heapq.heappush(pq, (distance - total_cost, (nexti, nextj, ori), act if act != Actions.none else Actions.step_forward))
        # turn right or left
        curr_has_fire = 1 if Terrains.fire == grid[i][j].terrain else 0
        cost = BASE_ENERGY + curr_has_fire * FIRE_DRAIN
        for k in [-1, 1]:
            nextori = (ori + k + 4) % 4
            if distance - cost < dist[i][j][nextori]:
                dist[i][j][nextori] = distance - cost
                heapq.heappush(pq, (distance - cost, (i, j, nextori), act if act != Actions.none else Actions.turn_left if k == -1 else Actions.turn_right))
    if bestact == Actions.quit:
        print('2')
        return bestact_without_bat
    print('3')
    return bestact

