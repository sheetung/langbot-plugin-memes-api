# memePlugin-api

这是一个为 LangBot 开发的表情包插件，通过 API 调用远程的表情包生成服务。

## 功能特点

- 通过 HTTP API 调用远程表情包生成服务
- 支持关键词匹配：用户输入中文关键词可以自动匹配到对应的表情包 key
- 支持图片上传：可以从消息中提取图片并发送给 API

## 安装方法

### Docker 部署

`docker-compose.yml`文件如下

```yaml
version: '3.8'

services:
  meme-generator:
    image: meetwq/meme-generator:main
    container_name: meme-generator
    restart: always
    ports:
      - "2233:2233"
    volumes:
      - ./data:/data
    environment:
      - MEME_DIRS=["/data/memes"]
      - MEME_DISABLED_LIST=[]
      - GIF_MAX_SIZE=10.0
      - GIF_MAX_FRAMES=100
      - BAIDU_TRANS_APPID=
      - BAIDU_TRANS_APIKEY=
      - LOG_LEVEL=INFO
```

通过命令 `docker-compose up -d` 启动容器

运行后可通过 api 方式调用

#### 环境变量



| 变量名               | 默认值              | 说明                    |
| -------------------- | ------------------- | ----------------------- |
| `MEME_DIRS`          | `'["/data/memes"]'` | 额外表情路径            |
| `MEME_DISABLED_LIST` | `'[]'`              | 禁用表情列表            |
| `GIF_MAX_SIZE`       | `10.0`              | 限制生成的 gif 文件大小 |
| `GIF_MAX_FRAMES`     | `100`               | 限制生成的 gif 文件帧数 |
| `BAIDU_TRANS_APPID`  | `''`                | 百度翻译 appid          |
| `BAIDU_TRANS_APIKEY` | `''`                | 百度翻译 apikey         |
| `LOG_LEVEL`          | `'INFO'`            | 日志等级                |

## 使用方法

在LnagBot市场安装`meme-plugin-api`, 并配置好环境变量

聊天中触发表情列表中的关键词生成表情包

- 例如：
  - 反了  --> 由QQ头像作为图片传入
  - 反了 [此处有张图] --> 由消息中的图片作为图片传入

### 表情列表

请参考 [表情列表](https://github.com/MemeCrafters/meme-generator/wiki/%E8%A1%A8%E6%83%85%E5%88%97%E8%A1%A8) 查看所有支持的表情包关键词

## 更新历史

- v0.2.4 修复传入文本或者图片的数量导致表情包生成出错的问题
- v0.1.3 增加默认图片使用qq头像
- v0.1.2 完善基础开发


## 问题反馈及功能开发

[![QQ群](https://img.shields.io/badge/QQ群-965312424-green)](https://qm.qq.com/cgi-bin/qm/qr?k=en97YqjfYaLpebd9Nn8gbSvxVrGdIXy2&jump_from=webapi&authKey=41BmkEjbGeJ81jJNdv7Bf5EDlmW8EHZeH7/nktkXYdLGpZ3ISOS7Ur4MKWXC7xIx)