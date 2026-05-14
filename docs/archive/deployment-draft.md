# AI 出题助手 - 部署指南

> **版本**：v1.0 | **日期**：2026-04-28

---

## 1. 环境变量

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| DATABASE_URL | PostgreSQL 连接串 | `postgresql://...` |
| ELASTICSEARCH_URL | ES 地址 | `http://localhost:9200` |
| DEEPSEEK_API_KEY | DeepSeek Key | `sk-...` |

---

## 2. Docker Compose 部署

```bash
docker-compose up -d
```

---

## 3. 监控与日志

详细部署指南待补充。

**文档维护者**：运维团队  
**最后更新**：2026-04-28
