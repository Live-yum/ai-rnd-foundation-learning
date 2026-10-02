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
