# 独立开发仓迁移

2026-10-15 按项目负责人指定，将双足程序的开发入口设为 [maganrobotics-boop/OmindOS-Locomotion](https://github.com/maganrobotics-boop/OmindOS-Locomotion)。

## 来源与兼容性

- 原目录：`maganrobotics-boop/omindos/apps/legged-robot`。
- 原源码提交：[c6881ed0882fa1837090d4e0388e420092a6ed14](https://github.com/maganrobotics-boop/omindos/tree/c6881ed0882fa1837090d4e0388e420092a6ed14/apps/legged-robot)，包含服务器回放与 OriginMind 标识。
- 原模块合并提交：[c570524ff29f133ef558c2fd0b40b4b92898105a](https://github.com/maganrobotics-boop/omindos/commit/c570524ff29f133ef558c2fd0b40b4b92898105a)，原发行标签 `legged-robot-v0.1.0a2` 保留。
- 34 个受 Git 跟踪文件移至新仓库根目录；运行时代码、测试、资产清单与原始 GPL 文本保持字节一致。说明、打包元数据和 CI 随独立仓库布局调整。
- 包名 `omindos-legged-robot`、模块名 `omindos_legged`、CLI `legged-robot`、版本 `0.1.0a2`、ROS 2 命名空间和默认速度范围不变。

上游模型、策略、CAD、运行视频、运行输出、虚拟环境及缓存不进入本仓库；固定资产清单仍要求显式下载与 SHA256 核验。

## 验证与发布

现有 `VALIDATION.json` 是原 `0.1.0a1` 的历史运行记录；`VALIDATION_DESCRIPTION_20261015.json` 是迁移前的描述与集成验证记录。两者保持原内容，不能当作新仓库重新执行全部验收的证据。

迁移当时根目录安装、测试与打包按 README 命令运行；初始 CI 允许主分支手动选择 `publish_release=true`。迁入主分支本身没有重发原发行包。

迁移时已从新仓库的 `src/` 执行全部 66 项测试（2.30 秒），使用已核验的外部固定资产缓存运行 20 秒平地基准，返回 `completed`。wheel 与 sdist 构建通过，wheel 保留 GPL 文本及原始资产清单，sdist 包含回放部署工具。独立源码 ZIP 的 CRC、清单范围和 SHA256 校验通过；没有把上游二进制资产加入包内。干净虚拟环境中的 wheel 安装、`legged-robot list` 与 23 关节模型 `describe` 通过；该描述检查本身不构成行走验收。

迁移不改变线上回放的 URL 或服务器已安装的软件，也不修改 Navigation 正式安装包及四足模块。本轮不连接真实电机；真实 ROS 2 图、导航闭环、复杂地形和长期稳定性仍沿用原验收限制。

## 后续确定的开发与发布分工

2026-10-15 项目负责人进一步明确：**OmindOS-Locomotion 放源程序，OmindOS-Locomotion-Release 放发布版**。从 `0.1.0a3` 起，本仓库保留开发源码、文档、测试及构建脚本，CI 执行检查和构建，不向本仓库创建 Release。发布仓库用 `release-source.json` 锁定本仓库的完整提交 SHA，重新执行检查，发布 wheel、对应源码包、使用指南、依赖清单和校验文件。操作见 [RELEASING.md](RELEASING.md)。
