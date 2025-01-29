<style>
.right-aligned {
    text-align: right;
}
.center-aligned {
    text-align: center;
}
</style>

<p class="right-aligned">
   <strong>简体中文</strong>
<!-- Tips: When English document is ready, replace Line 2 with the following line:
    <strong>简体中文</strong> | <a href="./README.en.md">English</a>
-->
</p>

<div class="center-aligned">
# SSH Alert
_✨ 基于 Docker 实现的 SSH 蜜罐 ✨_
[![LICENSE](https://img.shields.io/badge/LICENSE-MIT-blue)](https://opensource.org/licenses/MIT)
[![知乎 - Kirsmin](https://img.shields.io/badge/知乎-Kirsmin-%23007AFF?style=flat-square&logo=zhihu&logoColor=white)](https://zhihu.com/people/kirsmin)
</div>

## 支持的平台

- Linux ARM 64 （已验证）
- Linux AMD 64
- Windows （未验证）

## 快速开始

1. 安装 Docker，具体方法：[Docker Docs](https://docs.docker.com/get-docker/)
2. 下载最新版本的 SSH Alert，地址：[GitHub Releases](https://github.com/KirsminX/SSHAlert/releases)
>! 提示：注意选择正确的架构
3. 修改 SSH 端口，注意**不要占用默认端口 22**，除非你在运行 SSH Alert 之前手动修改配置文件的 Port 值。具体方法自行查找
4. 启动 SSH Alert
```bash
# 对于 Linux
./ssh-alert start
# 对于 Windows
.\ssh-alert.exe start 
```
5. 查看日志
```bash
# 对于 Linux
./ssh-alert log
# 对于 Windows
.\ssh-alert.exe log
```

## 命令参数

**Linux**
`./ssh-alert [参数]`
**Windows**
`.\ssh-alert.exe [参数]`

**参数**
`（无参数）` 启动 SSH Alert
`start` 启动 SSH Alert 驻守进程
`stop` 停止 SSH Alert 驻守进程
`log` 查看 SSH Alert 日志（最新 25 条 + 概况）
`status` 查看 SSH Alert 状态（概况）
`update` 更新 SSH Alert
`docs` 打印命令列表
