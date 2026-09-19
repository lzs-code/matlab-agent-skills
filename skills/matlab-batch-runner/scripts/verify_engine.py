"""验证 MATLAB Engine for Python：能否启动、能否连续调用、省了多少冷启动时间。"""
import time

t0 = time.time()
import matlab.engine  # noqa: E402

t_import = time.time() - t0

t1 = time.time()
eng = matlab.engine.start_matlab()
t_start = time.time() - t1

print(f"[1] import 耗时      : {t_import:.1f}s")
print(f"[2] 引擎启动耗时     : {t_start:.1f}s")
print(f"[3] 版本             : {eng.version()}")

# 连续调用，验证不再重复付启动成本
t2 = time.time()
results = []
for expr in ["max(sin(0:0.01:2*pi))", "eig([2 0; 0 3])", "sum(1:100)"]:
    results.append(eng.eval(expr, nargout=1))
t_calls = time.time() - t2

print(f"[4] 连续 3 次调用耗时: {t_calls:.2f}s  (平均 {t_calls/3:.2f}s/次)")
for expr, val in zip(["max(sin)", "eig", "sum(1:100)"], results):
    print(f"      {expr:14s} = {val}")

# 数组双向传递
nums = matlab.double([1.0, 4.0, 9.0, 16.0])
sq = eng.sqrt(nums)
print(f"[5] 数组传递 sqrt    : {list(sq)}")

# 工作区变量 + 取值
eng.workspace["a"] = 3.0
eng.workspace["b"] = 4.0
print(f"[6] 工作区 hypot(3,4): {eng.eval('hypot(a, b)', nargout=1)}")

eng.quit()
t_total = time.time() - t0
print(f"[7] 全程总耗时       : {t_total:.1f}s")
print("VERIFY_OK")
