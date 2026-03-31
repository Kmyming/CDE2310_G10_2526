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

### 3. Trigger the Changelog Update
Once you are satisfied with your code and ready to merge, reply to the PR comment section with this exact command:
```text
/update_changelog
```
---

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