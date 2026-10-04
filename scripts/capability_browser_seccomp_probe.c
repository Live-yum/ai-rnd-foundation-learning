/*
 * Live negative evidence for the approved, native-amd64 browser policy.
 * Build/inspect only outside the authorized disposable, network-none worker.
 * This program NEVER installs a filter or changes host security settings.
 * Its expected hash is an assertion to be bound by the controller's independent
 * Docker inspection and source receipts, not a measurement of the loaded BPF.
 */
#define _GNU_SOURCE
#if !defined(__linux__) || !defined(__x86_64__) || defined(__ILP32__)
#error "This live probe requires native Linux amd64; no compatibility fallback."
#endif
#include <asm/unistd.h>
#include <errno.h>
#include <inttypes.h>
#include <signal.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

_Static_assert(sizeof(long) == 8 && sizeof(void *) == 8, "native amd64 ABI required");
_Static_assert(__NR_socket == 41 && __NR_socketpair == 53 && __NR_clone == 56,
               "unexpected native syscall table");
_Static_assert(__NR_io_uring_setup == 425 && __NR_io_uring_enter == 426 &&
               __NR_io_uring_register == 427 && __NR_clone3 == 435,
               "unexpected native syscall table");

#define PROFILE_HASH "9e4d4398b47e0bdbd937121091aa846ebdba68e758561b417951d9a56bd4c69f"
#define X32_BIT UINT64_C(0x40000000)
#define I386_SOCKETCALL 102U
#define I386_SOCKET 359U
#define I386_SOCKETPAIR 360U
#define MAX_RESULTS 32U
#define CHILD_WAIT_POLLS 200U
#define CHILD_POLL_NS 10000000L

/* Keep all 64 argument bits: libc's typed socket wrappers would truncate them. */
__attribute__((noinline)) static long raw_syscall6(uint64_t number, uint64_t a1,
        uint64_t a2, uint64_t a3, uint64_t a4, uint64_t a5, uint64_t a6) {
    register uint64_t r10 __asm__("r10") = a4;
    register uint64_t r8 __asm__("r8") = a5;
    register uint64_t r9 __asm__("r9") = a6;
    long result;
    __asm__ __volatile__("syscall" : "=a"(result)
        : "a"(number), "D"(a1), "S"(a2), "d"(a3), "r"(r10), "r"(r8), "r"(r9)
        : "rcx", "r11", "memory", "cc");
    return result;
}

/* int 0x80 enters the i386 syscall ABI even from a native 64-bit executable. */
__attribute__((noinline)) static long raw_i386_syscall4(uint32_t number, uint32_t a1,
        uint32_t a2, uint32_t a3, uint32_t a4) {
    uint32_t result;
    __asm__ __volatile__("int $0x80" : "=a"(result)
        : "a"(number), "b"(a1), "c"(a2), "d"(a3), "S"(a4)
        : "r8", "r9", "r10", "r11", "memory", "cc");
    return (int32_t)result;
}

struct result {
    const char *name;
    bool passed, returned, timed_out;
    long value;
    int signal_number, exit_status, setup_errno;
};
static struct result results[MAX_RESULTS];
static size_t result_count;

static struct result *new_result(const char *name) {
    if (result_count == MAX_RESULTS) {
        puts("{\"protocol\":\"browser-seccomp-transport-v1\",\"passed\":false,"
             "\"error\":\"result_capacity\"}");
        (void)fflush(stdout);
        _exit(2);
    }
    struct result *r = &results[result_count++];
    r->name = name;
    r->exit_status = -1;
    return r;
}

static int raw_errno(long result) {
    return result < 0 && result >= -4095 ? (int)-result : 0;
}

static bool close_fd(long fd) {
    return fd >= 0 && raw_syscall6(__NR_close, (uint64_t)fd, 0, 0, 0, 0, 0) == 0;
}

static void socket_case(const char *name, uint64_t domain, bool pair, bool allowed) {
    int fds[2] = {-1, -1};
    struct result *r = new_result(name);
    r->value = raw_syscall6(pair ? __NR_socketpair : __NR_socket, domain,
        SOCK_STREAM | SOCK_CLOEXEC, 0, (uintptr_t)fds, 0, 0);
    r->returned = true;
    r->passed = allowed ? (pair ? r->value == 0 : r->value >= 0) : r->value == -EPERM;
    /* Close unexpected successes too; a denial failure must not leak resources. */
    if (pair && r->value == 0) {
        bool closed0 = close_fd(fds[0]);
        bool closed1 = close_fd(fds[1]);
        r->passed = r->passed && closed0 && closed1;
    } else if (!pair && r->value >= 0) {
        r->passed = close_fd(r->value) && r->passed;
    }
}

static void errno_case(const char *name, uint64_t number, uint64_t a1, uint64_t a2,
        uint64_t a3, uint64_t a4, uint64_t a5, int expected) {
    struct result *r = new_result(name);
    r->value = raw_syscall6(number, a1, a2, a3, a4, a5, 0);
    r->returned = true;
    r->passed = r->value == -expected;
    if (number == __NR_io_uring_setup && r->value >= 0)
        (void)close_fd(r->value);
}

enum child_kind { X32_SOCKET, X32_PAIR, I386_CALL_SOCKET, I386_CALL_PAIR,
                  I386_DIRECT_SOCKET, I386_DIRECT_PAIR, EXTRA_CLONE, EXTRA_UNSHARE };
struct child_case { const char *name; enum child_kind kind; uint64_t flags; };
static const struct child_case child_cases[] = {
    {"x32_socket_killed", X32_SOCKET, 0},
    {"x32_socketpair_killed", X32_PAIR, 0},
    {"i386_socketcall_socket_killed", I386_CALL_SOCKET, 0},
    {"i386_socketcall_socketpair_killed", I386_CALL_PAIR, 0},
    {"i386_socket_killed", I386_DIRECT_SOCKET, 0},
    {"i386_socketpair_killed", I386_DIRECT_PAIR, 0},
    /* Exact allowed clone flags plus CLONE_NEWNS; none is an allowed pattern. */
    {"clone_user_extra_mount_denied", EXTRA_CLONE, UINT64_C(0x10020011)},
    {"clone_user_pid_net_extra_mount_denied", EXTRA_CLONE, UINT64_C(0x70020011)},
    {"clone_pid_extra_mount_denied", EXTRA_CLONE, UINT64_C(0x20020011)},
    {"unshare_user_extra_mount_denied", EXTRA_UNSHARE, UINT64_C(0x10020000)},
    {"unshare_user_extra_net_denied", EXTRA_UNSHARE, UINT64_C(0x50000000)},
};

/* Shared return evidence prevents a later SIGSYS (e.g. on exit) being mistaken
 * for a syscall kill. MAP_32BIT gives compat syscalls actual valid pointers. */
struct shared_result {
    uint32_t arguments[4];
    int fds[2];
    volatile sig_atomic_t entered, returned;
    volatile long value;
};

static long child_syscall(const struct child_case *test, struct shared_result *shared) {
    uint32_t pointer = (uint32_t)(uintptr_t)shared->fds;
    uint32_t argument_pointer = (uint32_t)(uintptr_t)shared->arguments;
    shared->entered = 1;
    switch (test->kind) {
    case X32_SOCKET:
        return raw_syscall6(X32_BIT | __NR_socket, 40, SOCK_STREAM, 0, 0, 0, 0);
    case X32_PAIR:
        return raw_syscall6(X32_BIT | __NR_socketpair, 40, SOCK_STREAM, 0, pointer, 0, 0);
    case I386_CALL_SOCKET:
        return raw_i386_syscall4(I386_SOCKETCALL, 1, argument_pointer, 0, 0);
    case I386_CALL_PAIR:
        return raw_i386_syscall4(I386_SOCKETCALL, 8, argument_pointer, 0, 0);
    case I386_DIRECT_SOCKET:
        return raw_i386_syscall4(I386_SOCKET, 40, SOCK_STREAM, 0, 0);
    case I386_DIRECT_PAIR:
        return raw_i386_syscall4(I386_SOCKETPAIR, 40, SOCK_STREAM, 0, pointer);
    case EXTRA_CLONE:
        return raw_syscall6(__NR_clone, test->flags, 0, 0, 0, 0, 0);
    case EXTRA_UNSHARE:
        return raw_syscall6(__NR_unshare, test->flags, 0, 0, 0, 0, 0);
    }
    return -EINVAL;
}

static bool reap_bounded(pid_t pid, int *status, struct result *r) {
    const struct timespec delay = {.tv_sec = 0, .tv_nsec = CHILD_POLL_NS};
    for (unsigned i = 0; i < CHILD_WAIT_POLLS; ++i) {
        pid_t found = waitpid(pid, status, WNOHANG);
        if (found == pid)
            return true;
        if (found < 0 && errno != EINTR) {
            r->setup_errno = errno;
            break;
        }
        (void)nanosleep(&delay, NULL);
    }
    r->timed_out = true;
    (void)kill(pid, SIGKILL);
    for (unsigned i = 0; i < CHILD_WAIT_POLLS; ++i) {
        pid_t found = waitpid(pid, status, WNOHANG);
        if (found == pid)
            return true;
        if (found < 0 && errno != EINTR)
            break;
        (void)nanosleep(&delay, NULL);
    }
    return false;
}

static void run_child_case(const struct child_case *test) {
    struct result *r = new_result(test->name);
    struct shared_result *shared = mmap(NULL, 4096, PROT_READ | PROT_WRITE,
        MAP_SHARED | MAP_ANONYMOUS | MAP_32BIT, -1, 0);
    if (shared == MAP_FAILED) {
        r->setup_errno = errno;
        return; /* This result remains false; setup failure is never a skip/pass. */
    }
    if ((uintptr_t)shared > UINT32_MAX - 4096) {
        r->setup_errno = EOVERFLOW;
        (void)munmap(shared, 4096);
        return;
    }
    memset(shared, 0, sizeof(*shared));
    shared->fds[0] = shared->fds[1] = -1;
    shared->arguments[0] = 40;
    shared->arguments[1] = SOCK_STREAM;
    shared->arguments[3] = (uint32_t)(uintptr_t)shared->fds;
    long pid = raw_syscall6(__NR_fork, 0, 0, 0, 0, 0, 0);
    if (pid == 0) {
        long value = child_syscall(test, shared);
        /* If broken filtering permitted clone, terminate its new child before
         * it can overwrite the original probe child's shared return evidence. */
        if (test->kind == EXTRA_CLONE && value == 0)
            _exit(101);
        shared->value = value;
        shared->returned = 1;
        if (test->kind == EXTRA_CLONE && value > 0) {
            int nested_status;
            (void)waitpid((pid_t)value, &nested_status, 0);
        }
        _exit(0); /* The parent validates the exact return, not merely this exit. */
    }
    if (pid < 0) {
        r->setup_errno = raw_errno(pid);
        (void)munmap(shared, 4096);
        return;
    }
    int status = 0;
    bool reaped = reap_bounded((pid_t)pid, &status, r);
    r->returned = shared->returned != 0;
    r->value = shared->value;
    if (reaped) {
        if (WIFSIGNALED(status))
            r->signal_number = WTERMSIG(status);
        if (WIFEXITED(status))
            r->exit_status = WEXITSTATUS(status);
        bool expected_kill = test->kind <= I386_DIRECT_PAIR;
        r->passed = shared->entered == 1 && !r->timed_out && r->setup_errno == 0 &&
            (expected_kill ? (!r->returned && r->signal_number == SIGSYS) :
             (r->returned && r->value == -EPERM && r->exit_status == 0));
    }
    if (munmap(shared, 4096) != 0) {
        r->setup_errno = errno;
        r->passed = false;
    }
}

int main(void) {
    socket_case("native_inet_socket", AF_INET, false, true);
    socket_case("native_unix_socket", AF_UNIX, false, true);
    socket_case("native_unix_socketpair", AF_UNIX, true, true);
    static const struct { const char *socket_name, *pair_name; uint64_t domain; } vsock[] = {
        {"vsock_socket_zero_high_word", "vsock_socketpair_zero_high_word", UINT64_C(0x0000000000000028)},
        {"vsock_socket_one_high_word", "vsock_socketpair_one_high_word", UINT64_C(0x0000000100000028)},
        {"vsock_socket_sign_high_word", "vsock_socketpair_sign_high_word", UINT64_C(0x8000000000000028)},
        {"vsock_socket_max_high_word", "vsock_socketpair_max_high_word", UINT64_C(0xffffffff00000028)},
    };
    for (size_t i = 0; i < sizeof(vsock) / sizeof(vsock[0]); ++i) {
        socket_case(vsock[i].socket_name, vsock[i].domain, false, false);
        socket_case(vsock[i].pair_name, vsock[i].domain, true, false);
    }
    /* Invalid arguments bound effects if filtering is broken. An unrelated
     * EINVAL/EFAULT/EBADF/ENOSYS does NOT satisfy an EPERM denial expectation. */
    errno_case("io_uring_setup", __NR_io_uring_setup, 0, 0, 0, 0, 0, EPERM);
    errno_case("io_uring_enter", __NR_io_uring_enter, UINT64_MAX, 0, 0, 0, 0, EPERM);
    errno_case("io_uring_register", __NR_io_uring_register, UINT64_MAX, 0, 0, 0, 0, EPERM);
    errno_case("clone3_enosys", __NR_clone3, 0, 0, 0, 0, 0, ENOSYS);
    errno_case("setns_denied", __NR_setns, UINT64_MAX, 0, 0, 0, 0, EPERM);
    errno_case("mount_denied", __NR_mount, 0, 0, 0, 0, 0, EPERM);
    for (size_t i = 0; i < sizeof(child_cases) / sizeof(child_cases[0]); ++i)
        run_child_case(&child_cases[i]);

    bool passed = result_count == 28;
    for (size_t i = 0; i < result_count; ++i)
        passed = passed && results[i].passed;
    printf("{\"protocol\":\"browser-seccomp-transport-v1\","
        "\"architecture\":\"native-amd64\",\"expected_profile_sha256\":\"%s\","
        "\"passed\":%s,\"checks\":{", PROFILE_HASH, passed ? "true" : "false");
    for (size_t i = 0; i < result_count; ++i)
        printf("%s\"%s\":%s", i ? "," : "", results[i].name,
            results[i].passed ? "true" : "false");
    fputs("},\"observations\":{", stdout);
    for (size_t i = 0; i < result_count; ++i) {
        struct result *r = &results[i];
        printf("%s\"%s\":{\"returned\":%s,\"return\":%ld,\"errno\":%d,"
            "\"signal\":%d,\"exit_status\":%d,\"setup_errno\":%d,\"timed_out\":%s}",
            i ? "," : "", r->name, r->returned ? "true" : "false", r->value,
            r->returned ? raw_errno(r->value) : 0, r->signal_number, r->exit_status,
            r->setup_errno, r->timed_out ? "true" : "false");
    }
    fputs("}}\n", stdout);
    return passed ? 0 : 1;
}
