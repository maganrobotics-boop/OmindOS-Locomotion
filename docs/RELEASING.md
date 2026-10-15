# 源程序与发布版维护

| 仓库 | 维护内容 |
| --- | --- |
| `maganrobotics-boop/OmindOS-Locomotion` | 开发源码、配置、资产锁定清单、测试、使用文档、打包脚本 |
| `maganrobotics-boop/OmindOS-Locomotion-Release` | 用户下载入口、版本记录、对应源码提交、发布工作流和 Releases 附件 |

`omindos` 中的旧双足源码与 `0.1.0a2` Release 保留为历史记录。后续改程序到 `OmindOS-Locomotion` 提交，下载和分发版本到 `OmindOS-Locomotion-Release`。

## 准备新版本

1. 在源程序仓库修改代码并运行带实际资产的测试和 20 秒基准仿真。
2. 同时更新 `pyproject.toml` 与 `src/omindos_legged/__init__.py` 的版本；在 `docs/releases/<版本>.md` 写本版说明，更新 `docs/USAGE.zh-CN.md` 的文件名和步骤。
3. 检查 `requirements-sim.txt`、固定上游清单、第三方通知；记录本版验收范围。构建 wheel、sdist 后执行 `python scripts/package_release.py --output dist`。
4. 将变更合入源程序仓库 `main`，等源码 CI 通过。记录该提交的完整 40 位 SHA。源码 CI 只检查和提供构建产物，不创建公开 Release。
5. 在发布仓库更新 `release-source.json` 的 `version`、`source_commit`，以及对应版本的 README、使用指南、依赖清单和说明。提交发布仓库 `main` 会对固定源码重新执行检查和构建，**全部通过后自动创建该版本 Release 及标签**。推送这份版本清单之前须已有项目负责人发布授权。
6. 如需重新执行，可在发布仓库的 Actions 中手动运行并选择 `publish_release=true`。已存在的版本会保留；不要通过修改附件覆盖旧版本。

发布仓库工作流从源程序仓库的完整 SHA 检出代码，不使用会漂移的 `main` 来生成已经命名的发布版；它必须核对配置和 Python 包的版本一致。Alpha、Beta、RC 版本保持 GitHub Pre-release 标记。仅修改发布仓库说明页不触发自动发布；更改版本清单或发布工作流才触发。工作流拒绝带未提交修改的构建。

## 发布附件

- wheel：安装包，保留软件许可及资产清单，不含模型/策略二进制。
- sdist：Python 标准源码发行包。
- `legged-robot-<版本>-source.zip`：完整受 Git 跟踪的程序源码快照，包括文档、测试与回放部署源码；不收集运行缓存。
- `USAGE.zh-CN.md`、`requirements-sim.txt`：独立可读的安装指南与已验收仿真依赖。
- `SHA256SUMS.txt`：上述所有附件的校验值。

打包脚本会把源程序 SHA 写入版本说明与构建元数据。发布页自动生成的 `Source code` 归档只对应发布仓库，因此页面须明确引导用户下载带 `-source.zip` 的完整程序附件。

本版发布不部署网页或更新服务器仿真环境；这两类变更分别验收。
