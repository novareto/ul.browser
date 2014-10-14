# -*- coding: utf-8 -*-

from IPython.config.loader import Config
from IPython.terminal.embed import InteractiveShellEmbed


def make_shell(banner=u'IPython', **namespace):
    cfg = Config()
    prompt_config = cfg.PromptManager
    prompt_config.in_template = r'{color.LightGreen}\u@\h{color.LightBlue}[{color.LightCyan}\Y1{color.LightBlue}]{color.Green}|\#> '
    prompt_config.out_template = r'<\#> '
    sh = InteractiveShellEmbed(config=cfg, banner1=banner)
    return sh.mainloop(local_ns=namespace)
