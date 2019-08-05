#!/bin/bash
source /home/hyunny88/.profile
source /home/hyunny88/.bashrc
cd $HOME/projects/auto-trading
/home/hyunny88/.virtualenvs/auto-trading/bin/python -m autotrading.scheduler.scheduler_currency_price
