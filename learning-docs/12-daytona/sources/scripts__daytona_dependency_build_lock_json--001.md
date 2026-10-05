# scripts/daytona_dependency_build.lock.json · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.daytona_dependency_build.lock.j；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `scripts/daytona_dependency_build.lock.json`；**本文件共有 1 段**。本段覆盖源文件 L1–L13。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1731`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/daytona_dependency_build.lock.json", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "395fe18fdeed403d765b0d5fa2c56f4df034ee7f5103333acb81b452e9596252"} -->
````json
// scripts/daytona_dependency_build.lock.json
{
  "schema": 1,
  "tools": [
    {"name": "setuptools", "version": "80.9.0", "url": "https://files.pythonhosted.org/packages/a3/dc/17031897dae0efacfea57dfd3a82fdd2a2aeb58e0ff71b77b87e44edc772/setuptools-80.9.0-py3-none-any.whl", "sha256": "062d34222ad13e0cc312a4c02d73f059e86a4acbfbdea8f8f76b28c99f306922"},
    {"name": "wheel", "version": "0.45.1", "url": "https://files.pythonhosted.org/packages/0b/2c/87f3254fd8ffd29e4c02732eee68a83a1d3c346ae39bc6822dcbcb697f2b/wheel-0.45.1-py3-none-any.whl", "sha256": "708e7481cc80179af0e556bbf0cc00b8444c7321e2700b8d8580231d13017248"},
    {"name": "maturin", "version": "1.9.4", "url": "https://files.pythonhosted.org/packages/d2/46/001fcc5c6ad509874896418d6169a61acd619df5b724f99766308c44a99f/maturin-1.9.4-py3-none-manylinux_2_12_x86_64.manylinux2010_x86_64.musllinux_1_1_x86_64.whl", "sha256": "a0868d52934c8a5d1411b42367633fdb5cd5515bec47a534192282167448ec30"}
  ],
  "sdists": [
    {"name": "crcmod", "version": "1.7", "url": "https://files.pythonhosted.org/packages/6b/b0/e595ce2a2527e169c3bcd6c33d2473c1918e0b7f6826a043ca1245dd4e5b/crcmod-1.7.tar.gz", "sha256": "dc7051a0db5f2bd48665a990d3ec1cc305a466a77358ca4492826f41f283601e"},
    {"name": "esdk-obs-python", "version": "3.26.6", "url": "https://files.pythonhosted.org/packages/e1/d4/c9a2b33935c620678bd5acf5e32feda70ef09f384b24eb17a5719f72f5fe/esdk_obs_python-3.26.6.tar.gz", "sha256": "5014e76e85ffa9eda821169302e74868991867ac947da73bc28eb0e6dfba3ab1"},
    {"name": "sqlglotrs", "version": "0.6.1", "url": "https://files.pythonhosted.org/packages/59/13/e77dcfd72b849a113bea7ccee79329f77751704e66560410176b1f4657f9/sqlglotrs-0.6.1.tar.gz", "sha256": "f638a7a544698ade8b0c992c8c67feae17bd5c2c760114ab164bd0b7dc8911e1"}
  ]
}
````
