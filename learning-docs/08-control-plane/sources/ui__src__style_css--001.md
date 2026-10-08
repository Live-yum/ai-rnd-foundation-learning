# ui/src/style.css · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 定义操作台的布局、间距、响应式断点和状态样式；真实组件仍负责交互与无障碍语义。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/src/style.css`；**本文件共有 1 段**。本段覆盖源文件 L1–L2669。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`45746`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/src/style.css", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ff810602d86690bf084c90c4f5a46199a640cafac0c03d9105e0160a6e04dc09"} -->
````css
/* ui/src/style.css */
:root {
  font-synthesis: weight;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  color: #27364f;
  background: #f6f8fc;
  font-family:
    Inter,
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    'PingFang SC',
    'Microsoft YaHei',
    sans-serif;
  font-size: 14px;
  line-height: 1.65;
  font-weight: 400;
}
* {
  box-sizing: border-box;
}
body {
  margin: 0;
}
button,
input,
textarea {
  font: inherit;
}
button {
  cursor: pointer;
}
button:disabled {
  cursor: not-allowed;
}
button,
a,
input,
textarea,
[tabindex] {
  -webkit-tap-highlight-color: transparent;
}
button:focus-visible,
a:focus-visible {
  outline: 3px solid #8c9bff;
  outline-offset: 4px;
}
h1,
h2,
h3,
h4,
p {
  margin: 0;
}
h1,
h2,
h3 {
  font-weight: 700;
  color: #26334c;
  letter-spacing: -0.02em;
}
h1 {
  font-size: 29px;
  line-height: 1.45;
}
h2 {
  font-size: 19px;
  line-height: 1.5;
}
h3 {
  font-size: 15px;
  line-height: 1.55;
}
p {
  line-height: 1.8;
  color: #5e708a;
}
ul {
  padding-left: 22px;
}
small {
  font-size: 12px;
}
.app-shell {
  min-height: 100vh;
}
.sidebar {
  position: fixed;
  z-index: 30;
  inset: 0 auto 0 0;
  width: 236px;
  background: #f9faff;
  border-right: 1px solid #e5ebf5;
  padding: 28px 16px 20px;
  display: flex;
  flex-direction: column;
}
.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  background: none;
  border: 0;
  padding: 0 8px;
  color: #27364f;
  text-align: left;
}
.brand strong {
  font-size: 20px;
  letter-spacing: 0.02em;
  white-space: nowrap;
}
.brand-mark {
  background: #445bf4;
  border-radius: 12px;
  color: white;
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  font-size: 24px;
}
.new-conversation.ant-btn {
  margin: 34px 8px 22px;
  background: white;
  color: #7487a4;
  font-weight: 500;
  height: 44px;
}
.main-nav,
.bottom-nav {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.main-nav button,
.bottom-nav button {
  display: flex;
  align-items: center;
  gap: 13px;
  border: 0;
  background: transparent;
  text-align: left;
  padding: 12px 14px;
  border-radius: 9px;
  color: #5e708a;
  font-size: 15px;
  min-height: 44px;
}
.main-nav button .anticon,
.bottom-nav button .anticon {
  font-size: 19px;
}
.main-nav button:hover,
.bottom-nav button:hover {
  background: #f0f3fa;
}
.main-nav button.active,
.bottom-nav button.active {
  background: #edf1ff;
  color: #445cff;
  font-weight: 600;
}
.sidebar-recents {
  margin-top: 35px;
  overflow: auto;
  min-height: 60px;
}
.sidebar-recents h3 {
  font-size: 13px;
  color: #5e708a;
  font-weight: 500;
  padding: 0 14px 16px;
}
.sidebar-recents button {
  display: flex;
  align-items: center;
  gap: 10px;
  background: none;
  border: 1px solid transparent;
  width: 100%;
  border-radius: 7px;
  padding: 11px 12px;
  text-align: left;
  color: #5e708a;
  font-size: 13px;
}
.sidebar-recents button span:last-child {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.sidebar-recents button.selected {
  border-color: #e1e8f5;
  background: white;
}
.recent-dot {
  width: 6px;
  height: 6px;
  background: #445cf7;
  border-radius: 50%;
  flex-shrink: 0;
}
.sidebar-empty {
  font-size: 12px;
  padding: 0 14px;
}
.bottom-nav {
  margin-top: auto;
  padding-top: 35px;
}
.workspace-profile {
  display: flex;
  align-items: center;
  gap: 11px;
  text-align: left;
  border: 0;
  border-top: 1px solid #e2e9f4;
  background: none;
  color: #5e708a;
  padding: 24px 10px 0;
  margin-top: 25px;
}
.workspace-profile small {
  display: block;
  font-size: 10px;
  color: #5e708a;
  letter-spacing: 0.03em;
}
.profile-avatar {
  display: grid;
  place-items: center;
  border-radius: 50%;
  width: 35px;
  height: 35px;
  color: #4b64fb;
  background: #e7ecff;
  font-weight: 600;
}
.app-body {
  margin-left: 236px;
  min-width: 0;
}
.topbar {
  height: 72px;
  border-bottom: 1px solid #e3eaf5;
  background: white;
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 0 33px;
  position: relative;
  z-index: 10;
}
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 18px;
  font-size: 14px;
  color: #5e708a;
}
.breadcrumb strong {
  font-weight: 500;
  color: #5e708a;
}
.topbar-status {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #5e708a;
  font-size: 12px;
}
.status-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex: none;
}
.status-dot.online {
  background: #21a682;
}
.status-dot.warning {
  background: #d3a343;
}
.status-dot.muted-dot {
  background: #a8b5cc;
}
main:focus {
  outline: none;
}
.global-alert {
  padding: 14px 32px 0;
}
.skip-link {
  position: fixed;
  top: -60px;
  left: 250px;
  z-index: 100;
  background: #fff;
  padding: 10px 20px;
}
.skip-link:focus {
  top: 8px;
}
.mobile-menu,
.mobile-bottom-nav {
  display: none;
}
.panel {
  background: white;
  border: 1px solid #e1e8f4;
  border-radius: 12px;
  overflow: hidden;
}
.page {
  padding: 30px 32px 52px;
  max-width: 1600px;
  margin: auto;
}
.page-heading {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: center;
  margin-bottom: 34px;
}
.page-heading p {
  margin-top: 9px;
}
.eyebrow {
  font-size: 10px;
  color: #5e708a;
  font-weight: 500;
  margin-bottom: 12px;
  letter-spacing: 0.025em;
}
.section-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.muted {
  color: #5e708a;
  font-size: 13px;
}
.success-icon {
  color: #24a884;
}
.error-icon {
  color: #de6177;
}
.panel-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
  padding: 22px 24px;
  border-bottom: 1px solid #e4eaf5;
}
.panel-heading p {
  font-size: 13px;
  margin-top: 6px;
}
.panel-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
  padding: 16px 24px;
  border-top: 1px solid #e4eaf5;
  color: #5e708a;
  font-size: 13px;
}
.panel-content {
  padding: 24px;
}
.field-hint {
  font-size: 12px;
  margin-top: 8px;
  color: #5e708a;
  line-height: 1.8;
}
.field-error {
  font-size: 13px;
  color: #d8546d;
  margin-top: 8px;
}
.page-footnote {
  font-size: 13px;
  color: #5e708a;
  margin-top: 24px;
}
.info-callout {
  background: #f0f4ff;
  border: 1px solid #dce5ff;
  border-radius: 10px;
  display: flex;
  gap: 15px;
  padding: 23px;
  color: #5e708a;
  margin-top: 22px;
}
.info-callout > .anticon {
  font-size: 20px;
  color: #5069ff;
  flex-shrink: 0;
  margin-top: 3px;
}
.info-callout strong {
  font-size: 15px;
}
.info-callout p {
  margin-top: 6px;
}
.info-callout .ant-btn {
  margin-top: 12px;
}
.home-page {
  max-width: 1280px;
  margin: auto;
  padding: 36px 32px 48px;
}
.home-hero .sparkle-tile {
  margin-bottom: 23px;
}
.sparkle-tile {
  width: 53px;
  height: 53px;
  display: grid;
  place-items: center;
  font-size: 29px;
  color: #4e65ff;
  background: #edf1ff;
  border: 1px solid #dbe3ff;
  border-radius: 16px;
}
.home-hero h1 {
  font-size: clamp(26px, 3vw, 36px);
  margin: 8px 0 12px;
  letter-spacing: -0.02em;
}
.home-hero > p {
  font-size: 15px;
  max-width: 820px;
}
.model-pill {
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
  border: 0;
  border-radius: 7px;
  background: #f6f8fd;
  padding: 10px 13px;
  color: #5e708a;
  text-align: left;
}
.starter-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.starter-card {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 20px;
  background: white;
  border: 1px solid #e1e8f4;
  border-radius: 11px;
  text-align: left;
  transition: border-color 0.2s;
}
.starter-card:hover {
  border-color: #8c9bff;
}
.starter-card > .anticon {
  font-size: 19px;
  color: #7f91ac;
  margin-bottom: 13px;
}
.starter-card h3 {
  font-size: 15px;
  margin-bottom: 10px;
}
.starter-card p {
  font-size: 13px;
  color: #5e708a;
}
.recent-section {
  margin-top: 40px;
}
.recent-section > .section-top {
  margin-bottom: 18px;
}
.recent-section h3 {
  font-size: 14px;
  color: #5e708a;
}
.recent-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}
.recent-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px;
  text-align: left;
  cursor: pointer;
}
.recent-card:hover {
  border-color: #bcc9ff;
}
.recent-card h3 {
  color: #34425b;
  font-size: 14px;
}
.recent-card p {
  font-size: 12px;
  margin-top: 7px;
}
.recent-card .ant-tag {
  margin-left: auto;
  margin-right: 0;
  white-space: normal;
  text-align: center;
  font-size: 11px;
}
.project-icon {
  display: grid;
  place-items: center;
  background: #eef2ff;
  color: #526aff;
  border-radius: 10px;
  width: 42px;
  height: 42px;
  font-size: 19px;
  flex: none;
}
.quiet-empty {
  display: flex;
  align-items: center;
  gap: 17px;
  padding: 24px 22px;
  color: #8a9bb5;
}
.quiet-empty > .anticon {
  font-size: 24px;
  color: #9badd1;
}
.quiet-empty strong {
  font-size: 14px;
  color: #5e708a;
}
.quiet-empty p {
  font-size: 12px;
  margin-top: 4px;
}
.quiet-empty > .ant-btn {
  margin-left: auto;
}
.form-label {
  display: block;
  font-size: 13px;
  color: #5e708a;
  margin-bottom: 9px;
  margin-top: 24px;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0 24px;
}
.form-grid .ant-select,
.form-grid .ant-input-number,
.create-form > .ant-select {
  width: 100%;
}
.full-width {
  grid-column: 1/-1;
}
.label-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
}
.label-row .ant-tag {
  margin-bottom: 8px;
}
.label-row .form-label {
  margin-bottom: 9px;
}
.form-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  margin: 26px 0 12px;
}
.form-actions > .muted {
  margin-right: auto;
}
.compact-alert {
  margin-top: 14px;
}
.question-text {
  margin-top: 12px;
}
.create-form {
  padding-top: 8px;
}
.create-form > p {
  font-size: 13px;
}
.auth-form .auth-symbol {
  display: grid;
  place-items: center;
  width: 45px;
  height: 45px;
  border-radius: 12px;
  color: #4d66f7;
  background: #eef2ff;
  font-size: 24px;
  margin: 12px 0 15px;
}
.auth-form p {
  font-size: 13px;
}
.auth-form code {
  font-size: 12px;
  background: #f0f3fa;
  padding: 3px 6px;
  border-radius: 4px;
  color: #4d6283;
}
.auth-form .ant-btn {
  margin-top: 24px;
}
.locked-page {
  min-height: 70vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
  text-align: center;
}
.locked-page h1 {
  font-size: 27px;
}
.list-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin: 12px 0 27px;
}
.search-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  width: 520px;
  max-width: 100%;
}
.list-toolbar .ant-segmented {
  background: none;
}
.ant-segmented .ant-segmented-item-selected {
  color: #4a62ff;
  background: #edf1ff;
  box-shadow: none;
}
.project-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
  margin-bottom: 27px;
}
.project-card {
  padding: 23px 20px 0;
  display: flex;
  flex-direction: column;
  min-height: 225px;
}
.project-card h2 {
  margin: 24px 0 12px;
  font-size: 19px;
  overflow-wrap: anywhere;
}
.project-card > p {
  font-size: 13px;
}
.project-card > .muted {
  margin: 15px 0;
}
.project-card-footer {
  border-top: 1px solid #e4eaf4;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  margin-top: auto;
  padding: 9px 0;
  font-size: 11px;
  color: #5e708a;
}
.project-card-footer .ant-btn {
  color: #4c65ff;
}
.table-scroll {
  overflow: auto;
}
table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  white-space: nowrap;
}
th {
  background: #f8f9fd;
  color: #5e708a;
  font-size: 12px;
  font-weight: 400;
  padding: 14px 22px;
}
td {
  padding: 18px 22px;
  border-bottom: 1px solid #e5ebf4;
  color: #5e708a;
  font-size: 13px;
}
tr:last-child td {
  border: 0;
}
td strong {
  color: #5e708a;
  font-size: 13px;
}
td small {
  display: block;
  color: #5e708a;
  margin-top: 5px;
}
td .ant-tag {
  white-space: nowrap;
}
.list-empty {
  padding: 45px 16px;
}
.run-heading {
  background: white;
  border-bottom: 1px solid #e2e9f4;
  padding: 21px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}
.run-heading h1 {
  font-size: 21px;
  display: flex;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
}
.run-heading h1 .ant-tag {
  font-weight: 400;
  font-size: 12px;
}
.run-heading p {
  font-size: 12px;
  margin-top: 7px;
  color: #5e708a;
}
.run-heading p span {
  margin: 0 6px;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.run-notice {
  padding: 16px 32px 0;
}
.conversation-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 272px;
  min-height: calc(100vh - 167px);
}
.conversation-main {
  padding: 31px 42px 32px;
  min-width: 0;
  position: relative;
}
.messages {
  display: flex;
  flex-direction: column;
  gap: 29px;
}
.chat-message {
  display: flex;
  gap: 12px;
  min-width: 0;
}
.user-message {
  justify-content: flex-end;
}
.user-message .message-body {
  max-width: 82%;
  border-radius: 12px;
  background: #eef2ff;
  padding: 15px 21px;
  color: #5e708a;
}
.message-text {
  font-size: 14px;
  line-height: 1.9;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  color: #5e708a;
}
.assistant-avatar {
  background: #eef2ff;
  color: #4d65ff;
  display: grid;
  place-items: center;
  border-radius: 9px;
  width: 32px;
  height: 32px;
  flex: none;
  font-size: 22px;
  margin-top: 2px;
}
.assistant-message .message-body {
  flex: 1;
  min-width: 0;
}
.message-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  margin: 3px 0 16px;
  color: #5e708a;
  font-size: 11px;
  flex-wrap: wrap;
}
.message-meta strong {
  font-size: 13px;
  color: #5e708a;
}
.message-meta .ant-tag {
  font-size: 10px;
}
.typing-cursor {
  display: inline-block;
  width: 2px;
  height: 16px;
  background: #536aff;
  animation: blink 1s infinite;
  vertical-align: middle;
  margin-left: 3px;
}
@keyframes blink {
  50% {
    opacity: 0;
  }
}
.conversation-gate {
  margin: 29px 0 0 44px;
}
.gate-preview {
  padding: 24px;
}
.gate-preview > p {
  margin: 15px 0;
}
.gate-preview > .ant-btn {
  margin-top: 14px;
}
.question-card {
  margin-top: 17px;
}
.question-body {
  padding: 22px;
}
.question {
  margin-bottom: 26px;
}
.question:last-child {
  margin-bottom: 0;
}
.question-title {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 17px;
}
.question-title h3 {
  margin-right: 12px;
  font-size: 15px;
}
.question-title .ant-tag {
  font-size: 11px;
  margin: 0;
}
.choice-list {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 9px;
}
.choice.ant-radio-wrapper,
.choice.ant-checkbox-wrapper {
  border: 1px solid #dfe7f4;
  border-radius: 7px;
  margin: 0;
  padding: 11px 13px;
  color: #5e708a;
  align-items: flex-start;
  line-height: 1.6;
  min-height: 42px;
  width: 100%;
}
.choice.ant-radio-wrapper-checked,
.choice.ant-checkbox-wrapper-checked {
  background: #f1f4ff;
  border-color: #9fadff;
  color: #657ba7;
}
.choice .ant-radio,
.choice .ant-checkbox {
  margin-top: 2px;
}
.choice small {
  display: block;
  margin-top: 3px;
  color: #5e708a;
}
.choice-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 9px;
  width: 100%;
}
.legacy-question {
  display: flex;
  gap: 12px;
  margin-bottom: 17px;
}
.legacy-question span {
  background: #eef2ff;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  display: grid;
  place-items: center;
  color: #596ffc;
  font-size: 11px;
  flex: none;
}
.legacy-question h3 {
  font-size: 14px;
}
.chat-composer {
  background: white;
  border: 1px solid #e2e9f4;
  border-radius: 12px;
  margin: 32px 0 0;
  display: flex;
  align-items: flex-end;
  gap: 13px;
  padding: 11px 13px;
}
.chat-composer textarea {
  resize: none;
  font-size: 13px;
  padding: 4px;
}
.chat-composer > .ant-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  flex: none;
  padding: 0;
}
.working-note {
  display: flex;
  gap: 14px;
  padding: 25px 15px;
  margin-left: 32px;
  font-size: 13px;
}
.working-note strong {
  color: #5e708a;
  font-weight: 500;
}
.working-note p {
  font-size: 12px;
}
.pulse-dot {
  width: 8px;
  height: 8px;
  background: #5269fd;
  border-radius: 50%;
  margin-top: 8px;
  box-shadow: 0 0 0 5px #e7ecff;
  animation: blink 1.5s infinite;
  flex: none;
}
.jump-latest {
  position: sticky;
  bottom: 22px;
  display: block;
  margin: 15px auto 0;
  box-shadow: 0 4px 20px #dbe1f080;
}
.progress-rail {
  background: white;
  border-left: 1px solid #e2e9f4;
  padding: 24px 26px;
  display: flex;
  flex-direction: column;
}
.progress-rail > .section-top h3 {
  font-size: 15px;
}
.progress-rail > .section-top .anticon {
  color: #94a5be;
  font-size: 18px;
}
.rail-steps {
  list-style: none;
  padding: 0;
  margin: 24px 0 22px;
}
.rail-steps li {
  position: relative;
  display: flex;
  gap: 13px;
  min-height: 75px;
  color: #5e708a;
}
.rail-steps li:not(:last-child):before {
  position: absolute;
  content: '';
  width: 1px;
  background: #e4eaf4;
  top: 26px;
  bottom: 5px;
  left: 11px;
}
.step-dot {
  border-radius: 50%;
  width: 23px;
  height: 23px;
  background: #f4f6fa;
  display: grid;
  place-items: center;
  color: #9cabc1;
  font-size: 10px;
  flex: none;
}
.rail-steps strong {
  font-size: 13px;
  font-weight: 400;
  color: #5e708a;
}
.rail-steps p {
  font-size: 12px;
  color: #5e708a;
  margin-top: 8px;
}
.rail-steps li.current .step-dot {
  background: #445df6;
  color: white;
}
.rail-steps li.current strong {
  color: #4b63fa;
  font-weight: 600;
}
.rail-steps li.done .step-dot {
  background: #ecf8f3;
  color: #22a481;
}
.rail-callout {
  background: #f8faff;
  border: 1px solid #e1e8f5;
  border-radius: 8px;
  padding: 14px;
  margin-top: 15px;
  font-size: 13px;
}
.rail-callout > span {
  color: #5e708a;
  font-size: 12px;
}
.rail-callout strong {
  display: block;
  color: #5e708a;
  font-size: 13px;
  margin-top: 9px;
}
.rail-callout p {
  font-size: 12px;
  margin-top: 9px;
  color: #5e708a;
}
.rail-callout.compact {
  padding: 10px 13px;
}
.rail-callout.compact strong {
  margin-top: 0;
  font-weight: 400;
}
.rail-callout .ant-btn {
  font-size: 11px;
  padding: 3px 0;
  height: auto;
  white-space: normal;
  text-align: left;
}
.stream-status {
  margin-top: auto;
  padding-top: 55px;
  color: #5e708a;
  font-size: 11px;
}
.stream-status .status-dot {
  margin-right: 7px;
}
.stream-status small {
  display: block;
  margin-top: 7px;
  font-size: 10px;
}
.blocked-list {
  background: #fff9ec;
  border: 1px solid #f4dfb7;
  padding: 12px 14px;
  border-radius: 10px;
  font-size: 13px;
  color: #ad8032;
}
.blocked-list .ant-alert {
  border: 0;
  padding: 0;
  background: transparent;
}
.blocked-list ul {
  margin-bottom: 0;
}
.recovery-panel {
  padding: 22px;
}
.recovery-panel h2 {
  margin: 12px 0;
}
.recovery-panel > .header-actions {
  margin-top: 20px;
}
.review-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 24px;
}
.review-document {
  padding: 28px;
}
.document-title {
  padding-bottom: 25px;
  border-bottom: 1px solid #e5ebf5;
  margin-bottom: 23px;
}
.document-title h2 {
  font-size: 23px;
  margin: 12px 0 15px;
}
.document-title p {
  font-size: 13px;
  color: #5e708a;
}
.document-section {
  margin: 22px 0 30px;
}
.document-section:last-child {
  margin-bottom: 0;
}
.document-section h3 {
  font-size: 16px;
  margin-bottom: 14px;
}
.section-number {
  font-size: 14px;
  font-weight: 700;
  margin-right: 12px;
}
.document-text {
  font-size: 14px;
  color: #5e708a;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
  line-height: 1.9;
}
.document-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.document-list li {
  position: relative;
  padding: 7px 0 7px 23px;
  color: #5e708a;
  font-size: 13px;
  line-height: 1.85;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
}
.document-list li:before {
  content: '✓';
  color: #23a886;
  position: absolute;
  left: 0;
  top: 7px;
}
.nested-document .document-section {
  margin: 7px 0 13px;
}
.nested-document h3.section-label {
  font-size: 12px;
  font-weight: 500;
  color: #5e708a;
  margin-bottom: 3px;
}
.nested-document .document-text {
  font-size: 13px;
}
.document-row {
  background: #f8faff;
  border-bottom: 1px solid #e5ebf5;
  border-radius: 6px;
  padding: 14px 15px;
  display: flex;
  align-items: flex-start;
  gap: 14px;
  margin: 6px 0;
}
.document-row > .data-document {
  flex: 1;
  min-width: 0;
}
.row-number {
  color: #acb7cb;
  font-size: 10px;
  margin-top: 3px;
}
.approval-panel {
  padding: 22px 18px;
}
.approval-panel h2 {
  font-size: 18px;
  margin: 18px 0 12px;
}
.approval-panel > p {
  font-size: 13px;
  margin-bottom: 23px;
}
.approval-panel > .ant-checkbox-wrapper {
  margin: 18px 0 20px;
  color: #5e708a;
  font-size: 12px;
}
.approval-panel > .ant-input {
  margin: 17px 0;
}
.approval-panel > .ant-btn {
  margin-top: 15px;
  white-space: normal;
  height: auto;
  min-height: 40px;
  font-size: 13px;
}
.approval-secondary {
  display: flex;
  align-items: center;
  gap: 5px;
  margin: 9px 0 15px;
}
.approval-secondary > .ant-btn:first-child {
  flex: 1;
}
.approval-panel .field-hint {
  font-size: 10px;
  margin: 15px 0 0;
}
.approval-panel ul {
  color: #a07d40;
  font-size: 12px;
  padding-left: 18px;
}
.review-actions > .info-callout {
  padding: 18px 15px;
  font-size: 12px;
}
.review-actions > .info-callout p {
  margin: 0;
  font-size: 12px;
}
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 17px;
  margin-bottom: 25px;
}
.stat {
  padding: 18px;
}
.stat > span {
  font-size: 12px;
  color: #5e708a;
}
.stat > strong {
  display: block;
  font-size: 24px;
  color: #2a3954;
  margin: 10px 0 15px;
  overflow-wrap: anywhere;
}
.stat > p {
  font-size: 12px;
  color: #5e708a;
}
.progress-columns {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 270px;
  gap: 22px;
}
.milestones {
  list-style: none;
  margin: 0;
  padding: 8px 24px;
}
.milestone {
  display: flex;
  align-items: center;
  gap: 14px;
  border: 0;
  border-bottom: 1px solid #edf1f8;
  background: transparent;
  width: 100%;
  text-align: left;
  padding: 17px 4px;
  border-radius: 6px;
}
.milestone > .anticon {
  font-size: 18px;
  color: #9caec8;
}
.milestone > .success-icon {
  color: #23a686;
}
.milestone > .error-icon {
  color: #db657c;
}
.milestone strong {
  display: block;
  font-size: 14px;
  color: #34425b;
}
.milestone > span:not(.anticon) {
  font-size: 11px;
  color: #5e708a;
  overflow-wrap: anywhere;
}
.milestone > .ant-tag {
  margin-left: auto;
  flex: none;
  font-size: 10px;
}
.phase-details {
  padding: 24px 21px;
}
.phase-details h2 {
  font-size: 17px;
}
.phase-details h3 {
  font-size: 20px;
  color: #4b64ff;
  margin: 24px 0 12px;
}
.phase-details p {
  font-size: 13px;
}
.phase-details > .muted {
  margin-top: 33px;
  margin-bottom: 12px;
}
.phase-details > .ant-btn {
  display: block;
  height: auto;
  white-space: normal;
  text-align: left;
  padding: 7px 0;
  font-size: 12px;
}
.event-panel {
  margin-top: 24px;
}
.event-list {
  padding: 14px 24px;
  max-height: 650px;
  overflow: auto;
}
.event-row {
  display: grid;
  grid-template-columns: 120px 135px minmax(0, 1fr);
  gap: 12px;
  padding: 10px 0;
  font-size: 12px;
}
.event-row time {
  color: #5e708a;
}
.event-kind {
  color: #647bfa;
  font-size: 11px;
}
.event-row p {
  font-size: 12px;
  line-height: 1.7;
  overflow-wrap: anywhere;
}
.delivery-page > .ant-alert {
  padding: 21px 24px;
}
.delivery-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 21px;
  margin-top: 24px;
}
.delivery-grid .panel-content > .ant-btn {
  margin-top: 25px;
}
.delivery-grid .data-document {
  max-height: 500px;
  overflow: auto;
}
.definition-panel {
  padding: 22px;
  margin-top: 24px;
}
.definition-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 17px;
  margin-top: 20px;
}
.definition {
  padding: 16px;
  border-radius: 7px;
  background: #f7f9fd;
  border: 1px solid #e2e9f5;
}
.definition h3 {
  font-size: 14px;
  color: #5e708a;
}
.definition p {
  font-size: 12px;
  margin-top: 10px;
}
.definition.runtime {
  background: #edf9f4;
  border-color: #d1edde;
}
.definition.runtime h3 {
  color: #28a485;
}
.delivery-approval {
  justify-content: space-between;
  align-items: center;
}
.delivery-approval h2 {
  font-size: 17px;
}
.delivery-approval p {
  font-size: 12px;
}
.delivery-approval .ant-checkbox-wrapper {
  font-size: 12px;
  color: #5e708a;
  margin-top: 15px;
}
.settings-layout {
  display: grid;
  grid-template-columns: 195px minmax(0, 1fr);
  gap: 23px;
}
.settings-tabs {
  padding: 12px;
}
.settings-tabs button {
  display: block;
  text-align: left;
  border: 0;
  background: none;
  color: #5e708a;
  border-radius: 8px;
  padding: 12px 13px;
  width: 100%;
  margin-bottom: 7px;
}
.settings-tabs button strong {
  font-size: 14px;
  font-weight: 500;
}
.settings-tabs button small {
  display: block;
  font-size: 11px;
  margin-top: 6px;
  color: #5e708a;
}
.settings-tabs button.active {
  background: #edf1ff;
  color: #4b63ff;
}
.settings-tabs button.active strong {
  font-weight: 600;
}
.security-note {
  padding: 27px 0 0;
  font-size: 12px;
}
.security-note h3 {
  font-size: 13px;
  color: #5e708a;
  margin-bottom: 14px;
}
.security-note p {
  font-size: 12px;
  margin-bottom: 8px;
  line-height: 1.9;
  color: #5e708a;
}
.settings-form {
  padding: 27px;
}
.settings-form > .section-top {
  margin-bottom: 26px;
  align-items: flex-start;
}
.settings-form > .section-top h2 {
  font-size: 20px;
}
.settings-form > .section-top p {
  font-size: 12px;
  margin-top: 12px;
}
.settings-form > .ant-alert {
  margin-top: 16px;
}
.settings-form .form-label {
  margin-top: 27px;
}
.settings-form .ant-input,
.settings-form .ant-select-selector,
.settings-form .ant-input-number {
  font-size: 13px;
}
.settings-footnote {
  display: flex;
  gap: 12px;
  border-bottom: 1px solid #e3eaf5;
  padding: 27px 0;
  margin-bottom: 19px;
  color: #5e708a;
  font-size: 14px;
}
.settings-footnote p {
  font-size: 12px;
}
.settings-footnote .anticon {
  margin-top: 4px;
}
.settings-main > .info-callout p {
  font-size: 12px;
}
.settings-main > .info-callout strong {
  font-size: 13px;
}
.review-toggle {
  margin-top: 45px;
  font-size: 13px;
  color: #5e708a;
}
.review-toggle > .ant-switch {
  margin-right: 10px;
}
.model-record {
  border-bottom: 1px solid #e4eaf4;
  padding: 14px 0;
}
.model-record:first-child {
  padding-top: 0;
}
.ant-drawer .data-document {
  overflow-wrap: anywhere;
}
.ant-tag {
  border: 0;
}
.ant-input::placeholder {
  color: #5e708a;
}
.ant-select-selection-placeholder {
  color: #5e708a !important;
}
.ant-btn-default {
  color: #5e708a;
}
.ant-btn-primary {
  background: #4359ef;
  box-shadow: none;
}
.ant-input,
.ant-select-selector {
  box-shadow: none !important;
}
.ant-input:focus,
.ant-input-focused,
.ant-select-focused .ant-select-selector {
  border-color: #8295fd !important;
}
.ant-checkbox-wrapper,
.ant-radio-wrapper {
  font-size: 13px;
}
.ant-alert-message {
  font-size: 13px;
}
.ant-alert-description {
  font-size: 12px;
}
.ant-modal-content {
  border: 1px solid #e0e6f5;
}
.ant-modal .ant-modal-title {
  font-size: 18px;
}
.ant-input-number {
  width: 100%;
}
/* Shared creation, queue and execution surfaces. */
.home-hero {
  margin-bottom: 28px;
}
.creation-panel {
  padding: 28px;
  margin-top: 24px;
}
.creation-panel .form-label {
  margin-top: 16px;
}
.template-picker {
  border: 0;
  padding: 0;
  margin: 28px 0 16px;
  min-width: 0;
}
.template-picker legend {
  margin-bottom: 14px;
  font-weight: 600;
  color: #27364f;
}
.template-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}
.template-card {
  display: grid;
  grid-template-columns: 16px minmax(0, 1fr);
  align-content: start;
  gap: 10px;
  padding: 18px 14px;
  border: 1px solid #dfe6f2;
  border-radius: 10px;
  background: #fbfcff;
  cursor: pointer;
  min-width: 0;
}
.template-card.selected {
  border-color: #5268ef;
  background: #f1f4ff;
  box-shadow: 0 0 0 1px #5268ef;
}
.template-card input {
  margin: 5px 0 0;
  accent-color: #445cf7;
}
.template-card > span:not(.template-card-title),
.template-card > small {
  grid-column: 2;
}
.template-card > span,
.template-card > small {
  color: #5e708a;
  font-size: 12px;
  overflow-wrap: anywhere;
}
.template-card-title strong {
  display: block;
  font-size: 14px;
  color: #27364f;
}
.template-card-title small {
  display: block;
  margin-top: 3px;
}
.selection-details {
  padding: 14px 16px;
  border-radius: 8px;
  background: #f7f9fd;
  margin-bottom: 24px;
}
.selection-details > p {
  font-size: 13px;
}
.selection-details .ant-collapse-header {
  padding: 12px 0 0 !important;
}
.selection-details .ant-collapse-content-box {
  padding-inline: 0 !important;
}
.coding-standard {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e1e8f4;
}
.coding-standard > small {
  display: block;
  overflow-wrap: anywhere;
  margin: 8px 0;
  color: #5e708a;
}
.coding-standard pre {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  max-height: 400px;
  overflow: auto;
  font: inherit;
  font-size: 13px;
  padding: 16px;
  background: white;
  border-radius: 8px;
}
.requirements-editor {
  border-top: 1px solid #e7ecf5;
  padding-top: 24px;
}
.requirements-editor textarea {
  line-height: 1.8;
}
.batch-draft {
  border: 1px solid #e1e8f4;
  border-radius: 10px;
  padding: 16px;
  margin: 16px 0;
}
.batch-draft .section-top h3 {
  color: #5064d8;
}
.add-batch {
  margin-top: 8px;
}
.execution-options {
  border-top: 1px solid #e7ecf5;
  padding-top: 24px;
  margin-top: 24px;
}
.execution-options > .ant-checkbox-wrapper {
  margin-top: 16px;
}
.execution-options .ant-alert {
  margin-top: 12px;
}
.extension-option {
  margin: 16px 0;
  font-size: 13px;
}
.extension-option > .ant-checkbox-wrapper {
  margin-top: 12px;
}
.creation-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-top: 24px;
}
.starter-section {
  margin-top: 28px;
}
.starter-section > .section-top {
  margin-bottom: 14px;
}
.batch-results {
  margin: 24px 0;
}
.queue-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  padding: 14px 24px;
  border-bottom: 1px solid #e7ecf5;
  font-size: 13px;
  color: #5e708a;
}
.queue-summary strong {
  font-size: 20px;
  color: #27364f;
  margin-right: 4px;
}
.filter-tabs {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}
.filter-tabs button {
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: #5e708a;
  min-height: 40px;
  padding: 7px 12px;
  white-space: nowrap;
}
.filter-tabs button.active {
  background: #eaf0ff;
  color: #3f55d5;
  font-weight: 600;
}
.filter-tabs button span {
  margin-left: 4px;
  font-size: 12px;
}
.template-filter {
  min-width: 150px;
}
.search-actions > .ant-input-affix-wrapper {
  flex: 1;
  min-width: 140px;
}
.list-error {
  margin-bottom: 20px;
}
.run-table td:first-child {
  white-space: normal;
  min-width: 180px;
  max-width: 300px;
  overflow-wrap: anywhere;
}
.run-table td:nth-child(3) {
  white-space: normal;
  min-width: 220px;
}
.run-tabs {
  display: flex;
  gap: 24px;
  border-bottom: 1px solid #e1e8f4;
  padding-inline: 32px;
  background: white;
}
.run-tabs button {
  background: none;
  border: 0;
  border-bottom: 3px solid transparent;
  color: #5e708a;
  min-height: 48px;
  padding: 12px 4px;
  white-space: nowrap;
}
.run-tabs button.active {
  border-bottom-color: #445cf7;
  color: #445cf7;
  font-weight: 600;
}
.run-context {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 32px;
  background: #f0f4fb;
  color: #5e708a;
  font-size: 13px;
}
.run-context .stream-status {
  margin: 0;
}
.rail-step {
  display: flex;
  gap: 14px;
  width: 100%;
}
.rail-steps li.failed .step-dot,
.milestones li.failed .step-dot {
  color: #d5526a;
  background: #fff0f3;
  border-color: #f0b7c0;
}
.milestones li.done .step-dot {
  color: #249673;
  background: #e8f7f0;
}
.milestones li.current .step-dot {
  border-color: #536bff;
  color: #445cf7;
}
.milestone > div {
  flex: 1;
  min-width: 0;
}
.milestone p {
  margin-top: 3px;
  font-size: 12px;
}
.milestone:hover,
.milestone[aria-pressed='true'] {
  background: #f1f4ff;
}
.phase-details .ant-empty {
  margin-block: 28px;
}
.event-panel .ant-select {
  min-width: 140px;
}
.event-row > div {
  min-width: 0;
}
.event-row details {
  margin-top: 6px;
  font-size: 12px;
}
.event-row .data-document {
  background: #f8faff;
  padding: 14px;
  border-radius: 8px;
  margin-top: 10px;
}
summary {
  cursor: pointer;
  color: #5064cc;
}
summary:focus-visible,
input[type='radio']:focus-visible {
  outline: 3px solid #8c9bff;
  outline-offset: 3px;
}
.panel,
.page,
.home-page,
.phase-details {
  min-width: 0;
}
@media (max-width: 1200px) {
  .sidebar {
    width: 210px;
    padding-inline: 12px;
  }
  .brand strong {
    font-size: 18px;
  }
  .app-body {
    margin-left: 210px;
  }
  .conversation-layout {
    grid-template-columns: minmax(0, 1fr) 230px;
  }
  .conversation-main,
  .progress-rail {
    padding: 24px;
  }
  .review-layout {
    grid-template-columns: minmax(0, 1fr) 250px;
    gap: 18px;
  }
  .project-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .list-toolbar {
    align-items: stretch;
    flex-direction: column;
  }
  .search-actions {
    width: 100%;
  }
}
@media (max-width: 980px) {
  .topbar {
    padding-inline: 24px;
  }
  .topbar-status > span:last-child {
    display: none;
  }
  .conversation-layout,
  .review-layout {
    display: block;
  }
  .progress-rail {
    display: none;
  }
  .review-actions {
    margin-top: 24px;
  }
  .review-actions > .info-callout {
    display: none;
  }
  .progress-columns,
  .delivery-grid,
  .settings-layout {
    grid-template-columns: minmax(0, 1fr);
  }
  .recent-grid,
  .template-grid {
    grid-template-columns: minmax(0, 1fr);
  }
  .stat-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .settings-tabs {
    display: flex;
    overflow-x: auto;
    gap: 5px;
    padding: 9px;
  }
  .settings-tabs button {
    min-width: 105px;
    flex: 1;
    margin: 0;
  }
  .security-note {
    display: none;
  }
  .run-heading {
    align-items: flex-start;
    flex-wrap: wrap;
  }
  .run-heading .header-actions {
    flex-wrap: wrap;
  }
  .delivery-approval {
    align-items: flex-start;
    flex-direction: column;
  }
}
@media (max-width: 720px) {
  .sidebar {
    visibility: hidden;
    transform: translateX(-100%);
    width: 260px;
    z-index: 60;
    padding: 24px 16px;
  }
  .sidebar.open {
    visibility: visible;
    transform: translateX(0);
  }
  .sidebar-overlay {
    position: fixed;
    inset: 0;
    background: #17264755;
    z-index: 50;
  }
  .app-body {
    margin-left: 0;
    padding-bottom: 78px;
  }
  .topbar {
    position: sticky;
    top: 0;
    height: 64px;
    padding-inline: 16px;
    gap: 12px;
    z-index: 25;
  }
  .mobile-menu {
    display: grid;
    place-items: center;
    border: 0;
    background: none;
    padding: 0;
    width: 32px;
    height: 44px;
    font-size: 21px;
  }
  .breadcrumb {
    gap: 0;
    min-width: 0;
    overflow: hidden;
    white-space: nowrap;
  }
  .breadcrumb > span {
    display: none;
  }
  .breadcrumb strong {
    color: #27364f;
  }
  .topbar-status {
    margin-left: auto;
  }
  .mobile-bottom-nav {
    display: flex;
    position: fixed;
    bottom: 0;
    inset-inline: 0;
    z-index: 35;
    background: #fffffffa;
    border-top: 1px solid #e3eaf5;
    justify-content: space-around;
    padding: 10px 10px max(10px, env(safe-area-inset-bottom));
  }
  .mobile-bottom-nav button {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    background: none;
    border: 0;
    min-width: 56px;
    min-height: 44px;
    color: #5e708a;
    font-size: 12px;
  }
  .mobile-bottom-nav .anticon {
    font-size: 20px;
  }
  .mobile-bottom-nav button.active {
    color: #445cf7;
  }
  .mobile-bottom-nav button:disabled {
    color: #a8b5cc;
  }
  .page,
  .home-page {
    padding: 24px 16px 32px;
  }
  .home-hero h1,
  .page-heading h1 {
    font-size: 26px;
  }
  .home-hero > p {
    font-size: 14px;
  }
  .page-heading {
    flex-wrap: wrap;
    gap: 16px;
    margin-bottom: 24px;
  }
  .creation-panel,
  .review-document,
  .approval-panel,
  .settings-form,
  .panel-content,
  .definition-panel,
  .gate-preview {
    padding: 20px 16px;
  }
  .creation-panel > .section-top {
    flex-wrap: wrap;
  }
  .creation-footer {
    align-items: stretch;
    flex-direction: column;
  }
  .creation-footer > .ant-btn {
    width: 100%;
  }
  .template-grid,
  .starter-grid,
  .project-grid,
  .form-grid,
  .definition-grid {
    grid-template-columns: minmax(0, 1fr);
  }
  .starter-card {
    min-height: 0;
  }
  .recent-card {
    padding: 16px;
  }
  .recent-card .project-icon {
    display: none;
  }
  .quiet-empty,
  .section-top,
  .panel-heading {
    flex-wrap: wrap;
  }
  .quiet-empty > .ant-btn {
    margin-left: 0;
  }
  .panel-heading {
    padding: 18px 16px;
  }
  .panel-footer,
  .form-actions {
    padding-inline: 16px;
    flex-wrap: wrap;
  }
  .search-actions {
    flex-wrap: wrap;
  }
  .search-actions > .ant-input-affix-wrapper {
    flex-basis: 100%;
  }
  .template-filter {
    flex: 1;
  }
  .filter-tabs {
    overflow-x: auto;
    flex-wrap: nowrap;
  }
  .filter-tabs button {
    flex: none;
  }
  .run-table thead {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip-path: inset(50%);
  }
  .run-table tbody {
    display: block;
  }
  .run-table tr {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    gap: 12px;
    padding: 18px 16px;
    border-bottom: 1px solid #e5ebf4;
  }
  .run-table td {
    display: block;
    padding: 0;
    border: 0;
    white-space: normal;
    overflow-wrap: anywhere;
  }
  .run-table td:nth-child(1),
  .run-table td:nth-child(3) {
    grid-column: 1 / -1;
  }
  .run-table td:nth-child(2) {
    grid-column: 1 / -1;
    font-size: 12px;
  }
  .run-table td:nth-child(2)::before {
    content: '模板：';
  }
  .run-table td:nth-child(4) {
    align-self: center;
    font-size: 12px;
  }
  .run-table td:nth-child(5) {
    text-align: right;
  }
  .global-alert,
  .run-notice {
    padding: 12px 16px 0;
  }
  .run-heading {
    display: block;
    padding: 20px 16px;
  }
  .run-heading h1 {
    font-size: 21px;
  }
  .run-heading .header-actions {
    margin-top: 12px;
  }
  .run-heading p {
    overflow-wrap: anywhere;
  }
  .run-tabs {
    padding-inline: 16px;
  }
  .run-tabs button {
    flex: 1;
    padding-inline: 8px;
  }
  .run-context {
    padding: 12px 16px;
    flex-direction: column;
    align-items: flex-start;
  }
  .conversation-main {
    padding: 24px 16px;
  }
  .assistant-avatar {
    width: 28px;
    height: 28px;
    font-size: 19px;
  }
  .chat-message {
    gap: 10px;
  }
  .message-meta {
    flex-wrap: wrap;
    gap: 8px;
  }
  .message-text {
    font-size: 14px;
  }
  .user-message .message-body {
    max-width: 94%;
  }
  .question-body {
    padding: 20px 16px;
  }
  .choice-grid {
    grid-template-columns: minmax(0, 1fr);
  }
  .choice.ant-radio-wrapper,
  .choice.ant-checkbox-wrapper {
    min-height: 44px;
  }
  .question-title {
    flex-wrap: wrap;
    gap: 8px;
  }
  .question-title h3 {
    flex-basis: 100%;
  }
  .gate-preview > .ant-btn,
  .delivery-approval .header-actions {
    width: 100%;
  }
  .delivery-approval .header-actions {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
  }
  .run-notice .ant-alert {
    flex-wrap: wrap;
  }
  .run-notice .ant-alert-action {
    margin-top: 12px;
  }
  .stat {
    padding: 16px;
  }
  .stat > strong {
    font-size: 21px;
  }
  .milestones {
    padding: 8px 16px;
  }
  .milestone {
    flex-wrap: wrap;
    gap: 10px;
  }
  .milestone > .ant-tag {
    margin-left: 36px;
  }
  .event-list {
    padding: 8px 16px;
  }
  .event-row {
    display: flex;
    flex-wrap: wrap;
    gap: 6px 12px;
  }
  .event-row > div {
    flex-basis: 100%;
  }
  .event-kind,
  .event-row time {
    font-size: 12px;
  }
  .event-panel .ant-select {
    width: 140px;
  }
  .form-grid {
    gap: 0;
  }
  .full-width {
    grid-column: auto;
  }
  .settings-layout {
    gap: 16px;
  }
  .settings-tabs button {
    min-width: 100px;
  }
  .settings-form .form-actions > .ant-btn {
    flex: 1;
  }
  .ant-modal {
    max-width: calc(100vw - 24px);
  }
  .ant-modal .ant-modal-content {
    padding: 22px 18px;
  }
  .skip-link {
    left: 12px;
  }
}
@media (prefers-reduced-motion: reduce) {
  *,
  *:before,
  *:after {
    animation: none !important;
    transition: none !important;
    scroll-behavior: auto !important;
  }
}

/* An unfinished operation cannot receive another answer, but the local composer remains visible. */
.local-draft-section {
  margin-top: 26px;
}
.busy-composer {
  margin-top: 0;
}
.draft-explanation {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  justify-content: space-between;
  padding: 9px 7px 0;
  font-size: 11px;
  color: #5e708a;
  line-height: 1.8;
}
.draft-explanation .ant-btn {
  flex: none;
  font-size: 11px;
}

/* Schema-aware documents keep design review scannable without hiding metadata. */
.metadata-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 13px 22px;
  margin: 0;
}
.metadata-grid > div {
  min-width: 0;
}
.metadata-grid dt {
  color: #71839e;
  font-size: 11px;
  margin: 0 0 3px;
}
.metadata-grid dd {
  margin: 0;
  color: #526780;
  font-size: 13px;
  line-height: 1.75;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
}
.entity-cards {
  display: flex;
  flex-direction: column;
  gap: 17px;
}
.entity-card {
  border: 1px solid #e1e8f4;
  border-radius: 10px;
  overflow: hidden;
  background: white;
}
.entity-card > header {
  display: flex;
  align-items: center;
  gap: 13px;
  padding: 17px 18px;
  background: #f6f8ff;
}
.entity-card > header h3 {
  font-size: 15px;
  margin: 0;
}
.entity-card > header p {
  font-size: 11px;
  color: #5e708a;
  margin-top: 4px;
}
.entity-symbol {
  font-size: 25px;
  color: #536bfa;
  background: #eaf0ff;
  width: 37px;
  height: 37px;
  display: grid;
  place-items: center;
  border-radius: 9px;
}
.field-table-region {
  overflow: auto;
}
.field-table {
  white-space: normal;
  table-layout: fixed;
}
.field-table th {
  padding: 12px 13px;
  font-size: 11px;
  color: #617590;
  background: #fafbfe;
}
.field-table td {
  padding: 14px 13px;
  font-size: 12px;
  line-height: 1.7;
  vertical-align: top;
  color: #5e708a;
  overflow-wrap: anywhere;
}
.field-table th:first-child {
  width: 18%;
}
.field-table th:nth-child(2) {
  width: 13%;
}
.field-table th:nth-child(3) {
  width: 11%;
}
.field-table th:nth-child(4) {
  width: 33%;
}
.field-table th:nth-child(5) {
  width: 25%;
}
.field-table td strong {
  color: #445873;
  font-size: 12px;
}
.field-table td small {
  color: #788ba6;
  font-size: 10px;
  margin-top: 2px;
}
.schema-type {
  font-size: 11px;
  background: #f0f3fb;
  color: #637ca5;
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-block;
  white-space: nowrap;
}
.constraint-line {
  display: block;
}
.document-details {
  margin: 0;
  border-top: 1px solid #e4ebf6;
  font-size: 12px;
  color: #5e708a;
}
.document-details > summary {
  cursor: pointer;
  padding: 12px 15px;
  color: #5870c6;
}
.document-details > .data-document {
  padding: 12px 18px 18px;
}
.complete-field {
  padding: 18px;
  border-top: 1px solid #edf1f7;
}
.complete-field h4 {
  margin: 0 0 14px;
  color: #354967;
  font-size: 13px;
}
@media (max-width: 720px) {
  .metadata-grid {
    gap: 12px 15px;
  }
  .metadata-grid dd {
    font-size: 12px;
  }
  .metadata-grid dt {
    font-size: 10px;
  }
  .field-table thead {
    display: none;
  }
  .field-table,
  .field-table tbody {
    display: block;
  }
  .field-table tr {
    display: grid;
    grid-template-columns: 1fr 1fr;
    padding: 14px 16px;
    gap: 8px 15px;
    border-bottom: 1px solid #e7edf6;
  }
  .field-table tr:last-child {
    border-bottom: 0;
  }
  .field-table td {
    display: block;
    border: 0;
    padding: 0;
    font-size: 11px;
  }
  .field-table td:before {
    content: attr(data-label);
    display: block;
    font-size: 10px;
    color: #71839e;
    margin-bottom: 2px;
  }
  .field-table td:first-child {
    grid-column: 1 / -1;
  }
  .field-table td:first-child:before {
    display: none;
  }
  .field-table td:first-child strong {
    font-size: 13px;
  }
  .entity-card > header {
    padding: 16px;
  }
  .entity-card > header h3 {
    font-size: 14px;
  }
  .entity-card > header p {
    font-size: 10px;
  }
  .document-details > summary {
    font-size: 11px;
  }
}

/* A horizontal stage picker scrolls within the viewport, never widens the grid. */
.settings-navigation,
.settings-main {
  min-width: 0;
}
.settings-tabs {
  max-width: 100%;
}
@media (max-width: 980px) {
  .settings-layout {
    grid-template-columns: minmax(0, 1fr);
  }
  .settings-tabs {
    overflow-x: auto;
    overscroll-behavior-x: contain;
  }
}
````
