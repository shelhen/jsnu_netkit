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
pip install requests parsel pycryptodome
```
建议将`python`添加至系统或用户环境，环境安装在基环境目录中。

### 3.配置开机自启

- Windows


- Mac

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





