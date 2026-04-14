# Zopia.ai API 接口完整文档

> 抓取时间: 2026-04-14
> 工具: Playwright + _buildManifest.js 静态分析
> 网站: https://zopia.ai
> 技术栈: Next.js (SSG/SSR) + React + i18n

---

## 一、网站概述

Zopia 是一个 **AI 影视创作平台**，号称"世界首个无限免费 AI 影视 Agent"。

**核心功能：**
- AI 导演 Agent：输入创意或剧本 → 自动生成完整视频
- Seedance 2.0：真人级视频生成模型
- 多模态创作：脚本 → 角色 → 分镜 → 时间线 → 最终视频
- 模板系统：预制模板快速创作
- 团队协作：多人项目管理
- 积分/订阅系统：付费解锁高级功能

**支持语言：** 英文 (en)、中文 (zh)、日文 (ja)

---

## 二、技术架构

```
┌─────────────────────────────────────────────────┐
│                  Next.js 前端                    │
│         React + SSG + i18n (3语言)              │
├─────────────────────────────────────────────────┤
│  zopia.ai          │  _next/                    │
│  (页面路由)         │  (JS/CSS/图片)            │
├────────────────────┴────────────────────────────┤
│              /api/* (RESTful API)               │
├─────────────────────────────────────────────────┤
│  认证: NextAuth (Google OAuth + Email)          │
│  支付: Stripe (Checkout Session)                │
│  存储: S3 (Presigned URL)                       │
│  监控: Sentry                                   │
│  分析: Amplitude                                │
└─────────────────────────────────────────────────┘
```

---

## 三、完整页面路由列表 (53个)

### 3.1 公开页面

| 路由 | 说明 | 类型 |
|------|------|------|
| `/` | 首页/Landing Page | SSG |
| `/home` | 用户主页面 (需登录) | SSR |
| `/auth/signin` | 登录页 (Google/Email) | SSR |
| `/pricing` | 价格页面 | SSG |
| `/blog` | 博客列表 | SSG |
| `/blog/[slug]` | 博客文章详情 | SSG |
| `/blog/rss.xml` | RSS 订阅源 | SSG |
| `/seedance` | Seedance 功能页 | SSG |
| `/openclaw` | OpenClaw API 页 | SSG |
| `/privacy` | 隐私政策 | SSR |
| `/terms` | 服务条款 | SSR |
| `/download` | 客户端下载 | SSG |

### 3.2 用户功能页面

| 路由 | 说明 |
|------|------|
| `/base/[baseId]` | 项目详情页 |
| `/bases` | 项目列表页 |
| `/team` | 团队列表 |
| `/team/[teamId]` | 团队详情 |
| `/affiliate` | 推广联盟 |
| `/go/[refId]` | 推广链接跳转 |
| `/settings/api-tokens` | API Token 管理 |
| `/payment-callback` | 支付回调页 |

### 3.3 编辑器页面

| 路由 | 说明 |
|------|------|
| `/editor/blog` | 博客编辑器列表 |
| `/editor/blog/create` | 创建博客 |
| `/editor/blog/edit/[id]` | 编辑博客 |
| `/editor/kol-rate` | KOL 费率管理 |
| `/editor/seo-examples` | SEO 示例 |
| `/editor/voices` | 语音管理 |

### 3.4 管理后台页面 (Admin)

| 路由 | 说明 |
|------|------|
| `/admin/home` | 管理首页 |
| `/admin/affiliate` | 推广联盟管理 |
| `/admin/analytics/cost` | 成本分析 |
| `/admin/analytics/everyday_cost` | 每日成本 |
| `/admin/analytics/payusers` | 付费用户分析 |
| `/admin/analytics/queue` | 队列监控 |
| `/admin/analytics/user-queue` | 用户队列 |
| `/admin/base/list` | 基础数据列表 |
| `/admin/coupon` | 优惠券管理 |
| `/admin/debug/impersonate` | 用户模拟调试 |
| `/admin/electron` | 电子客户端管理 |
| `/admin/invite` | 邀请管理 |
| `/admin/invite/send` | 发送邀请 |
| `/admin/migrate/account_v2` | 账户迁移 |
| `/admin/migrate/base_attachment` | 基础附件迁移 |
| `/admin/migrate/subscription_v2` | 订阅迁移 |
| `/admin/migrate/table_attachment` | 表格附件迁移 |
| `/admin/migrate_multi_ep` | 多端点迁移 |
| `/admin/prompts` | Prompt 管理 |
| `/admin/recharge-discount-codes` | 充值折扣码 |
| `/admin/reward` | 奖励管理 |
| `/admin/short-links` | 短链接管理 |
| `/admin/sitevar` | 站点变量 |
| `/admin/style/demo` | 样式演示 |

### 3.5 测试页面

| 路由 | 说明 |
|------|------|
| `/test/billing` | 计费测试 |
| `/test/chat-socket` | 聊天 Socket 测试 |
| `/test/s3` | S3 存储测试 |
| `/test/sentry` | Sentry 监控测试 |
| `/test/volces-asset` | 火山引擎资源测试 |

---

## 四、核心 API 接口详解 (30+)

### 4.1 认证相关 (Auth)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/auth/session` | 获取当前会话状态 |
| POST | `/api/auth/signin` | 登录 (NextAuth) |
| POST | `/api/auth/callback/email` | Email 验证码登录回调 |

```
GET /api/auth/session
Response: {} (未登录) 或 {user: {...}, expires: "..."} (已登录)

POST /api/auth/callback/email?email=user@example.com
Body: {csrfToken, callbackUrl}
作用: 发送登录链接到邮箱
```

### 4.2 用户与账户 (User)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/user/api-token` | 获取用户的 API Token 列表 |
| POST | `/api/user/api-token` | 创建新的 API Token |

### 4.3 计费与订阅 (Billing)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/billing/getBalance` | 获取账户余额/积分 |
| POST | `/api/billing/createCheckoutSession` | 创建 Stripe 支付会话 |
| GET | `/api/billing/listTransactions?pageSize=N` | 获取交易记录 |
| GET | `/api/billing/recharge-discount-codes/summary` | 充值折扣码汇总 |
| GET | `/api/subscription/get` | 获取订阅信息 |

```
POST /api/billing/createCheckoutSession
Body: {planId, amount, currency}
Response: {sessionId, url} (Stripe Checkout URL)

GET /api/billing/getBalance
Response: {balance: 1500, subscription: {...}}

GET /api/subscription/get
Response: {plan: "pro", status: "active", expiresAt: "..."}
```

### 4.4 项目管理 (Base)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/base/list` | 获取项目列表 |
| POST | `/api/base/create` | 创建新项目 |
| GET | `/api/base/[baseId]` | 获取项目详情 |
| POST | `/api/base/import` | 导入项目 |
| POST | `/api/base/task` | 创建任务 |
| GET | `/api/base/task/status` | 获取任务状态 |

```
POST /api/base/create
Body: {name, template, settings}
Response: {id: "xxx", name: "...", createdAt: "..."}

POST /api/base/task
Body: {baseId, type: "video_generation", prompt, settings}
Response: {taskId: "xxx", status: "pending"}
```

### 4.5 作品展示 (Showcase)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/showcase/list?page=N` | 获取展示列表 (分页) |
| GET | `/api/showcase/[id]` | 获取单个展示详情 |
| POST | `/api/showcase/review` | 审核展示作品 |
| POST | `/api/showcase/migrate` | 迁移展示数据 |

```
GET /api/showcase/list?page=1
Response: {items: [{id, title, thumbnail, author, likes, views}], total, page}

POST /api/showcase/review
Body: {id, status: "approved"|"rejected", reason}
Response: {success: true}
```

### 4.6 文件上传 (Upload)

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/upload/attachment` | 上传附件 |
| GET | `/api/s3/presigned-url` | 获取 S3 预签名上传 URL |

```
POST /api/upload/attachment
Body: FormData {file}
Response: {url: "https://s3.../xxx.jpg", key: "attachments/xxx.jpg"}

GET /api/s3/presigned-url
Response: {url: "https://s3...?signature=...", expires: 3600}
```

### 4.7 模型管理 (Model)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/model/listModelByFolderName?folder=checkpoints` | 获取 Checkpoint 模型列表 |
| GET | `/api/model/listModelByFolderName?folder=loras` | 获取 LoRA 模型列表 |
| GET | `/api/model/listModelByFolderName?folder=controlnet` | 获取 ControlNet 模型 |
| GET | `/api/model/listModelByFolderName?folder=vae` | 获取 VAE 模型 |
| GET | `/api/model/listModelByFolderName?folder=animatediff_models` | 获取 AnimateDiff 模型 |

```
GET /api/model/listModelByFolderName?folder=checkpoints
Response: [{name: "model_v1.safetensors", size: 2137000000, url: "..."}, ...]
```

### 4.8 机器管理 (Machine)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/machine/listMyMachines` | 获取用户的机器列表 |
| GET | `/api/machine/listMachineModels?machineID=*` | 获取机器可用模型 |

### 4.9 存储管理 (Storage)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/storage/listMyStorage` | 获取用户存储使用情况 |

### 4.10 团队管理 (Team)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/team/list` | 获取团队列表 |
| POST | `/api/team/create` | 创建团队 |
| POST | `/api/team/[teamId]/invite` | 邀请成员 |

### 4.11 邀请系统 (Invite)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/invite/list` | 获取邀请列表 |
| POST | `/api/invite/create` | 创建邀请链接 |

### 4.12 推广联盟 (Affiliate)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/affiliate/first-purchase-discount-status` | 首购折扣状态 |

### 4.13 图片审核 (Image)

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/image/volces-moderation` | 火山引擎图片审核 |

### 4.14 Seedance (视频生成)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/seedance-modes` | 获取 Seedance 可用模式 |

### 4.15 管理后台 API (Admin)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/admin/base/list?page=N` | 获取基础数据列表 |
| GET | `/api/admin/analytics/cost?date=YYYY-MM` | 获取成本分析 |
| POST | `/api/admin/coupon-codes/create` | 创建优惠券 |
| GET | `/api/admin/coupon-codes/list?pageSize=1000` | 获取优惠券列表 |
| POST | `/api/admin/invite/create` | 创建管理员邀请 |
| GET | `/api/admin/invite/list?pageSize=1000` | 获取邀请列表 |
| POST | `/api/admin/debug/stop-impersonate` | 停止用户模拟 |

### 4.16 编辑器 API (Editor)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/editor/blog/list` | 获取博客编辑列表 |
| GET | `/api/editor/blog/[id]` | 获取博客详情 |
| POST | `/api/editor/blog/create` | 创建博客 |
| PUT | `/api/editor/blog/[id]` | 更新博客 |
| DELETE | `/api/editor/blog/[id]` | 删除博客 |

---

## 五、URL Rewrite 规则

```
/:nextInternalLocale(en|zh|ja)/express/:path*  →  未知内部路由
/:nextInternalLocale(en|zh|ja)/skill           →  内部 skill 路由
/:nextInternalLocale(en|zh|ja)/skill.md        →  内部 skill 文档
```

---

## 六、第三方服务集成

| 服务商 | 域名/端点 | 用途 |
|--------|-----------|------|
| Google Fonts | `fonts.gstatic.com` | 字体加载 |
| Amplitude | `api2.amplitude.com` | 用户行为分析 |
| Amplitude Config | `sr-client-cfg.amplitude.com` | 分析配置 |
| Google OAuth | NextAuth 内置 | 用户登录 |
| Stripe | `/api/billing/*` | 支付处理 |
| AWS S3 | `/api/s3/presigned-url` | 文件存储 |
| 火山引擎 | `/api/image/volces-moderation` | 内容审核 |
| Sentry | 页面JS中引用 | 错误监控 |

---

## 七、认证机制

```
认证方式: NextAuth.js
├── Google OAuth (主要登录方式)
├── Email Magic Link (邮箱验证码登录)
└── Session Cookie (会话管理)

登录流程:
1. 用户访问 /auth/signin
2. 选择 Google 或 Email 登录
3. Google: 重定向到 Google OAuth → 回调
4. Email: 输入邮箱 → POST /api/auth/callback/email → 收到邮件 → 点击链接
5. 建立 Session → Cookie
6. 后续请求自动携带 Cookie

Token 管理:
- /settings/api-tokens 管理 API Token
- GET /api/user/api-token 获取 Token 列表
- POST /api/user/api-token 创建新 Token
```

---

## 八、积分/订阅系统

```
积分类型:
├── 永久积分 (Permanent Credits) - 不过期
├── 订阅积分 (Subscription Credits) - 订阅期内有效
├── 每日签到积分 (Daily Sign-in Credits) - 7天过期
├── 促销积分 (Promotional Credits) - 活动赠送
└── 团队积分 (Team Credits) - 团队共享

订阅计划:
- Free: 基础功能
- Pro: 高级功能 + 更多积分
- Enterprise: 团队/企业级

支付流程:
1. 用户选择充值/订阅
2. POST /api/billing/createCheckoutSession
3. 重定向到 Stripe Checkout
4. 支付成功 → /payment-callback
5. 系统验证 → 充值积分/激活订阅
```

---

## 九、Seedance 视频生成

```
Seedance 2.0 是 Zopia 的核心 AI 视频生成模型

GET /api/seedance-modes
→ 返回可用的生成模式

POST /api/base/task
Body: {
  baseId: "项目ID",
  type: "video_generation",
  prompt: "视频描述",
  settings: {
    mode: "seedance",
    duration: 5,
    resolution: "1080p",
    ...
  }
}
→ 返回 taskId

GET /api/base/task/status?taskId=xxx
→ 返回 {status: "processing"|"completed"|"failed", result: {...}}
```

---

## 十、完整 API 端点列表

```
# 认证
GET  /api/auth/session
POST /api/auth/signin
POST /api/auth/callback/email

# 用户
GET  /api/user/api-token
POST /api/user/api-token

# 计费
GET  /api/billing/getBalance
POST /api/billing/createCheckoutSession
GET  /api/billing/listTransactions
GET  /api/billing/recharge-discount-codes/summary
GET  /api/subscription/get

# 项目
GET  /api/base/list
POST /api/base/create
GET  /api/base/[baseId]
POST /api/base/import
POST /api/base/task
GET  /api/base/task/status

# 展示
GET  /api/showcase/list
GET  /api/showcase/[id]
POST /api/showcase/review
POST /api/showcase/migrate

# 文件
POST /api/upload/attachment
GET  /api/s3/presigned-url

# 模型
GET  /api/model/listModelByFolderName

# 机器
GET  /api/machine/listMyMachines
GET  /api/machine/listMachineModels

# 存储
GET  /api/storage/listMyStorage

# 团队
GET  /api/team/list

# 邀请
GET  /api/invite/list

# 推广
GET  /api/affiliate/first-purchase-discount-status

# 图片
POST /api/image/volces-moderation

# Seedance
GET  /api/seedance-modes

# 管理后台
GET  /api/admin/base/list
GET  /api/admin/analytics/cost
POST /api/admin/coupon-codes/create
GET  /api/admin/coupon-codes/list
POST /api/admin/invite/create
GET  /api/admin/invite/list
POST /api/admin/debug/stop-impersonate

# 编辑器
GET  /api/editor/blog/list
GET  /api/editor/blog/[id]
```

---

*文档由 Playwright + 静态分析自动生成*
