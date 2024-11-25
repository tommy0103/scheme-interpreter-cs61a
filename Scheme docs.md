### Problem 3

实现 `scheme_eval` 的 `BuiltinProcedure` 部分。

```
((print-then-return 1 +) 1 2)
```

需要意识到 `first` 并不总是一个可以被直接计算的值，可能会是一个 `Pair` 嵌套。

而且 `first.first` 计算完毕之后可能是一个 `Procedure` 或者是一个 `str`，需要继续和 `scheme_apply(eval_procedure, first.rest.map(scheme_eval_closure), env)`，并且也要考虑到这个值仍然可以继续用作 `Procedure` 来计算的可能。

### Problem 4

实现 `define` 定义变量。

```scheme
(define x 0)
; expect x
((define x (+ x 1)) 2)
; expect Error
x
; expect 1
```

仍然需要意识到 `first` 并不总是一个可以被直接计算的值，可能会是一个 `Pair` 嵌套。

在 `Special Form` 下处理 `first.first` 的情况使得 $\text{x}$ 在报错前被正确赋值。

### Problem 5

实现 `quote` 。

```scheme
(eval (define tau 6.28))
```

`eval` 并不是任何 `BuiltinProcedure`，需要自己实现，本质就是再 `scheme_eval` 一次。

### Problem 6-10

实现 `LambdaProcedure` 并在 `scheme_apply` 中实现对应情况。

主要问题出现在对于 `Special Form` 中 `first.first` 的处理，如果有 `expr` 在被计算之后返回了一个 `Procedure`，应该 `return scheme_apply(result, rest.map(scheme_eval_closure), env)`，而非随便返回一个值。 

```scheme
((lambda (x) (list x (list (quote quote) x))) (quote (lambda (x) (list x (list (quote quote) x))))) 
```

如果随便返回一个值就会出现表达式的值为 `()` 的情况（

### Problem 11

实现对 `Mu` 函数的支持，其中 `Mu` 函数是一种 `Dynamic scope` 函数。

本体实现并没有出现什么问题，问题出现在 `Lambda` 函数相同的逻辑

```scheme
(define (f x) (mu () (lambda (y) (+ x y))))
(define (f x) (lambda (y) (lambda (y) (+ x y))))
(define (g x) (((f (+ x 1))) (+ x 2)))
(g 3)
```

如果只是简单检查参数数量，会对 `(+ x 2)` 报错，而不会将这个部分作为参数传递给 $\lambda: y\to x+y$。在 `Problem 9` 处也添加相关逻辑，即如果有多的参数，传递给计算完成的表达式。

还有一个问题是对于 `scheme_eval` 函数中第一个有效 operator 并不总在 `first.first` 所在位置的问题，通过观察不难发现找到第一个 `rest` 不为 `nil` 的有效表达式计算即可。