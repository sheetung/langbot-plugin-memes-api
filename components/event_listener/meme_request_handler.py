import base64
import json
from io import BytesIO
from pathlib import Path

import httpx
import yaml

# 表情包信息文件路径
MEMES_INFO_FILE = Path(__file__).parent.parent.parent / "data" / "memes_info.yaml"


class MemeRequestHandler:
    def __init__(self, memeurl=None):
        self.memes_info = {}
        self.keyword_to_key = {}
        # 默认API URL
        self.memeurl = memeurl or "http://127.0.0.1:2233"
        # 加载表情包信息
        self._load_memes_info()
    
    def _load_memes_info(self):
        """加载表情包信息（key一级格式）"""
        try:
            if MEMES_INFO_FILE.exists():
                with open(MEMES_INFO_FILE, 'r', encoding='utf-8') as f:
                    # 直接加载为字典格式
                    self.memes_info = yaml.safe_load(f) or {}
                
                # 构建关键词到key的映射
                self.keyword_to_key = {}
                for key, meme_info in self.memes_info.items():
                    if 'keywords' in meme_info:
                        for keyword in meme_info['keywords']:
                            self.keyword_to_key[keyword] = key
                
                print(f"成功加载 {len(self.memes_info)} 个表情包信息")
                print(f"成功构建 {len(self.keyword_to_key)} 个关键词映射")
            else:
                print(f"表情包信息文件不存在: {MEMES_INFO_FILE}")
                print("请先运行 utils/fetch_meme_info.py 脚本获取表情包信息")
        except Exception as e:
            print(f"加载表情包信息失败: {str(e)}")
            self.memes_info = {}
            self.keyword_to_key = {}
    
    def match_keyword(self, text):
        """匹配关键词，返回对应的meme key"""
        # 精确匹配
        if text in self.keyword_to_key:
            return self.keyword_to_key[text]
        
        # 模糊匹配（可选）
        # for keyword, key in self.keyword_to_key.items():
        #     if keyword in text:
        #         return key
        
        return None
    
    async def generate_meme(self, meme_key, texts, images):
        """
        生成表情包
        :param meme_key: 表情包key
        :param texts: 文本内容列表
        :param images: 图片二进制数据列表
        :return: 生成的图片二进制数据
        """
        try:
            # 构建API请求参数 - 符合curl请求示例格式
            # 准备files参数用于文件上传
            files = {}
            # 检查是否有图片
            if images and len(images) > 0:
                # 创建一个BytesIO对象来模拟文件上传
                img_file = BytesIO(images[0])
                # 为图片指定文件名和类型
                files['images'] = ('image.png', img_file, 'image/png')
            
            # 准备data参数
            data = {}
            # 添加texts参数 - 只有当文本不为空时才添加
            if texts and texts[0]:
                data['texts'] = texts[0]
            
            # 添加args参数 - 使用JSON字符串格式
            args = '{"user_infos":[]}'
            data['args'] = args
            
            # 构建API URL
            url = f"{self.memeurl}/memes/{meme_key}/"
            # print(f'API请求URL：{url}')
            # print(f'匹配到的关键词：{meme_key}')
            
            # 设置请求头
            headers = {
                'accept': 'application/json'
            }
            
            # 发送API请求
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, files=files, data=data, headers=headers)
            
            # 检查响应状态
            resp.raise_for_status()
            
            # 返回生成的图片二进制数据
            return resp.content
            
        except httpx.HTTPStatusError as e:
            return
            # if e.response.status_code == 404:
            #     raise ValueError(f"未找到表情包：{meme_key}")
            # else:
            #     print(f"生成表情包时出错：HTTP错误 {e.response.status_code}")
            #     print("响应内容：", e.response.text)
            #     raise RuntimeError(f"生成表情包时出错：HTTP错误 {e.response.status_code}")
        except Exception as e:
            # print(f"生成表情包时出错：{str(e)}")
            # raise RuntimeError(f"生成表情包时出错：{str(e)}")
            return