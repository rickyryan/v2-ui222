import threading

from apscheduler.triggers.interval import IntervalTrigger

from init import db
from util import config, v2_util
from util.schedule_util import scheduler
from v2ray.models import Inbound

__lock = threading.Lock()


@scheduler.scheduled_job(trigger=IntervalTrigger(seconds=config.get_v2_config_check_interval()))
def check_v2_config_job():
    with __lock:
        v2_config = v2_util.gen_v2_config_from_db()
        v2_util.write_v2_config(v2_config)


@scheduler.scheduled_job(trigger=IntervalTrigger(seconds=config.get_traffic_job_interval()))
def traffic_job():
    with __lock:
        if not v2_util.is_running():
            return
        traffics = v2_util.get_inbounds_traffic()
        if not traffics:
            return
        for traffic in traffics:
            upload = int(traffic.get('uplink', 0))
            download = int(traffic.get('downlink', 0))
            tag = traffic['tag']
            Inbound.query.filter_by(tag=tag).update({'up': Inbound.up + upload, 'down': Inbound.down + download})
        db.session.commit()


def init():
    pass
