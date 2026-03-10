# Desenvolvimento do Micro Serviço de Model Serving

docker build . -t microservice_ner
docker run -d --name ner_instance -p 80:80 microservice_ner

acesse http://localhost/docs para documentação do serviço


