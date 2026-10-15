# OmindOS Locomotion 使用指南 · 0.1.0a3

这个版本用于在自己的 Linux 电脑或服务器上运行 **Roboto Origin 双足机器人平地仿真**，可输出运动记录和视频，也提供可选的 ROS 2 速度/状态接口。

- 源程序和开发：[OmindOS-Locomotion](https://github.com/maganrobotics-boop/OmindOS-Locomotion)。
- 安装包和版本下载：[OmindOS-Locomotion-Release · 0.1.0a3](https://github.com/maganrobotics-boop/OmindOS-Locomotion-Release/releases/tag/legged-robot-v0.1.0a3)。
- 只想观看演示：打开 [在线仿真回放](https://cloud.omindos.cn/legged-robot/)，可以播放、暂停、跳转阶段。它播放已有计算结果；启动新仿真请用下面的命令。线上回放显示自己的实际运行版本，安装包发布不会改写历史记录。

## 1. 先选对下载文件和环境

| Release 中的文件 | 用途 |
| --- | --- |
| `omindos_legged_robot-0.1.0a3-py3-none-any.whl` | 推荐给使用者的 Python 安装包，安装后得到 `legged-robot` 命令 |
| `requirements-sim.txt` | 已验收的 Python 3.12 仿真依赖版本，与 wheel 一起下载 |
| `USAGE.zh-CN.md` | 本使用指南，可单独下载阅读 |
| `legged-robot-0.1.0a3-source.zip` | 完整程序源码快照，含文档、测试和回放页面源码；用于阅读或修改程序 |
| `omindos_legged_robot-0.1.0a3.tar.gz` | 标准 Python 源码发行包，供构建工具使用 |
| `SHA256SUMS.txt` | 校验上述文件的 SHA256 |

GitHub 页面底部自动生成的 `Source code (zip/tar.gz)` 是**发布仓库本身**的文件。需要机器人程序源码时，请下载上表中名称带 `-source.zip` 的附件，或进入源程序仓库。

已验收环境为 Linux x86_64、Python 3.12、CPU 推理；普通物理计算不要求 NVIDIA GPU、CUDA、Isaac Sim 或 ROS 2。Windows、macOS、ARM 和实机不在本版验收范围。基础 Python 接口声明支持 Python 3.10 及以上，但本页固定仿真依赖按 Python 3.12 验收。

首次安装需要访问 Python 包源和 GitHub 上游资产，模型、网格和策略合计约 34.1 MB；Python 仿真依赖另行下载。模型不会塞进 wheel，也不会在 `simulate` 时自动下载。联网安装及 `fetch-assets` 完成后可在本机离线运行仿真；完整离线安装还需提前准备所用平台的 Python 依赖 wheel。

## 2. 安装发布版（推荐）

准备 Python 3.12，先运行 `python3.12 --version` 确认。把上述 `.whl`、`requirements-sim.txt` 和 `SHA256SUMS.txt` 下载到同一个新目录，然后在该目录打开终端。

以下命令逐行执行；后续章节默认仍在这个目录中：

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-sim.txt
python -m pip install './omindos_legged_robot-0.1.0a3-py3-none-any.whl[sim]'
python -c 'import omindos_legged; print(omindos_legged.__version__)'
legged-robot list
```

版本应输出 `0.1.0a3`，`list` 应包含 `roboto-origin`、`biped` 和 `dof: 23`。不需要 `sudo pip`，也不需要 `colcon build`。这个包通过 pip 安装，不是需要编译的 ROS 工作区。

校验下载文件：

```bash
sha256sum --ignore-missing -c SHA256SUMS.txt
```

此命令只检查已经下载的附件，其他附件会跳过。检查输出中 `.whl` 和 `requirements-sim.txt` 均为 `OK`。

首次显式下载并核验模型、配置和策略：

```bash
legged-robot fetch-assets --asset-dir assets/roboto-origin
```

成功时结果包含 `files: 34`；首次正常下载通常为 `downloaded: 34`，再次执行则复用通过校验的缓存。下载失败可在网络恢复后重复同一命令，已完成且哈希正确的文件不会重复下载。所有运行命令使用同一个 `--asset-dir`。

## 3. 运行第一次完整仿真

```bash
legged-robot simulate --robot roboto-origin \
  --asset-dir assets/roboto-origin \
  --scenario baseline --duration 20 --output outputs/baseline
```

这是一个新的、从初始姿态开始的物理仿真，流程固定为：

| 仿真时间 | 动作指令 |
| --- | --- |
| 0–3 秒 | 站立，速度指令为零 |
| 3–10 秒 | 向前，`vx=0.3 m/s` |
| 10–14 秒 | 前进并转向，`vx=0.3 m/s`、`wz=0.3 rad/s` |
| 14–20 秒 | 速度指令归零，过渡到停车 |

成功时终端显示 `status: completed`、`simulated_duration_s` 约 20，并返回退出码 0。输出在当前目录的 `outputs/baseline/`：

| 输出 | 怎么看 |
| --- | --- |
| `summary.json` | 运行状态、控制步数、生效速度范围、初末姿态和统计 |
| `simulation.csv` | 初始状态加每个控制周期的记录；20 秒基准应有 1,001 条数据，可用表格软件或 Python 读取 |
| `simulation.mp4` | 只有加 `--video` 时生成的运动视频 |

`--duration 20` 是物理仿真时间，不保证电脑正好运行 20 秒；默认尽快计算，加 `--realtime` 会按实际时间节奏推进。浮点计时接近 20 即可。基准场景要求至少 20 秒，不要改成 5 秒。普通 `simulate` 生成文件，不会自动弹出三维窗口。

每次重新运行从初始状态开始。要保留前次结果，请更换 `--output` 目录；同一目录内的同名日志会被覆盖。按 `Ctrl+C` 可以中断当前计算，`summary.json` 会记录 `interrupted`。

## 4. 改速度、站立和转向

使用 `constant` 场景时，`--vx`、`--vy`、`--wz` 在整个运行期间作为固定指令；`baseline` 会按自己的时间表运行，不采用这些参数来修改阶段动作。

```bash
# 前进 10 秒
legged-robot simulate --asset-dir assets/roboto-origin \
  --scenario constant --vx 0.3 --vy 0 --wz 0 \
  --duration 10 --output outputs/forward

# 原地站立 5 秒
legged-robot simulate --asset-dir assets/roboto-origin \
  --scenario constant --vx 0 --vy 0 --wz 0 \
  --duration 5 --output outputs/stand

# 前进并左转 10 秒（正偏航角速度）
legged-robot simulate --asset-dir assets/roboto-origin \
  --scenario constant --vx 0.3 --vy 0 --wz 0.3 \
  --duration 10 --output outputs/turn
```

| 参数 | 含义与单位 | 本版指令范围 |
| --- | --- | --- |
| `--vx` | 机身前后速度，m/s | -0.4～0.6 |
| `--vy` | 机身侧向速度，m/s | -0.4～0.4 |
| `--wz` | 机身偏航角速度，rad/s | -0.8～0.8 |

超出范围会被钳制，并在 JSON 中记录请求值与生效值；NaN 和无穷值会被拒绝。上述范围来自锁定的官方策略配置，是命令范围，不是机器人最高实测速度。实际速度请看 CSV 的 `vx_body`、`vy_body`、`wz_body`。关节越限、倾斜或数值故障会触发停止并记录 `fault_reason`；检查结果后重新启动仿真。

## 5. 输出可播放视频

Linux 需安装 Mesa/EGL 渲染库和带 `libx264` 编码器的 `ffmpeg`。在 Ubuntu/Debian 上可先安装系统依赖：

```bash
sudo apt-get update
sudo apt-get install ffmpeg libegl1 libgl1 libgl1-mesa-dri
MUJOCO_GL=egl legged-robot simulate --asset-dir assets/roboto-origin \
  --scenario baseline --duration 20 --output outputs/video --video
```

打开 `outputs/video/simulation.mp4` 观看，分辨率为 720×540，帧率为 20 fps。CPU 软件渲染可能明显慢于不带视频的仿真；服务器上 20 秒视频可能需要数分钟。

若服务器没有可用显卡，但 Mesa 软件渲染已配置，可以尝试：

```bash
MUJOCO_GL=egl LIBGL_ALWAYS_SOFTWARE=1 LP_NUM_THREADS=1 \
  legged-robot simulate --asset-dir assets/roboto-origin \
  --scenario baseline --duration 20 --output outputs/video-software --video
```

若只想验证机器人是否能运行，先去掉 `--video`，这样无需 GL 渲染环境。没有 ffmpeg 时，可在下载目录安装 OpenCV 后备编码依赖：`python -m pip install './omindos_legged_robot-0.1.0a3-py3-none-any.whl[video]'`。后备编码为 `mp4v`，部分浏览器可能不支持，建议使用 ffmpeg 的 H.264。本版安装使用下载的本地 wheel，不依赖 PyPI 上是否存在同名发行版本。

## 6. 查看模型和接入自己的程序

安装并获取资产后：

```bash
legged-robot describe --asset-dir assets/roboto-origin --output outputs/description
```

生成 `description.json` 与网格路径解析后的 `robot.urdf`。描述检查不运行策略、不需要 MuJoCo；如果仅预置模型描述文件，不要求同时预置策略。这个检查证明模型能加载，不能代替行走验收。

Python 中使用的导入名是 `omindos_legged`：

```python
from omindos_legged.profiles import create_controller
from omindos_legged.types import VelocityCommand

controller = create_controller("roboto-origin", "assets/roboto-origin")
try:
    # 50 Hz 策略；每步推进 0.02 秒，以下运行 5 秒仿真。
    for _ in range(250):
        state = controller.step(VelocityCommand(vx=0.3))
        if state.status == "fault":
            raise RuntimeError(state.fault_reason)
    print(state.to_dict())
finally:
    controller.close()
```

该例每一步主动提供固定指令；接入外部导航或任务程序时请使用 `CommandGate` 和时效检查，示例见源程序仓库的 README。

## 7. 可选 ROS 2 接口

ROS 2 不属于普通仿真的必装项。ROS 2 桥接已有接口及单元测试，**尚未在原生 ROS 2 图完成端到端验收**。以下是集成步骤，不属于已验证的完整导航方案。

Ubuntu 22.04/ROS 2 Humble 应使用发行版匹配的系统 Python 3.10。不要复用前述 Python 3.12 虚拟环境，也不要直接套用 `requirements-sim.txt` 的 Python 3.12 固定版本。在单独目录放置发布 wheel，并先准备 ROS 2 Humble，然后：

```bash
sudo apt-get install ros-humble-ros-base ros-humble-geometry-msgs \
  ros-humble-nav-msgs ros-humble-sensor-msgs ros-humble-std-msgs ros-humble-tf2-ros
source /opt/ros/humble/setup.bash
/usr/bin/python3 -m venv --system-site-packages .venv-ros
source .venv-ros/bin/activate
python -m pip install './omindos_legged_robot-0.1.0a3-py3-none-any.whl[sim]'
legged-robot fetch-assets --asset-dir assets/roboto-origin
legged-robot ros2 --asset-dir assets/roboto-origin
```

另开终端，`source /opt/ros/humble/setup.bash` 后发布前进指令并观察状态：

```bash
ros2 topic pub --rate 10 /legged_robot/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 0.3, y: 0.0}, angular: {z: 0.0}}'
```

再开终端可执行 `ros2 topic echo /legged_robot/state` 或 `ros2 topic hz /legged_robot/odom`。停止指令发布后，0.5 秒超时看门狗会把后续指令归零；机器人仍需步态过渡。退出桥接节点用 `Ctrl+C`。

默认输入为 `/legged_robot/cmd_vel`；输出为 `/legged_robot/joint_states`、`/legged_robot/odom`、`/legged_robot/state`。默认 TF 为 `legged_robot/odom → legged_robot/base_link`。桥接本身不弹出三维窗口；RViz/robot_state_publisher 与 Nav2 的坐标、时间、消息类型和缺失组件见[完整 ROS 2 说明](https://github.com/maganrobotics-boop/OmindOS-Locomotion/blob/main/docs/ROS2.md)。

## 8. 开发源码怎么用

开发主线在 `OmindOS-Locomotion`，发布包在 `OmindOS-Locomotion-Release`。想修改代码时克隆源程序仓库：

```bash
git clone https://github.com/maganrobotics-boop/OmindOS-Locomotion.git
cd OmindOS-Locomotion
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-sim.txt
python -m pip install -e '.[sim,test]'
legged-robot fetch-assets --asset-dir assets/roboto-origin
OMINDOS_LEGGED_TEST_ASSETS="$PWD/assets/roboto-origin" python -m pytest
legged-robot simulate --asset-dir assets/roboto-origin \
  --scenario baseline --duration 20 --output outputs/baseline
```

`-e` 表示 Python 直接读取这个工作目录中的源码。要精确复现某个发布版，在安装前按发布仓库的 `release-source.json` 中的 `source_commit` 执行 `git checkout <source_commit>`；`main` 可能持续更新。自定义源码 ZIP 解压后的根目录是 `legged-robot-0.1.0a3/`，在该目录执行上述创建环境、安装和运行命令即可。

每次新开终端需回到自己的工作目录并运行 `source .venv/bin/activate`。也可以不用激活，直接运行 `.venv/bin/legged-robot ...`。改换工作目录时，使用资产的绝对路径，或设置 `OMINDOS_LEGGED_ASSETS`；本页显式的 `--asset-dir` 优先于环境变量。

## 9. 常见问题

| 现象 | 处理 |
| --- | --- |
| `python3.12: command not found` | 先准备 Python 3.12 及 venv 组件；不要把 ROS Humble 的系统 Python 强行换成 3.12 |
| `No matching distribution found` | 检查 Python 版本及平台。本页固定依赖用于 Python 3.12/Linux x86_64；同时确认包源可用 |
| `legged-robot: command not found` | 在安装目录激活 `.venv`，或使用 `.venv/bin/legged-robot` |
| `Missing or changed asset` | 对同一资产目录重新执行 `fetch-assets`；程序会校验并补齐资源 |
| 下载中断、GitHub 访问失败 | 恢复网络后重试；离线机可复制已验证的完整资产目录，保持目录结构及来源文件 |
| 没看到机器人窗口 | 普通命令输出日志；加 `--video` 后查看生成的 MP4，或打开在线回放 |
| EGL/OpenGL 或视频编码报错 | 先不带 `--video` 验证物理计算，再配置 Mesa/EGL 和 ffmpeg |
| `ROS2 support is unavailable` | 加载 ROS 环境，用匹配系统 Python 创建 `--system-site-packages` 环境；普通 `simulate` 不需要 ROS |
| `status: fault/error` 或退出码非零 | 打开本次 `summary.json` 的 `fault_reason`/`error`，保留日志后排查，不把部分运行视为成功 |

本版没有连接真实电机、加载自制四足 CAD、训练新策略或完成复杂地形/完整导航验收。软件采用 GPL-3.0-only；上游资产保留各自来源与许可。发布附件不内置模型、策略、CAD 或运行环境，具体范围见源程序仓库的 `THIRD_PARTY_NOTICES.md`。
