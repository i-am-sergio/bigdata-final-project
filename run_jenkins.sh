#!/bin/bash
JAVA17=/usr/lib/jvm/java-17-openjdk-amd64/bin/java 
WAR_PATH=jenkins.war 

$JAVA17 -jar $WAR_PATH --httpPort=8080