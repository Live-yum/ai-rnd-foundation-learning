# tools/embeddings/uv.lock · 1/1

[阶段导读](../../README.md) · [本阶段文件顺序](../../files.md) · [全部文件索引](../../../source-index.md)



**作用：精确依赖锁。** pyproject声明允许的依赖，uv.lock记录本次可复现安装的具体版本、平台条件及下载哈希。先抄写对应pyproject再完整保存此文件，使用uv sync --locked；不要为了跳过报错随意删锁。

**对应关系：** 平台、Aider和产品各有独立环境与锁，不能混用Python3.12和3.14依赖。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/embeddings/uv.lock`；**本文件共有 1 段**。本段覆盖源文件 L1–L356。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`44270`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/embeddings/uv.lock", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "90ff42cd704ae8f6b19cb71dadd005e833513c1330fb274e223bf2d91e9a1bc1"} -->
````toml
# tools/embeddings/uv.lock
version = 1
revision = 3
requires-python = "==3.12.*"

[[package]]
name = "certifi"
version = "2026.7.22"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/a3/c2/24167ea9858356b47a87a50d39908bfdb72ceeefe0041586e704e5376b3a/certifi-2026.7.22.tar.gz", hash = "sha256:741e2c3b351ddf169a738da9f2c048608ff7f2c5cc02f1ebc6b118bb090d5d55", size = 138112, upload-time = "2026-07-22T03:35:12.644Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/0b/a7/71ac2cff56fec219ed242bb11b8efb69fcc4bec75db06fb7bfe35de520e6/certifi-2026.7.22-py3-none-any.whl", hash = "sha256:62f22742b58a1a33014a2b6b706588a8d7e2a88ae7bd1a6ebe8c992928483775", size = 136983, upload-time = "2026-07-22T03:35:11.276Z" },
]

[[package]]
name = "charset-normalizer"
version = "3.5.2"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/33/1c/f41d4e74c28ab327ff3acd36053f7ea506c55872d7a90b0fa71aa3ab0c89/charset_normalizer-3.5.2.tar.gz", hash = "sha256:39de2a259fc954455c57274dc94c79d5842774e1247a016aff30bc0efed0f4ef", size = 172659, upload-time = "2026-09-30T04:39:23.398Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/e7/c8/693809898870237d82785a03f3b2b58fe4c9f14669f84a7d4e623c92a59e/charset_normalizer-3.5.2-cp312-cp312-macosx_10_13_universal2.whl", hash = "sha256:ed2a239c0ea213acc1908150a3037257083c7c083128f1a4cec2ec4b97dca491", size = 367780, upload-time = "2026-09-30T04:35:30.888Z" },
    { url = "https://files.pythonhosted.org/packages/c9/87/2fea8c13dc24b3ca9c6f803a5b2dfdeae73eb4f9e12c7885ed908ff0433c/charset_normalizer-3.5.2-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:b91363207bd9dc966a691e959bb47f64b30f7ac4b072be9968b366982f7db77c", size = 246730, upload-time = "2026-09-30T04:35:32.286Z" },
    { url = "https://files.pythonhosted.org/packages/a8/9e/09efac30b937722f46d3110ba30b875b24b2e3a266ed746cc4e376a94d80/charset_normalizer-3.5.2-cp312-cp312-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:38a873987f3be698494da8b2e3085e29da02da7b633dce73e79c699a113d7bf0", size = 237707, upload-time = "2026-09-30T04:35:33.709Z" },
    { url = "https://files.pythonhosted.org/packages/9e/18/70d76670b13686237863a379928d60bd10e021f17d243ab3d7014c4a5f4e/charset_normalizer-3.5.2-cp312-cp312-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:355ad8011081dec5412240c087a9a0c9d4d5039f3ed11a3f13e18c2b29b56c51", size = 273050, upload-time = "2026-09-30T04:35:35.138Z" },
    { url = "https://files.pythonhosted.org/packages/54/e2/77a8b09d5adc013ed07b95b01b8b8fa5441c4e810e83ee7e4aae2fa4d91a/charset_normalizer-3.5.2-cp312-cp312-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:ee21e28f0430bd6dc9086c6e525d5e818a44a5ad19720c8a0ef766792f3eb5e5", size = 270345, upload-time = "2026-09-30T04:35:36.502Z" },
    { url = "https://files.pythonhosted.org/packages/7f/c5/38806a25ab5e65fc178f39affeda20858efafede2fce1ffc2556cfc9fe73/charset_normalizer-3.5.2-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:3d31298449090ab8d47b7b1b2a555ff73cac7ed438a08b7ac160980c7ebed649", size = 257601, upload-time = "2026-09-30T04:35:37.919Z" },
    { url = "https://files.pythonhosted.org/packages/ae/8d/213565184708fdb263ae55e2c04ee1ff748129dd65d48ed0e3502da9c85a/charset_normalizer-3.5.2-cp312-cp312-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:5cde776b7cc66e4f6c99612cea4aa7269aa65863f7a15841b2c264f103822f4e", size = 252222, upload-time = "2026-09-30T04:35:39.544Z" },
    { url = "https://files.pythonhosted.org/packages/7e/24/76d2cefc25472531e4c5c7dfff68865eb1c39b78482f0fdc15b46f047830/charset_normalizer-3.5.2-cp312-cp312-musllinux_1_2_aarch64.whl", hash = "sha256:ae4f5fea5b8b8ccff88238cc8569303e5ee95efae67fa62922a311397a71f346", size = 248482, upload-time = "2026-09-30T04:35:41.088Z" },
    { url = "https://files.pythonhosted.org/packages/7d/dc/65a801b66ab4c197e22c433ab25e7ac24324ac6f45a2269aca42cce309bf/charset_normalizer-3.5.2-cp312-cp312-musllinux_1_2_armv7l.whl", hash = "sha256:f7d486c83842422badd511868fd8a9a20e9407ace71564b6af47ce7e60a336c1", size = 241206, upload-time = "2026-09-30T04:35:42.59Z" },
    { url = "https://files.pythonhosted.org/packages/a7/95/ca9b5eabde673002c6f1e7ada1b223916fe18f6d661da7aabd4d643718f1/charset_normalizer-3.5.2-cp312-cp312-musllinux_1_2_ppc64le.whl", hash = "sha256:11a4d68a6ecda3292cb1e50239e111543ba5d709bb62a6b4ea1afcfa729d8875", size = 273190, upload-time = "2026-09-30T04:35:44.347Z" },
    { url = "https://files.pythonhosted.org/packages/2d/8b/803b4d2a3f6e1740f63f1e87b04d14b42f3d4fdfe6ed7d4db2d34102b14f/charset_normalizer-3.5.2-cp312-cp312-musllinux_1_2_riscv64.whl", hash = "sha256:d6734d2ef8a50fbf8445c139477da401f50d62a0606bf00e20ec6d87773fefb1", size = 253527, upload-time = "2026-09-30T04:35:45.915Z" },
    { url = "https://files.pythonhosted.org/packages/a9/55/93c0e5dbd085ae0471346026abbe7e0db9ea2d6fea74e51f0b5a46f233a7/charset_normalizer-3.5.2-cp312-cp312-musllinux_1_2_s390x.whl", hash = "sha256:a815775b6c38d4e0ff7bcffbeba67feded90202bb6a226b8dd35f1c855217413", size = 271285, upload-time = "2026-09-30T04:35:47.49Z" },
    { url = "https://files.pythonhosted.org/packages/95/69/0dbd0e0b9b16cfa816cdfcb3e2e3854a1f680dc07fb1245ea125e7448060/charset_normalizer-3.5.2-cp312-cp312-musllinux_1_2_x86_64.whl", hash = "sha256:23851fb4e1b85ed3f6c2a27b777cdfe2e19fb5b38429a8faf38c7542b7665869", size = 260010, upload-time = "2026-09-30T04:35:48.996Z" },
    { url = "https://files.pythonhosted.org/packages/58/9d/e7b88e7b1bf403590c3b573277b5e1e488c68c7a6fbacca310a2c324e90c/charset_normalizer-3.5.2-cp312-cp312-win32.whl", hash = "sha256:db19d07e2e0129e974a0e65d0064fc222a446cd5122c2fd4184d2af9fc734a9e", size = 184125, upload-time = "2026-09-30T04:35:50.777Z" },
    { url = "https://files.pythonhosted.org/packages/eb/e6/e6e083884cbcfd49c64865af05027fe7011be7b2d9179524f099a1b611f3/charset_normalizer-3.5.2-cp312-cp312-win_amd64.whl", hash = "sha256:780fbe7cab297b81dad9fb8dc5eb003c0468ffb0d9e5f65068c53a34661a96bc", size = 207486, upload-time = "2026-09-30T04:35:52.194Z" },
    { url = "https://files.pythonhosted.org/packages/c4/e3/017aea0911ada7405a825c7d937eb3a13009664e2f5b38e8c4bbf2abf894/charset_normalizer-3.5.2-cp312-cp312-win_arm64.whl", hash = "sha256:e2af3aad578aa6bd1384bcf4750fc285e5a9de53f40b7d41e5a0bf748edeb2b3", size = 196734, upload-time = "2026-09-30T04:35:53.636Z" },
    { url = "https://files.pythonhosted.org/packages/8c/ab/176fbfd5b64939c55d652366aa5b9ef1d767af207a3aa6ebeb0d226c484d/charset_normalizer-3.5.2-cp37-abi3-macosx_10_9_universal2.whl", hash = "sha256:4275811936e2f06feff5e598fb42a1b7ae852da8e39605211892b56b81a34efd", size = 331815, upload-time = "2026-09-30T04:38:26.216Z" },
    { url = "https://files.pythonhosted.org/packages/7e/84/371eac6b30bdbcbf2d632a1a01809103459216fcaae61b8b8d922c1bfb8a/charset_normalizer-3.5.2-cp37-abi3-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl", hash = "sha256:1c50fe28bbc2ced33386f298650d91218076c05420e6cbd790b913adc41659e7", size = 253276, upload-time = "2026-09-30T04:38:28.032Z" },
    { url = "https://files.pythonhosted.org/packages/43/6f/c4fbae58febff71709c51bc7e18fdfa55341dc382704740f9f0cbf03817b/charset_normalizer-3.5.2-cp37-abi3-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:d19fbd981a488e22cd04883659ca6b08f50b5974f9fd7c95655ef6a043e5893f", size = 241239, upload-time = "2026-09-30T04:38:29.732Z" },
    { url = "https://files.pythonhosted.org/packages/61/71/458c3f42164a07d0c5210798e9e704b39e540a6793b05aba67f3a35243a9/charset_normalizer-3.5.2-cp37-abi3-manylinux2014_armv7l.manylinux_2_17_armv7l.manylinux_2_31_armv7l.whl", hash = "sha256:0fed1d06615f022ee3b13caf5e8b180cfea32bb2c5aded8a9d44277afc040f93", size = 231121, upload-time = "2026-09-30T04:38:31.462Z" },
    { url = "https://files.pythonhosted.org/packages/09/54/ab9e89367076f6331bb6c65c4bf14a5361fa5191cb6561bf534f18504e1b/charset_normalizer-3.5.2-cp37-abi3-manylinux2014_ppc64le.manylinux_2_17_ppc64le.manylinux_2_28_ppc64le.whl", hash = "sha256:838dcc90063569a0448120554591a1d6c4a4ffe11babf048908793154ab86ade", size = 260350, upload-time = "2026-09-30T04:38:33.239Z" },
    { url = "https://files.pythonhosted.org/packages/7c/c1/061431ecc688d9d76602502cb57cc01e691e682c18f1beb45f9673b5bbd2/charset_normalizer-3.5.2-cp37-abi3-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:2ce45c6627b22c47e390bc91a41c3d13032192e699fa0bea96e9671b373d69b0", size = 255430, upload-time = "2026-09-30T04:38:34.865Z" },
    { url = "https://files.pythonhosted.org/packages/8d/1f/20c8949f0676f7ab811abdeb7f4d7f1cbc6e61ff20bef08b44edeb092bc8/charset_normalizer-3.5.2-cp37-abi3-manylinux_2_31_riscv64.manylinux_2_39_riscv64.whl", hash = "sha256:0774bf9bf620249fee3e0b8b9fd3065de213be30f3aa94ce2494b3b638949e26", size = 250612, upload-time = "2026-09-30T04:38:36.649Z" },
    { url = "https://files.pythonhosted.org/packages/2b/9e/46f2fa4c431fc98c4ae76a8cb5bdca54e0341e3cfc3fcfd8e82740250818/charset_normalizer-3.5.2-cp37-abi3-musllinux_1_2_aarch64.whl", hash = "sha256:1db38f4c5496827c1a501846d64d14c3b80c7e6714e406cd7dc36a9899fa1011", size = 242083, upload-time = "2026-09-30T04:38:38.26Z" },
    { url = "https://files.pythonhosted.org/packages/bd/39/559be29a0c0f086e0bba6922babd38916cc5e0b58ced4de13ee01ea05508/charset_normalizer-3.5.2-cp37-abi3-musllinux_1_2_armv7l.whl", hash = "sha256:304d8e4d493af723536393eee0c689eb7813f4a474c8b479dee63f1fdd98f621", size = 232738, upload-time = "2026-09-30T04:38:39.81Z" },
    { url = "https://files.pythonhosted.org/packages/ff/6c/387b0e4f756a282831c1d9fc6aeb6c51ca4507ca202767c8de15ce9b12e2/charset_normalizer-3.5.2-cp37-abi3-musllinux_1_2_ppc64le.whl", hash = "sha256:9b7f416ff0978e2f2249330527f0ad6fa02f4932e6199692d3b52da2048c19e4", size = 260703, upload-time = "2026-09-30T04:38:41.346Z" },
    { url = "https://files.pythonhosted.org/packages/96/92/1fdf015f09ef449f50d3ac4b67c90887c9c318b727daa95cc4f866e6521d/charset_normalizer-3.5.2-cp37-abi3-musllinux_1_2_riscv64.whl", hash = "sha256:01077390b03f7988f11d700a2194e69b119741a86b1a638b1db88891e3eced8e", size = 247622, upload-time = "2026-09-30T04:38:42.937Z" },
    { url = "https://files.pythonhosted.org/packages/dc/3c/8e7b8a5671ad5d433669fb2a76f1a0164df2d9b1718b0206bc2a16d840cc/charset_normalizer-3.5.2-cp37-abi3-musllinux_1_2_s390x.whl", hash = "sha256:7e841fb9010836c992c9f12fcbd43a831de93a5f726fc1ccd8ca1d0268c5014c", size = 257500, upload-time = "2026-09-30T04:38:44.604Z" },
    { url = "https://files.pythonhosted.org/packages/b4/f0/45b579df5cabc1d5d53ea1cc35e8437d3ca768c0acccc7041517cb6fbb32/charset_normalizer-3.5.2-cp37-abi3-musllinux_1_2_x86_64.whl", hash = "sha256:9cae88599c7219005d879f98e5ed53341e9a122af585e1091200358a3003d2a0", size = 255100, upload-time = "2026-09-30T04:38:46.289Z" },
    { url = "https://files.pythonhosted.org/packages/31/68/fdec18a343f5fb3f310588dd478b09ac4799e0b187dbade3a8cd776f03ef/charset_normalizer-3.5.2-cp37-abi3-win32.whl", hash = "sha256:01b0c0d2262a9e28e8484a278c7e1b5d650e3ac8cf2683d2967e25899f208bdf", size = 174499, upload-time = "2026-09-30T04:38:47.999Z" },
    { url = "https://files.pythonhosted.org/packages/9d/8a/b618149cc5207943a0242068d7a27897f56a62947b5a039085f2a22029f8/charset_normalizer-3.5.2-cp37-abi3-win_amd64.whl", hash = "sha256:9f56f72050826f63dcee7a7f55b0a77168cb3bfc553fd405e7f8f9ece75a4036", size = 200092, upload-time = "2026-09-30T04:38:49.707Z" },
    { url = "https://files.pythonhosted.org/packages/03/cf/4c66866fa9e2b1c78e3c911516d1de497a677b7ac60f1eceda74ce777ca3/charset_normalizer-3.5.2-cp37-abi3-win_arm64.whl", hash = "sha256:40ab6bffa02ae10a0581e6c198be7d2d8ca5c2a0c64e4ed3465d766df457573e", size = 294363, upload-time = "2026-09-30T04:38:51.312Z" },
    { url = "https://files.pythonhosted.org/packages/fc/ad/d07d7862a62ffa6d79d68074d14823243dd235a77c45262acbf6adeb28bf/charset_normalizer-3.5.2-py3-none-any.whl", hash = "sha256:b6b751274acb69d77b3323d6b7dbaa3c7fdfc1eb829b7eb61d262f32e1af9685", size = 68872, upload-time = "2026-09-30T04:39:21.828Z" },
]

[[package]]
name = "colorama"
version = "0.4.6"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/d8/53/6f443c9a4a8358a93a6792e2acffb9d9d5cb0a5cfd8802644b7b1c9a02e4/colorama-0.4.6.tar.gz", hash = "sha256:08695f5cb7ed6e0531a20572697297273c47b8cae5a63ffc6d6ed5c201be6e44", size = 27697, upload-time = "2022-10-25T02:36:22.414Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/d1/d6/3965ed04c63042e047cb6a3e6ed1a63a35087b6a609aa3a15ed8ac56c221/colorama-0.4.6-py2.py3-none-any.whl", hash = "sha256:4f1d9991f5acc0ca119f9d443620b77f9d6b33703e51011c16baf57afb285fc6", size = 25335, upload-time = "2022-10-25T02:36:20.889Z" },
]

[[package]]
name = "coloredlogs"
version = "15.0.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "humanfriendly" },
]
sdist = { url = "https://files.pythonhosted.org/packages/cc/c7/eed8f27100517e8c0e6b923d5f0845d0cb99763da6fdee00478f91db7325/coloredlogs-15.0.1.tar.gz", hash = "sha256:7c991aa71a4577af2f82600d8f8f3a89f936baeaf9b50a9c197da014e5bf16b0", size = 278520, upload-time = "2021-06-11T10:22:45.202Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/a7/06/3d6badcf13db419e25b07041d9c7b4a2c331d3f4e7134445ec5df57714cd/coloredlogs-15.0.1-py2.py3-none-any.whl", hash = "sha256:612ee75c546f53e92e70049c9dbfcc18c935a2b9a53b66085ce9ef6a6e5c0934", size = 46018, upload-time = "2021-06-11T10:22:42.561Z" },
]

[[package]]
name = "filelock"
version = "4.0.7"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/35/f5/14097cca69f53794270d8c7970b48321636302affe3154c7e0ba114eeff9/filelock-4.0.7.tar.gz", hash = "sha256:da5915714a70b55d167fdc7e251ad91302b0a36816fb574dfafae8f4f2c9bb21", size = 248489, upload-time = "2026-09-29T23:04:05.995Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/06/cf/1731c0dd182ee35f80a39e63afb3d03056ea0dd561b7498932b10b2e34d9/filelock-4.0.7-py3-none-any.whl", hash = "sha256:a93c4d93269b339a6af4848342c7e940d0f9928ad95eff64764699e5f1bf8a6a", size = 109242, upload-time = "2026-09-29T23:04:04.696Z" },
]

[[package]]
name = "flatbuffers"
version = "25.12.19"
source = { registry = "https://pypi.org/simple" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/e8/2d/d2a548598be01649e2d46231d151a6c56d10b964d94043a335ae56ea2d92/flatbuffers-25.12.19-py2.py3-none-any.whl", hash = "sha256:7634f50c427838bb021c2d66a3d1168e9d199b0607e6329399f04846d42e20b4", size = 26661, upload-time = "2025-12-19T23:16:13.622Z" },
]

[[package]]
name = "fsspec"
version = "2026.9.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/77/cd/9be253869fc42e764de7f3dedd6969af7d44ff9c3375214a3442a6f3fc08/fsspec-2026.9.0.tar.gz", hash = "sha256:0f08147951c8cb31d844c3547d631053b127863b60be04cf06e121333ee0e2fe", size = 333545, upload-time = "2026-09-18T17:50:42.825Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/6c/c0/a98505f18594f1bce828bb159cec0fcf9860562f1a2c85913409fc8f3d9e/fsspec-2026.9.0-py3-none-any.whl", hash = "sha256:8dd6e646e99ea382bd85f97a45e6b526a442d79423a7dc673f1e2756d05fcb5f", size = 221738, upload-time = "2026-09-18T17:50:41.341Z" },
]

[[package]]
name = "hf-xet"
version = "1.6.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/1b/ab/522a2ab67f27971a9d48ca666d4fca85ef7d5282d142e31fd087e27b1bbe/hf_xet-1.6.0.tar.gz", hash = "sha256:2e58454a340b3556dfa4972d5451aff4fba8dd42a236600ba1a1d2b1514f0fef", size = 920527, upload-time = "2026-08-03T22:33:13.243Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/a2/50/7afa2c9c787405864fc47a0d1bbc02c62e9101947ed43c1f43899fc7d91d/hf_xet-1.6.0-cp38-abi3-macosx_10_12_x86_64.whl", hash = "sha256:633dc0cd71d32da58ab8c03ad38e2fac452c15c2b0a2866ebf6ededfe0a5061d", size = 4071729, upload-time = "2026-08-03T22:33:00.721Z" },
    { url = "https://files.pythonhosted.org/packages/4b/69/55b8dcf636142ae660fec1869fcac14c4da2e8412e14d6eee1523be77e9f/hf_xet-1.6.0-cp38-abi3-macosx_11_0_arm64.whl", hash = "sha256:f0906082d9932ae0c0057fa194041c22b4e2cdb46b2592ef3b91f020d62a081a", size = 3876287, upload-time = "2026-08-03T22:33:02.251Z" },
    { url = "https://files.pythonhosted.org/packages/67/4e/a28359bf1c1ecf11eba22123168c138698f7cb576ac678f5a2e16cd5da08/hf_xet-1.6.0-cp38-abi3-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:d62671bb130879cef0ee4c9ebe47a14af6c66ec53e6d84dc15936e5ffdfac82f", size = 4464663, upload-time = "2026-08-03T22:33:03.802Z" },
    { url = "https://files.pythonhosted.org/packages/9a/69/1f0cbc2fb22ae6082d094f743d1b8945a3f36f6089cb95f42b7ee348cda7/hf_xet-1.6.0-cp38-abi3-manylinux_2_28_aarch64.whl", hash = "sha256:0e6e21fa3cdfcdcd76748564bf593870a5e013f47d97cf10aed63aa222cff5b7", size = 4262538, upload-time = "2026-08-03T22:33:05.287Z" },
    { url = "https://files.pythonhosted.org/packages/d1/3a/4f4f2301ade26e404462d3336fa11f7958d914cabbabdd6e03c3c5d5658c/hf_xet-1.6.0-cp38-abi3-musllinux_1_2_aarch64.whl", hash = "sha256:4fc74352a17015bd0ee90038bc9efe38db894cde45f268b6712b04fce8cd0acb", size = 4460520, upload-time = "2026-08-03T22:33:06.81Z" },
    { url = "https://files.pythonhosted.org/packages/ab/5f/311725e2a905534dfee2dcb5b08414f249147f1f12252bfc2bd24caa075c/hf_xet-1.6.0-cp38-abi3-musllinux_1_2_x86_64.whl", hash = "sha256:8fb4f71cba6129110c3374a33f919001ff130488fc23553698e34cc1c2a1198c", size = 4675937, upload-time = "2026-08-03T22:33:08.616Z" },
    { url = "https://files.pythonhosted.org/packages/98/b7/8c59a66d15205024662f1d66968136f13893f96df1ddc5087e2e281fc95f/hf_xet-1.6.0-cp38-abi3-win_amd64.whl", hash = "sha256:fb4fadde1b2b70bf4c0c14a6dccbe7194b1c28947fefd5bbe3fed9d940676c3b", size = 4033128, upload-time = "2026-08-03T22:33:10.171Z" },
    { url = "https://files.pythonhosted.org/packages/73/63/ca511b6f802f28cf3489b280fe77475bcca8de85e81a6299d7916b5b5555/hf_xet-1.6.0-cp38-abi3-win_arm64.whl", hash = "sha256:3dc3e35441ba395006af5aaacc40ef2e603c51ef46c3530b9156185f00935ea3", size = 3859359, upload-time = "2026-08-03T22:33:11.725Z" },
]

[[package]]
name = "huggingface-hub"
version = "0.36.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "filelock" },
    { name = "fsspec" },
    { name = "hf-xet", marker = "platform_machine == 'aarch64' or platform_machine == 'amd64' or platform_machine == 'arm64' or platform_machine == 'x86_64'" },
    { name = "packaging" },
    { name = "pyyaml" },
    { name = "requests" },
    { name = "tqdm" },
    { name = "typing-extensions" },
]
sdist = { url = "https://files.pythonhosted.org/packages/98/63/4910c5fa9128fdadf6a9c5ac138e8b1b6cee4ca44bf7915bbfbce4e355ee/huggingface_hub-0.36.0.tar.gz", hash = "sha256:47b3f0e2539c39bf5cde015d63b72ec49baff67b6931c3d97f3f84532e2b8d25", size = 463358, upload-time = "2025-10-23T12:12:01.413Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/cb/bd/1a875e0d592d447cbc02805fd3fe0f497714d6a2583f59d14fa9ebad96eb/huggingface_hub-0.36.0-py3-none-any.whl", hash = "sha256:7bcc9ad17d5b3f07b57c78e79d527102d08313caa278a641993acddcb894548d", size = 566094, upload-time = "2025-10-23T12:11:59.557Z" },
]

[[package]]
name = "humanfriendly"
version = "10.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "pyreadline3", marker = "sys_platform == 'win32'" },
]
sdist = { url = "https://files.pythonhosted.org/packages/cc/3f/2c29224acb2e2df4d2046e4c73ee2662023c58ff5b113c4c1adac0886c43/humanfriendly-10.0.tar.gz", hash = "sha256:6b0b831ce8f15f7300721aa49829fc4e83921a9a301cc7f606be6686a2288ddc", size = 360702, upload-time = "2021-09-17T21:40:43.31Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/f0/0f/310fb31e39e2d734ccaa2c0fb981ee41f7bd5056ce9bc29b2248bd569169/humanfriendly-10.0-py2.py3-none-any.whl", hash = "sha256:1697e1a8a8f550fd43c2865cd84542fc175a61dcb779b6fee18cf6b6ccba1477", size = 86794, upload-time = "2021-09-17T21:40:39.897Z" },
]

[[package]]
name = "idna"
version = "3.20"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/f5/08/8eea9d4b8302028f3abb2c0813953f7aec26d33b7a8960ed760e65ff29fa/idna-3.20.tar.gz", hash = "sha256:a7db850025b95ded1eae8a46181a1a6c56c92c96f0e2b005d9ff8dc0210cab44", size = 216463, upload-time = "2026-09-17T14:11:04.752Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/58/a2/bb081bab032533a855d44de1d56f8e8426114ff1ba5d1f07a438a0a654f8/idna-3.20-py3-none-any.whl", hash = "sha256:ab7ae7122974553370f0bdb919e1a960b2cd1bc1ef0276416d896db81c14582c", size = 69583, upload-time = "2026-09-17T14:11:03.168Z" },
]

[[package]]
name = "mpmath"
version = "1.3.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/e0/47/dd32fa426cc72114383ac549964eecb20ecfd886d1e5ccf5340b55b02f57/mpmath-1.3.0.tar.gz", hash = "sha256:7a28eb2a9774d00c7bc92411c19a89209d5da7c4c9a9e227be8330a23a25b91f", size = 508106, upload-time = "2023-03-07T16:47:11.061Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/43/e3/7d92a15f894aa0c9c4b49b8ee9ac9850d6e63b03c9c32c0367a13ae62209/mpmath-1.3.0-py3-none-any.whl", hash = "sha256:a0b2b9fe80bbcd81a6647ff13108738cfb482d481d826cc0e02f5b35e5c88d2c", size = 536198, upload-time = "2023-03-07T16:47:09.197Z" },
]

[[package]]
name = "numpy"
version = "2.3.4"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/b5/f4/098d2270d52b41f1bd7db9fc288aaa0400cb48c2a3e2af6fa365d9720947/numpy-2.3.4.tar.gz", hash = "sha256:a7d018bfedb375a8d979ac758b120ba846a7fe764911a64465fd87b8729f4a6a", size = 20582187, upload-time = "2025-10-15T16:18:11.77Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/96/7a/02420400b736f84317e759291b8edaeee9dc921f72b045475a9cbdb26b17/numpy-2.3.4-cp312-cp312-macosx_10_13_x86_64.whl", hash = "sha256:ef1b5a3e808bc40827b5fa2c8196151a4c5abe110e1726949d7abddfe5c7ae11", size = 20957727, upload-time = "2025-10-15T16:15:44.9Z" },
    { url = "https://files.pythonhosted.org/packages/18/90/a014805d627aa5750f6f0e878172afb6454552da929144b3c07fcae1bb13/numpy-2.3.4-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:c2f91f496a87235c6aaf6d3f3d89b17dba64996abadccb289f48456cff931ca9", size = 14187262, upload-time = "2025-10-15T16:15:47.761Z" },
    { url = "https://files.pythonhosted.org/packages/c7/e4/0a94b09abe89e500dc748e7515f21a13e30c5c3fe3396e6d4ac108c25fca/numpy-2.3.4-cp312-cp312-macosx_14_0_arm64.whl", hash = "sha256:f77e5b3d3da652b474cc80a14084927a5e86a5eccf54ca8ca5cbd697bf7f2667", size = 5115992, upload-time = "2025-10-15T16:15:50.144Z" },
    { url = "https://files.pythonhosted.org/packages/88/dd/db77c75b055c6157cbd4f9c92c4458daef0dd9cbe6d8d2fe7f803cb64c37/numpy-2.3.4-cp312-cp312-macosx_14_0_x86_64.whl", hash = "sha256:8ab1c5f5ee40d6e01cbe96de5863e39b215a4d24e7d007cad56c7184fdf4aeef", size = 6648672, upload-time = "2025-10-15T16:15:52.442Z" },
    { url = "https://files.pythonhosted.org/packages/e1/e6/e31b0d713719610e406c0ea3ae0d90760465b086da8783e2fd835ad59027/numpy-2.3.4-cp312-cp312-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:77b84453f3adcb994ddbd0d1c5d11db2d6bda1a2b7fd5ac5bd4649d6f5dc682e", size = 14284156, upload-time = "2025-10-15T16:15:54.351Z" },
    { url = "https://files.pythonhosted.org/packages/f9/58/30a85127bfee6f108282107caf8e06a1f0cc997cb6b52cdee699276fcce4/numpy-2.3.4-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:4121c5beb58a7f9e6dfdee612cb24f4df5cd4db6e8261d7f4d7450a997a65d6a", size = 16641271, upload-time = "2025-10-15T16:15:56.67Z" },
    { url = "https://files.pythonhosted.org/packages/06/f2/2e06a0f2adf23e3ae29283ad96959267938d0efd20a2e25353b70065bfec/numpy-2.3.4-cp312-cp312-musllinux_1_2_aarch64.whl", hash = "sha256:65611ecbb00ac9846efe04db15cbe6186f562f6bb7e5e05f077e53a599225d16", size = 16059531, upload-time = "2025-10-15T16:15:59.412Z" },
    { url = "https://files.pythonhosted.org/packages/b0/e7/b106253c7c0d5dc352b9c8fab91afd76a93950998167fa3e5afe4ef3a18f/numpy-2.3.4-cp312-cp312-musllinux_1_2_x86_64.whl", hash = "sha256:dabc42f9c6577bcc13001b8810d300fe814b4cfbe8a92c873f269484594f9786", size = 18578983, upload-time = "2025-10-15T16:16:01.804Z" },
    { url = "https://files.pythonhosted.org/packages/73/e3/04ecc41e71462276ee867ccbef26a4448638eadecf1bc56772c9ed6d0255/numpy-2.3.4-cp312-cp312-win32.whl", hash = "sha256:a49d797192a8d950ca59ee2d0337a4d804f713bb5c3c50e8db26d49666e351dc", size = 6291380, upload-time = "2025-10-15T16:16:03.938Z" },
    { url = "https://files.pythonhosted.org/packages/3d/a8/566578b10d8d0e9955b1b6cd5db4e9d4592dd0026a941ff7994cedda030a/numpy-2.3.4-cp312-cp312-win_amd64.whl", hash = "sha256:985f1e46358f06c2a09921e8921e2c98168ed4ae12ccd6e5e87a4f1857923f32", size = 12787999, upload-time = "2025-10-15T16:16:05.801Z" },
    { url = "https://files.pythonhosted.org/packages/58/22/9c903a957d0a8071b607f5b1bff0761d6e608b9a965945411f867d515db1/numpy-2.3.4-cp312-cp312-win_arm64.whl", hash = "sha256:4635239814149e06e2cb9db3dd584b2fa64316c96f10656983b8026a82e6e4db", size = 10197412, upload-time = "2025-10-15T16:16:07.854Z" },
]

[[package]]
name = "onnxruntime"
version = "1.23.2"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "coloredlogs" },
    { name = "flatbuffers" },
    { name = "numpy" },
    { name = "packaging" },
    { name = "protobuf" },
    { name = "sympy" },
]
wheels = [
    { url = "https://files.pythonhosted.org/packages/1b/9e/f748cd64161213adeef83d0cb16cb8ace1e62fa501033acdd9f9341fff57/onnxruntime-1.23.2-cp312-cp312-macosx_13_0_arm64.whl", hash = "sha256:b8f029a6b98d3cf5be564d52802bb50a8489ab73409fa9db0bf583eabb7c2321", size = 17195929, upload-time = "2025-10-22T03:47:36.24Z" },
    { url = "https://files.pythonhosted.org/packages/91/9d/a81aafd899b900101988ead7fb14974c8a58695338ab6a0f3d6b0100f30b/onnxruntime-1.23.2-cp312-cp312-macosx_13_0_x86_64.whl", hash = "sha256:218295a8acae83905f6f1aed8cacb8e3eb3bd7513a13fe4ba3b2664a19fc4a6b", size = 19157705, upload-time = "2025-10-22T03:46:40.415Z" },
    { url = "https://files.pythonhosted.org/packages/3c/35/4e40f2fba272a6698d62be2cd21ddc3675edfc1a4b9ddefcc4648f115315/onnxruntime-1.23.2-cp312-cp312-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:76ff670550dc23e58ea9bc53b5149b99a44e63b34b524f7b8547469aaa0dcb8c", size = 15226915, upload-time = "2025-10-22T03:46:27.773Z" },
    { url = "https://files.pythonhosted.org/packages/ef/88/9cc25d2bafe6bc0d4d3c1db3ade98196d5b355c0b273e6a5dc09c5d5d0d5/onnxruntime-1.23.2-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:0f9b4ae77f8e3c9bee50c27bc1beede83f786fe1d52e99ac85aa8d65a01e9b77", size = 17382649, upload-time = "2025-10-22T03:47:02.782Z" },
    { url = "https://files.pythonhosted.org/packages/c0/b4/569d298f9fc4d286c11c45e85d9ffa9e877af12ace98af8cab52396e8f46/onnxruntime-1.23.2-cp312-cp312-win_amd64.whl", hash = "sha256:25de5214923ce941a3523739d34a520aac30f21e631de53bba9174dc9c004435", size = 13470528, upload-time = "2025-10-22T03:47:28.106Z" },
]

[[package]]
name = "packaging"
version = "26.3"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/7d/fa/3944b40b07da9ce895c0e6303a5ab7d53da063554f534556b134a54d6093/packaging-26.3.tar.gz", hash = "sha256:94edc256424af38762eb31306eed28beb9f0efc50a8837492c9d6fd6004aed79", size = 313412, upload-time = "2026-08-04T18:15:28.737Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/63/34/ba1c580383c9eada3711951fef0795c80b829a078d72188184bcab9dd527/packaging-26.3-py3-none-any.whl", hash = "sha256:d7193f7c8e4e93f444fde0262bf90af30e16fa0ad0ad44cb553c87339b23cd1c", size = 129956, upload-time = "2026-08-04T18:15:27.159Z" },
]

[[package]]
name = "protobuf"
version = "7.36.2"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/d9/89/5b8517baa72f84a67b8a307ba953c91057af618bf40bf676f3c03551f8f0/protobuf-7.36.2.tar.gz", hash = "sha256:497d0463ff3316681da6c0b9e8d06cb465d61abce00b613ab42226175644d1bb", size = 512737, upload-time = "2026-09-17T20:07:59.326Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/32/72/98342feb672507c8f3a69e34b4fa8961f608edba5c1a48a6f47156d92cb5/protobuf-7.36.2-cp310-abi3-macosx_10_9_universal2.whl", hash = "sha256:cbc70b17ee27e28894c7fee8bb04be1abead49e936bc70eb60052531eee2079e", size = 456039, upload-time = "2026-09-17T20:07:51.542Z" },
    { url = "https://files.pythonhosted.org/packages/b6/ea/91fdf7c2b8bbd49cde056f00a9df6773532987e1c00fe2830b895af95c7e/protobuf-7.36.2-cp310-abi3-manylinux2014_aarch64.whl", hash = "sha256:e11e1f0180583a2af89db6a2ecd9e8dc40aa6d2988ca175bfd0e6d12ea72d74e", size = 344219, upload-time = "2026-09-17T20:07:52.914Z" },
    { url = "https://files.pythonhosted.org/packages/17/ab/5fd5f8ece73fad885c5a09aa849b32d70472f954ba3a92d3bb5974ea953b/protobuf-7.36.2-cp310-abi3-manylinux2014_s390x.whl", hash = "sha256:f4fee11ec330d238b34a05c9b675f693c20415d1c5bd7d5320cc2f8a798eb9cf", size = 357223, upload-time = "2026-09-17T20:07:53.985Z" },
    { url = "https://files.pythonhosted.org/packages/db/f3/3996583dd2906297a637af12114deddf7658af6e683fedb83be061983fb5/protobuf-7.36.2-cp310-abi3-manylinux2014_x86_64.whl", hash = "sha256:89f23aa53c24553a2416fd4fd1ec06f74fa42b14b546d8883128813f775bbfd2", size = 343223, upload-time = "2026-09-17T20:07:54.931Z" },
    { url = "https://files.pythonhosted.org/packages/fc/1b/dcc64f358fcb51811b58ae40b3d28f820725f116d86487cc20bd4b130701/protobuf-7.36.2-cp310-abi3-win32.whl", hash = "sha256:912c1221170e16c08d1f086762f563dd61ff83c18b5fa6652952dfaded66f728", size = 442998, upload-time = "2026-09-17T20:07:55.826Z" },
    { url = "https://files.pythonhosted.org/packages/8a/55/b77bda4e5e5f5971fb51b07663694690e9afdb9402136c16a522bd621cad/protobuf-7.36.2-cp310-abi3-win_amd64.whl", hash = "sha256:a300819d441e078a5608c0d3c709796bb548136058fda017ae51d425b44fd353", size = 456514, upload-time = "2026-09-17T20:07:57.188Z" },
    { url = "https://files.pythonhosted.org/packages/e4/04/d52c7016b04b6c5108f26691f9d33ec82a9b65d041f1a9c771137693d618/protobuf-7.36.2-py3-none-any.whl", hash = "sha256:bdb3a345d48db958e6ce1f18e508beb0cc981d64f24088427549c866cd039f1e", size = 179806, upload-time = "2026-09-17T20:07:58.211Z" },
]

[[package]]
name = "pyreadline3"
version = "3.5.6"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/b6/6d/f94028646d7bbe6d9d873c47ee7c246f2d29129d253f0d96cb6fcab70733/pyreadline3-3.5.6.tar.gz", hash = "sha256:61e53218b99656091ddb077df9e71f25850e72e030b6183b39c9b7e6e4f4a9bf", size = 100368, upload-time = "2026-05-14T17:55:04.471Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/f7/5e/35c856e186b74678c24927847ad9895a51f1bc02a0c6126477a6c6040064/pyreadline3-3.5.6-py3-none-any.whl", hash = "sha256:8449b734232e42a5dcd74048e39b60db2839a4c38cf3ae2bf7707d58b5389c0d", size = 85243, upload-time = "2026-05-14T17:55:03.262Z" },
]

[[package]]
name = "pyyaml"
version = "6.0.3"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/05/8e/961c0007c59b8dd7729d542c61a4d537767a59645b82a0b521206e1e25c2/pyyaml-6.0.3.tar.gz", hash = "sha256:d76623373421df22fb4cf8817020cbb7ef15c725b9d5e45f17e189bfc384190f", size = 130960, upload-time = "2025-09-25T21:33:16.546Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/d1/33/422b98d2195232ca1826284a76852ad5a86fe23e31b009c9886b2d0fb8b2/pyyaml-6.0.3-cp312-cp312-macosx_10_13_x86_64.whl", hash = "sha256:7f047e29dcae44602496db43be01ad42fc6f1cc0d8cd6c83d342306c32270196", size = 182063, upload-time = "2025-09-25T21:32:11.445Z" },
    { url = "https://files.pythonhosted.org/packages/89/a0/6cf41a19a1f2f3feab0e9c0b74134aa2ce6849093d5517a0c550fe37a648/pyyaml-6.0.3-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:fc09d0aa354569bc501d4e787133afc08552722d3ab34836a80547331bb5d4a0", size = 173973, upload-time = "2025-09-25T21:32:12.492Z" },
    { url = "https://files.pythonhosted.org/packages/ed/23/7a778b6bd0b9a8039df8b1b1d80e2e2ad78aa04171592c8a5c43a56a6af4/pyyaml-6.0.3-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:9149cad251584d5fb4981be1ecde53a1ca46c891a79788c0df828d2f166bda28", size = 775116, upload-time = "2025-09-25T21:32:13.652Z" },
    { url = "https://files.pythonhosted.org/packages/65/30/d7353c338e12baef4ecc1b09e877c1970bd3382789c159b4f89d6a70dc09/pyyaml-6.0.3-cp312-cp312-manylinux2014_s390x.manylinux_2_17_s390x.manylinux_2_28_s390x.whl", hash = "sha256:5fdec68f91a0c6739b380c83b951e2c72ac0197ace422360e6d5a959d8d97b2c", size = 844011, upload-time = "2025-09-25T21:32:15.21Z" },
    { url = "https://files.pythonhosted.org/packages/8b/9d/b3589d3877982d4f2329302ef98a8026e7f4443c765c46cfecc8858c6b4b/pyyaml-6.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:ba1cc08a7ccde2d2ec775841541641e4548226580ab850948cbfda66a1befcdc", size = 807870, upload-time = "2025-09-25T21:32:16.431Z" },
    { url = "https://files.pythonhosted.org/packages/05/c0/b3be26a015601b822b97d9149ff8cb5ead58c66f981e04fedf4e762f4bd4/pyyaml-6.0.3-cp312-cp312-musllinux_1_2_aarch64.whl", hash = "sha256:8dc52c23056b9ddd46818a57b78404882310fb473d63f17b07d5c40421e47f8e", size = 761089, upload-time = "2025-09-25T21:32:17.56Z" },
    { url = "https://files.pythonhosted.org/packages/be/8e/98435a21d1d4b46590d5459a22d88128103f8da4c2d4cb8f14f2a96504e1/pyyaml-6.0.3-cp312-cp312-musllinux_1_2_x86_64.whl", hash = "sha256:41715c910c881bc081f1e8872880d3c650acf13dfa8214bad49ed4cede7c34ea", size = 790181, upload-time = "2025-09-25T21:32:18.834Z" },
    { url = "https://files.pythonhosted.org/packages/74/93/7baea19427dcfbe1e5a372d81473250b379f04b1bd3c4c5ff825e2327202/pyyaml-6.0.3-cp312-cp312-win32.whl", hash = "sha256:96b533f0e99f6579b3d4d4995707cf36df9100d67e0c8303a0c55b27b5f99bc5", size = 137658, upload-time = "2025-09-25T21:32:20.209Z" },
    { url = "https://files.pythonhosted.org/packages/86/bf/899e81e4cce32febab4fb42bb97dcdf66bc135272882d1987881a4b519e9/pyyaml-6.0.3-cp312-cp312-win_amd64.whl", hash = "sha256:5fcd34e47f6e0b794d17de1b4ff496c00986e1c83f7ab2fb8fcfe9616ff7477b", size = 154003, upload-time = "2025-09-25T21:32:21.167Z" },
    { url = "https://files.pythonhosted.org/packages/1a/08/67bd04656199bbb51dbed1439b7f27601dfb576fb864099c7ef0c3e55531/pyyaml-6.0.3-cp312-cp312-win_arm64.whl", hash = "sha256:64386e5e707d03a7e172c0701abfb7e10f0fb753ee1d773128192742712a98fd", size = 140344, upload-time = "2025-09-25T21:32:22.617Z" },
]

[[package]]
name = "requests"
version = "2.34.2"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "certifi" },
    { name = "charset-normalizer" },
    { name = "idna" },
    { name = "urllib3" },
]
sdist = { url = "https://files.pythonhosted.org/packages/ac/c3/e2a2b89f2d3e2179abd6d00ebd70bff6273f37fb3e0cc209f48b39d00cbf/requests-2.34.2.tar.gz", hash = "sha256:f288924cae4e29463698d6d60bc6a4da69c89185ad1e0bcc4104f584e960b9ed", size = 142856, upload-time = "2026-05-14T19:25:27.735Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/a0/f4/c67b0b3f1b9245e8d266f0f112c500d50e5b4e83cb6f3b71b6528104182a/requests-2.34.2-py3-none-any.whl", hash = "sha256:2a0d60c172f83ac6ab31e4554906c0f3b3588d37b5cb939b1c061f4907e278e0", size = 73075, upload-time = "2026-05-14T19:25:26.443Z" },
]

[[package]]
name = "rnd-local-embedding-runtime"
version = "0.1.0"
source = { virtual = "." }
dependencies = [
    { name = "huggingface-hub" },
    { name = "numpy" },
    { name = "onnxruntime" },
    { name = "tokenizers" },
]

[package.metadata]
requires-dist = [
    { name = "huggingface-hub", specifier = "==0.36.0" },
    { name = "numpy", specifier = "==2.3.4" },
    { name = "onnxruntime", specifier = "==1.23.2" },
    { name = "tokenizers", specifier = "==0.22.1" },
]

[[package]]
name = "sympy"
version = "1.14.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "mpmath" },
]
sdist = { url = "https://files.pythonhosted.org/packages/83/d3/803453b36afefb7c2bb238361cd4ae6125a569b4db67cd9e79846ba2d68c/sympy-1.14.0.tar.gz", hash = "sha256:d3d3fe8df1e5a0b42f0e7bdf50541697dbe7d23746e894990c030e2b05e72517", size = 7793921, upload-time = "2025-04-27T18:05:01.611Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/a2/09/77d55d46fd61b4a135c444fc97158ef34a095e5681d0a6c10b75bf356191/sympy-1.14.0-py3-none-any.whl", hash = "sha256:e091cc3e99d2141a0ba2847328f5479b05d94a6635cb96148ccb3f34671bd8f5", size = 6299353, upload-time = "2025-04-27T18:04:59.103Z" },
]

[[package]]
name = "tokenizers"
version = "0.22.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "huggingface-hub" },
]
sdist = { url = "https://files.pythonhosted.org/packages/1c/46/fb6854cec3278fbfa4a75b50232c77622bc517ac886156e6afbfa4d8fc6e/tokenizers-0.22.1.tar.gz", hash = "sha256:61de6522785310a309b3407bac22d99c4db5dba349935e99e4d15ea2226af2d9", size = 363123, upload-time = "2025-09-19T09:49:23.424Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/bf/33/f4b2d94ada7ab297328fc671fed209368ddb82f965ec2224eb1892674c3a/tokenizers-0.22.1-cp39-abi3-macosx_10_12_x86_64.whl", hash = "sha256:59fdb013df17455e5f950b4b834a7b3ee2e0271e6378ccb33aa74d178b513c73", size = 3069318, upload-time = "2025-09-19T09:49:11.848Z" },
    { url = "https://files.pythonhosted.org/packages/1c/58/2aa8c874d02b974990e89ff95826a4852a8b2a273c7d1b4411cdd45a4565/tokenizers-0.22.1-cp39-abi3-macosx_11_0_arm64.whl", hash = "sha256:8d4e484f7b0827021ac5f9f71d4794aaef62b979ab7608593da22b1d2e3c4edc", size = 2926478, upload-time = "2025-09-19T09:49:09.759Z" },
    { url = "https://files.pythonhosted.org/packages/1e/3b/55e64befa1e7bfea963cf4b787b2cea1011362c4193f5477047532ce127e/tokenizers-0.22.1-cp39-abi3-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:19d2962dd28bc67c1f205ab180578a78eef89ac60ca7ef7cbe9635a46a56422a", size = 3256994, upload-time = "2025-09-19T09:48:56.701Z" },
    { url = "https://files.pythonhosted.org/packages/71/0b/fbfecf42f67d9b7b80fde4aabb2b3110a97fac6585c9470b5bff103a80cb/tokenizers-0.22.1-cp39-abi3-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:38201f15cdb1f8a6843e6563e6e79f4abd053394992b9bbdf5213ea3469b4ae7", size = 3153141, upload-time = "2025-09-19T09:48:59.749Z" },
    { url = "https://files.pythonhosted.org/packages/17/a9/b38f4e74e0817af8f8ef925507c63c6ae8171e3c4cb2d5d4624bf58fca69/tokenizers-0.22.1-cp39-abi3-manylinux_2_17_i686.manylinux2014_i686.whl", hash = "sha256:d1cbe5454c9a15df1b3443c726063d930c16f047a3cc724b9e6e1a91140e5a21", size = 3508049, upload-time = "2025-09-19T09:49:05.868Z" },
    { url = "https://files.pythonhosted.org/packages/d2/48/dd2b3dac46bb9134a88e35d72e1aa4869579eacc1a27238f1577270773ff/tokenizers-0.22.1-cp39-abi3-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:e7d094ae6312d69cc2a872b54b91b309f4f6fbce871ef28eb27b52a98e4d0214", size = 3710730, upload-time = "2025-09-19T09:49:01.832Z" },
    { url = "https://files.pythonhosted.org/packages/93/0e/ccabc8d16ae4ba84a55d41345207c1e2ea88784651a5a487547d80851398/tokenizers-0.22.1-cp39-abi3-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:afd7594a56656ace95cdd6df4cca2e4059d294c5cfb1679c57824b605556cb2f", size = 3412560, upload-time = "2025-09-19T09:49:03.867Z" },
    { url = "https://files.pythonhosted.org/packages/d0/c6/dc3a0db5a6766416c32c034286d7c2d406da1f498e4de04ab1b8959edd00/tokenizers-0.22.1-cp39-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:e2ef6063d7a84994129732b47e7915e8710f27f99f3a3260b8a38fc7ccd083f4", size = 3250221, upload-time = "2025-09-19T09:49:07.664Z" },
    { url = "https://files.pythonhosted.org/packages/d7/a6/2c8486eef79671601ff57b093889a345dd3d576713ef047776015dc66de7/tokenizers-0.22.1-cp39-abi3-musllinux_1_2_aarch64.whl", hash = "sha256:ba0a64f450b9ef412c98f6bcd2a50c6df6e2443b560024a09fa6a03189726879", size = 9345569, upload-time = "2025-09-19T09:49:14.214Z" },
    { url = "https://files.pythonhosted.org/packages/6b/16/32ce667f14c35537f5f605fe9bea3e415ea1b0a646389d2295ec348d5657/tokenizers-0.22.1-cp39-abi3-musllinux_1_2_armv7l.whl", hash = "sha256:331d6d149fa9c7d632cde4490fb8bbb12337fa3a0232e77892be656464f4b446", size = 9271599, upload-time = "2025-09-19T09:49:16.639Z" },
    { url = "https://files.pythonhosted.org/packages/51/7c/a5f7898a3f6baa3fc2685c705e04c98c1094c523051c805cdd9306b8f87e/tokenizers-0.22.1-cp39-abi3-musllinux_1_2_i686.whl", hash = "sha256:607989f2ea68a46cb1dfbaf3e3aabdf3f21d8748312dbeb6263d1b3b66c5010a", size = 9533862, upload-time = "2025-09-19T09:49:19.146Z" },
    { url = "https://files.pythonhosted.org/packages/36/65/7e75caea90bc73c1dd8d40438adf1a7bc26af3b8d0a6705ea190462506e1/tokenizers-0.22.1-cp39-abi3-musllinux_1_2_x86_64.whl", hash = "sha256:a0f307d490295717726598ef6fa4f24af9d484809223bbc253b201c740a06390", size = 9681250, upload-time = "2025-09-19T09:49:21.501Z" },
    { url = "https://files.pythonhosted.org/packages/30/2c/959dddef581b46e6209da82df3b78471e96260e2bc463f89d23b1bf0e52a/tokenizers-0.22.1-cp39-abi3-win32.whl", hash = "sha256:b5120eed1442765cd90b903bb6cfef781fd8fe64e34ccaecbae4c619b7b12a82", size = 2472003, upload-time = "2025-09-19T09:49:27.089Z" },
    { url = "https://files.pythonhosted.org/packages/b3/46/e33a8c93907b631a99377ef4c5f817ab453d0b34f93529421f42ff559671/tokenizers-0.22.1-cp39-abi3-win_amd64.whl", hash = "sha256:65fd6e3fb11ca1e78a6a93602490f134d1fdeb13bcef99389d5102ea318ed138", size = 2674684, upload-time = "2025-09-19T09:49:24.953Z" },
]

[[package]]
name = "tqdm"
version = "4.70.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "colorama", marker = "sys_platform == 'win32'" },
]
sdist = { url = "https://files.pythonhosted.org/packages/0d/ea/b2a5bd54b28a324dae8211928b2d730b6547500342c7e6c6dea08bd0a485/tqdm-4.70.1.tar.gz", hash = "sha256:cefd0eca11b2a37a3aee776544d4f4ae913f02688135b5556b8788dfa474afc4", size = 171846, upload-time = "2026-09-11T07:25:16.601Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/a7/03/921a3d3c75785aca9ebfbfcabfbc3a1be12e2ab5265deb026d55a5a3f83e/tqdm-4.70.1-py3-none-any.whl", hash = "sha256:c293e525e6fef9c20e8728fd4612df02a0aa31bb5fe91ecd93e123b1b7bffa73", size = 80199, upload-time = "2026-09-11T07:25:14.599Z" },
]

[[package]]
name = "typing-extensions"
version = "4.16.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/f6/cc/6253133b5bb138fc3306cebfbda2c520f545d36b5be2c7255cc528bb45d6/typing_extensions-4.16.0.tar.gz", hash = "sha256:dc983d19a509c94dba722ee6abd33940f7c05a89e243c47e907eb4db6f1a43e5", size = 113555, upload-time = "2026-07-02T08:40:05.92Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/49/d3/b8441a820a491ddfc024b0b0cf0393375b75ea13866d9c66727e54c2fc80/typing_extensions-4.16.0-py3-none-any.whl", hash = "sha256:481caa481374e813c1b176ada14e97f1f67a4539ce9cfeb3f350d78d6370c2e8", size = 45571, upload-time = "2026-07-02T08:40:04.659Z" },
]

[[package]]
name = "urllib3"
version = "2.8.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/e3/05/b17359e1cefb4f909b5e40b1b90a496d987258916dbbf88e842c729f510e/urllib3-2.8.0.tar.gz", hash = "sha256:63bf2ead4c879426ebf22ef2a781eeb4aa3b4ae798a0435506f8687fd5bb9b63", size = 458972, upload-time = "2026-09-15T19:29:36.253Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/92/9d/c4e665119135114480843e7ab388fa94d8480650450e6f8e26b70d323a4c/urllib3-2.8.0-py3-none-any.whl", hash = "sha256:0cf3cae568d36aa9576b28dfb35f11328f1cb974ca7647d9475ebb86c75ac6e3", size = 135717, upload-time = "2026-09-15T19:29:34.577Z" },
]
````
