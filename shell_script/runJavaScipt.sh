#!/bin/bash

#source /etc/profile
# Auth：Charseki
# Please change these parameters according to your real env.
# set Java Home: Remember that dolphin only supports JDK8!
JAVA_HOME=/usr/java/jdk1.8.0_162

# application directory
cd `dirname $0`
APP_HOME=`pwd`

APP_NAME="`cd ${APP_HOME} && find -name '*.jar' `"
JAR_HOME=`pwd |awk -F"/" '{print $NF}'`
# Java JVM lunch parameters
if [ x"$JAVA_MEM_OPTS" == x ];then
    JAVA_MEM_OPTS="-server -Xms512m -Xmx512m -Xmn128m -Xss256k -XX:+DisableExplicitGC -XX:+UseConcMarkSweepGC -XX:+CMSParallelRemarkEnabled -XX:LargePageSizeInBytes=128m -XX:+UseFastAccessorMethods -XX:+UseCMSInitiatingOccupancyOnly -XX:CMSInitiatingOccupancyFraction=70 "
fi


# waiting timeout for starting, in seconds
START_WAIT_TIMEOUT=30

psid=0
 
checkpid() {
   javaps=`$JAVA_HOME/bin/jps -l | grep "$JAR_HOME"`
   if [ -n "$javaps" ]; then
      psid=`echo $javaps | awk '{print $1}'`
   else
      psid=0
   fi
}



start() {
   checkpid

   if [ $psid -ne 0 ]; then
      echo "================================"
      echo "warn: $APP_NAME already started! (pid=$psid)"
      echo "================================"
   else
      echo -n "Starting $APP_NAME ..."
      #-Dspring.profiles.active=dev 指定环境
      nohup $JAVA_HOME/bin/java -jar -Dspring.profiles.active=dev -DCONFIG_ENABLE=true $JAVA_MEM_OPTS  ${APP_NAME} >${JAR_HOME}.log 2>&1 &   
      checkpid
      if [ $psid -ne 0 ]; then
         echo "(pid=$psid) [OK]"
      else
         echo "[Failed]"
      fi
   fi
}

stop() {
    
   sleep 2
   checkpid

   if [ $psid -ne 0 ]; then
      echo -n "Stopping $APP_NAME ...(pid=$psid) "
      #kill -9 $psid
      kill -9 $psid
      if [ $? -eq 0 ]; then
         echo "[OK]"
      else
         echo "[Failed]"
      fi

#      checkpid
#      if [ $psid -ne 0 ]; then
#         stop
#      fi
   else
      echo "================================"
      echo "warn: $APP_NAME is not running"
      echo "================================"
   fi
}



status() {
   checkpid

   if [ $psid -ne 0 ];  then
      echo "$APP_NAME is running! (pid=$psid)"
   else
      echo "$APP_NAME is not running"
   fi
}


info() {
   echo "System Information:"
   echo "****************************"
   echo `head -n 1 /etc/issue`
   echo `uname -a`
   echo
   echo "JAVA_HOME=$JAVA_HOME"
   echo `$JAVA_HOME/bin/java -version`
   echo
   echo "APP_HOME=$APP_HOME"
   echo "APP_NAME=$APP_NAME"
   echo "****************************"
}

case "$1" in
   'start')
      start
      ;;
   'stop')
     stop
     ;;
   'restart')
     stop
     echo "You restart the application ..."
     start #
     ;;
   'status')
     status
     ;;
   'info')
     info
     ;;
  *)
     echo "Usage: $0 {start|stop|restart|status|info}"
     exit 1
esac
