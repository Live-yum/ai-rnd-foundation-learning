# templates/business/yudao/RndBusinessRegistration.java · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Yudao原生注册后的业务角色连接。** 沿用框架注册、校验与密码处理，事务性分配合同默认非管理员角色，不签发假令牌或存储明文密码。

**对应关系：** 原生账号注册 → 本产品角色钩子 → 初始化与权限验证。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `templates/business/yudao/RndBusinessRegistration.java`；**本文件共有 1 段**。本段覆盖源文件 L1–L33。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1476`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/business/yudao/RndBusinessRegistration.java", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "c51465bb06f8efbebb51825d44bc80f291f92e21265ffd691e546fa59cb10045"} -->
````java
// templates/business/yudao/RndBusinessRegistration.java
package cn.iocoder.yudao.module.infra.business;

import jakarta.annotation.Resource;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.springframework.beans.BeanWrapperImpl;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.support.TransactionTemplate;

/** Keep native registration/password hashing; attach only the declared business default role. */
@Aspect
@Component
@Order(-100)
public class RndBusinessRegistration {
    @Resource private RndBusinessService business;
    @Resource private PlatformTransactionManager transactionManager;

    @Around("execution(* cn.iocoder.yudao.module.system.service.user.AdminUserService.registerUser(..))")
    public Object register(ProceedingJoinPoint call) {
        return new TransactionTemplate(transactionManager).execute(status -> {
            try {
                Object nativeUser=call.proceed();
                Object id=new BeanWrapperImpl(nativeUser).getPropertyValue("id");
                business.registered(Long.valueOf(String.valueOf(id)));
                return nativeUser;
            } catch(RuntimeException error) { throw error; }
            catch(Throwable error) { throw new IllegalStateException("Native registration failed",error); }
        });
    }
}
````
