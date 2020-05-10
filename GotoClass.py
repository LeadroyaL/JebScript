# author = LeadroyaL

from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext, IUnitView, IUnitFragment
from com.pnfsoftware.jeb.core.units.code.android import IDexUnit, IApkUnit
from com.pnfsoftware.jeb.core.units.code.android.dex import IDexClass

class GotoClass(IScript):
    def run(self, ctx):
        if not isinstance(ctx, IGraphicalClientContext):
            print ('This script must be run within a graphical client')
            return

        apk = None
        for u in ctx.getEnginesContext().getProject(0).getLiveArtifact(0).getUnits():
            if isinstance(u, IApkUnit):
                apk = u
                break
        if not apk:
            print('APK unit not found')
            return
        # auto completed with focusText
        focusText = ctx.getFocusedView().getActiveFragment().getActiveItemAsText()
        className = ctx.displayQuestionBox("ClassName",
                                           "input class name(eg. com.test.classname, Lcom/test/classname;):",
                                           focusText)
        if not className:
            print ('Please input classname')
            return

        self.goto(ctx, apk, className)

        print ('Run script finished')

    def goto(self, ctx, apk, className):
        assert isinstance(apk, IApkUnit)
        dexUnit = None
        dexClass = None
        if className[0] == 'L' and className[-1] == ';':
            genericName = className
        else:
            genericName = 'L' + className.replace('.', '/') + ';'
        for u in apk.getChildren():
            if isinstance(u, IDexUnit):
                dexClass = u.getClass(genericName)
                if dexClass:
                    dexUnit = u
                    print ("FIND %s AT %s" % (genericName, u.getName()))
                    break

        if not dexClass or not dexUnit:
            print("CANNOT FIND %s" % genericName)
            return

        assert isinstance(dexClass, IDexClass)
        assert isinstance(dexUnit, IDexUnit)

        # open disasembly view
        if not ctx.openView(dexUnit):
            print("open disasembly fail")
            return

        # focus it
        disasmFragment = None
        for view in ctx.getViews():
            assert isinstance(view, IUnitView)
            if view.getUnit() == dexUnit:
                for fragment in view.getFragments():
                    if view.getFragmentLabel(fragment) == 'Disassembly':
                        view.setFocus()
                        view.setActiveFragment(fragment)
                        disasmFragment = fragment

        if not disasmFragment:
            print ('Disassembly fragment for %s not found' % dexUnit.getName())
            return

        assert isinstance(disasmFragment, IUnitFragment)
        disasmFragment.setActiveAddress(genericName)
