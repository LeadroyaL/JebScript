# author: LeadroyaL

from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
from com.pnfsoftware.jeb.core.units.code.java import IJavaSourceUnit

FMT = """Java.use("{class_name}")
    .{method_name}
    .overload({param_list})
    .implementation = function (this, ...args) {{ // for javascript
    // .implementation = function (this: Java.Wrapper, ...args: any[]) {{ // for typescript
        console.log("before hooked {method_sig}");
        this.{method_name}({args_list});
        console.log("after hooked {method_sig}");
    }};"""


class FastFrida(IScript):
    def run(self, ctx):
        if not isinstance(ctx, IGraphicalClientContext):
            print ('This script must be run within a graphical client')
            return
        if not isinstance(ctx.getFocusedView().getActiveFragment().getUnit(), IJavaSourceUnit):
            print ('This script must be run within IJavaSourceUnit')
            return
        sig = ctx.getFocusedView().getActiveFragment().getActiveAddress()
        clz, method = sig.split("->")
        assert isinstance(clz, unicode)
        assert isinstance(method, unicode)
        params = self.split(method[method.index('(') + 1:method.index(')')])
        print FMT.format(
            class_name=clz[1:-1].replace('/', '.'),
            method_name=method[0:method.index('(')],
            method_sig=sig,
            param_list=','.join([self.toFrida(x) for x in params]),
            args_list=self.gen_args(params))

    def gen_args(self, params):
        return ','.join(['args[%d]' % i for i in range(len(params))])

    def toFrida(self, param):
        # input: [I, return: "[I"
        # input: [Ljava/lang/String; return: "[Ljava.lang.String;"
        if param[0] == '[':
            return '"' + param.replace('/', '.') + '"'
        # input: Ljava/lang/String; return: "java.lang.String"
        # input: I, return: "int"
        else:
            if param[-1] == ';':
                return '"' + param[1:-1].replace('/', '.') + '"'
            else:
                return '"' + self.basicTypeMap[param[0]] + '"'

    basicTypeMap = {'C': u'char',
                    'B': u'byte',
                    'D': u'double',
                    'F': u'float',
                    'I': u'int',
                    'J': u'long',
                    'L': u'ClassName',
                    'S': u'short',
                    'Z': u'boolean',
                    '[': u'Reference',
                    }

    def split(self, params):
        ret = []
        offset = 0
        length = len(params)
        while offset < length:
            startIdx = offset
            while params[offset] == '[':
                offset += 1
            char = params[offset]
            if char == 'L':
                end = params.index(';', offset)
                ret.append(params[startIdx: end + 1])
                offset = end
            elif char in self.basicTypeMap:
                ret.append(params[startIdx: offset + 1])
            offset += 1
        return ret
