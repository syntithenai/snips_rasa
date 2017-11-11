#!/bin/bash
SUPERVISORD_CONF_FILE="/etc/supervisor/conf.d/supervisord.conf"
#touch $SUPERVISORD_CONF_FILE
/usr/bin/supervisord -c $SUPERVISORD_CONF_FILE

