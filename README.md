# Back Video Highlight

Бэкенд для обработки и хранения видео.

Проект состоит из двух частей:
- **main** — взаимодействие с фронтендом (API, модели, представления)
- **logistic** — работа с ML (задачи обработки, логика работы с ML)

## Запуск Backend

```bash
docker-compose up -d
```

## URL сервисов
- API: http://45.80.129.41:8001  
- Админка: http://45.80.129.41:8001/admin/ (admin/admin)
- Swagger (документация API): http://45.80.129.41:8001/api/docs/
- MinIO (хранилище): http://45.80.129.41:9001 (minioadmin / minioadmin)
