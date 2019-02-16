from spl_parser import *
from spl_lib import *
from spl_lexer import BINARY_OPERATORS

LST = [72, 97, 112, 112, 121, 32, 66, 105, 114, 116, 104, 100, 97, 121, 32,
       73, 115, 97, 98, 101, 108, 108, 97, 33, 33, 33]
PRI = {"int", "float", "Primitive", "NativeType"}


class Interpreter:
    """
    :type ast: Node
    :type argv: list
    :type encoding: str
    """

    def __init__(self, argv, encoding):
        self.ast = None
        self.argv = argv
        self.env = Environment(True, {})
        self.env.add_heap("system", System(argv, encoding))
        self.env.scope_name = "Global"

    def set_ast(self, ast: BlockStmt):
        """
        Sets up the abstract syntax tree to be interpreted.

        :param ast: the root of the abstract syntax tree to be interpreted
        :return: None
        """
        self.ast = ast

    def interpret(self):
        """
        Starts the interpretation.

        :return: the exit value
        """
        return evaluate(self.ast, self.env)


class ClassInstance:
    def __init__(self, env: Environment, class_name: str):
        """
        ===== Attributes =====
        :param class_name: name of this class
        :param env: instance attributes
        """
        self.class_name = class_name
        self.env = env
        self.env.variables["id"] = ID_COUNTER.get()
        ID_COUNTER.increment()
        self.env.variables["this"] = self

    def __hash__(self):
        if self.env.contains_key("__hash__"):
            call = psr.FuncCall((0, "interpreter"), "__hash__")
            call.args = []
            return inter.evaluate(call, self.env)
        else:
            return hash(self)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if self.env.contains_key("__str__"):
            call = psr.FuncCall((0, "interpreter"), "__str__")
            call.args = []
            return str(evaluate(call, self.env))
        else:
            return self.class_name + ": " + str(self.env.variables)
        # return bytes(LST).decode("ascii")


class RuntimeException(SplException):
    def __init__(self, exception: ClassInstance):
        SplException.__init__(self, "RuntimeException")

        self.exception = exception


def evaluate(node: Node, env: Environment):
    """
    Evaluates a abstract syntax tree node, with the corresponding working environment.

    :param node: the node in abstract syntax tree to be evaluated
    :param env: the working environment
    :return: the evaluation result
    """
    if node is None:
        return NULL
    elif node == NULL:
        return NULL
    elif env.terminated:
        return env.exit_value
    elif env.paused:
        return NULL
    # elif isinstance(node, int) or isinstance(node, float) or isinstance(node, Primitive) or \
    #         isinstance(node, NativeType):
    #     return node
    tn = type(node).__name__
    if tn in PRI:
        return node
    elif isinstance(node, Node):
        t = node.type
        node.execution += 1
        if t == INT_NODE:
            node: IntNode
            return node.value
        elif t == FLOAT_NODE:
            node: FloatNode
            return node.value
        elif t == LITERAL_NODE:
            node: LiteralNode
            # s = node.literal
            s = node.literal
            return String(s)
        elif t == NAME_NODE:
            node: NameNode
            value = env.get(node.name, (node.line_num, node.file))
            return value
        elif t == BOOLEAN_STMT:
            node: BooleanStmt
            if node.value in {"true", "false"}:
                return get_boolean(node.value == "true")
            else:
                raise InterpretException("Unknown boolean value")
        elif t == NULL_STMT:
            return NULL
        elif t == BREAK_STMT:
            env.break_loop()
        elif isinstance(node, ContinueStmt):
            env.pause_loop()
        elif isinstance(node, AssignmentNode):
            return assignment(node, env)
        elif isinstance(node, Dot):
            return call_dot(node, env)
        elif isinstance(node, AnonymousCall):
            evaluate(node.left, env)
            right = node.right.args
            fc = FuncCall((node.line_num, node.file), "=>")
            fc.args = right
            return evaluate(fc, env)
        elif t == OPERATOR_NODE:
            node: OperatorNode
            return eval_operator(node, env)
        elif t == NEGATIVE_EXPR:
            node: NegativeExpr
            value = evaluate(node.value, env)
            return -value
        elif t == NOT_EXPR:
            node: NotExpr
            value = evaluate(node.value, env)
            if value:
                return FALSE
            else:
                return TRUE
        elif t == RETURN_STMT:
            node: ReturnStmt
            value = node.value
            if isinstance(value, Node):
                res = evaluate(value, env)
            else:
                res = value
            # print(env.variables)
            env.terminate(res)
            return res
        elif t == BLOCK_STMT:
            node: BlockStmt
            result = 0
            for line in node.lines:
                result = evaluate(line, env)
            return result
        elif t == IF_STMT:
            node: IfStmt
            cond = evaluate(node.condition, env)
            if cond:
                return evaluate(node.then_block, env)
            else:
                return evaluate(node.else_block, env)
        elif t == WHILE_STMT:
            node: WhileStmt
            result = 0
            while not env.broken and evaluate(node.condition, env):
                result = evaluate(node.body, env)
                env.paused = False  # reset the environment the the next iteration
            env.broken = False  # reset the environment for next loop
            return result
        elif t == FOR_LOOP_STMT:
            node: ForLoopStmt
            arg_num = len(node.condition.lines)
            if arg_num == 3:
                return eval_for_loop(node, env)
            elif arg_num == 2:
                return eval_for_each_loop(node, env)
            else:
                raise InterpretException("Wrong argument number for 'for' loop, in {}, at line {}"
                                         .format(node.file, node.line_num))
        elif t == DEF_STMT:
            node: DefStmt
            f = Function(node.params, node.presets, node.body)
            f.outer_scope = env
            env.assign(node.name, f)
            if node.auth == lex.PRIVATE:
                env.add_private(node.name)
            return f
        elif t == FUNCTION_CALL:
            node: FuncCall
            return call_function(node, env)
        elif t == CLASS_STMT:
            node: ClassStmt
            cla = Class(node.class_name, node.block)
            cla.superclass_names = node.superclass_names
            env.assign(node.class_name, cla)
            return cla
        elif t == CLASS_INIT:
            node: ClassInit
            return init_class(node, env)
        elif t == INVALID_TOKEN:
            raise InterpretException("Argument error, in {}, at line {}"
                                     .format(node.file, node.line_num))
        elif t == ABSTRACT:
            raise AbstractMethodException("Method is not implemented, in {}, at line {}"
                                          .format(node.file, node.line_num))
        elif t == THROW_STMT:
            node: ThrowStmt
            raise RuntimeException(evaluate(node.value, env))
        elif t == TRY_STMT:
            node: TryStmt
            return eval_try_catch(node, env)
        elif isinstance(node, JumpNode):
            func: Function = env.get(node.to, (0, "f"))
            for i in range(len(node.args.lines)):
                env.assign(func.params[i].name, evaluate(node.args.lines[i], env))
            return evaluate(func.body, env)
        else:
            raise InterpretException("Invalid Syntax Tree in {}, at line {}".format(node.file, node.line_num))
    else:
        raise InterpretException("Invalid Syntax Tree in {}, at line {}".format(node.file, node.line_num))


def eval_for_loop(node: ForLoopStmt, env: Environment):
    con: BlockStmt = node.condition
    start = con.lines[0]
    end = con.lines[1]
    step = con.lines[2]
    result = evaluate(start, env)
    while not env.broken and evaluate(end, env):
        result = evaluate(node.body, env)
        env.paused = False
        evaluate(step, env)
    env.broken = False
    return result


def eval_for_each_loop(node: ForLoopStmt, env: Environment):
    con: BlockStmt = node.condition
    invariant = con.lines[0].name
    target = con.lines[1]
    iterable = evaluate(target, env)
    if isinstance(iterable, Iterable):
        result = None
        for x in iterable:
            env.assign(invariant, x)
            result = evaluate(node.body, env)
            env.paused = False
            if env.broken:
                break
        env.broken = False
        return result
    elif isinstance(iterable, ClassInstance) and is_subclass_of(env.get_class(iterable.class_name), "Iterable", env):
        lf = (0, "interpreter")
        ite = FuncCall(lf, "__iter__")
        iterator: ClassInstance = evaluate(ite, iterable.env)
        result = None
        while not env.broken:
            nex = FuncCall(lf, "__next__")
            r = evaluate(nex, iterator.env)
            if isinstance(r, ClassInstance) and is_subclass_of(env.get_class(r.class_name), "StopIteration", env):
                break
            env.assign(invariant, r)
            result = evaluate(node.body, env)
            env.paused = False
        env.broken = False
        return result
    else:
        raise SplException("For-each loop on non-iterable objects, in {}, at line {}".format(node.file, node.line_num))


def eval_try_catch(node: TryStmt, env: Environment):
    try:
        result = evaluate(node.try_block, env)
        env.terminated = False
        return result
    except RuntimeException as re:  # catches the exceptions thrown by SPL program
        exception: ClassInstance = re.exception
        exception_class = env.get_class(exception.class_name)
        catches = node.catch_blocks
        for cat in catches:
            for line in cat.condition.lines:
                catch_name = line.right.name
                if is_subclass_of(exception_class, catch_name, env):
                    result = evaluate(cat.then, env)
                    env.terminated = False
                    return result
                    # if node.finally_block is None:
                    #     return result
                    # else:
                    #     env.terminated = False
        raise re
    except Exception as e:  # catches the exceptions raised by python
        catches = node.catch_blocks
        for cat in catches:
            for line in cat.condition.lines:
                catch_name = line.right.name
                # exception_name = exception.class_name
                if catch_name == "Exception":
                    result = evaluate(cat.then, env)
                    env.terminated = False
                    return result
                    # if node.finally_block is None:
                    #     return result
                    # else:
                    #     env.terminated = False
        raise e
    finally:
        if node.finally_block:
            return evaluate(node.finally_block, env)


def is_subclass_of(child_class: Class, class_name: str, env: Environment) -> bool:
    """
    Returns whether the child class is the ancestor class itself or inherited from that class.

    :param child_class: the child class to be check
    :param class_name: the ancestor class
    :param env: the environment, doesn't matter whether it is global or not
    :return: whether the child class is the ancestor class itself or inherited from that class
    """
    if child_class.class_name == class_name:
        return True
    else:
        return any([is_subclass_of(env.get_class(ccn), class_name, env) for ccn in child_class.superclass_names])


def eval_operator(node: OperatorNode, env: Environment):
    if isinstance(node.left, Node):
        left = evaluate(node.left, env)
    else:
        left = node.left
    if node.assignment:
        right = evaluate(node.right, env)
        symbol = node.operation[:-1]
        res = arithmetic(left, right, symbol, env)
        asg = AssignmentNode((node.line_num, node.file))
        asg.left = node.left
        asg.operation = "="
        asg.right = res
        return evaluate(asg, env)
    else:
        symbol = node.operation
        right_node = node.right
        return arithmetic(left, right_node, symbol, env)


def assignment(node: AssignmentNode, env: Environment):
    key = node.left
    v = node.right
    value = evaluate(node.right, env)
    t = key.type
    if t == NAME_NODE:
        env.assign(key.name, value)
        if key.auth == lex.PRIVATE:
            env.add_private(key.name)
        return value
    elif t == DOT:
        node = key
        name_lst = []
        while isinstance(node, Dot):
            name_lst.append(node.right.name)
            node = node.left
        name_lst.append(node.name)
        name_lst.reverse()
        # print(name_lst)
        scope = env
        for t in name_lst[:-1]:
            scope = scope.get(t, (node.line_num, node.file)).env
        scope.assign(name_lst[-1], value)
        return value
    else:
        raise InterpretException("Unknown assignment, in {}, at line {}".format(node.file, node.line_num))


def init_class(node: ClassInit, env: Environment):
    cla: Class = env.get_class(node.class_name)

    scope = Environment(False, env.heap)
    scope.scope_name = "Class scope<{}>".format(cla.class_name)
    class_inheritance(cla, env, scope)

    # print(scope.variables)
    instance = ClassInstance(scope, node.class_name)
    for k in scope.variables:
        v = scope.variables[k]
        if isinstance(v, Function):
            # v.parent = instance
            v.outer_scope = scope

    if node.args:
        # constructor: Function = scope.variables[node.class_name]
        fc = FuncCall((node.line_num, node.file), node.class_name)
        fc.args = node.args
        for a in fc.args.lines:
            scope.temp_vars.append(evaluate(a, env))
        # print(scope.variables)
        evaluate(fc, scope)
    return instance


def call_function(node: FuncCall, env: Environment):
    func = env.get(node.f_name, (node.line_num, node.file))
    if isinstance(func, Function):
        scope = Environment(False, env.heap)
        scope.scope_name = "Function scope<{}>".format(node.f_name)
        scope.outer = func.outer_scope  # supports for closure

        if len(env.temp_vars) == len(func.params) > 0:
            for i in range(len(func.params)):
                scope.assign(func.params[i].name, env.temp_vars[i])
            env.temp_vars.clear()
        else:
            check_args_len(func, node)
            for i in range(len(func.params)):
                # Assign function arguments
                if i < len(node.args.lines):
                    arg = node.args.lines[i]
                else:
                    arg = func.presets[i]
                e = evaluate(arg, env)
                scope.assign(func.params[i].name, e)
        result = evaluate(func.body, scope)
        env.assign("=>", result)
        return result
    elif isinstance(func, NativeFunction):
        args = []
        for i in range(len(node.args.lines)):
            # args.append(evaluate(node.args[i], env))
            args.append(evaluate(node.args.lines[i], env))
        result = func.call(args)
        if isinstance(result, BlockStmt):
            # Special case for "eval"
            r = evaluate(result, env)
            return r
        else:
            return result
    else:
        raise InterpretException("Not a function call")


def check_args_len(function: Function, call: FuncCall):
    if call.args and not list(filter(lambda k: not isinstance(k, InvalidToken), function.presets)).count(True) \
           <= len(call.args.lines) <= len(function.params):
        raise SplException("Too few or too many arguments for function '{}', in '{}', at line {}"
                           .format(call.f_name, call.file, call.line_num))


def call_dot(node: Dot, env: Environment):
    instance = evaluate(node.left, env)
    obj = node.right
    t = obj.type
    if t == NAME_NODE:
        if isinstance(instance, NativeType):
            return native_types_invoke(instance, obj)
        elif isinstance(instance, ClassInstance):
            if instance.env.is_private(obj.name):
                raise UnauthorizedException("Class attribute {} has private access".format(obj.name))
            else:
                attr = instance.env.variables[obj.name]
                return attr
        else:
            raise InterpretException("Not a class instance, in {}, at line {}".format(node.file, node.line_num))
    elif t == FUNCTION_CALL:
        if isinstance(instance, NativeType):
            try:
                return native_types_call(instance, obj, env)
            except IndexError as ie:
                raise IndexOutOfRangeException(str(ie) + " in file: '{}', at line {}"
                                               .format(node.file, node.line_num))
        elif isinstance(instance, ClassInstance):
            if instance.env.is_private(obj.f_name):
                raise UnauthorizedException("Class attribute {} has private access".format(obj.f_name))
            else:
                result = evaluate(obj, instance.env)
                env.assign("=>", result)
                return result
        else:
            raise InterpretException("Not a class instance, in {}, at line {}".format(node.file, node.line_num))
    else:
        raise InterpretException("Unknown Syntax")


def arithmetic(left, right_node: Node, symbol, env: Environment):
    if symbol in lex.LAZY:
        if isinstance(left, int) or isinstance(left, float):
            return num_and_or(left, right_node, symbol, env)
        elif isinstance(left, Primitive):
            return primitive_and_or(left, right_node, symbol, env)
        else:
            raise InterpretException("Operator '||' '&&' do not support type.")
    else:
        if isinstance(right_node, Node):
            right = evaluate(right_node, env)
        else:
            right = right_node
        if isinstance(left, int) or isinstance(left, float):
            return num_arithmetic(left, right, symbol)
        elif isinstance(left, String):
            return string_arithmetic(left, right, symbol)
        elif isinstance(left, Primitive):
            return primitive_arithmetic(left, right, symbol)
        elif isinstance(left, ClassInstance):
            return instance_arithmetic(left, right, symbol, env)
        else:
            return raw_type_comparison(left, right, symbol)


def instance_arithmetic(left: ClassInstance, right, symbol, env: Environment):
    if symbol == "===":
        return TRUE if isinstance(right, ClassInstance) and \
                       left.env.variables["id"] == right.env.variables["id"] else FALSE
    elif symbol == "!==":
        return TRUE if not isinstance(right, ClassInstance) or \
                       left.env.variables["id"] != right.env.variables["id"] else FALSE
    elif symbol == "instanceof":
        if isinstance(right, Class):
            return TRUE if is_subclass_of(env.get_class(left.class_name), right.class_name, env) else FALSE
        else:
            return FALSE
    else:
        fc = FuncCall((0, "interpreter"), "@" + BINARY_OPERATORS[symbol])
        left.env.temp_vars.append(right)
        res = evaluate(fc, left.env)
        return res


def string_arithmetic(left, right, symbol):
    if symbol == "==":
        result = left == right
    elif symbol == "!=":
        result = left != right
    elif symbol == "+":
        result = left + right
    elif symbol == "===":
        result = left == right
    elif symbol == "!==":
        result = left != right
    elif symbol == "instanceof":
        if isinstance(right, NativeFunction) and right.name == "string":
            return TRUE
        else:
            return FALSE
    else:
        raise TypeException("Unsupported operation between string and " + typeof(right))

    return result


def raw_type_comparison(left, right, symbol):
    if symbol == "==":
        result = left == right
    elif symbol == "!=":
        result = left != right
    elif symbol == "===":
        result = left == right
    elif symbol == "!==":
        result = left != right
    elif symbol == "instanceof":
        if isinstance(right, String):
            return TRUE if type(left).__name__ == right.literal else FALSE
        else:
            return FALSE
    else:
        raise InterpretException("Unsupported operation for raw type " + left.type_name())

    return get_boolean(result)


def primitive_and_or(left: Primitive, right_node: Node, symbol, env: Environment):
    if left:
        if symbol == "&&":
            right = evaluate(right_node, env)
            return get_boolean(right)
        elif symbol == "||":
            return TRUE
        else:
            raise InterpretException("Unsupported operation for primitive type " + left.type_name())
    else:
        return FALSE


def primitive_arithmetic(left: Primitive, right, symbol):
    if symbol == "==":
        result = left == right
    elif symbol == "!=":
        result = left != right
    elif symbol == "===":
        result = left == right
    elif symbol == "!==":
        result = left != right
    elif symbol == "instanceof":
        if isinstance(right, NativeFunction) and right.name == left.type_name():
            return TRUE
        else:
            return FALSE
    else:
        raise InterpretException("Unsupported operation for primitive type " + left.type_name())

    return get_boolean(result)


def num_and_or(left, right_node: Node, symbol, env: Environment):
    if left:
        if symbol == "||":
            return TRUE
        elif symbol == "&&":
            right = evaluate(right_node, env)
            return get_boolean(right)
        else:
            raise InterpretException("No such symbol")
    else:
        return FALSE


def num_arithmetic(left, right, symbol):
    if symbol == "+":
        result = left + right
    elif symbol == "-":
        result = left - right
    elif symbol == "*":
        result = left * right
    elif symbol == "/":
        result = left / right
    elif symbol == "%":
        result = left % right
    elif symbol == "==":
        result = left == right
    elif symbol == "!=":
        result = left != right
    elif symbol == ">":
        result = left > right
    elif symbol == "<":
        result = left < right
    elif symbol == ">=":
        result = left >= right
    elif symbol == "<=":
        result = left <= right
    elif symbol == "<<":
        result = left << right
    elif symbol == ">>":
        result = left >> right
    elif symbol == "&":
        result = left & right
    elif symbol == "^":
        result = left ^ right
    elif symbol == "|":
        result = left | right
    elif symbol == "===":
        result = left == right
    elif symbol == "!==":
        result = left != right
    elif symbol == "instanceof":
        if isinstance(right, NativeFunction) and right.name == type(left).__name__:
            return TRUE
        else:
            return FALSE
    else:
        raise InterpretException("No such symbol")

    if isinstance(result, bool):
        return get_boolean(result)
    else:
        return result


def class_inheritance(cla, env, scope):
    """

    :param cla:
    :type cla: Class
    :param env: the global environment
    :type env: Environment
    :param scope: the class scope
    :type scope: Environment
    :return:
    """
    for sc in cla.superclass_names:
        class_inheritance(env.get_class(sc), env, scope)

    evaluate(cla.body, scope)  # this step just fills the scope


def native_types_call(instance, method, env):
    """

    :param instance:
    :type instance: NativeType
    :param method:
    :type method: FuncCall
    :type env: Environment
    :return:
    """
    args = []
    for x in method.args.lines:
        args.append(evaluate(x, env))
    name = method.f_name
    type_ = type(instance)
    method = getattr(type_, name)
    res = method(instance, *args)
    return res


def native_types_invoke(instance: NativeType, node: NameNode):
    """

    :param instance:
    :param node:
    :return:
    """
    name = node.name
    type_ = type(instance)
    res = getattr(type_, name)
    return res


def get_boolean(expr):
    if expr:
        return TRUE
    else:
        return FALSE
