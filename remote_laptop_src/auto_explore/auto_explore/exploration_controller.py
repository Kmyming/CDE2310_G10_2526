import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid, Odometry, Path
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist, PoseStamped
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool
import numpy as np
import heapq, math, random, yaml
import scipy.interpolate as si
import threading, time
import os
from ament_index_python.packages import get_package_share_directory

config_path = os.path.join(
    get_package_share_directory('auto_explore'),
    'config',
    'params.yaml'
)

with open(config_path, 'r', encoding='utf-8') as file:
    params = yaml.load(file, Loader=yaml.FullLoader)

lookahead_distance = params['lookahead_distance']
speed = params['speed']
expansion_size = params['expansion_size']
target_error = params['target_error']
robot_r = params['robot_r']

pathGlobal = 0


def euler_from_quaternion(x, y, z, w):
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    return math.atan2(t3, t4)


def heuristic(a, b):
    return np.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)


def astar(array, start, goal):
    neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic(start, goal)}
    oheap = []
    heapq.heappush(oheap, (fscore[start], start))

    while oheap:
        current = heapq.heappop(oheap)[1]
        if current == goal:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            data = data + [start]
            return data[::-1]

        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            tentative_g_score = gscore[current] + heuristic(current, neighbor)

            if 0 <= neighbor[0] < array.shape[0]:
                if 0 <= neighbor[1] < array.shape[1]:
                    if array[neighbor[0]][neighbor[1]] == 1:
                        continue
                else:
                    continue
            else:
                continue

            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                continue

            if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1] for i in oheap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(oheap, (fscore[neighbor], neighbor))

    if goal not in came_from:
        closest_node = None
        closest_dist = float('inf')
        for node in close_set:
            dist = heuristic(node, goal)
            if dist < closest_dist:
                closest_node = node
                closest_dist = dist

        if closest_node is not None:
            data = []
            while closest_node in came_from:
                data.append(closest_node)
                closest_node = came_from[closest_node]
            data = data + [start]
            return data[::-1]

    return False


def bspline_planning(array, sn):
    try:
        array = np.array(array)
        x = array[:, 0]
        y = array[:, 1]
        t = range(len(x))
        x_tup = si.splrep(t, x, k=2)
        y_tup = si.splrep(t, y, k=2)

        x_list = list(x_tup)
        x_list[1] = x.tolist() + [0.0, 0.0, 0.0, 0.0]
        y_list = list(y_tup)
        y_list[1] = y.tolist() + [0.0, 0.0, 0.0, 0.0]

        ipl_t = np.linspace(0.0, len(x) - 1, sn)
        rx = si.splev(ipl_t, x_list)
        ry = si.splev(ipl_t, y_list)
        return [(rx[i], ry[i]) for i in range(len(rx))]
    except Exception:
        return array


def pure_pursuit(current_x, current_y, current_heading, path, index):
    closest_point = None
    v = speed
    for i in range(index, len(path)):
        x = path[i][0]
        y = path[i][1]
        distance = math.hypot(current_x - x, current_y - y)
        if lookahead_distance < distance:
            closest_point = (x, y)
            index = i
            break

    if closest_point is not None:
        target_heading = math.atan2(closest_point[1] - current_y, closest_point[0] - current_x)
        desired_steering_angle = target_heading - current_heading
    else:
        target_heading = math.atan2(path[-1][1] - current_y, path[-1][0] - current_x)
        desired_steering_angle = target_heading - current_heading
        index = len(path) - 1

    if desired_steering_angle > math.pi:
        desired_steering_angle -= 2 * math.pi
    elif desired_steering_angle < -math.pi:
        desired_steering_angle += 2 * math.pi

    if desired_steering_angle > math.pi / 6 or desired_steering_angle < -math.pi / 6:
        sign = 1 if desired_steering_angle > 0 else -1
        desired_steering_angle = sign * math.pi / 4
        v = 0.0

    return v, desired_steering_angle, index


def frontierB(matrix):
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] == 0.0:
                if i > 0 and matrix[i - 1][j] < 0:
                    matrix[i][j] = 2
                elif i < len(matrix) - 1 and matrix[i + 1][j] < 0:
                    matrix[i][j] = 2
                elif j > 0 and matrix[i][j - 1] < 0:
                    matrix[i][j] = 2
                elif j < len(matrix[i]) - 1 and matrix[i][j + 1] < 0:
                    matrix[i][j] = 2
    return matrix


def assign_groups(matrix):
    group = 1
    groups = {}
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if matrix[i][j] == 2:
                group = dfs(matrix, i, j, group, groups)
    return matrix, groups


def dfs(matrix, i, j, group, groups):
    if i < 0 or i >= len(matrix) or j < 0 or j >= len(matrix[0]):
        return group
    if matrix[i][j] != 2:
        return group

    if group in groups:
        groups[group].append((i, j))
    else:
        groups[group] = [(i, j)]

    matrix[i][j] = 0
    dfs(matrix, i + 1, j, group, groups)
    dfs(matrix, i - 1, j, group, groups)
    dfs(matrix, i, j + 1, group, groups)
    dfs(matrix, i, j - 1, group, groups)
    dfs(matrix, i + 1, j + 1, group, groups)
    dfs(matrix, i - 1, j - 1, group, groups)
    dfs(matrix, i - 1, j + 1, group, groups)
    dfs(matrix, i + 1, j - 1, group, groups)
    return group + 1


def fGroups(groups):
    sorted_groups = sorted(groups.items(), key=lambda x: len(x[1]), reverse=True)
    return [g for g in sorted_groups[:5] if len(g[1]) > 2]


def calculate_centroid(x_coords, y_coords):
    n = len(x_coords)
    return (int(sum(x_coords) / n), int(sum(y_coords) / n))


def findClosestGroup(matrix, groups, current, resolution, originX, originY):
    targetP = None
    distances = []
    paths = []
    score = []
    max_score = -1

    for i in range(len(groups)):
        middle = calculate_centroid([p[0] for p in groups[i][1]], [p[1] for p in groups[i][1]])
        path = astar(matrix, current, middle)
        path = [(p[1] * resolution + originX, p[0] * resolution + originY) for p in path]
        total_distance = pathLength(path)
        distances.append(total_distance)
        paths.append(path)

    for i in range(len(distances)):
        if distances[i] == 0:
            score.append(0)
        else:
            score.append(len(groups[i][1]) / distances[i])

    for i in range(len(distances)):
        if distances[i] > target_error * 3:
            if max_score == -1 or score[i] > score[max_score]:
                max_score = i

    if max_score != -1:
        targetP = paths[max_score]
    else:
        index = random.randint(0, len(groups) - 1)
        target = groups[index][1]
        target = target[random.randint(0, len(target) - 1)]
        path = astar(matrix, current, target)
        targetP = [(p[1] * resolution + originX, p[0] * resolution + originY) for p in path]

    return targetP


def pathLength(path):
    points = np.array([(p[0], p[1]) for p in path])
    differences = np.diff(points, axis=0)
    distances = np.hypot(differences[:, 0], differences[:, 1])
    return np.sum(distances)


def costmap(data, width, height, resolution):
    data = np.array(data).reshape(height, width)
    wall = np.where(data == 100)
    for i in range(-expansion_size, expansion_size + 1):
        for j in range(-expansion_size, expansion_size + 1):
            if i == 0 and j == 0:
                continue
            x = np.clip(wall[0] + i, 0, height - 1)
            y = np.clip(wall[1] + j, 0, width - 1)
            data[x, y] = 100

    return data * resolution


def exploration(data, width, height, resolution, column, row, originX, originY):
    global pathGlobal

    data = costmap(data, width, height, resolution)
    data[row][column] = 0
    data[data > 5] = 1
    data = frontierB(data)
    data, groups = assign_groups(data)
    groups = fGroups(groups)

    if len(groups) == 0:
        path = -1
    else:
        data[data < 0] = 1
        path = findClosestGroup(data, groups, (row, column), resolution, originX, originY)
        if path is not None:
            path = bspline_planning(path, len(path) * 5)
        else:
            path = -1

    pathGlobal = path


def publish_path(node, path, start_index=0):
    if path is None or isinstance(path, int):
        return

    path_msg = Path()
    path_msg.header.frame_id = 'map'
    path_msg.header.stamp = node.get_clock().now().to_msg()

    for i in range(start_index, len(path)):
        point = path[i]
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = node.get_clock().now().to_msg()
        pose.pose.position.x = point[0]
        pose.pose.position.y = point[1]
        pose.pose.position.z = 0.0
        path_msg.poses.append(pose)

    node.path_pub.publish(path_msg)


def localControl(scan):
    if scan is None or len(scan) == 0:
        return None, None

    s = np.array(scan, dtype=float)
    s = np.nan_to_num(s, nan=10.0, posinf=10.0, neginf=0.0)
    n = len(s)

    front_range = max(1, n // 12)
    front_left_end = max(1, n // 6)
    front_right_start = max(0, n - n // 6)

    front_center = s[:front_range].tolist() + s[n - front_range:].tolist()
    front_left = s[:front_left_end].tolist()
    front_right = s[front_right_start:].tolist()

    min_front = min(front_center)
    min_left = min(front_left)
    min_right = min(front_right)

    stop_dist = robot_r * 0.6
    slow_dist = robot_r * 1.2
    avoid_dist = robot_r

    if min_front < stop_dist:
        return 0.0, 0.0

    if min_front < avoid_dist:
        if min_left > min_right:
            return 0.05, math.pi / 4
        return 0.05, -math.pi / 4

    if min_left < avoid_dist:
        intensity = 1.0 - (min_left / avoid_dist)
        return 0.08, -(math.pi / 6 + intensity * math.pi / 6)

    if min_right < avoid_dist:
        intensity = 1.0 - (min_right / avoid_dist)
        return 0.08, (math.pi / 6 + intensity * math.pi / 6)

    if min_front < slow_dist:
        slow_speed = speed * (min_front / slow_dist)
        return max(slow_speed, 0.05), 0.0

    return None, None


class navigationControl(Node):
    def __init__(self):
        super().__init__('exploration_controller')

        self.create_subscription(OccupancyGrid, 'map', self.map_callback, 10)
        self.create_subscription(Odometry, 'odom', self.odom_callback, 10)
        self.create_subscription(LaserScan, 'scan', self.scan_callback, qos_profile_sensor_data)

        self.publisher = self.create_publisher(Twist, '/cmd_vel_nav', 10)
        self.map_explored_pub = self.create_publisher(Bool, '/map_explored', 10)
        self.path_pub = self.create_publisher(Path, '/exploration_path', 10)

        self.exploration_mode = True
        self.exploration_done_announced = False
        self.path = None
        self.i = 0

        threading.Thread(target=self.exp, daemon=True).start()

    def exp(self):
        twist = Twist()

        while rclpy.ok():
            if not hasattr(self, 'map_data') or not hasattr(self, 'odom_data') or not hasattr(self, 'scan_data'):
                time.sleep(0.1)
                continue

            if self.exploration_mode:
                if isinstance(pathGlobal, int) and pathGlobal == 0:
                    column = int((self.x - self.originX) / self.resolution)
                    row = int((self.y - self.originY) / self.resolution)
                    exploration(self.data, self.width, self.height, self.resolution, column, row, self.originX, self.originY)
                    self.path = pathGlobal
                else:
                    self.path = pathGlobal

                if isinstance(self.path, int) and self.path == -1:
                    if not self.exploration_done_announced:
                        self.map_explored_pub.publish(Bool(data=True))
                        self.exploration_done_announced = True
                    self.publisher.publish(Twist())
                    time.sleep(0.2)
                    continue

                self.c = int((self.path[-1][0] - self.originX) / self.resolution)
                self.r = int((self.path[-1][1] - self.originY) / self.resolution)
                self.exploration_mode = False
                self.i = 0

                publish_path(self, self.path)
                t = max((pathLength(self.path) / speed) - 0.2, 0.1)
                self.t = threading.Timer(t, self.target_callback)
                self.t.start()

            else:
                v, w = localControl(self.scan)
                avoiding = v is not None

                if avoiding:
                    twist.linear.x = v
                    twist.angular.z = w
                else:
                    v, w, self.i = pure_pursuit(self.x, self.y, self.yaw, self.path, self.i)
                    if abs(self.x - self.path[-1][0]) < target_error and abs(self.y - self.path[-1][1]) < target_error:
                        v = 0.0
                        w = 0.0
                        self.exploration_mode = True
                        if hasattr(self, 't') and self.t.is_alive():
                            self.t.join()

                    twist.linear.x = v
                    twist.angular.z = w

                publish_path(self, self.path, self.i)
                self.publisher.publish(twist)
                time.sleep(0.1)

    def target_callback(self):
        exploration(self.data, self.width, self.height, self.resolution, self.c, self.r, self.originX, self.originY)

    def scan_callback(self, msg):
        self.scan_data = msg
        self.scan = msg.ranges

    def map_callback(self, msg):
        self.map_data = msg
        self.resolution = self.map_data.info.resolution
        self.originX = self.map_data.info.origin.position.x
        self.originY = self.map_data.info.origin.position.y
        self.width = self.map_data.info.width
        self.height = self.map_data.info.height
        self.data = self.map_data.data

    def odom_callback(self, msg):
        self.odom_data = msg
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        self.yaw = euler_from_quaternion(
            msg.pose.pose.orientation.x,
            msg.pose.pose.orientation.y,
            msg.pose.pose.orientation.z,
            msg.pose.pose.orientation.w,
        )


def main(args=None):
    rclpy.init(args=args)
    navigation_control = navigationControl()
    rclpy.spin(navigation_control)
    navigation_control.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
