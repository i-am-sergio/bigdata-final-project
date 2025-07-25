pipeline {
    agent any

    environment {
        USER_HADOOP = "/home/hadoop/"
    }

    stages {
        stage('Start Services in Parallel') {
            parallel {
                stage('Start Elasticsearch') {
                    steps {
                        sh '''
                            echo "Iniciando Elasticsearch con Java 17..."
                            cd /home/hadoop/elasticsearch-7.17.15/
                            ./bin/elasticsearch &
                            sleep 10
                        '''
                    }
                }

                stage('Start Grafana') {
                    steps {
                        sh '''
                            echo "Iniciando Grafana..."
                            cd /home/hadoop/grafana-v10.4.2/
                            ./bin/grafana-server web &
                            sleep 10
                        '''
                    }
                }

                stage('Consumer Elasticsearch') {
                    steps {
                        sh '''
                            echo "Activando entorno virtual y ejecutando consumerfinal.py..."
                            export PYENV_ROOT="$HOME/.pyenv"
                            export PATH="$PYENV_ROOT/bin:$PATH"
                            eval "$(pyenv init -)"
                            eval "$(pyenv virtualenv-init -)"
                            pyenv activate pyspark-env
                            cd /home/hadoop/
                            python3 consumerfinal.py
                        '''
                    }
                }
            }
        }
    }
}
