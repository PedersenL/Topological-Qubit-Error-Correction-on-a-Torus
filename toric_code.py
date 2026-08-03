from numpy import *
import numpy as np
import builtins
import networkx as nx
from itertools import combinations
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.optimize import curve_fit
import random
import time

def start_up(sizex,sizey, error_rate_x,error_rate_z, z = True):
    x_start = zeros((sizex*2,sizey*2))
    z_start = zeros((sizex*2,sizey*2))
    x_start[::2, 1::2] = 1
    x_start[1::2, ::2] = 1
    z_start[::2, 1::2] = 1
    z_start[1::2, ::2] = 1
    for i in range(sizex*2):
        for j in range(sizey*2):
            if x_start[i, j] == 1:
                if random.random() < error_rate_x:
                    x_start[i, j] = -1
                if random.random() < error_rate_z:
                    z_start[i, j] = -1

    return x_start, z_start

def start_up2(sizex,sizey, error_rate_x,error_rate_z, z = True):
    x_start = zeros((sizex*2,sizey*2))
    z_start = zeros((sizex*2,sizey*2))
    x_start[::2, 1::2] = 1
    x_start[1::2, ::2] = 1
    z_start[::2, 1::2] = 1
    z_start[1::2, ::2] = 1
    for i in range(sizex*2):
        for j in range(sizey*2):
            if x_start[i, j] == 1:
                if random.random() < error_rate_x: #even rows start with x flips
                    if i % 2 == 0:
                        x_start[i, j] = -1
                    else:
                        z_start[i, j] = -1
                if random.random() < error_rate_z:
                    if i % 2 == 0:
                        z_start[i, j] = -1
                    else:
                        x_start[i, j] = -1


    return x_start, z_start

def create_parody(x_start, z_start):
    limit_x = x_start.shape[0]
    limit_y = x_start.shape[1]
    sizex = limit_x // 2
    sizey = limit_y // 2

    parody_x = zeros((limit_x, limit_y))
    parody_z = zeros((limit_x, limit_y))

    for i in range(sizex):
        for j in range(sizey):
            parody_x[2*i, 2*j] = (
                x_start[2*i, (2*j + 1) % limit_y] *
                x_start[(2*i + 1) % limit_x, 2*j] *
                x_start[2*i, (2*j - 1) % limit_y] *
                x_start[(2*i - 1) % limit_x, 2*j]
            )
            parody_z[(2*i + 1) % limit_x, (2*j + 1) % limit_y] = (
                z_start[(2*i + 1) % limit_x, 2*j] *
                z_start[2*i, (2*j + 1) % limit_y] *
                z_start[(2*i + 2) % limit_x, (2*j + 1) % limit_y] *
                z_start[(2*i + 1) % limit_x, (2*j + 2) % limit_y]
            )

    return parody_x, parody_z


def create_graph(parody,weightx = 1, weightz = 1):
    G = nx.Graph()
    nodes_matrix = zeros(parody.shape, dtype=int)
    points = []
    pons = 1
    for i in range(parody.shape[0]):
        for j in range(parody.shape[1]):
            if parody[i, j] == -1:
                nodes_matrix[i, j] = pons
                points.append((i, j))
                pons += 1
    G.add_nodes_from(points)
    # print(points)
    for p1,p2 in combinations(points, 2):
        xdist = builtins.min(abs(p1[0] - p2[0]), parody.shape[0] - abs(p1[0] - p2[0]))
        ydist = builtins.min(abs(p1[1] - p2[1]), parody.shape[1] - abs(p1[1] - p2[1]))
        dist = xdist*weightx + ydist*weightz #fix for ends :)
        G.add_edge(p1, p2, weight=-dist)
        # print(f"Edge added: {p1} to {p2}, weight: {dist}, {pons}")
    return G

def create_parody2(x_start, z_start):
    limit_x = x_start.shape[0]
    limit_y = x_start.shape[1]
    sizex = limit_x // 2
    sizey = limit_y // 2
    parody = zeros((limit_x, limit_y))
    for i in range(sizex):
        for j in range(sizey):
            parody[2*i, 2*j] = (
                z_start[2*i, (2*j + 1) % limit_y] *
                x_start[(2*i + 1) % limit_x, 2*j] *
                z_start[2*i, (2*j - 1) % limit_y] *
                x_start[(2*i - 1) % limit_x, 2*j]
            )

            parody[(2*i+1)%limit_x, (2*j+1)%limit_y] = (
                z_start[(2*i+1)%limit_x, (2*j + 2) % limit_y] *
                x_start[(2*i + 2) % limit_x, (2*j+1)%limit_y] *
                z_start[(2*i+1)%limit_x, (2*j) % limit_y] *
                x_start[(2*i) % limit_x, (2*j+1)%limit_y]
            )
    return parody
def go_direction2(rows, cols, x, y, direction): #old and bad dw abt it
    if direction == 'up':
        return (x - 1) % rows, y
    elif direction == 'down':
        return (x + 1) % rows, y
    elif direction == 'left':
        return x, (y - 1) % cols
    elif direction == 'right':
        return x, (y + 1) % cols
def search_errx(start,parody,point,debugging = False): #also old and bad but it works and i dont want to spend more time on it
    rows, cols = start.shape # Get dimensions for modulo
    startcopy = start.copy()
    parodycopy = parody.copy()
    keep = True
    direction = None
    x,y = point[0], point[1]
    # Apply modulo to initial directional checks
    if startcopy[(point[0]+1) % rows, point[1] % cols] == -1:
        direction = 'down'
    elif startcopy[point[0] % rows, (point[1]+1) % cols] == -1:
        direction = 'right'
    elif startcopy[(point[0]-1) % rows, point[1] % cols] == -1:
        direction = 'up'
    elif startcopy[point[0] % rows, (point[1]-1) % cols] == -1:
        direction = 'left'
    else:
        print("No adjacent error found.")
    while keep:
        x, y = go_direction2(rows, cols, x, y, direction)
        if debugging:
            print('step to direction:', direction, 'current position:', (x,y))
        startcopy[x % rows, y % cols] = 1
        x,y = go_direction2(rows, cols, x, y, direction) # Update x,y based on direction
        if debugging:
            print('step to direction:', direction, 'current position:', (x,y))
        if startcopy[(x+1) % rows, y % cols] == -1:
            direction = 'down'
            continue
        if startcopy[x % rows, (y+1) % cols] == -1:
            direction = 'right'
            continue
        if startcopy[(x-1) % rows, y % cols] == -1:
            direction = 'up'
            continue
        if startcopy[x % rows, (y-1) % cols] == -1:
            direction = 'left'
            continue
        keep = False

    if startcopy[(point[0]+1) % rows, point[1] % cols] == -1:
        x,y = (point[0]+1) % rows, point[1] % cols
    elif startcopy[point[0] % rows, (point[1]+1) % cols] == -1:
        x,y = point[0] % rows, (point[1]+1) % cols
    elif startcopy[(point[0]-1) % rows, point[1] % cols] == -1:
        x,y = (point[0]-1) % rows, point[1] % cols
    elif startcopy[point[0] % rows, (point[1]-1) % cols] == -1:
        x,y = point[0] % rows, (point[1]-1) % cols

    parodycopy[x % rows, y % cols] = 1
    return startcopy, parodycopy, (point,(x,y))
def actualpairs(startx,startz,parodyx,parodyz): #old i think its not worth putting more time into this method is messy
    xcopy = startx.copy()
    zcopy = startz.copy()
    parodyxcopy = parodyx.copy()
    parodyzcopy = parodyz.copy()
    xpairs = []
    zpairs = []
    for i in range(parodyx.shape[0]):
        for j in range(parodyx.shape[1]):
            if parodyxcopy[i, j] == -1:
                print(f"X Error found at parodyxcopy[{i}, {j}]")
                xcopy, parodyxcopy, pair = search_errx(xcopy, parodyxcopy, (i, j))
                xpairs.append(pair)
                print(f'x pairs: {xpairs}')
            if parodyzcopy[i, j] == -1:
                print(f"Z Error found at parodyzcopy[{i}, {j}]")
                zcopy, parodyzcopy, pair = search_errx(zcopy, parodyzcopy, (i, j))
                zpairs.append(pair)
                print(f'z pairs: {zpairs}')
    return xpairs, zpairs
def fix_err(start, parody, point1,point2,debugging = False):  #flip x going up/down flip z going left/right for part 2
    startcopy = start.copy()
    sizex, sizey = startcopy.shape
    x1, y1 = point1[0], point1[1]
    x2, y2 = point2[0], point2[1]
    shortest_x,shortest_y = 0,0
    dx = abs((x2-x1))
    if dx <= abs(dx-sizex):
        shortest_x = (x2-x1) #go in this direction
    else:
        if x2-x1 ==0:
            shortest_x = 0
        elif x2-x1>0:
            shortest_x = (x2-x1)-sizex #go reverse direction
        else:
            shortest_x = (x2-x1)+sizex #go reverse direction
    dy = abs((y2-y1))
    if dy <= abs(dy-sizey):
        shortest_y = (y2-y1) #go in this direction
    else:
        if y2-y1 == 0:
            shortest_y = 0
        elif y2-y1>0:
            shortest_y = (y2-y1)-sizey #go reverse direction
        else:
            shortest_y = (y2-y1)+sizey #go reverse direction
    x,y = x1,y1
    if debugging:
         print(f"Starting point: {(x1,y1)}, Ending point: {(x2,y2)}, Shortest path: (x: {shortest_x}, y: {shortest_y})")
    if shortest_x == 0:
        if shortest_y > 0:
            y += 1
            shortest_y -= 1
        else:
            y -= 1
            shortest_y += 1
    elif shortest_x > 0:
        x += 1
        shortest_x -= 1
    elif shortest_x < 0:
        x -= 1
        shortest_x += 1
    else:
        print("Error: No movement needed, points are the same.")
    while (x,y) != (x2,y2):
        startcopy[x % sizex, y % sizey] *=-1
        if debugging:
            print(f"Flipped at: {(x,y)}, remaining path: (x: {shortest_x}, y: {shortest_y})")
        # print(x,y, 'flipped, remaining path:', shortest_x, shortest_y)
        if shortest_x == 0:
            if shortest_y >= 1:
                y += 1
                shortest_y -= 1
            elif shortest_y <= -1:
                y -= 1
                shortest_y += 1
            else:
                x,y = x2,y2
        elif shortest_x >= 1:
            x += 1
            shortest_x -= 1
        elif shortest_x <= -1:
            x -= 1
            shortest_x += 1
        else:
            x,y = x2,y2
    if debugging:
        print('finished at point:', (x,y))
    return startcopy, parody

def fix_from_pairs(start, parody, pairs,debugging = False): #YESSSSSSSS
    startcopy = start.copy()
    for pair in pairs:
        point1, point2 = pair
        startcopy, parody = fix_err(startcopy, parody, point1,point2,debugging = debugging)
    return startcopy, parody
def go_direction(rows, cols, x, y, direction,xindex,yindex): #old and bad dw abt it
    if direction == 'up':
        return (x - 1) % rows, y, xindex-1, yindex
    elif direction == 'down':
        return (x + 1) % rows, y, xindex+1, yindex
    elif direction == 'left':
        return x, (y - 1) % cols, xindex, yindex-1
    elif direction == 'right':
        return x, (y + 1) % cols, xindex, yindex+1
def check_around(start,point,number = -1,debugging = False):
    rows, cols = start.shape
    x, y = point[0], point[1]
    if debugging:
        print(start[(x+1) % rows, y % cols], start[x % rows, (y+1) % cols], start[(x-1) % rows, y % cols], start[x % rows, (y-1) % cols])
    if start[(x+1) % rows, y % cols] == number:
        return 'down'
    elif start[x % rows, (y+1) % cols] == number:
        return 'right'
    elif start[(x-1) % rows, y % cols] == number:
        return 'up'
    elif start[x % rows, (y-1) % cols] == number:
        return 'left'
    else:
        if debugging:
            print("No adjacent error found.")
        return False
def check_loop(start,parody,point,groupname,debugging = False):
    xindex, yindex = 0,0
    startcopy = start.copy()
    logical_flip = False
    rows, cols = start.shape # Get dimensions for modulo
    startcopy = start.copy()
    parodycopy = parody.copy()
    keep = True
    direction = None
    x,y = point[0], point[1]
    started = False
    startcopy[x,y] = -groupname
    if parody[(point[0]+1) % rows, point[1] % cols] != 0:
        direction = check_around(startcopy, ((point[0]+1) % rows, point[1] % cols))
        if debugging:
            print('initial direction check down:', direction)
        if direction:
            started = 'down'
    if parody[point[0] % rows, (point[1]+1) % cols] != 0 and not started:
        direction = check_around(startcopy, (point[0] % rows, (point[1]+1) % cols))
        if debugging:
            print('initial direction check right:', direction)
        if direction:
            started = 'right'
    if parody[(point[0]-1) % rows, point[1] % cols] != 0 and not started:
        direction = check_around(startcopy, ((point[0]-1) % rows, point[1] % cols))
        if debugging:
            print('initial direction check up:', direction)
        if direction:
            started = 'up'
    if parody[point[0] % rows, (point[1]-1) % cols] != 0 and not started:
        direction = check_around(startcopy, (point[0] % rows, (point[1]-1) % cols))
        if debugging:
            print('initial direction check left:', direction)
        if direction:
            started = 'left'
    if not started and debugging:
        print("No adjacent error found to start loop.")
        print(start,parody,point,started,direction)
    if not started:
        return startcopy,False
    x, y,xindex,yindex = go_direction(rows, cols, x, y, started,xindex,yindex)

    while keep:
        if not direction and debugging:
            print(startcopy, x,y)
            print('No direction found, breaking loop.')
        if not direction:
            return startcopy,False
        x, y,xindex,yindex = go_direction(rows, cols, x, y, direction,xindex,yindex)
        if debugging:
            print('step to direction:', direction, 'current position:', (x,y))
        startcopy[x % rows, y % cols] = groupname
        x, y,xindex,yindex = go_direction(rows, cols, x, y, direction,xindex,yindex) # Update x,y based on direction
        if debugging:
            print('checking around at position:', (x,y))
        direction = check_around(startcopy, (x,y))
        direction2 = check_around(startcopy, (x,y),-groupname)
        if direction2:
            x, y,xindex,yindex = go_direction(rows, cols, x, y, direction2,xindex,yindex) # Update x,y based on direction
            if xindex != 0 or yindex != 0:
                if debugging:
                    print(f'xindex: {xindex}, yindex: {yindex} with starting point: {point}')
                logical_flip = True
                keep = False
            else:
                keep = False
    return startcopy, logical_flip

def check_logic_loop(start, parody,debugging = False): #for x y seperate
    startcopy = start.copy()
    parodycopy = parody.copy()
    flips = 0
    groupnumber = 2
    for i in range(parodycopy.shape[0]):
        for j in range(parodycopy.shape[1]):
            if startcopy[i, j] == -1:
                if debugging:
                    print(f"Flip found at startcopy[{i}, {j}]")
                startcopy, logical_flip = check_loop(startcopy, parodycopy, (i,j),groupnumber,debugging = debugging)
                groupnumber +=1
                if logical_flip == -1:
                    if debugging:
                        print('rare issue in code returning -1')
                    return -1
                elif logical_flip:
                    flips += 1
                    if debugging:
                        print('Found logical loop at location:', (i,j))
                        print(startcopy)
                    return flips

    return flips

def test(params):
    failures = 0
    runs = params['runs']
    size = params['size']

    for i in range(runs):
        x_start, z_start = start_up(
            size, size,
            error_rate_x=params['error_rate_x'],
            error_rate_z=params['error_rate_z']
        )
        if params['Base basis'] == False:
            x_start, z_start = start_up2(
            size, size,
            error_rate_x=params['error_rate_x'],
            error_rate_z=params['error_rate_z']
            )
        parody_x, parody_z = create_parody(x_start, z_start)
        graphx = create_graph(parody_x, weightx=params['weightx'], weightz=params['weightz'])
        graphz = create_graph(parody_z, weightx=params['weightx'], weightz=params['weightz'])
        matchingx = nx.max_weight_matching(graphx, maxcardinality=True)
        matchingz = nx.max_weight_matching(graphz, maxcardinality=True)
        x_fixed, parody_x = fix_from_pairs(x_start, parody_x, matchingx)
        z_fixed, parody_z = fix_from_pairs(z_start, parody_z, matchingz)

        if check_logic_loop(x_fixed, parody_x) > 0 or check_logic_loop(z_fixed, parody_z) > 0:
            failures += 1

    return failures, failures / runs

#Code below is mostly AI-generated as it's not the main focus of the project and just data analysis/plotting

def sweep_variable(variable_name, start, end, steps, is_log, base_params,debugging = False):
    """
    Varies a single parameter and runs the test function for each step.
    """
    if is_log:
        values = logspace(log10(start), log10(end), num=steps)
    else:
        values = linspace(start, end, num=steps)

    results = []

    for val in values:
        # Create a copy so we don't mutate the original dictionary
        current_params = base_params.copy()
        current_params[variable_name] = val
        if variable_name == 'error_rate':
            current_params['error_rate_x'] = val
            current_params['error_rate_z'] = val

        _, rate = test(current_params)
        results.append((val, rate))
        if debugging:
            print(f"{variable_name}: {val:.4f} | Failure Rate: {rate:.2%}")

    return results
def plot_multi_size_sweep(sizes, var1, var_name, start, end, steps, is_log, base_params):
    """
    Sweeps a target variable for multiple code sizes, plots the failure rate,
    and prints a copy-pasteable dictionary of the results.
    """
    plt.figure(figsize=(10, 6))
    sorted_sizes = sorted(sizes)
    colors = cm.turbo(linspace(0.2, 0.8, len(sorted_sizes)))

    # Dictionary to store all sweep data for export
    all_results_data = {}

    for i, size in enumerate(sorted_sizes):
        current_config = base_params.copy()
        current_config[var1] = size

        results = sweep_variable(
            variable_name=var_name,
            start=start,
            end=end,
            steps=steps,
            is_log=is_log,
            base_params=current_config
        )

        x_vals = [r[0] for r in results]
        y_vals = [r[1] for r in results]

        # Store in dictionary: {size_value: {"x": [...], "y": [...]}}
        all_results_data[size] = {
            "x": x_vals,
            "y": y_vals
        }

        plt.plot(
            x_vals,
            y_vals,
            marker='o',
            label=f'{var1}: {size}',
            color=colors[i]
        )

    # --- PRINTING DATA FOR ANALYSIS ---
    print("\n" + "="*30)
    print("COPY-PASTEABLE DATA OBJECT")
    print("="*30)
    # Print as a clean dictionary format
    print(f"sweep_data = {all_results_data}")
    print("="*30 + "\n")

    # Formatting the chart
    plt.xscale('log') if is_log else plt.xscale('linear')
    plt.xlabel(f'{var_name.replace("_", " ").title()}')
    plt.ylabel('Failure Rate')
    plt.title(f'Failure Rate vs {var_name} across {var1}')
    plt.legend(title=var1)
    plt.grid(True, which="both", linestyle='--', alpha=0.5)
    plt.tight_layout()

    plt.savefig('error_rate_sweep.png')
    plt.show()

    return all_results_data
def plot_smoothed_results(all_results_data, window_percentage=0.2, is_log=False):
    """
    Computes moving average and plots both raw and smoothed data.
    """
    plt.figure(figsize=(10, 6))
    sorted_sizes = sorted(all_results_data.keys())
    colors = cm.turbo(linspace(0.2, 0.8, len(sorted_sizes)))

    for i, size in enumerate(sorted_sizes):
        x_vals = array(all_results_data[size]["x"])
        y_vals = array(all_results_data[size]["y"])

        # Calculate window size as a portion of the dataset
        n = len(y_vals)
        window_size = builtins.max(1, int(n * window_percentage))

        # Compute moving average
        weights = ones(window_size) / window_size
        y_smoothed = convolve(y_vals, weights, mode='valid')

        # Center the x_vals for the smoothed line
        start_idx = (window_size - 1) // 2
        end_idx = start_idx + len(y_smoothed)
        x_smoothed = x_vals[start_idx:end_idx]

        # Plot raw data with transparency
        plt.plot(x_vals, y_vals, 'o', alpha=0.3, color=colors[i], markersize=4)

        # Plot smoothed line
        plt.plot(x_smoothed, y_smoothed, '-', linewidth=2,
                 label=f'Size {size} (Smoothed)', color=colors[i])

    plt.xscale('log') if is_log else plt.xscale('linear')
    plt.xlabel('Variable Value')
    plt.ylabel('Failure Rate')
    plt.title(f'Smoothed Failure Rate (Window: {window_percentage*100}%)')
    plt.legend()
    plt.grid(True, which="both", linestyle='--', alpha=0.5)
    plt.show()


def logistic_model(x, A, k, x0):

    return 1 / (1 + np.exp(-k * (x - x0)))

def analyze_sweep_data(data):
    plt.figure(figsize=(12, 8))

    sizes = sorted(data.keys())
    colors = cm.turbo(np.linspace(0.1, 0.9, len(sizes)))

    print(f"{'Size':<6} | {'Threshold (x0)':<15} | {'Steepness (k)':<15} | {'Asymptote (A)':<10}")
    print("-" * 55)

    for i, size in enumerate(sizes):
        x_data = np.array(data[size]['x'], dtype=float)
        y_data = np.array(data[size]['y'], dtype=float)


        initial_guess = [max(y_data), 20, np.median(x_data)]

        try:
            # 3. Perform the fit
            popt, _ = curve_fit(logistic_model, x_data, y_data, p0=initial_guess, maxfev=10000)
            A_fit, k_fit, x0_fit = popt

            # 4. Generate smooth curve for the "Line of Best Fit"
            x_smooth = np.logspace(np.log10(min(x_data)), np.log10(max(x_data)), 200)
            y_smooth = logistic_model(x_smooth, *popt)

            # 5. Plotting
            plt.scatter(x_data, y_data, color=colors[i], alpha=0.4, s=20) # Original points
            plt.plot(x_smooth, y_smooth, color=colors[i], label=f'Size {size} (x0={x0_fit:.3f})', linewidth=2)

            print(f"{size:<6} | {x0_fit:<15.4f} | {k_fit:<15.2f} | {A_fit:<10.2f}")

        except RuntimeError:
            print(f"Size {size}: Fit failed to converge.")
            plt.scatter(x_data, y_data, color=colors[i], label=f'Size {size} (No Fit)')

    # Chart Formatting
    plt.xscale('log')
    plt.xlabel('Physical Error Rate ($x$)')
    plt.ylabel('Logical Failure Rate ($y$)')
    plt.title('Logistic S-Curve Analysis of Simulation Results')
    plt.legend(title="Code Size & Midpoint")
    plt.grid(True, which="both", linestyle='--', alpha=0.5)
    plt.ylim(-0.05, 1.05)

    plt.savefig('logistic_analysis.png')
    plt.show()


def sweep_variable_time(variable_name, start, end, steps, is_log, base_params, debugging=False):
    """
    Varies a single parameter and measures the average simulation time per run.
    """
    if is_log:
        values = logspace(log10(start), log10(end), num=steps)
    else:
        values = linspace(start, end, num=steps)

    results = []

    for val in values:
        current_params = base_params.copy()
        current_params[variable_name] = val

        # Handle the special case for error_rate
        if variable_name == 'error_rate':
            current_params['error_rate_x'] = val
            current_params['error_rate_z'] = val

        # Timing the execution of the test function
        start_time = time.time()
        _, _ = test(current_params)
        end_time = time.time()

        total_duration = end_time - start_time
        avg_time = total_duration / current_params['runs']

        results.append((val, avg_time))

        if debugging:
            print(f"{variable_name}: {val:.4f} | Avg Time: {avg_time:.6f}s")

    return results

