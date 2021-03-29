#!/bin/bash

# meant to be used with adore_ci docker container
# in the context of a gitlab ci job

# setup script to fail if any one of the following command fails
set -Eeuxo pipefail

echo "just testing "


# setup and run simulation
export ROS_DISTRO=noetic
export ROS_MASTER_URI=http://localhost:11351
export SUMO_HOME=/home/adore_workspace_dir/src/adore/sumo


#source /opt/ros/noetic/setup.bash
source /home/adore_workspace_dir/install/setup.bash

#sudo echo "source /home/adore_workspace_dir/install/setup.bash" >> ~/.bashrc
#source ~/.bashrc
cd /home/adore_workspace_dir/src/adore/test/ci
roscore -p 11351 &
sleep 1
timeout 120 roslaunch -p 11351 --wait test001_parking.launch > /home/outputdir/build/test_ci_1.log
#mv /home/outputdir/build/test_ci_1*bag /home/outputdir/build/test_ci_1.bag
chmod +x ModelChecker.py
python3 ModelChecker.py -i /home/outputdir/build/test_ci_1.bag -o /home/outputdir/build/test_ci_1.txt -t /vehicle1/ENV/propositions /vehicle1/VEH/ax /vehicle1/odom /vehicle1/traffic
EVAL=$(head -n 1 /home/outputdir/build/test_ci_1.txt)
if [ "$EVAL" = "test passed" ]; then echo "test1" >> /home/outputdir/build/variables && echo $EVAL; else EVAL=false && echo $EVAL && exit 1; fi

