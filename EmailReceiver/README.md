# Email Receiver
一个用于自动收取作业的bot

因为不想手动收作业，所以花费比手动收作业多n倍的时间开发了一个自动收发作业bot。

## 功能

- 匹配格式正确的邮件主题，并自动分类、存取作业。
- 支持后台定时运行or一键识别前n封邮件。
- 支持作业匹配成功后自动回复。
- 支持Server酱通知。
- 支持多门课程作业同时接收。
- 支持文件格式匹配。
- 温馨的问候语。

## 环境及配置指南
- 安装python3及jieba库。
`pip3 install --index-url https://pypi.tuna.tsinghua.edu.cn/simple/ jieba`
- 复制config.sample.ini并改名为config.ini
- 配置config.ini
- 在根目录下运行命令即可：
`python3 main.py`
