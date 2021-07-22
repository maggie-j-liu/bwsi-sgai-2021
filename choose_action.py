from gym_sgw.envs.enums.Enums import Actions, Terrains, MapObjects
from collections import deque
from gym_sgw.envs.model.Constants import BASE_ENERGY, BAT_POWER, FIRE_DRAIN
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
    prev_action = [[[[Actions.none for _ in range(2)] for _ in range(4)] for _ in range(m)] for _ in range(n)]
    q = deque()
    pq = []
    in_queue = [[[[False for _ in range(2)] for _ in range(4)] for _ in range(m)] for _ in range(n)]
    initiali = status['player_location'][0]
    initialj = status['player_location'][1]
    initialor = status['player_orientation'].value
    initial_has_person = 1 if MapObjects.injured in original_grid[initiali][initialj].objects else 0
    q.append((original_grid, (initiali, initialj, initialor, initial_has_person)))
    heapq.heappush(pq, (0, (initiali, initialj, initialor, initial_has_person), Actions.none, original_grid))
    dist[initiali][initialj][initialor][initial_has_person] = 0
    in_queue[initiali][initialj][initialor][initial_has_person] = True
    besti, bestj, bestori, bestdist = 0, 0, 0, 1000000
    q_count = 1
    bestact = Actions.none
    while len(pq) > 0:
        distance, loc, act, grid = heapq.heappop(pq)
        i, j, ori, has_person = loc
        if distance != dist[i][j][ori][has_person]:
            continue
        if has_person and Terrains.hospital == grid[i][j].terrain:
            if distance < bestdist:
                bestdist = distance
                besti = i
                bestj = j
                bestori = ori
                bestact = act

        # forward
        nexti = i + di[ori]
        nextj = j + dj[ori]
        if grid[nexti][nextj].terrain not in [Terrains.none, Terrains.out_of_bounds, Terrains.wall]:
            next_has_person = 1 if MapObjects.injured in grid[nexti][nextj].objects or has_person else 0
            next_has_fire = 1 if Terrains.fire == grid[nexti][nextj].terrain else 0
            next_has_bat = 1 if MapObjects.battery in grid[nexti][nextj].objects else 0
            total_cost = BASE_ENERGY + next_has_bat * BAT_POWER + next_has_fire * FIRE_DRAIN + (5 if MapObjects.injured in grid[nexti][nextj].objects else -5)
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
                #prev_action[i][j][nextori][has_person] = Actions.turn_left if k == -1 else Actions.turn_right
    return bestact
    # spfa
    '''
    while q_count > 0:
        grid, info = q.popleft()
        i, j, ori, has_person = info
        in_queue[i][j][ori][has_person] = False
        q_count -= 1
        # go forward
        nexti = i + di[ori]
        nextj = j + dj[ori]
        if grid[nexti][nextj].terrain not in [Terrains.none, Terrains.out_of_bounds, Terrains.wall]:
            if MapObjects.injured not in grid[nexti][nextj].objects or has_person == 0:
                next_has_person = 1 if MapObjects.injured in grid[nexti][nextj].objects or has_person else 0
                next_has_fire = 1 if Terrains.fire == grid[nexti][nextj].terrain else 0
                next_has_bat = 1 if MapObjects.battery in grid[nexti][nextj].objects else 0
                total_cost = BASE_ENERGY + next_has_bat * BAT_POWER + next_has_fire * FIRE_DRAIN
                if dist[i][j][ori][has_person] - total_cost < dist[nexti][nextj][ori][next_has_person]:
                    dist[nexti][nextj][ori][next_has_person] = dist[i][j][ori][has_person] - total_cost
                    prev_action[nexti][nextj][ori][next_has_person] = Actions.step_forward

                    if next_has_bat:
                        print(grid[nexti][nextj].objects)
                        grid[nexti][nextj].objects.remove(MapObjects.battery)
                        print(grid[nexti][nextj].objects)

                    q.append((grid, (nexti, nextj, ori, next_has_person)))
                    in_queue[nexti][nextj][ori][next_has_person] = True
                    q_count += 1
                
        # turn left or right
        curr_has_fire = 1 if Terrains.fire == grid[i][j].terrain else 0
        cost = BASE_ENERGY + curr_has_fire * FIRE_DRAIN
        for k in [-1, 1]:
            nextori = (ori + k + 4) % 4
            if dist[i][j][ori][has_person] - cost < dist[i][j][nextori][has_person]:
                dist[i][j][nextori][has_person] = dist[i][j][ori][has_person] - cost
                prev_action[i][j][nextori][has_person] = Actions.turn_left if k == -1 else Actions.turn_right
                q.append((grid, (i, j, nextori, has_person)))
                in_queue[i][j][nextori][has_person] = True
                q_count += 1

    besti, bestj, bestori, bestdist = 0, 0, 0, 1000000
    for i in range(n):
        for j in range(m):
            if Terrains.hospital == original_grid[i][j].terrain:
                for ori in range(4):
                    if dist[i][j][ori][1] < bestdist:
                        bestdist = dist[i][j][ori][1]
                        besti = i; bestj = j; bestori = ori
    '''
    '''
    curri, currj, currori = besti, bestj, bestori
    curr_has_person = 1
    last_action = None
    seen_a_person = False
    while curri != initiali or currj != initialj or currori != initialor:
        if MapObjects.injured in original_grid[curri][currj].objects:
            seen_a_person = True
        elif seen_a_person:
            curr_has_person = 0
        action_taken = prev_action[curri][currj][currori][curr_has_person]
        last_action = action_taken
        if action_taken == Actions.step_forward:
            curri -= di[currori]
            currj -= dj[currori]
        elif action_taken == Actions.turn_left:
            currori = (currori + 1) % 4
        elif action_taken == Actions.turn_right:
            currori = (currori - 1 + 4) % 4
        else:
            print(action_taken)
            raise RuntimeError('rip')
    return last_action
    '''
