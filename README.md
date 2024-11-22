# jsnu_netkit

`jsnu_netkit`是一个跨平台（Windows、macOS、Linux）的 Python 脚本，用于实现江苏师范大学校园网络环境下开机自动登录。脚本能够检测是否连接到校园网络，并根据用户提供的账号和密码完成登录操作，从而省去每次手动输入的麻烦。

## 功能特性

- 自动网络检测：脚本能够识别当前连接的网络是否为目标网络。
- 跨平台支持：适配 Windows、macOS 和 Linux 系统；
- 可配置性：支持用户自定义登录接口参数。

## 安装步骤

### 1.克隆项目
```shell
git clone git@github.com:shelhen/jsnu_netkit.git
```
这里记住项目文件 `jsnu_netkit.py`的绝对路径，为描述方便，以下简称为`script_path`。

### 2.安装依赖
```python
pip install requests parsel pycryptodome psutil
```
建议将`python`添加至系统或用户环境，环境安装在基环境目录中。

### 3.配置开机自启

- Windows

Windows 通过批处理文件 `(.bat) `脚本设置开机启动，输入`win + R`，输入`shell:startup`点击确定进入启动项目录，
在目录中新建`setup_windows.bat`，在其中粘贴如下代码：
```bash
@echo off
pythonw <script_path> <username> <password> <server>
exit
```
其中`<script_path>`应是脚本文件的绝对路径，`<username>`和`<password>`分别为自己登录校园网的账号和密码，`<server>`是自己的服务商，可选填入 “中国电信”、“中国移动”或“中国联通”，例如：`pythonw C:\...\jsnu_netkit\jsnu_netkit.py 20202*0078 password123 中国电信`。 
- Mac

`mac`系统中通过编写自启动的 `Shell` 脚本实现。

首先在任意路径新建名为`jsnu_netkit.sh`的脚本文件，内容如下：
```shell
# 激活环境
source ~/projects/envs/common/bin/activate
python3 <script_path> <username> <password> <server>
```
其中`<script_path>`应是脚本文件的绝对路径，`<username>`和`<password>`分别为自己登录校园网的账号和密码，`<server>`是自己的服务商，可选填入 “中国电信”、“中国移动”或“中国联通”，例如：`python3 ~/jsnu_netkit/jsnu_netkit.py 20202*0078 password123 中国电信`。 

其次，赋予脚本执行权限，打开终端，在其中输入：
```bash
chmod +x ./jsnu_netkit.sh
```
最后，打开终端进入文件夹`~/Library/LaunchAgents`新建文件`com.jsnu.netkit.plist`，内容如下：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.jsnu.netkit</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/****/projects/jsnu_netkit/jsnu_netkit.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```
其中 `ProgramArguments`参数对应的`string`中填入自己新建的 `jsnu_netkit.sh`绝对路径，如：`/Users/*****/projects/jsnu_netkit/jsnu_netkit.sh`，`label`标签对应的`string`应该是该文件去掉后缀的文件名。 然后打开终端执行：
```shell
# 检查任务格式是否正确
plutil -lint com.jsnu.netkit.plist
# .... ok

# 加载开机自动任务
launchctl load -w com.jsnu.netkit.plist
# 查看当前任务中包含 com.jsnu 的任务
launchctl list | grep com.jsnu
# -   78    com.jsnu.netkit # 错误结果
# -   0     om.jsnu.netkit # 正确结果
```
从爱师大登出设备，重新启动pc测试是否已经正常连接网络。


- Linux
暂不支持。

## 贡献
欢迎提交 Issue 和 Pull Request！
- Fork 本项目。
- 创建特性分支：`git checkout -b feature/your-feature`。
- 提交改动：`git commit -m 'Add your feature'`。
- 推送分支：`git push origin feature/your-feature`。
- 提交 `Pull Request`。

## 许可证

本项目采用 MIT 许可证。





