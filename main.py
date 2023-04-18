import math
import os
import requests
import user_setting

QMSG_KEY = os.environ["QMSG_KEY"]
TORN_KEY = os.environ["TORN_KEY"]
TORN_ID = user_setting.user_id
webhook = 'https://qmsg.zendee.cn:443/send/' + QMSG_KEY
api_url = 'https://api.torn.com/user/' + TORN_ID + '?selections=&key=' + TORN_KEY
misc_url = 'https://api.torn.com/user/' + TORN_ID + '?selections=cooldowns,bars,newevents,newmessages,refills&key=' + TORN_KEY


def analyse_second(second):
    m, s = divmod(second, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, s)


def events_reader(events_list):
    event_str = '未读Events:\n'
    index = 1
    for i in events_list:
        event_str = event_str + str(index) + '. ' + events_list[i]['event'] + '\n'
        index += 1
    return event_str


def main_handler():
    energy_regen = 0.333
    nerve_regen = 0.2
    data = requests.get(api_url).json()
    misc = requests.get(misc_url).json()
    name = data['name'] + '[{}]'.format(data['player_id'])
    status = '你还在城里面潇洒着'
    more_info = '------\n'

    if data["donator"] != 0:
        energy_regen = 0.5

    if data["status"]["state"] == 'Hospital':
        status = '你看起来在医院潇洒 ' + data["status"]["description"]
    if data["status"]["state"] == 'Jail':
        status = '你看起来在监狱潇洒 ' + data["status"]["description"]
    if data["status"]["state"] == 'Traveling':
        status = '你看起来在飞机潇洒 ' + data["status"]["description"]

    event = events_reader(misc['events'])

    life = '{}/{}'.format(misc['life']['current'], misc['life']['maximum'])
    energy = '{}/{}'.format(misc['energy']['current'], misc['energy']['maximum'])
    nerve = '{}/{}'.format(misc['nerve']['current'], misc['nerve']['maximum'])

    drug = '药物CD好了'
    if misc['cooldowns']['drug'] != 0:
        drug = '药物CD: {}'.format(analyse_second(misc['cooldowns']['drug']))

    booster = '饮料CD好了'
    if misc['cooldowns']['booster'] != 0:
        booster = '饮料CD: {}'.format(analyse_second(misc['cooldowns']['booster']))

    medical = '医药CD好了'
    if misc['cooldowns']['medical'] != 0:
        medical = '医药CD: {}'.format(analyse_second(misc['cooldowns']['medical']))

    if misc['energy']['current'] >= misc['energy']['maximum']:
        more_info += '能量满了哦'
    else:
        achive_max_time = float(misc['energy']['maximum']) - int(misc['energy']['current'])
        achive_max_time = achive_max_time/energy_regen
        if achive_max_time > 60:
            achive_max_time = (str(round(achive_max_time / 60, 1))) + '小时'
        else:
            achive_max_time = str(math.floor(achive_max_time)) + '分钟'
        more_info += '能量预计还有{}补满\n'.format(str(achive_max_time))

    if misc['nerve']['current'] >= misc['nerve']['maximum']:
        more_info += '勇气满了哦'
    else:
        achive_max_time = float(misc['nerve']['maximum']) - int(misc['nerve']['current'])
        achive_max_time = achive_max_time/nerve_regen
        if achive_max_time > 60:
            achive_max_time = (str(round(achive_max_time / 60, 1))) + '小时'
        else:
            achive_max_time = str(math.floor(achive_max_time)) + '分钟'
        more_info += '勇气预计还有{}补满'.format(str(achive_max_time))

    energy_refill = 'E Refill: '
    if not misc['refills']['energy_refill_used']:
        energy_refill += '未使用'
    else:
        energy_refill += '已使用'
    nerve_refill = 'N Refill: '
    if not misc['refills']['nerve_refill_used']:
        nerve_refill += '未使用'
    else:
        nerve_refill += '已使用'
    token_refill = 'T Refill: '
    if not misc['refills']['token_refill_used']:
        token_refill += '未使用'
    else:
        token_refill += '已使用'

    message = '{}\n{}\n能量: {}\n勇气: {}\n生命: {}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}'.format(
        name, status, energy, nerve, life, drug, booster, medical, more_info, energy_refill, nerve_refill, token_refill,
        event
    )
    QQPusher(message)


def QQPusher(data):
    data = data.encode('UTF-8')
    massage = {
        'msg': data
    }
    requests.post(webhook, massage)
    print("发送完成")


main_handler()
