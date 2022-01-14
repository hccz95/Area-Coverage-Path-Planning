from plots import *
from robot import *
from robot_animation import *

"""
The main script for path planning 
"""
###################################################################
# environment initialization
# define the 2D map with length 100 width 100 and grid length 1
mymap = EnvMap(gv.x_bound, gv.y_bound, gv.grid_length)
# add a circle
# mymap.add_circle(7,7,3)

# add polygon
mymap.add_polygon([15, 15, 23, 15, 23, 23, 15, 23])

# mymap.show_map()

#####################################################################
# robot initialization

# define robots
robotList = define_robot(gv.robot_number)

# set the initial state and target randomly or manually
random = 1
if random:
    # initialize the state and target automatically and randomly
    for robot in robotList:
        robot.random_init_state(mymap)
        robot.random_init_target()
        print(robot.state[0])  # test the initial state has been passed to the state
        print(robot.target[0])
else:
    # initialize the robot manually
    # the number of robot is set in global_value.py file
    robot1 = robotList[0]
    robot1.set_init_state(22, 6)
    robot1.set_init_target(19, 12)
    #
    robot2 = robotList[1]
    robot2.set_init_state(25, 3)
    robot2.set_init_target(22, 7)
    #
    robot3 = robotList[2]
    robot3.set_init_state(9, 9)
    robot3.set_init_target(13, 7)

# show the robot initial position and environment map
show_robot(robotList, mymap)

# iteration
# monitor the coverage percent
c_percent = np.zeros(gv.Iteration - 1)
# todo there is index problem with time+1

for time in range(gv.Iteration - 1):
    for robot in robotList:
        # get current robot state
        cur_state = robot.state[time, :2]
        # update information map and motion-mode
        robot.update_info_map(time, mymap)

        # check nearby obstacle
        is_obstacle = robot.check_nearby_obs(time)
        if is_obstacle:
            robot.d_position_limit = robot.step_len

        # if robot.motionmode==0:
        #     robot.update_target(time)
        # robot.update_target(time)
        cur_target = robot.target[time]
        if robot.motion_mode == 0:
            robot.update_motion_mode(time, mymap, cur_target)
        # update the target based on the motion-mode
        if robot.motion_mode == 1 and not robot.inside_tangent_planner:
            target_t = robot.target[time]
            print("start boundary follow")
            print("motion-mode:", robot.motion_mode)
            targets, boundary_follow_finished, followed_curve = robot.tangent_bug_planner(time, mymap)
            # if boundary_follow_finished:
            #     robot.followed_curve.remove([0, 0])
            #     sr, sc = get_middle_point(robot.followed_curve)
            #     print("sr,sc:", sr, sc)
            #     obstacle_color = -1
            #     robot.tarobsmap = flood_fill(robot, sr, sc, obstacle_color)
            cur_target = robot.get_target_from_tangent(time)
            robot.update_state_tangent(time, cur_target)

        elif robot.inside_tangent_planner and time < robot.tangent_end_time - 1:
            cur_target = robot.get_target_from_tangent(time)
            if robot.check_bug_neighbour(time):
                robot.reset_target(time)
                robot.update_state(time)
                robot.reset_tangent()
                print("******robot meet and stop boundary following******")
            else:
                cur_target = robot.get_target_from_tangent(time)
                robot.update_state_tangent(time, cur_target)
        elif not robot.boundary_follow_finished and time == robot.tangent_end_time - 1:
            if robot.check_bug_neighbour(time):
                robot.reset_target(time)
                robot.update_state(time)
                robot.reset_tangent()
                print("******robot meet and stop boundary following******")
            else:
                cur_target = robot.get_target_from_tangent(time)
                robot.update_state_tangent(time, cur_target)

        elif robot.boundary_follow_finished and time == robot.tangent_end_time - 1:
            cur_target = robot.get_target_from_tangent(time)
            robot.update_state_tangent(time, cur_target)
            robot.followed_curve.remove([0, 0])
            sr, sc = get_middle_point(robot.followed_curve)
            print("sr,sc:", sr, sc)

            obstacle_color = -1
            robot.tarobsmap = flood_fill(robot, sr, sc, obstacle_color)
            print("********flood fill is done********")
            robot.reset_tangent()
        else:
            robot.update_target(time)
            robot.update_state(time)

    # merge the infomap of the robots
    coverage_percent = merge_infomap(robotList)
    c_percent[time] = coverage_percent

    # print log info
    print("Time step:", time)
    print("Coverage percent:", coverage_percent)
    if coverage_percent >= 0.95 or time > 600:
        print("Area Covered successfully with 95%")
        break

####################################################################
# Plots and animations
# plot the coverage percent
plot_coverage_percent(c_percent, time)
# plot the robot target position
plot_target_position(robotList, mymap, time)
# plot the robot path
plot_robot_path(robotList, mymap, time)
# show 2D animation
anim = visualize_motion(robotList, mymap, time)
# plot the information map of the robot
plot_robot_infomap(robotList, mymap)
