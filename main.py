import httpx
import re
import logging
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Star, register
from astrbot.api.all import Context

logger = logging.getLogger("astrbot")

@register("astrbot_plugin_mixiaSteps", "mixia", "支持通过用户简单的格式指令进行修改运动步数华米数据步数。", "1.4.0", "https://github.com/jilei522/astrbot_plugin_mixiaSteps")
class XiaomiStepsPlugin(Star):
    def __init__(self, context: Context, config: dict = None):
        super().__init__(context)
        self.config = config if config else {}
        # 预编译正则，提高匹配效率
        self.pattern = re.compile(r'^(.+?)#(.+?)#(\d+)$')

    @filter.command("步数")
    async def handle_steps(self, event: AstrMessageEvent, msg: str = ""):
        """
        通过指令触发：/步数 账号#密码#步数
        """
        # 获取输入字符串
        input_str = msg.strip() if msg else event.message_str.replace("步数", "").strip()
        
        if not input_str:
            yield event.plain_result("请输入参数！格式：/步数 账号#密码#步数")
            return

        # 1. 正则解析
        match = self.pattern.match(input_str)
        if not match:
            yield event.plain_result("格式错误！请使用：账号#密码#步数")
            return

        # 2. 安全性检查：强制私聊
        is_group = False
        try:
            if hasattr(event, 'is_group'):
                is_group = event.is_group()
            elif hasattr(event.message_obj, 'group_id'):
                is_group = event.message_obj.group_id > 0
            elif hasattr(event.message_obj, 'type'):
                is_group = event.message_obj.type == "group"
        except:
            pass

        if is_group:
            # 尝试撤回消息（如果平台支持）
            try:
                platform = self.context.get_platform(event.platform)
                if hasattr(platform, 'delete_msg'):
                    await platform.delete_msg(event.message_obj.message_id)
            except Exception as e:
                logger.warning(f"撤回消息失败: {e}")
            
            yield event.plain_result("⚠️ 为了您的账号安全，【修改步数】指令仅限【私聊】使用！\n密码已在群聊暴露，建议您尽快修改密码。")
            return

        user, password, steps_str = match.groups()
        user = user.strip()
        password = password.strip()
        steps = int(steps_str)

        # 3. 业务逻辑校验
        if steps < 0 or steps > 100000:
            yield event.plain_result("❌ 步数设置不合理（建议 0-100,000 之间）。")
            return

        # 4. 获取配置
        ckey = self.config.get("ckey", "").strip()
        if not ckey:
            yield event.plain_result("⚠️ 插件未配置 API Key (ckey)，请联系管理员在后台设置。")
            return
        
        api_url = self.config.get("api_url", "https://tmini.net/api/xiaomi").strip()

        # 5. 使用 httpx 进行异步请求
        try:
            params = {
                "ckey": ckey,
                "user": user,
                "pass": password,
                "steps": steps
            }
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(api_url, params=params)
                
                if response.status_code != 200:
                    yield event.plain_result(f"❌ 接口请求失败 (HTTP {response.status_code})，请稍后再试。")
                    return

                data = response.json()
            
            # 6. 业务结果反馈
            code = data.get("code")
            msg_res = data.get("msg", "未知返回信息")
            
            if code == 200:
                res_data = data.get("data", {})
                current_steps = res_data.get("steps", steps)
                yield event.plain_result(f"✅ 修改成功！\n账号：{user}\n当前步数：{current_steps}\n提示：{msg_res}")
            else:
                yield event.plain_result(f"❌ 修改失败\n原因：{msg_res}")

        except httpx.TimeoutException:
            yield event.plain_result("⚠️ 请求超时，接口服务器响应过慢，请稍后重试。")
        except httpx.RequestError as e:
            yield event.plain_result(f"⚠️ 网络请求异常：{str(e)}")
        except (ValueError, KeyError):
            yield event.plain_result("⚠️ 接口返回数据格式错误，解析失败。")
        except Exception as e:
            yield event.plain_result(f"⚠️ 发生未知错误：{str(e)}")

    def info(self):
        return {
            "name": "astrbot_plugin_mixiaSteps",
            "desc": "支持通过用户简单的格式指令运动步数进行修改。",
            "help": "【安全提示】请务必在【私聊】中使用！\n使用方法：/步数 账号#密码#步数\n例如：/步数 example@mail.com#password123#20000",
            "version": "1.4.0",
            "author": "mixia"
        }
