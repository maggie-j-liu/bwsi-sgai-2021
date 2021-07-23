from gym_sgw.envs.enums.Enums import Actions, Terrains, MapObjects
from gym_sgw.envs.model.Constants import BASE_ENERGY, BAT_POWER, FIRE_DRAIN, PICK_UP_PERSON, NOT_PICK_UP_PERSON, RUN_INTO_PERSON
import heapq
import copy

def choose_action(observation):
    original_grid, status = observation
    print(status)
    # up, right, down, left
    di = [-1, 0, 1, 0]; dj = [0, 1, 0, -1]
    n = len(original_grid); m = len(original_grid[0])
    # dist[i][j][k][l] -> at pos (i, j) with orientation k, l represents with person or not
    dist = [[[[1000000 for _ in range(2)] for _ in range(4)] for _ in range(m)] for _ in range(n)]
    pq = []
    initiali = status['player_location'][0]
    initialj = status['player_location'][1]
    initialor = status['player_orientation'].value
    initial_has_person = 1 if MapObjects.injured in original_grid[initiali][initialj].objects else 0
    heapq.heappush(pq, (0, (initiali, initialj, initialor, initial_has_person), Actions.none, original_grid))
    dist[initiali][initialj][initialor][initial_has_person] = 0
    bestdist = 1000000
    bestact = Actions.quit
    while len(pq) > 0:
        distance, loc, act, grid = heapq.heappop(pq)
        i, j, ori, has_person = loc
        if distance != dist[i][j][ori][has_person]:
            continue
        if has_person and Terrains.hospital == grid[i][j].terrain:
            if distance < bestdist:
                bestdist = distance
                bestact = act

        # forward
        nexti = i + di[ori]
        nextj = j + dj[ori]
        if grid[nexti][nextj].terrain not in [Terrains.none, Terrains.out_of_bounds, Terrains.wall]:
            next_has_person = 1 if MapObjects.injured in grid[nexti][nextj].objects or has_person else 0
            next_has_fire = 1 if Terrains.fire == grid[nexti][nextj].terrain else 0
            next_has_bat = 1 if MapObjects.battery in grid[nexti][nextj].objects else 0
            will_run_into = 1 if MapObjects.injured in grid[nexti][nextj].objects and has_person else 0
            total_cost = BASE_ENERGY + next_has_bat * BAT_POWER + next_has_fire * FIRE_DRAIN + (PICK_UP_PERSON if MapObjects.injured in grid[nexti][nextj].objects else NOT_PICK_UP_PERSON) + will_run_into * RUN_INTO_PERSON
            if distance - total_cost < dist[nexti][nextj][ori][next_has_person]:
                dist[nexti][nextj][ori][next_has_person] = distance - total_cost
                newgrid = copy.deepcopy(grid)
                if next_has_bat:
                    newgrid[nexti][nextj].objects.remove(MapObjects.battery)
                if MapObjects.injured in grid[nexti][nextj].objects:
                    newgrid[nexti][nextj].objects.remove(MapObjects.injured)
                heapq.heappush(pq, (distance - total_cost, (nexti, nextj, ori, next_has_person), act if act != Actions.none else Actions.step_forward, newgrid))
                #prev_action[nexti][nextj][ori][next_has_person] = Actions.step_forward
        # turn right or left
        curr_has_fire = 1 if Terrains.fire == grid[i][j].terrain else 0
        cost = BASE_ENERGY + curr_has_fire * FIRE_DRAIN
        for k in [-1, 1]:
            nextori = (ori + k + 4) % 4
            if distance - cost < dist[i][j][nextori][has_person]:
                dist[i][j][nextori][has_person] = distance - cost
                heapq.heappush(pq, (distance - cost, (i, j, nextori, has_person), act if act != Actions.none else Actions.turn_left if k == -1 else Actions.turn_right, grid))
    return bestact
