from gym_sgw.envs.enums.Enums import Actions, Terrains, MapObjects
import heapq
from collections import deque

def choose_action(observation):
    grid, status = observation
    print(status)
    i, j = status['player_location']
    # up, right, down, left
    di = [-1, 0, 1, 0]; dj = [0, 1, 0, -1]
    n = len(grid); m = len(grid[0])
    # dist[i][j][k][l] -> at pos (i, j) with orientation k, l represents with person or not
    dist = [[[[1000000 for _ in range(2)] for _ in range(4)] for _ in range(m)] for _ in range(n)]
    #prev_action_code = [[[Actions.none.value for _ in range(4)] for _ in range(m)] for _ in range(n)]
    prev_action = [[[[Actions.none for _ in range(2)] for _ in range(4)] for _ in range(m)] for _ in range(n)]
    q = deque()
    in_queue = [[[[False for _ in range(2)] for _ in range(4)] for _ in range(m)] for _ in range(n)]
    initiali = status['player_location'][0]
    initialj = status['player_location'][1]
    initialor = status['player_orientation'].value
    #heapq.heappush(q, (0, (initiali, initialj, initialor)))
    initial_has_person = 1 if MapObjects.injured in grid[initiali][initialj].objects else 0
    q.append((initiali, initialj, initialor, initial_has_person))
    dist[initiali][initialj][initialor][initial_has_person] = 0
    in_queue[initiali][initialj][initialor][initial_has_person] = True
    q_count = 1
    #can_break = True
    # bellman ford - could be optimized but 😶
    while q_count > 0:
        i, j, ori, has_person = q.popleft()
        in_queue[i][j][ori][has_person] = False
        q_count -= 1
        # go forward
        nexti = i + di[ori]
        nextj = j + dj[ori]
        if grid[nexti][nextj].terrain not in [Terrains.none, Terrains.out_of_bounds, Terrains.wall]:
            next_has_person = 1 if MapObjects.injured in grid[nexti][nextj].objects or has_person else 0
            if dist[i][j][ori][has_person] + 1 < dist[nexti][nextj][ori][next_has_person]:
                dist[nexti][nextj][ori][next_has_person] = dist[i][j][ori][has_person] + 1
                prev_action[nexti][nextj][ori][next_has_person] = Actions.step_forward
                q.append((nexti, nextj, ori, next_has_person))
                in_queue[nexti][nextj][ori][next_has_person] = True
                q_count += 1
        # turn left or right
        for k in [-1, 1]:
            nextori = (ori + k + 4) % 4
            if dist[i][j][ori][has_person] + 1 < dist[i][j][nextori][has_person]:
                dist[i][j][nextori][has_person] = dist[i][j][ori][has_person] + 1
                prev_action[i][j][nextori][has_person] = Actions.turn_left if k == -1 else Actions.turn_right
                q.append((i, j, nextori, has_person))
                in_queue[i][j][nextori][has_person] = True
                q_count += 1
    '''
    for _ in range(n * m * 4 * 2):
        for i in range(n):
            for j in range(m):
                if grid[i][j].terrain in [Terrains.none, Terrains.out_of_bounds, Terrains.wall]:
                    continue
                for ori in range(4):
                    for has_person in range(2):
                        # go forward
                        nexti = i + di[ori]
                        nextj = j + dj[ori]
                        if grid[nexti][nextj].terrain not in [Terrains.none, Terrains.out_of_bounds, Terrains.wall]:
                            next_has_person = 1 if MapObjects.injured in grid[nexti][nextj].objects or has_person else 0
                            if dist[i][j][ori][has_person] + 1 < dist[nexti][nextj][ori][next_has_person]:
                                dist[nexti][nextj][ori][next_has_person] = dist[i][j][ori][has_person] + 1
                                prev_action[nexti][nextj][ori][next_has_person] = Actions.step_forward
                                can_break = False
                        # turn left or right
                        for k in [-1, 1]:
                            nextori = (ori + k + 4) % 4
                            if dist[i][j][ori][has_person] + 1 < dist[i][j][nextori][has_person]:
                                dist[i][j][nextori][has_person] = dist[i][j][ori][has_person] + 1
                                prev_action[i][j][nextori][has_person] = Actions.turn_left if k == -1 else Actions.turn_right
                                can_break = False
        if can_break:
            break
    '''
    besti, bestj, bestori, bestdist = 0, 0, 0, 1000000
    for i in range(n):
        for j in range(m):
            if Terrains.hospital == grid[i][j].terrain:
                for ori in range(4):
                    if dist[i][j][ori][1] < bestdist:
                        bestdist = dist[i][j][ori][1]
                        besti = i; bestj = j; bestori = ori
    curri, currj, currori = besti, bestj, bestori
    curr_has_person = 1
    last_action = None
    seen_a_person = False
    while curri != initiali or currj != initialj or currori != initialor:
        if MapObjects.injured in grid[curri][currj].objects:
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

    # dijkstra's
    '''
    while len(q) > 0:
        distance, loc = heapq.heappop(q)
        if distance != dist[loc[0]][loc[1]][loc[2]]:
            continue
        i, j, orientation = loc
        if MapObjects.injured in grid[i][j].objects:
            curri = i
            currj = j
            curror = orientation
            lastaction = 0
            while curri != initiali or currj != initialj or curror != initialor:
                action_taken = prev_action_code[curri][currj][curror]
                lastaction = action_taken
                if action_taken == 3:  # forward
                    curri -= di[curror]
                    currj -= dj[curror]
                elif action_taken == 1:  # left
                    curror = (curror + 1) % 4
                elif action_taken == 2:  # right
                    curror = (curror - 1 + 4) % 4
                else:
                    raise RuntimeError('rip')
            if lastaction == 1:
                return Actions.turn_left
            elif lastaction == 2:
                return Actions.turn_right
            elif lastaction == 3:
                return Actions.step_forward
        # forward
        nexti = i + di[orientation]
        nextj = j + dj[orientation]
        if grid[nexti][nextj].terrain not in [Terrains.none, Terrains.out_of_bounds, Terrains.wall]:
            if distance + 1 < dist[nexti][nextj][orientation]:
                dist[nexti][nextj][orientation] = distance + 1
                heapq.heappush(q, (distance + 1, (nexti, nextj, orientation)))
                prev_action_code[nexti][nextj][orientation] = Actions.step_forward.value
        # turn right or left
        for k in [-1, 1]:
            nextorientation = (orientation + k + 4) % 4
            if distance + 1 < dist[i][j][nextorientation]:
                dist[i][j][nextorientation] = distance + 1
                heapq.heappush(q, (distance + 1, (i, j, nextorientation)))
                prev_action_code[i][j][nextorientation] = Actions.turn_left.value if k == -1 else Actions.turn_right.value
    '''