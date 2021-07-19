from gym_sgw.envs.enums.Enums import Actions, Terrains, MapObjects
import heapq
def choose_action(observation):
    grid, status = observation
    print(status)
    i, j = status['player_location']
    # up, right, down, left
    di = [-1, 0, 1, 0]; dj = [0, 1, 0, -1]
    dist = [[[1000000 for _ in range(4)] for _ in range(len(grid[0]))] for _ in range(len(grid))]
    prev_action_code = [[[Actions.none.value for _ in range(4)] for _ in range(len(grid[0]))] for _ in range(len(grid))]
    q = []
    initiali = status['player_location'][0]
    initialj = status['player_location'][1]
    initialor = status['player_orientation'].value
    heapq.heappush(q, (0, (initiali, initialj, initialor)))
    dist[initiali][initialj][initialor] = 0
    # dijkstra's
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
