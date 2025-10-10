from __future__ import annotations

import base64
import httpx
from langbot_plugin.api.definition.components.common.event_listener import EventListener
from langbot_plugin.api.entities import events, context
from langbot_plugin.api.entities.builtin.platform import message as platform_message

from .meme_request_handler import MemeRequestHandler


class DefaultEventListener(EventListener):
    def __init__(self):
        super().__init__()
        # 从配置中获取memeurl
        self.memeurl = None
        # 初始化表情包请求处理器，但暂时不传入memeurl参数
        # 将在initialize方法中重新设置meme_handler
        
    async def initialize(self):
        await super().initialize()

        self.memeurl = self.plugin.get_config().get("memeurl", None)
        # 初始化表情包请求处理器，传入memeurl参数
        self.meme_handler = MemeRequestHandler(self.memeurl)
        
        @self.handler(events.GroupMessageReceived)
        async def handler(event_context: context.EventContext):
            # 获取用户消息文本
            message_text = str(event_context.event.message_chain)
            # print(f'event={event_context.event}')
            event_context.prevent_default()
            # 如果用户输入包含[Image]标记，剔除它
            if '[Image]' in message_text:
                message_text = message_text.replace('[Image]', '').strip()
            
            # 解析用户消息，格式：表情包关键词 文本内容
            parts = message_text.strip().split(" ", 1)
            if len(parts) < 1:
                await event_context.reply(
                    platform_message.MessageChain([
                        platform_message.Plain(text="请输入表情包关键词和文本内容，格式：表情包关键词 文本内容\n")
                    ])
                )
                return
            
            # 首先尝试匹配 keywords
            first_word = parts[0]
            meme_key = self.meme_handler.match_keyword(first_word)
            
            # 如果没有匹配到 keywords，回退使用第一个词作为 meme_key
            if meme_key is None:
                meme_key = first_word
            
            # 初始化texts列表
            texts = []
            
            # 检查meme_key是否存在于memes_info中，以及其是否需要多个文本
            if meme_key in self.meme_handler.memes_info:
                meme_info = self.meme_handler.memes_info[meme_key]
                # 如果有文本内容
                if len(parts) > 1:
                    # 默认以逗号分隔多个文本
                    texts = [t.strip() for t in parts[1].split(',')]
                    
                    # 检查文本数量是否符合要求
                    min_texts = meme_info.get('params_type', {}).get('min_texts', 0)
                    max_texts = meme_info.get('params_type', {}).get('max_texts', 0)
                    
                    # 如果文本数量不足，使用默认文本填充
                    if len(texts) < min_texts and 'default_texts' in meme_info.get('params_type', {}):
                        default_texts = meme_info['params_type']['default_texts']
                        # 只填充需要的数量
                        texts += default_texts[len(texts):min_texts]
                    
                    # 如果文本数量超过最大限制，截断
                    if max_texts > 0 and len(texts) > max_texts:
                        texts = texts[:max_texts]
                else:
                    # 没有提供文本，检查是否有默认文本
                    if 'default_texts' in meme_info.get('params_type', {}):
                        texts = meme_info['params_type']['default_texts']
            else:
                # 如果meme_key不在memes_info中，使用原来的处理方式
                if len(parts) > 1:
                    texts = [parts[1]]
                else:
                    texts = []
            
            # 初始化images列表并从消息链中提取图片的base64数据
            images = []
            for element in event_context.event.message_chain:
                if hasattr(element, 'type') and element.type == 'Image' and hasattr(element, 'base64') and element.base64:
                    # 如果base64字符串包含前缀（如'data:image/png;base64,'），则移除前缀
                    base64_data = element.base64
                    if ',' in base64_data:
                        base64_data = base64_data.split(',')[1]
                    # 将base64数据转换为二进制形式
                    img_bytes = base64.b64decode(base64_data)
                    images.append(img_bytes)
            
            # 如果没有提取到图片，使用发送者的QQ头像
            if not images and hasattr(event_context.event, 'sender_id'):
                sender_id = event_context.event.sender_id
                # print(f'senderid={sender_id}')
                try:
                    # 使用QQ官方头像URL获取头像
                    async with httpx.AsyncClient() as client:
                        # 使用指定的QQ头像URL格式
                        img_url = f"http://q1.qlogo.cn/g?b=qq&nk={sender_id}&s=100"
                        img_resp = await client.get(img_url)
                        img_resp.raise_for_status()
                        images.append(img_resp.content)
                except Exception as e:
                    print(f"获取QQ头像时出错：{repr(e)}")
            
            print(f'用户输入：{message_text}')
            print(f'解析后的关键词：{meme_key}')
            print(f'解析后的文本内容：{texts}')
            print(f'提取到的图片数量：{len(images)}')
            
            try:
                # 调用表情包请求处理器生成图片
                img_bytes = await self.meme_handler.generate_meme(meme_key, texts, images)
                
                # 将生成的图片转换为base64格式
                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                
                # 发送生成的表情包
                await event_context.reply(
                    platform_message.MessageChain([
                        platform_message.Image(base64=img_base64)
                    ])
                )
            except ValueError as e:
                # 处理未找到表情包的情况
                await event_context.reply(
                    platform_message.MessageChain([
                        platform_message.Plain(text=str(e))
                    ])
                )
            except RuntimeError as e:
                # 处理其他运行时错误
                await event_context.reply(
                    platform_message.MessageChain([
                        platform_message.Plain(text=str(e))
                    ])
                )
            except Exception as e:
                # 处理未知错误
                # await event_context.reply(
                #     platform_message.MessageChain([
                #         platform_message.Plain(text=f"生成表情包时出错：{str(e)}")
                #     ])
                # )
                return
                
    # 匹配关键词，返回对应的meme key
    def _match_keyword(self, text):
        return self.meme_handler.match_keyword(text)