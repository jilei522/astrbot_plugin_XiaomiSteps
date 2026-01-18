# AstrBot 运动步数修改插件 (v1.1)

这是一个为 AstrBot 开发的插件，用于通过指定接口修改运动步数。

## 功能介绍

- 支持用户通过 `账号#密码#步数` 格式修改步数。
- **配置管理**: 支持在 AstrBot 管理面板直接修改 API Key 和接口地址。

## 使用方法

在聊天框输入以下格式：
`账号#密码#步数`

**示例：**
`test@qq.com#123456#18000`

## 配置说明

插件安装后，您可以通过以下两种方式修改 API Key：
1. **Web 管理面板**: 在插件管理页面找到 "XiaomiSteps"，点击配置即可看到 `ckey` 输入框。
2. **配置文件**: 修改 `data/config/XiaomiSteps_config.json` 文件。

## 安装说明

1. 在 `data/plugins` 下创建 `xiaomi_steps` 文件夹。
2. 将 `main.py`、`_conf_schema.json` 放入该文件夹。
3. 重启 AstrBot。
