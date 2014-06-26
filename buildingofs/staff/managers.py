from buildingofs.utils.managers import RPCManager


class StaffManager(RPCManager):
    topic = 'staff'
    method = 'query_staff_members'
    legacy = True
