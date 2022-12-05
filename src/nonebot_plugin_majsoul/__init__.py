from importlib import resources

from matplotlib import font_manager
from matplotlib import pyplot as plt

from . import res

with resources.path(res, "LXGWWenKaiMonoLite-Regular.ttf") as path:
    font_manager.fontManager.addfont(path)
plt.rcParams['font.sans-serif'] = 'LXGW WenKai Mono Lite'

from . import paifuya
