# Jenkins
- install
wget https://get.jenkins.io/war-stable/2.516.1/jenkins.war
- run
/usr/lib/jvm/java-17-openjdk-amd64/bin/java -jar jenkins.war # jdk 17

# run consumer elasticsearch

# run kibana

# 






# configurar nuevo id de cluster kafka (Kraft)
bin/kafka-storage.sh random-uuid

# configurar nuevo cluster kafka
sudo nano config/kraft/server.properties ## actualizar ips publicas

# Formatear (3 brokers)
bin/kafka-storage.sh format -t KREHPzDEQhabiHDvPgWI6A -c config/kraft/server.properties


# iniciar kafka (3 brokers)
bin/kafka-server-start.sh config/kraft/server.properties

# crear topics kafka

bin/kafka-topics.sh --list --bootstrap-server localhost:9092

bin/kafka-topics.sh --create --topic temperature --bootstrap-server localhost:9092 --replication-factor 3 --partitions 1
bin/kafka-topics.sh --create --topic humidity --bootstrap-server localhost:9092 --replication-factor 3 --partitions 1
bin/kafka-topics.sh --create --topic pressure --bootstrap-server localhost:9092 --replication-factor 3 --partitions 1
bin/kafka-topics.sh --create --topic sound --bootstrap-server localhost:9092 --replication-factor 3 --partitions 1
bin/kafka-topics.sh --create --topic light --bootstrap-server localhost:9092 --replication-factor 3 --partitions 1

bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# consumer kafka
bin/kafka-console-consumer.sh --topic temperature --from-beginning --bootstrap-server localhost:9092