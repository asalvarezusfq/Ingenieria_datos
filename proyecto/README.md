# Sistema de Monitoreo de Transporte Público

Proyecto académico de Data Engineering.

## Levantar el proyecto

```bash
docker compose build
docker compose up -d
docker compose ps
```

- Elasticsearch: http://localhost:9201
- Kibana: http://localhost:5602
- Airflow: http://localhost:8081 (usuario/clave en `docker compose logs airflow | grep password`)
- MySQL: localhost:3307
- PostgreSQL: localhost:5433
