#? shortcut=Shift+X
# author: LeadroyaL

from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
from com.pnfsoftware.jeb.core.units.code.java import IJavaSourceUnit

FMT_NO_PARAMS = """XposedHelpers.findAndHookMethod("%s", classLoader, "%s", new XC_MethodHook() {
    @Override
    protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
        super.beforeHookedMethod(param);
    }
    @Override
    protected void afterHookedMethod(MethodHookParam param) throws Throwable {
        super.afterHookedMethod(param);
    }
});"""

FMT_WITH_PARAMS = """XposedHelpers.findAndHookMethod("%s", classLoader, "%s", %s, new XC_MethodHook() {
    @Override
    protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
        super.beforeHookedMethod(param);
    }
    @Override
    protected void afterHookedMethod(MethodHookParam param) throws Throwable {
        super.afterHookedMethod(param);
    }
});"""


class FastXposed(IScript):
    def run(self, ctx):
        if not isinstance(ctx, IGraphicalClientContext):
            print ('This script must be run within a graphical client')
            return
        if not isinstance(ctx.getFocusedView().getActiveFragment().getUnit(), IJavaSourceUnit):
            print ('This script must be run within IJavaSourceUnit')
            return
        sig = ctx.getFocusedView().getActiveFragment().getActiveAddress()
        clz, method = sig.split("->")
        assert isinstance(method, unicode)
        methodName = method[0:method.index('(')]
        params = self.split(method[method.index('(') + 1:method.index(')')])
        if len(params) == 0:
            print FMT_NO_PARAMS % (
                clz[1:-1].replace('/', '.'),
                methodName)
        else:
            print FMT_WITH_PARAMS % (
                clz[1:-1].replace('/', '.'), methodName,
                ','.join([self.toXposed(x.replace('/', '.')) for x in params]))

    def toXposed(self, param):
        depth = 0
        while param[depth] == '[':
            depth += 1
        if param[-1] == ';':
            return '"' + param[depth + 1:-1] + '"' + "[]" * depth
        else:
            return self.basicTypeMap[param[depth]] + "[]" * depth + ".class"

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
