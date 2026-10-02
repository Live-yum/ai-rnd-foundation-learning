# 05 · 产品模板与认证

[总目录](../README.md) · [上一阶段](../04-local-foundation/README.md) · [下一阶段](../06-generation/README.md)

## 为什么先写模板，再写生成器

生成器的主要工作不是让模型写一整套CRUD，而是把已审阅的应用模板和批准的结构组合起来。因此这一站先完成“将被复制的产品”，下一站才写复制和冻结设计的过程。`templates/product` 整个目录都需要落盘，包括业务扩展和验证脚本，因为生成器按完整目录复制；不能把尚未讲解的业务文件先省略，否则最终包不再是同一实现。

从 `schema.py` 阅读数据流：它读取生成后的 `approved-spec.json`，根据字段声明建SQLAlchemy表，决定使用独立 SQLite 文件还是本机 PostgreSQL。`fields.py` 为请求建立严格输入模型，`querying.py` 把关键词、枚举筛选和含边界的日期查询变成参数化条件。`app.py` 提供注册、登录与CRUD，每条数据通过服务端当前用户约束所属范围，不能信任客户端提交的 owner_id。

密码使用带盐哈希；产品发出的访问Token在数据库中保存其哈希与有效期。平台访问令牌保护“谁能操作研发平台”，产品Token保护“谁能访问最终客户记录”，模型API_KEY则只用于推理供应商，三者不能互换。普通注册和管理员初始化也是两回事：业务产品的初始化管理员由 `manage.py bootstrap-admin` 单独建立，密码通过终端隐藏输入，不能凭借普通注册获得管理角色。

## 页面只是完整链路的一环

`templates/frontends/simple-admin/app.js` 根据 `/schema` 呈现已批准实体和字段，把日期、枚举、搜索/筛选条件映射到HTTP请求。选择关系、提交表单、显示错误和重新加载需要保持一致；不能只看首屏渲染就认为认证和业务完成。业务模式安装时，`business_runtime.py` 替换相关CRUD与schema路由，继续使用同一个认证入口，并在每次请求从服务端重新加载角色。

`verify.py` 是可信验收入口。普通实体走 `verify-browser.cjs`；客服业务由 `verify_business.py` 与 `verify-business-browser.cjs` 检查。这些测试脚本也会进入交付包，让新目录复验不必借平台源码。它们不受编码模型控制，不能在规则失败时改测试以求通过。

## 本站检查：模板齐全，但暂时不启动

```bash
# .learning/commands/05-syntax.sh
uv run python -m compileall -q templates/product templates/business/common
```

命令应退出码为0；成功可能没有输出。它只编译语法，不导入模板应用，也不创建产品数据库。此刻不要在 `templates/product` 中执行 `uv run python app.py`：它尚没有生成的 `approved-spec.json`、`selection.json`、迁移文件和从规则解释器复制出的 `rule_engine.py`。缺这些文件是阶段边界，不是应当手工做一套重复配置。

Node22准备好后，可增加下面的纯语法检查；没有Node时将本项记录为“待第06阶段浏览器准备”，不能伪装通过。

```bash
# .learning/commands/05-node-syntax.sh
node --check templates/frontends/simple-admin/app.js
node --check templates/product/verify-browser.cjs
node --check templates/product/verify-business-browser.cjs
```

本阶段完成后，你应该能沿着“批准字段 → schema → API输入校验 → SQL写入 → 前端表单”口述完整路径，并指出服务端何处阻止跨用户访问。第10站会把角色、关联、工作流、提醒和统计展开；这里先保证完整产品文件集合就位，不把未来功能留成 `pass`。

## 本阶段源码和后续依赖

本阶段首次创建 22 个源文件，完整位置见[文件落盘顺序](files.md)。已在前站创建的模块不重复覆盖；本章深入使用已有模块时回到[总索引](../source-index.md)查找。只有各步骤写明的检查代表本阶段成果，完整平台和外部服务验收留到最后一站。
