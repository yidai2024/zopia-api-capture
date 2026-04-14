# Zopia.ai 安全漏洞分析报告

> 分析时间: 2026-04-14
> 目标: https://zopia.ai
> 发现问题: 7 个

---

## 漏洞汇总

| # | 严重性 | 类型 | 名称 |
|---|--------|------|------|
| 1 | 🟡 中危 | 信息泄露 | 测试/调试端点暴露在生产环境 |
| 2 | 🟢 低危 | 信息泄露 | 公开展示接口泄露用户数据 |
| 3 | 🟢 低危 | 认证缺陷 | CSRF Token 可未认证获取 |
| 4 | 🟢 低危 | 信息泄露 | Base ID 可通过公开接口枚举 |
| 5 | 🟢 低危 | 信息泄露 | Seedance AI 模型配置公开 |
| 6 | 🟡 中危 | 信息泄露 | 管理后台路由可完整枚举 |
| 7 | 🟢 低危 | 信息泄露 | robots.txt 泄露敏感路径 |

---

## 详细分析

### 1. 测试/调试端点暴露在生产环境 [中危]

**问题**: 测试页面和调试功能暴露在生产环境

**影响端点**:
- `/test/billing` - 计费测试
- `/test/chat-socket` - Socket 测试
- `/test/s3` - S3 配置测试
- `/test/sentry` - Sentry 配置
- `/test/volces-asset` - 火山引擎资源测试
- `/admin/debug/impersonate` - 用户冒充功能

**影响**: 泄露内部配置、可能被利用进行用户冒充

**建议**: 移除生产环境中的测试路由，或添加 IP 白名单

---

### 2. 公开展示接口泄露用户数据 [低危]

**问题**: `/api/showcase/list` 返回完整的用户对象

**泄露字段**:
- `user.id` - 用户内部 ID
- `user.username` - 用户名
- `user.image_url` - Google 头像 URL
- `base_id` - 项目 ID (可枚举)

**实际数据**:
```json
{
  "id": "bGWkXmw4rxUjm-B6xgIUF",
  "base_id": "base_X_XzOAYCHthD9x5r3yytp",
  "title": "她的审判日(1)",
  "user": {
    "id": 37687,
    "username": "yeticn_nWuwxC",
    "image_url": "https://lh3.googleusercontent.com/..."
  }
}
```

**影响**: 收集用户用户名和 ID，可用于社工或账号枚举

**建议**: 仅返回必要字段，添加分页限制

---

### 3. CSRF Token 可未认证获取 [低危]

**问题**: `/api/auth/csrf` 返回有效的 CSRF Token

**影响**: 配合其他漏洞进行 CSRF 攻击

**建议**: 检查 NextAuth 配置，确保 CSRF 保护完整

---

### 4. Base ID 可通过公开接口枚举 [低危]

**问题**: 通过 `/api/showcase/list` 可获取大量 `base_id`

**获取示例**:
```
base_X_XzOAYCHthD9x5r3yytp
base_HJye9j550dQqD5qmiR1m4
base_cXUhmgWxcXwPMcaAgmMZq
```

**影响**: 可用于尝试访问未公开的项目

**建议**: 使用 UUID 格式，避免可预测的 ID 格式

---

### 5. Seedance AI 模型配置公开 [低危]

**问题**: `/api/seedance-modes` 无需认证即可访问

**泄露内容**: 4 个生成模式的完整配置
- `n_grid` - 多宫格分镜生视频
- `multi_ref_v2` - 元素到视频顺序
- `video_ref` - 视频参考
- `multi_ref` - 元素到视频并行

**影响**: 了解内部 AI 模型配置

**建议**: 敏感配置需要认证访问

---

### 6. 管理后台路由可完整枚举 [中危]

**问题**: `_buildManifest.js` 暴露所有 24 个管理路由

**暴露的管理路由**:
```
/admin/home
/admin/affiliate
/admin/analytics/cost
/admin/analytics/everyday_cost
/admin/analytics/payusers
/admin/analytics/queue
/admin/analytics/user-queue
/admin/base/list
/admin/coupon
/admin/debug/impersonate  ← 高危
/admin/electron
/admin/invite
/admin/invite/send
/admin/migrate/*
/admin/prompts
/admin/recharge-discount-codes
/admin/reward
/admin/short-links
/admin/sitevar
/admin/style/demo
```

**影响**: 攻击者可以精确了解管理后台结构

**建议**: 管理路由不应出现在前端构建清单中

---

### 7. robots.txt 泄露敏感路径 [低危]

**问题**: robots.txt 明确列出敏感路径

**泄露路径**:
```
Disallow: /api/
Disallow: /admin/
Disallow: /home
Disallow: /affiliate
Disallow: /template/manage
```

**影响**: 确认敏感路径存在

**建议**: robots.txt 仅包含必要信息

---

## 安全评估

| 维度 | 评分 | 说明 |
|------|------|------|
| 认证保护 | ⭐⭐⭐⭐ | 敏感 API 均返回 401/403 |
| 信息泄露 | ⭐⭐⭐ | 存在多处信息泄露 |
| 测试端点 | ⭐⭐ | 测试页面暴露在生产环境 |
| 配置安全 | ⭐⭐⭐ | Next.js 构建清单泄露路由 |

**总体评价**: 中等安全水平。认证保护较好，但存在信息泄露和测试端点暴露问题。

---

*分析工具: Playwright + 静态分析*
*分析时间: 2026-04-14*
