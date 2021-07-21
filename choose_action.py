from gym_sgw.envs.enums.Enums import Actions, Terrains, MapObjects
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
    prev_action = [[[[Actions.none for _ in range(2)] for _ in range(4)] for _ in range(m)] for _ in range(n)]
    q = deque()
    in_queue = [[[[False for _ in range(2)] for _ in range(4)] for _ in range(m)] for _ in range(n)]
    initiali = status['player_location'][0]
    initialj = status['player_location'][1]
    initialor = status['player_orientation'].value
    initial_has_person = 1 if MapObjects.injured in grid[initiali][initialj].objects else 0
    q.append((initiali, initialj, initialor, initial_has_person))
    dist[initiali][initialj][initialor][initial_has_person] = 0
    in_queue[initiali][initialj][initialor][initial_has_person] = True
    q_count = 1
    # spfa
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
