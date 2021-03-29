#!/bin/bash

# meant to be used with adore_ci docker container
# in the context of a gitlab ci job

# setup script to fail if any one of the following command fails
set -Eeuxo pipefail

echo "just testing 2"


# setup and run simulation
export ROS_DISTRO=noetic
export ROS_MASTER_URI=http://localhost:11352
export SUMO_HOME=/home/adore_workspace_dir/src/adore/sumo


#source /opt/ros/noetic/setup.bash
source /home/adore_workspace_dir/install/setup.bash


cd /home/adore_workspace_dir/src/adore/test/ci
roscore -p 11352 &
sleep 1
timeout 120 roslaunch -p 11352 --wait test002_lane_following.launch  > /home/outputdir/build/test_ci_2.log
#mv /home/outputdir/build/test_ci_2*bag /home/outputdir/build/test_ci.bag
chmod +x ModelChecker.py
python3 ModelChecker.py --input /home/outputdir/build/test_ci_2.bag --output /home/outputdir/build/test_ci_2.txt --topic /vehicle2/ENV/propositions /vehicle2/VEH/ax /vehicle2/odom /vehicle2/traffic
EVAL=$(head -n 1 /home/outputdir/build/test_ci_2.txt)
if [ "$EVAL" = "test passed" ]; then echo "test2" >> /home/outputdir/build/variables && echo $EVAL; else EVAL=false && echo $EVAL && exit 1; fi


