



## device position in time(AndroidRequests.models.DevicePositionInTime)

```
Helps storing the position of active users
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |serial |True |True | |Blank | |
|Longitude |longitud |double precision | | | | | |
|Latitude |latitud |double precision | | | | | |
|timeStamp |timeStamp |timestamp with time zone | | | | |longitude from the geolocation   |

Options
```
default_permissions : (u'add', u'change', u'delete')
```


## event(AndroidRequests.models.Event)

```
Here are all the events, its configurarion and info.
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|id |id |varchar(8) |True |True | | | |
|name |name |varchar(30) | | | | | |
|description |description |varchar(140) | | | |Null | |
|lifespam |lifespam |integer | | | | | |
|category |category |varchar(20) | | | | | |
|origin |origin |varchar(1) | | | | |i:the event was taken insede the bus, o:the event was taken from a bustop |
|eventType |eventType |varchar(7) | | | | |bus:An event for the bus., busStop:An event for the busStop. |

Options
```
default_permissions : (u'add', u'change', u'delete')
```


## stadistic data from registration bus(AndroidRequests.models.StadisticDataFromRegistrationBus)

```
StadisticDataFromRegistrationBus(id, longitud, latitud, timeStamp, confirmDecline, reportOfEvent)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |serial |True |True | |Blank | |
|Longitude |longitud |double precision | | | | | |
|Latitude |latitud |double precision | | | | | |
|timeStamp |timeStamp |timestamp with time zone | | | | | |
|confirmDecline |confirmDecline |varchar(10) | | | | | |
|reportOfEvent |reportOfEvent |integer | | |True | |FK:AndroidRequests.models.EventForBus |

Options
```
default_permissions : (u'add', u'change', u'delete')
```


## stadistic data from registration bus stop(AndroidRequests.models.StadisticDataFromRegistrationBusStop)

```
StadisticDataFromRegistrationBusStop(id, longitud, latitud, timeStamp, confirmDecline, reportOfEvent)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |serial |True |True | |Blank | |
|Longitude |longitud |double precision | | | | | |
|Latitude |latitud |double precision | | | | | |
|timeStamp |timeStamp |timestamp with time zone | | | | | |
|confirmDecline |confirmDecline |varchar(10) | | | | | |
|reportOfEvent |reportOfEvent |integer | | |True | |FK:AndroidRequests.models.EventForBusStop |

Options
```
default_permissions : (u'add', u'change', u'delete')
```


## event for bus stop(AndroidRequests.models.EventForBusStop)

```
This model stores the reported events for the busStop
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |serial |True |True | |Blank | |
|timeStamp |timeStamp |timestamp with time zone | | | | | |
|timeCreation |timeCreation |timestamp with time zone | | | | | |
|The event information |event |varchar(8) | | |True | |FK:AndroidRequests.models.Event |
|eventConfirm |eventConfirm |integer | | | | | |
|eventDecline |eventDecline |integer | | | | | |
|The bustop |busStop |varchar(6) | | |True | |FK:AndroidRequests.models.BusStop |
|aditionalInfo |aditionalInfo |varchar(140) | | | | | |

Options
```
default_permissions : (u'add', u'change', u'delete')
```


## event for bus(AndroidRequests.models.EventForBus)

```
This model stores the reported events for the Bus
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |serial |True |True | |Blank | |
|timeStamp |timeStamp |timestamp with time zone | | | | | |
|timeCreation |timeCreation |timestamp with time zone | | | | | |
|The event information |event |varchar(8) | | |True | |FK:AndroidRequests.models.Event |
|eventConfirm |eventConfirm |integer | | | | | |
|eventDecline |eventDecline |integer | | | | | |
|the bus |bus |integer | | |True | |FK:AndroidRequests.models.Bus |

Options
```
default_permissions : (u'add', u'change', u'delete')
```


## services by bus stop(AndroidRequests.models.ServicesByBusStop)

```
This model helps to determin the direction of the bus service I or R.
	All of this is tide to the bus stop code and the service provided by it.
	It's usefull to hace the direction of the service to been able to determin
	position of the bus.
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |serial |True |True | |Blank | |
|code |code |varchar(6) | | | | | |
|the busStop |busStop |varchar(6) | | |True | |FK:AndroidRequests.models.BusStop |
|the service |service |varchar(5) | | |True | |FK:AndroidRequests.models.Service |

Options
```
default_permissions : (u'add', u'change', u'delete')
```


## bus stop(AndroidRequests.models.BusStop)

```
Represents the busStop itself.
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|Longitude |longitud |double precision | | | | | |
|Latitude |latitud |double precision | | | | | |
|code |code |varchar(6) |True |True | | | |
|name |name |varchar(70) | | | | | |
|the event |events | | | | | |M2M:AndroidRequests.models.Event (through: AndroidRequests.models.EventForBusStop) |

Options
```
default_permissions : (u'add', u'change', u'delete')
```


## service(AndroidRequests.models.Service)

```
 Represent a Service like '506' and save his data 
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|service |service |varchar(5) |True |True | | | |
|origin |origin |varchar(100) | | | | | |
|destiny |destiny |varchar(100) | | | | | |
|color |color |varchar(7) | | | | | |
|color id |color_id |integer | | | | | |
|the Bus Stop |busStops | | | | | |M2M:AndroidRequests.models.BusStop (through: AndroidRequests.models.ServicesByBusStop) |

Options
```
default_permissions : (u'add', u'change', u'delete')
```


## bus(AndroidRequests.models.Bus)

```
The bus. The bus is consideres the unique combination of registration plate and service as one.
	So there can be two buses whit same service (da) and two buses whit same registration plate.
	The last thing means that one fisical bus can work in two different service.
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |serial |True |True | |Blank | |
|registrationPlate |registrationPlate |varchar(8) | | | | | |
|service |service |varchar(5) | | | | | |
|the event |events | | | | | |M2M:AndroidRequests.models.Event (through: AndroidRequests.models.EventForBus) |

Options
```
unique_together : (('registrationPlate', 'service'),)
default_permissions : (u'add', u'change', u'delete')
```


## service location(AndroidRequests.models.ServiceLocation)

```
This models stores the position allong the route of every bus at 10 meters apart. 
	You can give the distance form the start of the travel and it return the position at 
	that distance.
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |serial |True |True | |Blank | |
|Longitude |longitud |double precision | | | | | |
|Latitude |latitud |double precision | | | | | |
|service |service |varchar(6) | | | | | |
|distance |distance |integer | | | | | |

Options
```
default_permissions : (u'add', u'change', u'delete')
index_together : (('service', 'distance'),)
```


## service stop distance(AndroidRequests.models.ServiceStopDistance)

```
This model stores the distance for every bustop in every bus rout for every service.
	Given a bus direction code xxxI or xxR or something alike.
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |serial |True |True | |Blank | |
|busStop |busStop |varchar(6) | | |True | |FK:AndroidRequests.models.BusStop |
|service |service |varchar(6) | | | | | |
|distance |distance |integer | | | | | |

Options
```
default_permissions : (u'add', u'change', u'delete')
```


## token(AndroidRequests.models.Token)

```
This table has all the tokens the have ever beeing used.
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|token |token |varchar(128) |True |True | | | |
|bus |bus |integer | | |True | |FK:AndroidRequests.models.Bus |
|color |color |varchar(7) | | | | | |

Options
```
default_permissions : (u'add', u'change', u'delete')
```


## pose in trajectory of token(AndroidRequests.models.PoseInTrajectoryOfToken)

```
This stores all the poses of a trajectory. The trajectory can start on foot and end on foot.
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |serial |True |True | |Blank | |
|Longitude |longitud |double precision | | | | | |
|Latitude |latitud |double precision | | | | | |
|timeStamp |timeStamp |timestamp with time zone | | |True | | |
|inVehicleOrNot |inVehicleOrNot |varchar(15) | | | | | |
|token |token |varchar(128) | | |True | |FK:AndroidRequests.models.Token |

Options
```
default_permissions : (u'add', u'change', u'delete')
index_together : (('token', 'timeStamp'),)
```


## active token(AndroidRequests.models.ActiveToken)

```
This are the tokens that are currently beeing use to upload positions.
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |serial |True |True | |Blank | |
|timeStamp |timeStamp |timestamp with time zone | | | | | |
|token |token |varchar(128) | |True |True | |FK:AndroidRequests.models.Token |

Options
```
default_permissions : (u'add', u'change', u'delete')
```


## report(AndroidRequests.models.Report)

```
 This is the free report, it save the message and the picture location in the system  
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |serial |True |True | |Blank | |
|message |message |text | | | | | |
|path |path |varchar(500) | | | | | |

Options
```
default_permissions : (u'add', u'change', u'delete')
```


## log entry(django.contrib.admin.models.LogEntry)

```
LogEntry(id, action_time, user, content_type, object_id, object_repr, action_flag, change_message)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |serial |True |True | |Blank | |
|action time |action_time |timestamp with time zone | | | |Blank | |
|user |user |integer | | |True | |FK:django.contrib.auth.models.User |
|content type |content_type |integer | | |True |Both |FK:django.contrib.contenttypes.models.ContentType |
|object id |object_id |text | | | |Both | |
|object repr |object_repr |varchar(200) | | | | | |
|action flag |action_flag |smallint | | | | | |
|change message |change_message |text | | | |Blank | |

Options
```
ordering : (u'-action_time',)
default_permissions : (u'add', u'change', u'delete')
```


## permission(django.contrib.auth.models.Permission)

```

    The permissions system provides a way to assign permissions to specific
    users and groups of users.

    The permission system is used by the Django admin site, but may also be
    useful in your own code. The Django admin site uses permissions as follows:

        - The "add" permission limits the user's ability to view the "add" form
          and add an object.
        - The "change" permission limits a user's ability to view the change
          list, view the "change" form and change an object.
        - The "delete" permission limits the ability to delete an object.

    Permissions are set globally per type of object, not per specific object
    instance. It is possible to say "Mary may change news stories," but it's
    not currently possible to say "Mary may change news stories, but only the
    ones she created herself" or "Mary may only change news stories that have a
    certain status or publication date."

    Three basic permissions -- add, change and delete -- are automatically
    created for each Django model.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |serial |True |True | |Blank | |
|name |name |varchar(255) | | | | | |
|content type |content_type |integer | | |True | |FK:django.contrib.contenttypes.models.ContentType |
|codename |codename |varchar(100) | | | | | |

Options
```
ordering : (u'content_type__app_label', u'content_type__model', u'codename')
unique_together : ((u'content_type', u'codename'),)
default_permissions : (u'add', u'change', u'delete')
```


## group-permission relationship(django.contrib.auth.models.Group_permissions)

```
Group_permissions(id, group, permission)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |serial |True |True | |Blank | |
|group |group |integer | | |True | |FK:django.contrib.auth.models.Group |
|permission |permission |integer | | |True | |FK:django.contrib.auth.models.Permission |

Options
```
unique_together : (('group', 'permission'),)
default_permissions : (u'add', u'change', u'delete')
```


## group(django.contrib.auth.models.Group)

```

    Groups are a generic way of categorizing users to apply permissions, or
    some other label, to those users. A user can belong to any number of
    groups.

    A user in a group automatically has all the permissions granted to that
    group. For example, if the group Site editors has the permission
    can_edit_home_page, any user in that group will have that permission.

    Beyond permissions, groups are a convenient way to categorize users to
    apply some label, or extended functionality, to them. For example, you
    could create a group 'Special users', and you could write code that would
    do special things to those users -- such as giving them access to a
    members-only portion of your site, or sending them members-only email
    messages.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |serial |True |True | |Blank | |
|name |name |varchar(80) | |True | | | |
|permissions |permissions | | | | |Blank |M2M:django.contrib.auth.models.Permission (through: django.contrib.auth.models.Group_permissions) |

Options
```
default_permissions : (u'add', u'change', u'delete')
```


## user-group relationship(django.contrib.auth.models.User_groups)

```
User_groups(id, user, group)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |serial |True |True | |Blank | |
|user |user |integer | | |True | |FK:django.contrib.auth.models.User |
|group |group |integer | | |True | |FK:django.contrib.auth.models.Group |

Options
```
unique_together : (('user', 'group'),)
default_permissions : (u'add', u'change', u'delete')
```


## user-permission relationship(django.contrib.auth.models.User_user_permissions)

```
User_user_permissions(id, user, permission)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |serial |True |True | |Blank | |
|user |user |integer | | |True | |FK:django.contrib.auth.models.User |
|permission |permission |integer | | |True | |FK:django.contrib.auth.models.Permission |

Options
```
unique_together : (('user', 'permission'),)
default_permissions : (u'add', u'change', u'delete')
```


## user(django.contrib.auth.models.User)

```

    Users within the Django authentication system are represented by this
    model.

    Username, password and email are required. Other fields are optional.
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |serial |True |True | |Blank | |
|password |password |varchar(128) | | | | | |
|last login |last_login |timestamp with time zone | | | |Both | |
|superuser status |is_superuser |boolean | | | |Blank | |
|username |username |varchar(30) | |True | | | |
|first name |first_name |varchar(30) | | | |Blank | |
|last name |last_name |varchar(30) | | | |Blank | |
|email address |email |varchar(254) | | | |Blank | |
|staff status |is_staff |boolean | | | |Blank | |
|active |is_active |boolean | | | |Blank | |
|date joined |date_joined |timestamp with time zone | | | | | |
|groups |groups | | | | |Blank |M2M:django.contrib.auth.models.Group (through: django.contrib.auth.models.User_groups) |
|user permissions |user_permissions | | | | |Blank |M2M:django.contrib.auth.models.Permission (through: django.contrib.auth.models.User_user_permissions) |

Options
```
default_permissions : (u'add', u'change', u'delete')
swappable : AUTH_USER_MODEL
```


## content type(django.contrib.contenttypes.models.ContentType)

```
ContentType(id, app_label, model)
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|ID |id |serial |True |True | |Blank | |
|app label |app_label |varchar(100) | | | | | |
|python model class name |model |varchar(100) | | | | | |

Options
```
unique_together : ((u'app_label', u'model'),)
default_permissions : (u'add', u'change', u'delete')
```


## session(django.contrib.sessions.models.Session)

```

    Django provides full support for anonymous sessions. The session
    framework lets you store and retrieve arbitrary data on a
    per-site-visitor basis. It stores data on the server side and
    abstracts the sending and receiving of cookies. Cookies contain a
    session ID -- not the data itself.

    The Django sessions framework is entirely cookie-based. It does
    not fall back to putting session IDs in URLs. This is an intentional
    design decision. Not only does that behavior make URLs ugly, it makes
    your site vulnerable to session-ID theft via the "Referer" header.

    For complete documentation on using Sessions in your code, consult
    the sessions documentation that is shipped with Django (also available
    on the Django Web site).
    
```

|Fullname|Name|Type|PK|Unique|Index|Null/Blank|Comment|
|---|---|---|---|---|---|---|---|
|session key |session_key |varchar(40) |True |True | | | |
|session data |session_data |text | | | | | |
|expire date |expire_date |timestamp with time zone | | |True | | |

Options
```
default_permissions : (u'add', u'change', u'delete')
```




