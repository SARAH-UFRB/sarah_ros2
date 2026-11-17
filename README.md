# `sarah_ros2`

This repo contains basic wrapper for SARAH robot comunication.

## Interface
### Overview

Basic set of nodes for robot monitore and control. Based in kobuki plataform comunication paterner.

### Tópicos Publicados
* `~cmd_vel` - informação do tóopico ([sensor_msgs/Image](http://docs.ros.org/api/sensor_msgs/html/msg/Image.html)) tipo de mensagem e link para a documentação do ROS

## Instalação

### 1. Copy o repositório
Copy the repo to your workspace source folder.
~~~
mkdir -p ~/ws/src
cd ~/ws/src
git clone https://github.com/SARAH-UFRB/sarah_ros2.git
~~~
### 2. Install any missing ROS packages
Use `rosdep` from the top directory of your workspace to install any missing ROS related dependency.
~~~
cd ~/ws
rosdep install --from-paths src --ignore-src -r -y
~~~



### 3. Configuring kobuki driver

Before running any driver, set up the udev rules so Ubuntu recognizes the robot at /dev/kobuki without requiring sudo.
• Download and install the udev rule. Run the following commands in your terminal:bash
~~~ 
wget https://raw.githubusercontent.com/kobuki-base/kobuki_ftdi/devel/60-kobuki.rules
sudo cp 60-kobuki.rules /etc/udev/rules.d/
sudo service udev reload
sudo service udev restart
~~~ 

### 3. Build your workspace
From the top directory of your workspace, use `colcon` to build your packages.
~~~
cd ~/ws
colcon build
~~~

## Using this package
