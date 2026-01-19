import requests
import re
import asyncio
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Star, register
from astrbot.api.all import Context

@register("xiaomi_steps", "Manus", "通过指定接口修改小米运动步数，支持账号#密码#步数格式。", "1.2.1", "https://github.com/jilei522/astrbot_plugin_XiaomiSteps")
class XiaomiStepsPlugin(Star):
    def __init__(self, context: Context, config: dict = None):
        super().__init__(context)
        self.config = config if config else {}
        # 预编译正则，提高匹配效率
        self.pattern = re.compile(r'^(.+?)#(.+?)#(\d+)$')

    @filter.on_message()
    async def handle_message(self, event: AstrMessageEvent):
        """
        监听消息，安全解析 账号#密码#步数 格式
        """
        raw_msg = event.message_str.strip()
        
        # 1. 快速过滤：必须包含两个 #
        if raw_msg.count('#') != 2:
            return

        # 2. 正则解析：确保格式严格匹配并提取字段
        match = self.pattern.match(raw_msg)
        if not match:
            # 如果包含 # 但格式不对，可以给予友好提示（可选，避免干扰普通聊天）
            # yield event.plain_result("格式似乎不对哦，请使用：账号#密码#步数")
            return

        user, password, steps_str = match.groups()
        user = user.strip()
        password = password.strip()
        steps = int(steps_str)

        # 3. 业务逻辑校验：步数范围检查
        if steps < 0 or steps > 100000:
            yield event.plain_result("❌ 步数设置不合理（建议 0-100,000 之间）。")
            return

        # 4. 获取配置
        ckey = self.config.get("ckey", "").strip()
        if not ckey:
            yield event.plain_result("⚠️ 插件未配置 API Key (ckey)，请联系管理员在后台设置。")
            return
        
        api_url = self.config.get("api_url", "https://tmini.net/api/xiaomi").strip()

        # 5. 安全的异步请求处理
        try:
            # 使用 run_in_executor 防止 requests 阻塞异步主线程
            loop = asyncio.get_event_loop()
            params = {
                "ckey": ckey,
                "user": user,
                "pass": password,
                "steps": steps
            }
            
            # 封装请求逻辑
            def make_request():
                return requests.get(api_url, params=params, timeout=15)

            response = await loop.run_in_executor(None, make_request)
            
            # 检查 HTTP 状态码
            if response.status_code != 200:
                yield event.plain_result(f"❌ 接口请求失败 (HTTP {response.status_code})，请稍后再试。")
                return

            data = response.json()
            
            # 6. 业务结果反馈
            code = data.get("code")
            msg = data.get("msg", "未知返回信息")
            
            if code == 200:
                # 成功：提取返回的步数（如果有）
                res_data = data.get("data", {})
                current_steps = res_data.get("steps", steps)
                yield event.plain_result(f"✅ 修改成功！\n账号：{user}\n当前步数：{current_steps}\n提示：{msg}")
            else:
                # 失败：反馈接口给出的具体原因
                yield event.plain_result(f"❌ 修改失败\n原因：{msg}")

        except requests.exceptions.Timeout:
            yield event.plain_result("⚠️ 请求超时，接口服务器响应过慢，请稍后重试。")
        except requests.exceptions.RequestException as e:
            yield event.plain_result(f"⚠️ 网络请求异常：{str(e)}")
        except ValueError:
            yield event.plain_result("⚠️ 接口返回数据格式错误，解析失败。")
        except Exception as e:
            yield event.plain_result(f"⚠️ 发生未知错误：{str(e)}")

    def info(self):
        return {
            "name": "XiaomiSteps",
            "desc": "通过指定接口修改小米运动步数，支持账号#密码#步数格式。",
            "help": "输入格式：账号#密码#步数\n例如：example@mail.com#password123#20000\n安全提示：请勿在公共群聊频繁发送密码。",
            "version": "v1.2.1",
            "author": "Manus"
        }
