# AI 语音外呼系统方案（马来西亚版"探客"）

> 目标：打造一个能用自己的声音、基于自己的产品资料库、主动联系马来西亚顾客并对话的 AI 系统，
> 并提供一个可以在手机上查看通话记录的管理界面。

---

## 一、五个核心问题的结论

### 1. 声音克隆 ✅
- **方案**：ElevenLabs Professional Voice Cloning
- 录制 30 分钟以上本人高质量讲话音频（安静环境、单人、自然语速）
- 克隆后的声音支持 **中文、马来语、英语** 等 32 种语言
- 实时对话用 ElevenLabs Flash 模型（端到端延迟 < 500ms）

### 2. 资料库训练 ✅（用 RAG 知识库，不是训练大模型）
- 不需要从零训练大模型（成本极高、效果反而差）
- 正确做法：**知识库 + RAG（检索增强生成）**
  - 把产品资料、价格表、FAQ、销售话术上传到平台知识库
  - AI 通话时实时检索资料回答顾客问题
  - 资料更新即时生效，不需要重新"训练"
- ElevenLabs Agents / Retell AI / Vapi 都内置知识库功能
- 自建方案：Claude API（`claude-opus-4-8`）+ 向量数据库做 RAG

### 3. 手机使用 ✅（云端运行 + 手机网页后台）
- AI 外呼引擎必须跑在云服务器上（需要 24/7 并发打电话）
- 管理后台做成响应式网页 / PWA，手机浏览器打开即用：
  - 查看通话记录、听录音、看文字转写
  - 修改话术、上传资料、管理客户名单

### 4. 马来西亚号码 ⚠️ 三条路

| 方案 | 说明 | 评价 |
|---|---|---|
| **WhatsApp Business Calling API** | AI 通过你的 WhatsApp Business 号码打语音电话。流程：先发消息请求通话许可 → 顾客同意 → 7 天内可拨打（15 天内最多发 2 次请求） | ⭐⭐⭐ 最推荐。马来西亚顾客都用 WhatsApp；本仓库已有 WhatsApp 发消息代理，可直接衔接"先发消息求许可"这一步 |
| **本地 SIP Trunk + BYOC** | 向 Toku / AVOXI / DIDlogic 或本地电信（Maxis、TIME 企业 SIP）申请马来西亚号码 SIP 中继，以 BYO SIP Trunk 方式接入 Vapi / Retell / ElevenLabs | ⭐⭐ 正式 PSTN 电话外呼用这条；来电显示 +60 号码 |
| GSM 网关 + 自己的 SIM 卡 | 用 SIM box 设备转接 | ❌ 不建议。MCMC 与电信公司打击 SIM box，会封号 |

> 注意：Twilio 对马来西亚本地号码限制很严，不能直接购买，所以需要 BYOC。

### 5. 通话记录界面 ✅
- Retell / Vapi / ElevenLabs 后台自带：录音、完整转写、AI 通话总结、时长与成功率统计
- 可通过 webhook 把每通电话的数据推到自己的数据库，做定制看板

---

## 二、推荐架构

```
客户名单 (CRM/Excel)
      │
      ▼
调度服务 (排程、批量外呼、重拨规则)        ← 自建（Python/Flask 起步即可）
      │
      ▼
AI 语音平台 (ElevenLabs Agents / Retell / Vapi)
  ├── 声音：你的 ElevenLabs 克隆音
  ├── 大脑：LLM + 知识库 RAG（自建走 Claude API: claude-opus-4-8）
  ├── 听写：平台内置 STT（中/马/英）
  └── 线路：WhatsApp Calling API 或 马来西亚 SIP Trunk (BYOC)
      │
      ▼
通话结束 webhook → 数据库 → 手机网页后台（记录/录音/转写/统计）
```

---

## 三、落地步骤

### 第一阶段：跑通原型（1–2 周）
1. 注册 ElevenLabs（或 Retell AI），克隆自己的声音
2. 上传产品资料建知识库，写好系统 prompt（开场白、话术、异议处理）
3. 用平台测试号码自己打给自己测试中文/马来语对话效果

### 第二阶段：接通马来西亚线路
4. 首选：申请 WhatsApp Business Calling API（通过 BSP，如 respond.io、Telnyx 等）
   - 复用本仓库的 WhatsApp 代理：先发模板消息请求通话许可
5. 备选：向 Toku / AVOXI / 本地电信申请 SIP trunk，BYOC 接入平台
6. 小批量（10–20 个老客户）实测，迭代话术

### 第三阶段：完整系统
7. 自建调度服务：名单导入、外呼排程、结果回写、失败重拨
8. 自建手机版后台（或先用平台自带后台 + webhook 导出数据）
9. 接 CRM：意向客户自动标记、转人工跟进

---

## 四、合规要点（马来西亚）

- **PDPA 2010**：只联系有既有业务关系或已同意被联系的客户
- 通话开场让 AI 表明身份（"我是 XX 公司的 AI 助手"）
- 顾客拒绝后加入内部黑名单，不再拨打
- WhatsApp 路线自带许可机制（先征得同意才能通话），合规风险最低
- 通话录音需告知对方

---

## 五、成本估算（参考）

| 项目 | 费用 |
|---|---|
| ElevenLabs 声音克隆 + Agents | 约 USD 22–99/月 起，通话约 USD 0.08–0.15/分钟 |
| Retell / Vapi 平台 | 约 USD 0.07–0.15/分钟（含 STT/TTS/LLM） |
| WhatsApp 外呼通话 | Meta 按分钟计费（按目的地国家费率） |
| SIP Trunk（如走 PSTN） | 月租 + 马来西亚本地话费 |
| 云服务器（调度+后台） | USD 10–40/月 |

月外呼几千通电话量级，总成本大致在几百美金。

---

## 参考资料

- ElevenLabs Voice Cloning: https://elevenlabs.io/voice-cloning
- ElevenLabs Agents Platform: https://elevenlabs.io/
- WhatsApp Business Calling API (Meta): https://developers.facebook.com/documentation/business-messaging/whatsapp/calling
- WhatsApp Calling + AI Voice Agents (Telnyx): https://telnyx.com/resources/whatsapp-calling-ai-voice-agents
- Retell AI: https://www.retellai.com/blog/best-voice-ai-providers
- Vapi 外呼文档: https://docs.vapi.ai/quickstart/phone/outbound
- BYOC / SIP Trunk for AI Voice (DIDlogic): https://didlogic.com/ai-voice/bring-your-own-carrier/
- Twilio 马来西亚语音规范: https://www.twilio.com/en-us/guidelines/my/voice
