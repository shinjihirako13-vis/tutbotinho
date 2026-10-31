## What I used

Ubuntu 22.04 on WSL2, ROS 2 Humble, Gazebo Classic, and Nav2.

## Install

```bash
sudo apt update
sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup ros-humble-gazebo-ros-pkgs ros-humble-rmw-cyclonedds-cpp ros-humble-rviz2
```

## Start the bot in Ubuntu terminal 1

```bash
cd ~/robot_projects/tutbotinho
source /opt/ros/humble/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export ROS_LOCALHOST_ONLY=1
export ROS_DOMAIN_ID=0
export CYCLONEDDS_URI='<CycloneDDS><Domain><Discovery><ParticipantIndex>auto</ParticipantIndex><MaxAutoParticipantIndex>100</MaxAutoParticipantIndex></Discovery></Domain></CycloneDDS>'
ros2 launch nav2_bringup tb3_simulation_launch.py headless:=True use_rviz:=False use_composition:=False world:="$PWD/worlds/warehouse.world" map:="$PWD/maps/warehouse.yaml" x_pose:=-4.6 y_pose:=-2.4
```


## Set its starting position and open Gazebo and RViz in Ubuntu terminal 2

```bash
source /opt/ros/humble/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export ROS_LOCALHOST_ONLY=1
export ROS_DOMAIN_ID=0
export CYCLONEDDS_URI='<CycloneDDS><Domain><Discovery><ParticipantIndex>auto</ParticipantIndex><MaxAutoParticipantIndex>100</MaxAutoParticipantIndex></Discovery></Domain></CycloneDDS>'
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped "{header: {frame_id: map}, pose: {pose: {position: {x: -4.6, y: -2.4, z: 0.0}, orientation: {w: 1.0}}}}"
gzclient &
LIBGL_ALWAYS_SOFTWARE=1 rviz2 -d /opt/ros/humble/share/nav2_bringup/rviz/nav2_default_view.rviz --ros-args -p use_sim_time:=true &
```


In RViz, click **Nav2 Goal**, then click and drag on an open part of the map and voila.
