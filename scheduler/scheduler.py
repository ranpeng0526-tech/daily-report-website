"""
定时任务配置 — macOS launchd 方案

不需要常驻进程。macOS 系统到点自动启动 Python，跑完即退出，零内存占用。

=== 安装 ===

1. 修改 com.dailyreport.plist 中的路径（如果项目不在默认位置）

2. 复制到 LaunchAgents 目录：
   cp com.dailyreport.plist ~/Library/LaunchAgents/

3. 加载任务：
   launchctl load ~/Library/LaunchAgents/com.dailyreport.plist

=== 管理命令 ===

   查看状态： launchctl list | grep com.dailyreport
   手动触发： launchctl start com.dailyreport
   停止任务： launchctl unload ~/Library/LaunchAgents/com.dailyreport.plist
   查看日志： cat launchd_stdout.log

=== 执行时间 ===

   北京时间 19:00（周一至周五），对应美东夏令时 7:00 AM（冬令时请改为 20:00）
"""

if __name__ == "__main__":
    print(__doc__)
