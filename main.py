import requests
from cores.qqbot.global_object import AstrMessageEvent

class XiaomiStepsPlugin:
    """
    小米运动/运动步数修改插件 (支持配置管理)
    """
    def __init__(self, context=None, config=None) -> None:
        """
        AstrBot 会在实例化时自动注入 config
        """
        # 默认配置，防止注入失败
        self.config = config if config else {
            "ckey": "AB3X3HLKNXZI5FNPRG9G",
            "api_url": "https://tmini.net/api/xiaomi"
        }

    def run(self, ame: AstrMessageEvent):
        """
        处理消息
        """
        msg = ame.message_str.strip()
        
        # 检查是否符合 账号#密码#步数 格式
        if "#" in msg:
            parts = msg.split("#")
            if len(parts) == 3:
                user = parts[0].strip()
                password = parts[1].strip()
                steps = parts[2].strip()
                
                # 简单校验步数是否为数字
                if not steps.isdigit():
                    return True, tuple([True, "步数必须是数字哦！格式：账号#密码#步数", "xiaomi_steps"])
                
                try:
                    # 从配置中获取 ckey 和 api_url
                    ckey = self.config.get("ckey", "AB3X3HLKNXZI5FNPRG9G")
                    api_url = self.config.get("api_url", "https://tmini.net/api/xiaomi")
                    
                    # 构造请求参数
                    params = {
                        "ckey": ckey,
                        "user": user,
                        "pass": password,
                        "steps": steps
                    }
                    
                    # 发送请求
                    response = requests.get(api_url, params=params, timeout=10)
                    data = response.json()
                    
                    if data.get("code") == 200:
                        # 成功返回
                        result_msg = f"✅ 修改成功！\n账号：{data['data']['user']}\n当前步数：{data['data']['steps']}\n提示：{data.get('msg', '请求成功')}"
                        return True, tuple([True, result_msg, "xiaomi_steps"])
                    else:
                        # 接口返回错误
                        error_msg = f"❌ 修改失败\n原因：{data.get('msg', '未知错误')}"
                        return True, tuple([True, error_msg, "xiaomi_steps"])
                        
                except Exception as e:
                    # 网络或解析异常
                    return True, tuple([True, f"⚠️ 请求接口出错：{str(e)}", "xiaomi_steps"])
        
        # 如果不符合格式，不响应消息
        return False, None

    def info(self):
        """
        插件元信息
        """
        return {
            "name": "XiaomiSteps",
            "desc": "修改运动步数插件 (支持 WebUI 配置)",
            "help": "输入格式：账号#密码#步数\n例如：example@mail.com#password123#20000\n您可以在管理面板修改 API Key。",
            "version": "v1.1",
            "author": "Manus",
            "repo": ""
        }
