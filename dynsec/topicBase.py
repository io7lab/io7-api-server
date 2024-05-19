def get_topics(devId):
    cmd_base = 'iot3/+devId/cmd/+/fmt/+'
    evt_base = 'iot3/+devId/evt/+/fmt/+'
    log_base = 'iot3/+devId/mgmt/device/status'
    meta_base = 'iot3/+devId/mgmt/device/meta'
    update_base = 'iot3/+devId/mgmt/device/update'
    reboot_base = 'iot3/+devId/mgmt/initiate/device/reboot'
    reset_base = 'iot3/+devId/mgmt/initiate/device/factory_reset'
    upgrade_base = 'iot3/+devId/mgmt/initiate/firmware/update'
    gw_query_base = 'iot3/+devId/gateway/query'
    gw_add_base = 'iot3/+devId/gateway/add'
    gw_list_base = 'iot3/+devId/gateway/list'

    return {
        'cmdTopic': cmd_base.replace('+devId', devId),
        'evtTopic': evt_base.replace('+devId', devId),
        'metaTopic': meta_base.replace('+devId', devId),
        'logTopic': log_base.replace('+devId', devId),
        'updateTopic': update_base.replace('+devId', devId),
        'rebootTopic': reboot_base.replace('+devId', devId),
        'resetTopic': reset_base.replace('+devId', devId),
        'upgradeTopic': upgrade_base.replace('+devId', devId),
        'gw_query': gw_query_base.replace('+devId', devId),
        'gw_add': gw_add_base.replace('+devId', devId),
        'gw_list': gw_list_base.replace('+devId', devId),
        'mgmtTopics': 'iot3/+/mgmt/#',
        'appSubTopic': 'iot3/+/evt/#',
        'appPubTopic': 'iot3/+/cmd/#',
        'id': devId
    }

def get_role_name(devId):
    devId = devId.replace(':', '-')
    return devId

class ACLBase:
    def __init__(self, devId):
        self.topics = get_topics(devId)
        self.id = devId

    def get_id(self):
        return self.id

    def get_topics(self):
        return self.topics

    def subTopic(self, t):
        return {
            'acltype': 'subscribePattern',
            'topic': self.topics[t],
            'priority': -1,
            'allow': True
        }
    
    def pubTopic(self, t):
        return {
            'acltype': 'publishClientSend',
            'topic': self.topics[t],
            'priority': -1,
            'allow': True
        }
