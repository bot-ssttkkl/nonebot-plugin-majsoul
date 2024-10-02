<!-- markdownlint-disable MD033 MD036 MD041 -->

<p align="center">
  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>
</p>

<div align="center">

nonebot-plugin-majsoul
============

_✨ 雀魂信息查询插件 ✨_

</div>


<p align="center">
  <a href="https://raw.githubusercontent.com/ssttkkl/nonebot-plugin-majsoul/master/LICENSE">
    <img src="https://img.shields.io/github/license/ssttkkl/nonebot-plugin-majsoul.svg" alt="license">
  </a>
  <a href="https://pypi.python.org/pypi/nonebot-plugin-majsoul">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-majsoul.svg" alt="pypi">
  </a>
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">
</p>

受[DaiShengSheng/Majsoul_bot](https://github.com/DaiShengSheng/Majsoul_bot)启发而写的雀魂信息查询 Bot 插件。

## 功能

### 雀魂牌谱屋

#### 查询个人数据（可按照时间、按照场数、按照房间类型查询）

指令：`/雀魂(三麻)信息 <雀魂账号> [<房间类型>] [最近<数量>场] [最近<数量>{天|周|个月|年}]`

![雀魂信息](img/majsoul_info.png)

![雀魂信息2](img/majsoul_info_2.png)

#### 查询个人最近对局（可按照房间类型查询）

指令：`/雀魂(三麻)对局 <雀魂账号> [<房间类型>]`

![最近对局](img/records.png)

#### 绘制个人PT推移图

**若绘图出现乱码或是需要更换绘图字体，请参考下文进行字体配置**

指令：`/雀魂(三麻)PT图 <雀魂账号> [最近<数量>场] [最近<数量>{天|周|个月|年}]`

![雀魂PT推移图](img/pt_plot.png)

![雀魂PT推移图（图）](img/pt_plot_img.png)

#### 下载雀魂牌谱

将雀魂牌谱保存为天凤JSON格式。**必须配置雀魂账号与密码。**

指令：`/下载雀魂牌谱 <牌谱链接或UUID>`

## 配置字体

### 更换为系统已安装字体

修改配置项`majsoul_font`为字体名。

例如：配置`majsoul_font=Microsoft YaHei`将使用微软雅黑字体

### 更换为外部字体

修改配置项`majsoul_font_path`为字体路径，并修改配置项`majsoul_font`为字体名。

例如：在 https://github.com/lxgw/LxgwWenKai-Lite/releases 下载LXGWWenKaiMonoLite-Regular.ttf并放置于bot根目录，配置`majsoul_font_path=LXGWWenKaiMonoLite-Regular.ttf`，配置`majsoul_font=LXGW WenKai Mono Lite`

## 配置项

### majsoul_query_timeout

指令超时（单位：秒）

### majsoul_font

绘图用的字体名称

### majsoul_font_path

绘图用的字体文件路径

### majsoul_send_aggregated_message

是否使用合并转发消息发送查询对局的结果

默认值：`True`

### majsoul_username

下载牌谱用的雀魂账号邮箱。推荐使用小号。

### majsoul_password

下载牌谱用的雀魂账号密码。推荐使用小号。

## See Also

- [nonebot-plugin-mahjong-utils](https://github.com/ssttkkl/nonebot-plugin-mahjong-utils)：日麻小工具插件。支持手牌分析、番符点数查询。
- [nonebot-plugin-mahjong-scoreboard](https://github.com/ssttkkl/nonebot-plugin-mahjong-scoreboard)
  ：日麻计分器。为面麻群友提供日麻对局分数记录。根据马点进行PT精算，统计PT增减，支持对局与榜单查询与导出。

## 在线乞讨

<details><summary>点击请我打两把maimai</summary>

![](https://github.com/ssttkkl/ssttkkl/blob/main/afdian-ssttkkl.jfif)

</details>

## LICENSE

[AGPLv3](https://raw.githubusercontent.com/ssttkkl/nonebot-plugin-majsoul/master/LICENSE)
