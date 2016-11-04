'django_archive',

# django_archive
ARCHIVE_DIRECTORY = "/tmp/backup_viz"
ARCHIVE_FILENAME  = "database"
ARCHIVE_FORMAT    = "gz"
ARCHIVE_EXCLUDE   = (
    'PredictorDTPM.buslog',
    'PredictorDTPM.log',
    'contenttypes.contenttype',
    'auth.group',
    'auth.permission',
    'auth.user',
    'admin.logentry',
    'sessions.session',
    'auth.group_permissions',
    'auth.user_groups',
    'auth.user_user_permissions',
    # 'AndroidRequests.DevicePositionInTime',
    # 'AndroidRequests.Event',
    # 'AndroidRequests.StadisticDataFromRegistrationBus',
    # 'AndroidRequests.StadisticDataFromRegistrationBusStop',
    # 'AndroidRequests.EventForBusStop',
    # 'AndroidRequests.EventForBus',
    # 'AndroidRequests.ServicesByBusStop',
    # 'AndroidRequests.BusStop',
    # 'AndroidRequests.Service',
    # 'AndroidRequests.Bus',
    # 'AndroidRequests.ServiceLocation',
    # 'AndroidRequests.ServiceStopDistance',
    # 'AndroidRequests.Token',
    # 'AndroidRequests.PoseInTrajectoryOfToken',
    # 'AndroidRequests.ActiveToken',
    # 'AndroidRequests.NearByBusesLog',
    # 'AndroidRequests.Route',
    # 'AndroidRequests.Report',
)
