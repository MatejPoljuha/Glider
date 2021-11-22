from asyncio import PriorityQueue


def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return (abs(x1 - x2)**2 + abs(y1 - y2)**2)**0.5

def alti_loss(a,b):
    (x1,y1)=a
    (x2,y2)=b
    return ((abs(x1 - x2)**2 + abs(y1 - y2)**2)**0.5)*5 #5 is glide ratio

def alti_add(upliftspeed):
    return upliftspeed*10   #10 is stay 10 seconds in the zone

def a_star_search(graph, start, goal):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()

        if current == goal:
            break
#we need to add the altitude control here,since Idk how you deal with the altitude, the pseudocode is :
# current altitude(x2) = last altitue(from x1) - alti_loss +alti_add
#if current altitude>0(or the one we set), then contitue with the judge "if next not in ....."

        for next in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                frontier.put(next, priority)
                came_from[next] = current

    return came_from, cost_so_far

