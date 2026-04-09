# Note: Full integrated marker detection coming soon.
# Setup Instructions

## Prerequisites

- ROS2 - Humble
- Slam Toolbox
- Turtlebot3 Package
- TurtleBot3 workspace (`turtlebot3_ws`)

## Installation

1. **Clone this repository into your TurtleBot3 workspace:**

```bash
cd ~/turtlebot3_ws/src
git clone https://github.com/Kmyming/CDE2310_G10_2526.git CDE2310_G10_2526
cd ~/turtlebot3_ws
```

2. **Build the auto_explore package using colcon:**

```bash
colcon build --packages-select auto_explore
source install/setup.bash
```

3. **Verify the build was successful:**

```bash
ros2 pkg list | grep auto_explore
```

Expected output:
```
auto_explore
```


# How to Run

## NEW: Independent Auto-Explore System (Recommended)

**Package Name:** `auto_explore` (completely independent mission control system)

### Setup

Build the `auto_explore` package:

```bash
cd ~/turtlebot3_ws
colcon build --packages-select auto_explore
source install/setup.bash
```

### Launch Sequences

#### Gazebo Simulation

**Terminal 1:** Launch default Gazebo world

```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

**Terminal 2:** Launch auto_explore mission control system

```bash
ros2 launch auto_explore global_bringup.py \
  use_sim_time:=true \
  enable_slam:=true \
  enable_rviz:=true \
  enable_markers:=true
```

#### Physical TurtleBot3 Robot

**Terminal 1:** Run TurtleBot3 bringup

```bash
# If 'rosbu' alias is set up:
rosbu

# Otherwise:
ros2 launch turtlebot3_bringup robot.launch.py
```

**Terminal 2:** Launch auto_explore mission control system

```bash
ros2 launch auto_explore global_bringup.py \
  use_sim_time:=false \
  enable_slam:=true \
  enable_rviz:=true \
  enable_markers:=true
```

### Launch Components

This launches:
- **SLAM Toolbox** (mapping) - enabled with `enable_slam:=true`
- **RViz** (visualization) - enabled with `enable_rviz:=true`
- **FSM Controller** (mission state machine)
- **Exploration Controller** (frontier-based autonomous navigation)
- **ArUco Marker Detection** (pose publisher) - enabled with `enable_markers:=true`
- **Marker Logger** (logging marker detections to `./logs/`)

### Launch Arguments

```bash
use_sim_time:=true|false      # Use Gazebo time (true) or real time (false)
enable_slam:=true|false        # Enable SLAM Toolbox mapping
enable_rviz:=true|false        # Enable RViz visualization
enable_markers:=true|false     # Enable ArUco marker detection
```

### Architecture

The `auto_explore` package contains:
- **global_bringup.py** - Entry point with component control flags
- **nav_bringup.py** - Navigation infrastructure (SLAM, RViz)
- **global_controller_bringup.py** - Mission logic (FSM, exploration, markers)
- **mission_controller.py** - FSM state machine orchestration
- **exploration_controller.py** - Frontier-based autonomous exploration
- **pose_publisher.py** - ArUco marker detection
- **pose_subscriber.py** - Marker logging with rolling buffer
- **config/params.yaml** - Local exploration tuning parameters

---

## ⚙️ SLAM Optimization - Required Configuration

**⚠️ IMPORTANT:** All team members must update the SLAM Toolbox parameters to improve map responsiveness and accuracy. This is a required setup step before running any autonomous exploration missions.

### Update SLAM Mapper Parameters

Navigate to the SLAM Toolbox configuration directory and update the `mapper_params_online_async.yaml` file:

```bash
# Edit the configuration file
nano /opt/ros/humble/share/slam_toolbox/config/mapper_params_online_async.yaml
```

Apply the following parameter changes to improve SLAM efficiency and map responsiveness:

```yaml
slam_toolbox:
    ros__parameters:
    
    solver_plugin: solver_plugins::CeresSolver
    ceres_linear_solver: SPARSE_NORMAL_CHOLESKY
    ceres_preconditioner: SCHUR_JACOBI
    ceres_trust_strategy: LEVENBERG_MARQUARDT
    ceres_dogleg_type: TRADITIONAL_DOGLEG
    ceres_loss_function: None

    odom_frame: odom
    map_frame: map
    base_frame: base_footprint
    scan_topic: /scan
    use_map_saver: true
    mode: mapping

    debug_logging: false
    throttle_scans: 1
    transform_publish_period: 0.02
    map_update_interval: 1.0        # was 5.0 - faster map updates
    resolution: 0.05
    min_laser_range: 0.12           # was 0.0 - match LiDAR's (LDS-02) actual min range
    max_laser_range: 3.5            # was 20.0 - match LiDAR's (LDS-02) actual max range
    minimum_time_interval: 0.2      # was 0.5 - process scans more frequently
    transform_timeout: 0.2
    tf_buffer_duration: 30.
    stack_size_to_use: 40000000
    enable_interactive_mode: true

    use_scan_matching: true
    use_scan_barycenter: true
    minimum_travel_distance: 0.2    # was 0.5 - update after smaller movements
    minimum_travel_heading: 0.2     # was 0.5 - update after smaller rotations
    scan_buffer_size: 10
    scan_buffer_maximum_scan_distance: 3.5  # match max_laser_range
    link_match_minimum_response_fine: 0.1  
    link_scan_maximum_distance: 1.5
    loop_search_maximum_distance: 3.0
    do_loop_closing: true 
    loop_match_minimum_chain_size: 10           
    loop_match_maximum_variance_coarse: 3.0  
    loop_match_minimum_response_coarse: 0.35    
    loop_match_minimum_response_fine: 0.45

    correlation_search_space_dimension: 0.5
    correlation_search_space_resolution: 0.01
    correlation_search_space_smear_deviation: 0.1 

    loop_search_space_dimension: 8.0
    loop_search_space_resolution: 0.05
    loop_search_space_smear_deviation: 0.03

    distance_variance_penalty: 0.5      
    angle_variance_penalty: 1.0    
    fine_search_angle_offset: 0.00349     
    coarse_search_angle_offset: 0.349   
    coarse_angle_resolution: 0.0349        
    minimum_angle_penalty: 0.9
    minimum_distance_penalty: 0.5
    use_response_expansion: true
    min_pass_through: 2
    occupancy_threshold: 0.1
```

### Key Changes Summary

The critical improvements made:
- **`map_update_interval`**: Reduced from 5.0 to 1.0 seconds for faster map updates
- **`min_laser_range`**: Set to 0.12 to match LiDAR (LDS-02) actual minimum range
- **`max_laser_range`**: Set to 3.5 to match LiDAR (LDS-02) actual maximum range
- **`minimum_time_interval`**: Reduced from 0.5 to 0.2 for more frequent scan processing
- **`minimum_travel_distance`**: Reduced from 0.5 to 0.2 for updates after smaller movements
- **`minimum_travel_heading`**: Reduced from 0.5 to 0.2 for updates after smaller rotations

These changes ensure the map updates more responsively as the robot explores, resulting in better real-time mapping performance and more accurate frontier detection for autonomous exploration.

---

## LEGACY: Manual Launch (For Testbedding & Reference)

### Installation (Legacy - autonomous_exploration package)

If you want to use the old `autonomous_exploration` package:

```bash
cd ~/turtlebot3_ws/src
git clone https://github.com/Kmyming/CDE2310_G10_2526.git autonomous_exploration
cd ~/turtlebot3_ws
colcon build --packages-select autonomous_exploration
source install/setup.bash
```

Verify:
```bash
ros2 pkg list | grep autonomous_exploration
```

### Manual Component Launch

If you prefer to run components separately:

1. **Launch the Map Node (SLAM):**

```bash
ros2 launch slam_toolbox online_async_launch.py
```

2. **Launch the Gazebo simulation environment:**

```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

3. **View the environment map in RViz:**

```bash
rviz2 -d ~/turtlebot3_ws/src/turtlebot3/turtlebot3_cartographer/rviz/tb3_cartographer.rviz
```

4. **Run the autonomous exploration package:**

```bash
ros2 run autonomous_exploration control
```

# CI/CD & Automated AI Code Review & Changelog Infrastructure

This repository uses a custom CI/CD pipeline powered by [Qodo PR-Agent](https://github.com/qodo-ai/pr-agent) and Google's **Gemini 2.5 Flash** model to automate pull request management and documentation, standardize our release documentation, enforce Semantic Versioning (SemVer 2.0.0), and reduce administrative overhead. 

Whenever a new Pull Request is opened, the pipeline automatically executes the following suite:
1. **Hardware-Aware Commit Scraping:** Bypasses Git's "binary blindspot" by scraping local git history to document physical CAD changes (`.SLDPRT`, `.STL`, etc.) before the AI runs.
2. **Auto-Describe:** Analyzes the code diff and commit history to automatically write a comprehensive PR Title and Description.
3. **Auto-Review & Improve:** Scans the code for bugs and leaves actionable, inline code suggestions.
4. **Auto-Changelog:** Generates a strict, version-bumped `CHANGELOG.md` block based on your branch's features and fixes.


## 🛠️ The Developer Workflow

To ensure our documentation remains perfectly synced with our codebase, all team members must follow this workflow when merging code into the `main` branch.

### 1. Write Conventional Commits
Make sure you are editing on your **LOCAL BRANCH** and not the `main` branch!

The AI agent calculates the next version number strictly based on the prefixes used in your commit messages and PR title. You **must** use one of the following prefixes:

* `feat: ` (New features, architectural additions, nodes. 'MAJOR' is to be included in the commit message for MAJOR versioning, else it defaults to MINOR versioning)
* `fix: ` (Bug fixes, path resolutions, logic errors)
* `docs: ` (Updates to README, comments, or documentation)
* `test: ` (Adding or updating tests/simulations)

for hardware/CAD changes: **BE DESCRIPTIVE** in your commit messages as the CHANGELOG.md will be updated based on your commit messages.

*Example: `feat(navigation): integrate frontier exploration algorithm`*

### 2. Open a Pull Request

Push your code to your **LOCAL BRANCH** and push that branch to GitHub.
```bash
git push origin [local_branch_name]
```
Open a Pull Request against `main`. 
if you have Github CLI:
```bash
gh pr create --fill
```
(auto-fills latest commit message as title)
* **The Auto-Review & changelog update:** The GitHub Action will immediately wake up, analyze your code diffs, and post a summary of your changes as a comment on the PR. **VERIFY** the documentation on your own and make necessary edits.

**Manual Commands:**
If you need the AI to re-run a specific task, you can type any of these commands as a standard comment in your Pull Request thread:
* `/update_changelog` - Regenerates the changelog.
* `/describe` - Regenerates the PR description.
* `/review` - Re-runs the high-level review.
* `/improve` - Scans for new inline code improvements.
* `/ask [question]` - Ask the AI a specific question about the PR's code.

## 🏗️ AI Pipeline Architecture

This repository utilizes a highly customized, hardware-aware CI/CD pipeline, reads binary CAD diffs (e.g., SolidWorks, STL files) by using a pre-processing commit scraper combined with a native Python implementation of [Qodo PR-Agent](https://github.com/qodo-ai/pr-agent), powered by **Google Gemini 2.5 Flash**.

### Data Flow Diagram

```mermaid
sequenceDiagram
    actor Developer
    participant GitHub as GitHub Actions
    participant Scraper as Context Scraper (Bash)
    participant Agent as PR-Agent CLI (Python)
    participant Gemini as Gemini 2.5 Flash

    Developer->>GitHub: Open PR or Post Comment
    GitHub->>Scraper: Trigger Workflow (fetch-depth: 0)
    Scraper->>GitHub: Read git log & inject commits into PR Body
    GitHub->>Agent: Initialize raw Python environment
    Agent->>Gemini: Send code diff + commit history payload
    Note right of Agent: 1,000,000 token limit override
    Gemini-->>Agent: Return generated reviews & changelog
    Agent->>GitHub: Update PR Description, Post Reviews, Update CHANGELOG.md